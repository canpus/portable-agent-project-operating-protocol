#!/usr/bin/env python3
"""Build PAPOP distribution ZIPs using only Python's standard library."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
COMMON_FILES = (
    "README.md", "README_EN.md", "LICENSE", "VERSION", "CHANGELOG.md",
    "docs/INSTALL.md", "docs/MIGRATION.md", "docs/BEHAVIOR_CHECKS.md",
    "GlobalRules/AGENTS.md",
)
PROFILE_IDS = ("plan-approval", "task-delegation")
PROFILE_DEFAULTS = {
    "plan-approval": ("PLAN_APPROVAL", "TRACKED"),
    "task-delegation": ("TASK_DELEGATION", "AUTO"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_version(root: Path = ROOT) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Invalid VERSION: {version!r}")
    return version


def read_profiles(root: Path = ROOT) -> list[dict]:
    profiles = []
    actual = {p.stem for p in (root / "profiles").glob("*.json")}
    if actual != set(PROFILE_IDS):
        raise ValueError(f"Expected exactly these profiles: {PROFILE_IDS}; found {actual}")
    for profile_id in PROFILE_IDS:
        profile = json.loads((root / "profiles" / f"{profile_id}.json").read_text(encoding="utf-8"))
        if profile.get("id") != profile_id:
            raise ValueError(f"Profile identity mismatch: {profile_id}")
        pair = profile.get("governance_mode"), profile.get("record_mode")
        if pair != PROFILE_DEFAULTS[profile_id]:
            raise ValueError(f"Invalid distribution defaults for {profile_id}: {pair}")
        if not isinstance(profile.get("name"), str) or not profile["name"].strip():
            raise ValueError(f"Missing profile name: {profile_id}")
        profiles.append(profile)
    return profiles


def render_entry(template: str, mode: str, record_mode: str, version: str) -> bytes:
    if mode not in {"PLAN_APPROVAL", "TASK_DELEGATION"}:
        raise ValueError(f"Invalid governance mode: {mode}")
    if record_mode not in {"AUTO", "TRACKED"} or (mode == "PLAN_APPROVAL" and record_mode != "TRACKED"):
        raise ValueError(f"Invalid record mode for {mode}: {record_mode}")
    for token in ("@@GOVERNANCE_MODE@@", "@@RECORD_MODE@@"):
        if template.count(token) != 1:
            raise ValueError(f"Entry must contain exactly one {token}")
    text = template.replace("@@GOVERNANCE_MODE@@", mode).replace("@@RECORD_MODE@@", record_mode)
    if "@@" in text or f"PROTOCOL_VERSION: {version}" not in text:
        raise ValueError("Unresolved entry token or protocol version mismatch")
    return text.encode("utf-8")


def valid_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and "\\" not in name and ":" not in name and all(
        part not in {"", ".", ".."} for part in name.split("/")
    )


def source_bytes(root: Path, relative: str) -> bytes:
    path = root / relative
    if not valid_member(relative) or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Missing or out-of-root source: {relative}")
    return path.read_bytes()


def package_guide(profile: dict, version: str) -> bytes:
    if profile["id"] == "global-rules-only":
        details = "只有全局行为规则；不包含项目状态机。安装 GlobalRules 后即可使用，无需创建 .agent-work。"
        english = "Global behavior rules only. No project state machine or PAPOP ledger installation."
    elif profile["id"] == "plan-approval":
        details = "确认需求 → 批准精确计划 → 按批准范围执行 → 人工验收 → 关闭。实际任务始终 TRACKED，纯讨论不建账。计划内步骤不默认逐步重新批准。"
        english = "Confirm requirements, approve the exact plan, execute within scope, obtain human acceptance, then close. Actual tasks are TRACKED."
    else:
        details = "用户委托目标后，在授权范围内持续执行；缺关键决定、具体外部授权或遇用户指定关卡时等待。默认 AUTO，按恢复需要升级 TRACKED。"
        english = "Proceed within delegated task scope; wait for missing decisions, specific authorization, or user-defined gates. AUTO recording by default."
    text = f"""# {profile['name']} · v{version}

{details}

{english}

## 安装 / Install

1. 将 GlobalRules/AGENTS.md 安装到宿主实际支持的全局规则机制；已有规则先备份、合并。
2. 本包若有 ProjectRules，将其内容（含隐藏 .agent-protocol）复制并合并到目标项目根。
3. 不安装第二套项目入口、不覆盖原有规则或搬动项目资产。
4. 按 [安装说明](docs/INSTALL.md) 先只读验证加载。安装不授予真实权限。

Install GlobalRules through your host's supported mechanism. If ProjectRules is present, merge its contents into the project root, including the hidden directory. Use one entry and preserve existing assets and rules.

[完整说明 / Overview](README.md) · [English](README_EN.md) · [迁移 / Migration](docs/MIGRATION.md)

Source: https://github.com/canpus/portable-agent-project-operating-protocol
"""
    return text.encode("utf-8")


def package_entries(root: Path = ROOT) -> dict[str, dict[str, bytes]]:
    version = read_version(root)
    profiles = [{"id": "global-rules-only", "name": "GlobalRules Only", "governance_mode": None, "record_mode": None}]
    profiles.extend(read_profiles(root))
    common = {name: source_bytes(root, name) for name in COMMON_FILES}
    template = (root / "ProjectRules/AGENTS.template.md").read_text(encoding="utf-8")
    shared = {
        p.relative_to(root).as_posix(): source_bytes(root, p.relative_to(root).as_posix())
        for p in sorted((root / "ProjectRules/.agent-protocol").rglob("*.md"))
    }
    if not shared:
        raise ValueError("Shared protocol sources are empty")
    packages = {}
    for profile in profiles:
        entries = dict(common)
        if profile["id"] != "global-rules-only":
            entries.update(shared)
            entries["ProjectRules/AGENTS.md"] = render_entry(template, profile["governance_mode"], profile["record_mode"], version)
        entries["PACKAGE.md"] = package_guide(profile, version)
        manifest = {
            "schema": "PAPOP-PACKAGE-1", "version": version, "profile": profile["id"],
            "governance_mode": profile["governance_mode"], "record_mode": profile["record_mode"],
            "files": {name: sha256(data) for name, data in sorted(entries.items())},
        }
        entries["MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if not all(valid_member(name) for name in entries):
            raise ValueError("Unsafe ZIP member name")
        packages[f"portable-agent-project-operating-protocol-v{version}-{profile['id']}.zip"] = entries
    return packages


def zip_bytes(entries: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            if not valid_member(name):
                raise ValueError(f"Unsafe ZIP member: {name}")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return stream.getvalue()


def write_atomic(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def build(root: Path = ROOT, output: Path | None = None, overwrite: bool = False) -> list[dict]:
    root = root.resolve()
    output = (output or root / "dist").resolve()
    artifacts = {name: zip_bytes(entries) for name, entries in package_entries(root).items()}
    records = [{"file": name, "bytes": len(data), "sha256": sha256(data)} for name, data in sorted(artifacts.items())]
    artifacts["SHA256SUMS"] = "".join(f"{r['sha256']}  {r['file']}\n" for r in records).encode("utf-8")
    artifacts["release-manifest.json"] = (json.dumps({"schema": "PAPOP-RELEASE-1", "version": read_version(root), "packages": records}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    # Check every target before writing any: an older user artifact is not silently replaced.
    for name, data in artifacts.items():
        target = output / name
        if target.exists() and (not target.is_file() or (target.read_bytes() != data and not overwrite)):
            raise FileExistsError(f"Different artifact exists: {target}; choose another output or use --overwrite deliberately")
    output.mkdir(parents=True, exist_ok=True)
    for name, data in artifacts.items():
        if not (output / name).exists() or (output / name).read_bytes() != data:
            write_atomic(output / name, data)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for record in build(output=args.output, overwrite=args.overwrite):
        print(f"{record['file']} ({record['bytes']} bytes)")


if __name__ == "__main__":
    main()
