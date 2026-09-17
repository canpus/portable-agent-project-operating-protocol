#!/usr/bin/env python3
"""Build the three reproducible PAPOP v5 ZIP distributions."""

from __future__ import annotations

import argparse, hashlib, io, json, re, tempfile, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
COMMON = ("README.md", "README_EN.md", "LICENSE", "VERSION", "CHANGELOG.md", ".gitattributes", ".editorconfig",
          "docs/INSTALL.md", "docs/MIGRATION.md", "docs/BEHAVIOR_CHECKS.md",
          "docs/WHY.md", "docs/WHY_EN.md", "docs/HOW.md", "docs/HOW_EN.md",
          "docs/diagrams/v5-user-workflow.mmd", "docs/diagrams/v5-user-workflow.png",
          "docs/diagrams/v5-agent-state-ledger-flow.mmd", "docs/diagrams/v5-agent-state-ledger-flow.png")
PROFILES = {"strict-approval": "STRICT_APPROVAL", "autonomous": "AUTONOMOUS"}


def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


def read_version(root: Path = ROOT) -> str:
    value = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", value): raise ValueError(f"invalid VERSION: {value!r}")
    return value


def valid_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and "\\" not in name and ":" not in name and all(p not in {"", ".", ".."} for p in name.split("/"))


def source(root: Path, name: str) -> bytes:
    path = root / name
    if not valid_member(name) or not path.is_file() or not path.resolve().is_relative_to(root.resolve()): raise ValueError(f"missing or unsafe source: {name}")
    return path.read_bytes()


def tree(root: Path, relative: str, suffixes: set[str]) -> dict[str, bytes]:
    result = {}
    for path in sorted(p for p in (root / relative).rglob("*") if p.is_file() and p.suffix in suffixes):
        name = path.relative_to(root).as_posix(); result[name] = source(root, name)
    return result


def render_entry(template: str, mode: str, version: str) -> bytes:
    if mode not in set(PROFILES.values()): raise ValueError("invalid profile")
    if template.count("@@GOVERNANCE_MODE@@") != 1: raise ValueError("entry token must occur exactly once")
    rendered = template.replace("@@GOVERNANCE_MODE@@", mode)
    if "@@" in rendered or f"PROTOCOL_VERSION: {version}" not in rendered: raise ValueError("unresolved token or version mismatch")
    return rendered.encode()


def guide(profile: str, version: str) -> bytes:
    description = {
        "global-rules-only": "只安装模块化全局行为规则，不启用任务状态机。",
        "strict-approval": "需求、Goal、每个 Stage Plan 与 Delivery 均经过精确人工审查。",
        "autonomous": "Task 授权后持续执行，只在关键决定、具体授权或用户关卡处等待。",
    }[profile]
    return f"""# PAPOP v{version} · {profile}

{description}

## 安装

1. 把 `GlobalRules/` 的完整内容（包括隐藏的 `.agent-rules/`）合并到宿主的全局规则位置。
2. 状态机包还需把 `ProjectRules/` 内容合并到工作区根，并保留 `.agent-protocol/`。
3. 不覆盖既有规则；先备份并人工合并冲突。按 `docs/INSTALL.md` 做只读加载验证。

Source: https://github.com/canpus/portable-agent-project-operating-protocol
""".encode()


def package_entries(root: Path = ROOT) -> dict[str, dict[str, bytes]]:
    version = read_version(root)
    common = {name: source(root, name) for name in COMMON}
    global_files = tree(root, "GlobalRules", {".md"})
    project_files = tree(root, "ProjectRules/.agent-protocol", {".md", ".txt", ".ps1", ".cmd", ".sh"})
    if len(global_files) != 8 or not project_files: raise ValueError("rule source tree is incomplete")
    template = (root / "ProjectRules/AGENTS.template.md").read_text(encoding="utf-8")
    packages = {}
    for profile in ("global-rules-only", *PROFILES):
        entries = dict(common); entries.update(global_files); mode = None
        if profile in PROFILES:
            mode = PROFILES[profile]; entries.update(project_files)
            entries["ProjectRules/README.md"] = source(root, "ProjectRules/README.md")
            entries["ProjectRules/AGENTS.md"] = render_entry(template, mode, version)
        entries["PACKAGE.md"] = guide(profile, version)
        manifest = {"schema": "PAPOP-PACKAGE-3", "version": version, "profile": profile,
                    "governance_mode": mode,
                    "files": {name: sha256(data) for name, data in sorted(entries.items())}}
        entries["MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        packages[f"portable-agent-project-operating-protocol-v{version}-{profile}.zip"] = entries
    return packages


def zip_bytes(entries: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            if not valid_member(name): raise ValueError(f"unsafe ZIP member: {name}")
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.create_system = 3; info.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16; info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return output.getvalue()


def atomic_write(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle: temporary = Path(handle.name); handle.write(data)
        temporary.replace(path)
    finally:
        if temporary and temporary.exists(): temporary.unlink()


def build(root: Path = ROOT, output: Path | None = None, overwrite: bool = False) -> list[dict]:
    root = root.resolve(); output = (output or root / "dist").resolve()
    artifacts = {name: zip_bytes(entries) for name, entries in package_entries(root).items()}
    records = [{"file": n, "bytes": len(d), "sha256": sha256(d)} for n, d in sorted(artifacts.items())]
    artifacts["SHA256SUMS"] = "".join(f"{r['sha256']}  {r['file']}\n" for r in records).encode()
    artifacts["release-manifest.json"] = (json.dumps({"schema": "PAPOP-RELEASE-3", "version": read_version(root), "packages": records}, ensure_ascii=False, indent=2) + "\n").encode()
    for name, data in artifacts.items():
        target = output / name
        if target.exists() and (not target.is_file() or (target.read_bytes() != data and not overwrite)): raise FileExistsError(f"different artifact exists: {target}")
    output.mkdir(parents=True, exist_ok=True)
    for name, data in artifacts.items():
        if not (output / name).exists() or (output / name).read_bytes() != data: atomic_write(output / name, data)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path); parser.add_argument("--overwrite", action="store_true"); args = parser.parse_args()
    for item in build(output=args.output, overwrite=args.overwrite): print(f"{item['file']} ({item['bytes']} bytes)")


if __name__ == "__main__": main()
