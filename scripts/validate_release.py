#!/usr/bin/env python3
"""Validate PAPOP v5 sources, byte policy, and release archives."""
from __future__ import annotations
import argparse, json, posixpath, re, sys, zipfile
from pathlib import Path
try:
    from scripts import build_release
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from scripts import build_release

ROOT=Path(__file__).resolve().parents[1]
GLOBAL={"collaboration-and-continuity.md","environments-and-dependencies.md","evidence-and-research.md","external-actions-and-data.md","implementation.md","tools-and-verification.md","workspace-and-version-control.md"}
RULES={"autonomous.md","cases.md","checkpoint.md","intake.md","lifecycle.md","recovery.md","strict-approval.md"}
TEMPLATES={"case-index-entry.md","case.md","current-state.md","decision.md","gitignore-recommended.txt","goal-revision.md","plan-revision.md"}
TOOLS={"checkpoint.cmd","checkpoint.ps1","checkpoint-core.ps1","checkpoint.sh","intake.cmd","intake.ps1","intake.sh"}

def byte_errors(name:str,data:bytes)->list[str]:
    out=[]
    if data.startswith(b"\xef\xbb\xbf") or data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"): out.append(f"{name}: BOM forbidden")
    if name.endswith((".cmd",".bat")):
        if data.replace(b"\r\n",b"").find(b"\n")>=0 or data.replace(b"\r\n",b"").find(b"\r")>=0: out.append(f"{name}: CMD must use CRLF only")
        if data and not data.endswith(b"\r\n"): out.append(f"{name}: missing CRLF at EOF")
    elif name.endswith((".md",".json",".toml",".yml",".yaml",".py",".sh",".ps1",".txt",".mmd")) or Path(name).name in {"LICENSE","VERSION",".gitattributes",".editorconfig",".gitignore"}:
        if b"\r" in data: out.append(f"{name}: LF text contains CR")
        if data and not data.endswith(b"\n"): out.append(f"{name}: missing LF at EOF")
    if name.endswith((".ps1",".cmd")):
        try: data.decode("ascii")
        except UnicodeDecodeError: out.append(f"{name}: Windows script must be ASCII")
    return out

def link_errors(name:str,data:bytes,members:set[str])->list[str]:
    if not name.endswith(".md"): return []
    out=[]
    for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)",data.decode("utf-8")):
        target=raw.strip().strip("<>").split("#",1)[0]
        if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:",target): continue
        resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
        if resolved.startswith("../") or resolved not in members: out.append(f"{name}: broken link {raw}")
    return out

def validate_sources(root:Path=ROOT)->list[str]:
    out=[]
    if not build_release.read_version(root): out.append("VERSION is unreadable")
    if {p.name for p in (root/"GlobalRules/.agent-rules").glob("*.md")}!=GLOBAL: out.append("global module set mismatch")
    if {p.name for p in (root/"ProjectRules/.agent-protocol/rules").glob("*.md")}!=RULES: out.append("project rule set mismatch")
    if {p.name for p in (root/"ProjectRules/.agent-protocol/templates").glob("*") if p.is_file()}!=TEMPLATES: out.append("template set mismatch")
    if {p.name for p in (root/"ProjectRules/.agent-protocol/tools").glob("*") if p.is_file()}!=TOOLS: out.append("tool set mismatch")
    active=[root/n for n in build_release.COMMON]
    active += [p for d in (root/"GlobalRules",root/"ProjectRules",root/"profiles",root/"scripts",root/"tests") for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    for p in active: out += byte_errors(p.relative_to(root).as_posix(),p.read_bytes())
    text="\n".join((root/p).read_text(encoding="utf-8") for p in ("ProjectRules/AGENTS.template.md","ProjectRules/.agent-protocol/SCHEMA.md"))
    for value in ("STRICT_APPROVAL","AUTONOMOUS","SESSION_ID","STAGE_ID","CASE_RECOMMENDATION_REQUIRED","UserInput/I-NNNN","SNAPSHOT_START_LINE","SNAPSHOT_BLOCK_SHA256"):
        if value not in text: out.append(f"protocol misses {value}")
    try: packages=build_release.package_entries(root)
    except Exception as exc: return out+[f"package render failed: {exc}"]
    if len(packages)!=3: out.append("exactly three packages required")
    for name,entries in packages.items():
        if name.endswith("global-rules-only.zip") and any(k.startswith("ProjectRules/") for k in entries): out.append("GlobalRules Only contains ProjectRules")
        if not name.endswith("global-rules-only.zip"):
            if any(k.endswith(".py") for k in entries if k.startswith("ProjectRules/")): out.append(f"{name}: Python runtime leaked")
            for tool in TOOLS:
                if f"ProjectRules/.agent-protocol/tools/{tool}" not in entries: out.append(f"{name}: missing {tool}")
    return out

def validate_dist(root:Path=ROOT,dist:Path|None=None)->list[str]:
    dist=(dist or root/"dist").resolve(); expected=build_release.package_entries(root); out=[]; paths=sorted(dist.glob("*.zip")) if dist.exists() else []
    if {p.name for p in paths}!=set(expected): return ["distribution ZIP set mismatch"]
    records=[]; globals_seen=[]
    for p in paths:
        with zipfile.ZipFile(p) as z:
            infos=z.infolist(); members={i.filename:z.read(i.filename) for i in infos}
        if members!=expected[p.name]: out.append(f"{p.name}: archive differs from source")
        if any(i.date_time!=(1980,1,1,0,0,0) or i.flag_bits&1 for i in infos): out.append(f"{p.name}: non-reproducible metadata")
        manifest=json.loads(members["MANIFEST.json"]); hashes={n:build_release.sha256(d) for n,d in sorted(members.items()) if n!="MANIFEST.json"}
        if manifest.get("files")!=hashes: out.append(f"{p.name}: manifest mismatch")
        for n,d in members.items(): out+=byte_errors(f"{p.name}:{n}",d); out+=link_errors(n,d,set(members))
        globals_seen.append({n:d for n,d in members.items() if n.startswith("GlobalRules/")}); records.append({"file":p.name,"bytes":p.stat().st_size,"sha256":build_release.sha256(p.read_bytes())})
    if any(g!=globals_seen[0] for g in globals_seen[1:]): out.append("GlobalRules bytes differ across packages")
    records.sort(key=lambda x:x["file"]); sums="".join(f"{r['sha256']}  {r['file']}\n" for r in records).encode()
    if not (dist/"SHA256SUMS").is_file() or (dist/"SHA256SUMS").read_bytes()!=sums: out.append("SHA256SUMS mismatch")
    rel=dist/"release-manifest.json"
    if not rel.is_file() or json.loads(rel.read_text(encoding="utf-8")).get("packages")!=records: out.append("release manifest mismatch")
    return out

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--source-only",action="store_true");ap.add_argument("--dist",type=Path);a=ap.parse_args();errors=validate_sources(ROOT)
    if not a.source_only: errors+=validate_dist(ROOT,a.dist)
    if errors:
        for e in errors: print("ERROR:",e)
        raise SystemExit(1)
    print("PAPOP v5 validation passed.")
if __name__=="__main__":main()
