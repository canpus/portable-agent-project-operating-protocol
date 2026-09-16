#!/usr/bin/env python3
"""Validate PAPOP v4 sources, packages, manifests, and synthetic state constraints."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

try:
    from scripts import build_release
except ModuleNotFoundError:  # direct execution from scripts/
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts import build_release

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RULES = {
    "checkpoint.md", "external-actions.md", "governance.md", "implementation.md", "lifecycle.md",
    "plan-approval.md", "recovery.md", "task-delegation.md", "verification.md", "workspace.md",
}
EXPECTED_TEMPLATES = {
    "active.md", "current-state.md", "decision.md", "history-event.md", "plan-revision.md", "task-index-event.md",
}
REQUIRED_CURRENT_FIELDS = {
    "SCHEMA", "TASK_ID", "GOVERNANCE_MODE", "STATUS", "WORKFLOW_PHASE", "AUTHORIZATION_STATUS",
    "AGENT_COMPLETION", "ACCEPTANCE_STATUS", "SUBJECT", "TAGS", "PLAN_REF", "PROPOSED_PLAN_REF",
    "ACTIVE_STEP", "REQUIREMENTS_CONFIRMATION_REF", "PLAN_APPROVAL_REF", "TASK_AUTHORIZATION_REF",
    "DELIVERY_REF", "ACCEPTANCE_REF", "LAST_DECISION_REF", "LAST_EVENT_ID", "LAST_EVENT_TYPE",
    "LAST_SNAPSHOT", "RESUME_MODE", "UPDATED_AT",
}
ENUMS = {
    "GOVERNANCE_MODE": {"PLAN_APPROVAL", "TASK_DELEGATION"},
    "STATUS": {"PLANNING", "EXECUTING", "VERIFYING", "WAITING_USER", "BLOCKED", "DONE", "CANCELLED"},
    "WORKFLOW_PHASE": {"REQUIREMENTS_CONFIRMATION", "PLAN_DRAFTING", "AWAITING_PLAN_APPROVAL", "IMPLEMENTATION", "VERIFYING", "AWAITING_ACCEPTANCE", "REPLAN_REQUIRED", "CLOSED"},
    "AUTHORIZATION_STATUS": {"PENDING_REQUIREMENTS", "PENDING_PLAN", "PLAN_AUTHORIZED", "TASK_AUTHORIZED", "PENDING_ACTION", "SUSPENDED"},
    "AGENT_COMPLETION": {"NOT_STARTED", "IN_PROGRESS", "COMPLETE"},
    "ACCEPTANCE_STATUS": {"NOT_REQUESTED", "AWAITING", "ACCEPTED", "REJECTED", "NOT_REQUIRED"},
    "RESUME_MODE": {"NORMAL", "READY_FOR_COMPACTION"},
}
AUTHORITY_DECISIONS = {
    "PLAN_APPROVED", "TASK_AUTHORIZED", "REQUIREMENTS_CONFIRMED", "DELIVERY_ACCEPTED", "ACTION_AUTHORIZED", "USER_GATE_RELEASED",
}


def machine_fields(text: str) -> dict[str, str]:
    top = text.split("\n## ", 1)[0]
    found: dict[str, str] = {}
    for line in top.splitlines():
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*):\s*(.+)", line.strip())
        if match:
            if match.group(1) in found:
                raise ValueError(f"Duplicate top-level field: {match.group(1)}")
            found[match.group(1)] = match.group(2)
    return found


def decision(decisions: dict[str, dict], ref: str, expected_type: str, task_id: str, target: str) -> list[str]:
    item = decisions.get(ref)
    if item is None:
        return [f"missing decision {ref}"]
    errors = []
    if item.get("DECISION_TYPE") != expected_type:
        errors.append(f"{ref} is not {expected_type}")
    if item.get("TASK_ID") != task_id:
        errors.append(f"{ref} belongs to another task")
    if item.get("TARGET_REF") != target:
        errors.append(f"{ref} targets {item.get('TARGET_REF')}, not {target}")
    if expected_type in AUTHORITY_DECISIONS:
        if item.get("DECISION_SOURCE") not in {"USER_MESSAGE", "USER_INSTRUCTION"}:
            errors.append(f"{ref} has no valid user source")
        if not str(item.get("USER_EVIDENCE", "")).strip() or item.get("USER_EVIDENCE") == "UNKNOWN":
            errors.append(f"{ref} has no user evidence")
    return errors


def validate_state_fixture(state: dict[str, str], decisions: dict[str, dict], plans: dict[str, dict], gates: list[dict] | None = None, action_target: str | None = None) -> list[str]:
    """Validate synthetic structured fixtures; this does not validate a real agent's behavior."""
    errors = []
    missing = REQUIRED_CURRENT_FIELDS - state.keys()
    if missing:
        errors.append(f"missing current fields: {sorted(missing)}")
        return errors
    for field, allowed in ENUMS.items():
        if state[field] not in allowed:
            errors.append(f"invalid {field}: {state[field]}")
    if errors:
        return errors
    task_id = state["TASK_ID"]
    plan_ref = state["PLAN_REF"]
    proposed_ref = state["PROPOSED_PLAN_REF"]
    if plan_ref != "NONE" and plan_ref not in plans:
        errors.append(f"active plan does not exist: {plan_ref}")
    if proposed_ref != "NONE" and proposed_ref not in plans:
        errors.append(f"proposed plan does not exist: {proposed_ref}")
    if plan_ref != "NONE" and plan_ref == proposed_ref:
        errors.append("active and proposed plan cannot be the same")

    if state["GOVERNANCE_MODE"] == "PLAN_APPROVAL":
        executing = state["STATUS"] in {"EXECUTING", "VERIFYING", "DONE"} or state["WORKFLOW_PHASE"] in {"IMPLEMENTATION", "VERIFYING", "AWAITING_ACCEPTANCE", "CLOSED"}
        if executing:
            if state["AUTHORIZATION_STATUS"] != "PLAN_AUTHORIZED" and state["STATUS"] != "DONE":
                errors.append("plan-approval execution lacks PLAN_AUTHORIZED")
            if plan_ref == "NONE" or plan_ref not in plans:
                errors.append("plan-approval execution lacks an active plan")
            else:
                plan = plans[plan_ref]
                if plan.get("TASK_ID") != task_id:
                    errors.append("active plan belongs to another task")
                errors += decision(decisions, state["REQUIREMENTS_CONFIRMATION_REF"], "REQUIREMENTS_CONFIRMED", task_id, task_id)
                errors += decision(decisions, state["PLAN_APPROVAL_REF"], "PLAN_APPROVED", task_id, plan_ref)
                if plan.get("REQUIREMENTS_CONFIRMATION_REF") != state["REQUIREMENTS_CONFIRMATION_REF"]:
                    errors.append("plan and current state use different requirements confirmation")
        if state["WORKFLOW_PHASE"] == "AWAITING_ACCEPTANCE":
            if state["STATUS"] != "WAITING_USER" or state["AGENT_COMPLETION"] != "COMPLETE" or state["ACCEPTANCE_STATUS"] != "AWAITING":
                errors.append("plan-approval acceptance state is inconsistent")
        if state["STATUS"] == "DONE":
            if state["WORKFLOW_PHASE"] != "CLOSED" or state["AGENT_COMPLETION"] != "COMPLETE" or state["ACCEPTANCE_STATUS"] != "ACCEPTED":
                errors.append("plan-approval DONE lacks human acceptance")
            if state["DELIVERY_REF"] == "NONE":
                errors.append("plan-approval DONE lacks a delivery candidate")
            else:
                errors += decision(decisions, state["ACCEPTANCE_REF"], "DELIVERY_ACCEPTED", task_id, state["DELIVERY_REF"])
    else:
        if state["STATUS"] in {"EXECUTING", "VERIFYING", "DONE"}:
            errors += decision(decisions, state["TASK_AUTHORIZATION_REF"], "TASK_AUTHORIZED", task_id, task_id)
        if state["STATUS"] == "DONE":
            if state["AGENT_COMPLETION"] != "COMPLETE" or state["WORKFLOW_PHASE"] != "CLOSED":
                errors.append("delegation DONE lacks agent completion")
            if state["ACCEPTANCE_STATUS"] not in {"ACCEPTED", "NOT_REQUIRED"}:
                errors.append("delegation DONE has unresolved acceptance")
            if state["ACCEPTANCE_STATUS"] == "ACCEPTED":
                errors += decision(decisions, state["ACCEPTANCE_REF"], "DELIVERY_ACCEPTED", task_id, state["DELIVERY_REF"])

    if state["ACCEPTANCE_STATUS"] != "ACCEPTED" and state["ACCEPTANCE_REF"] != "NONE":
        errors.append("acceptance reference exists without ACCEPTED status")
    if state["ACCEPTANCE_STATUS"] == "ACCEPTED" and state["DELIVERY_REF"] == "NONE":
        errors.append("accepted state lacks a delivery candidate")
    for gate in gates or []:
        if gate.get("GATE_STATUS") == "PENDING" and gate.get("TARGET") in {"TASK", plan_ref, proposed_ref, state["ACTIVE_STEP"], action_target}:
            if state["STATUS"] not in {"WAITING_USER", "BLOCKED", "PLANNING"}:
                errors.append(f"pending gate {gate.get('GATE_ID')} does not stop its target")
    return errors


def markdown_link_errors(name: str, data: bytes, members: set[str]) -> list[str]:
    if not name.endswith(".md"):
        return []
    text = data.decode("utf-8")
    errors = []
    for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
        if resolved.startswith("../") or resolved not in members:
            errors.append(f"{name}: broken local link {raw}")
    return errors


def validate_sources(root: Path = ROOT) -> list[str]:
    errors = []
    version = build_release.read_version(root)
    for name in ("README.md", "README_EN.md", "CHANGELOG.md"):
        if f"4.0.1" not in (root / name).read_text(encoding="utf-8"):
            errors.append(f"{name} does not identify v4.0.1")
    if version != "4.0.1":
        errors.append(f"expected v4.0.1, found {version}")
    rules = {p.name for p in (root / "ProjectRules/.agent-protocol/rules").glob("*.md")}
    templates = {p.name for p in (root / "ProjectRules/.agent-protocol/templates").glob("*.md")}
    if rules != EXPECTED_RULES:
        errors.append(f"rule set mismatch: {sorted(rules)}")
    if templates != EXPECTED_TEMPLATES:
        errors.append(f"template set mismatch: {sorted(templates)}")
    current = (root / "ProjectRules/.agent-protocol/templates/current-state.md").read_text(encoding="utf-8")
    if set(machine_fields(current)) != REQUIRED_CURRENT_FIELDS:
        errors.append(f"current-state fields mismatch: {sorted(set(machine_fields(current)) ^ REQUIRED_CURRENT_FIELDS)}")
    schema = (root / "ProjectRules/.agent-protocol/SCHEMA.md").read_text(encoding="utf-8")
    for enum_values in ENUMS.values():
        for value in enum_values:
            if value not in schema:
                errors.append(f"schema misses enum value {value}")
    try:
        packages = build_release.package_entries(root)
    except Exception as exc:
        errors.append(f"cannot render package entries: {exc}")
        return errors
    if len(packages) != 3:
        errors.append("exactly three packages are required")
    plan_name = next(name for name in packages if name.endswith("-plan-approval.zip"))
    delegate_name = next(name for name in packages if name.endswith("-task-delegation.zip"))
    for package_name, expected_mode, expected_record in (
        (plan_name, "PLAN_APPROVAL", "TRACKED"), (delegate_name, "TASK_DELEGATION", "AUTO")
    ):
        entry = packages[package_name]["ProjectRules/AGENTS.md"].decode("utf-8")
        if entry.count(f"GOVERNANCE_MODE: {expected_mode}") != 1 or entry.count(f"RECORD_MODE: {expected_record}") != 1 or "@@" in entry:
            errors.append(f"incorrect rendered entry: {package_name}")
    global_name = next(name for name in packages if name.endswith("-global-rules-only.zip"))
    if any(path.startswith("ProjectRules/") for path in packages[global_name]):
        errors.append("GlobalRules Only contains ProjectRules")
    return errors


def validate_dist(root: Path = ROOT, dist: Path | None = None) -> list[str]:
    dist = (dist or root / "dist").resolve()
    expected = build_release.package_entries(root)
    errors = []
    zip_paths = sorted(dist.glob("*.zip")) if dist.exists() else []
    if {p.name for p in zip_paths} != set(expected):
        errors.append(f"distribution ZIP set mismatch: {[p.name for p in zip_paths]}")
        return errors
    actual_records = []
    globals_seen = []
    for path in zip_paths:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)) or any(not build_release.valid_member(name) for name in names):
                errors.append(f"unsafe or duplicate members: {path.name}")
            if any(info.date_time != (1980, 1, 1, 0, 0, 0) or info.flag_bits & 1 for info in infos):
                errors.append(f"non-reproducible timestamp or encrypted member: {path.name}")
            members = {name: archive.read(name) for name in names}
        if members != expected[path.name]:
            errors.append(f"archive bytes differ from source render: {path.name}")
        manifest = json.loads(members["MANIFEST.json"].decode("utf-8"))
        if manifest["files"] != {name: build_release.sha256(data) for name, data in sorted(members.items()) if name != "MANIFEST.json"}:
            errors.append(f"package manifest hashes mismatch: {path.name}")
        for name, data in members.items():
            errors += markdown_link_errors(name, data, set(members))
            if name.endswith(".md"):
                try:
                    data.decode("utf-8")
                except UnicodeDecodeError:
                    errors.append(f"non-UTF-8 Markdown: {path.name}:{name}")
        globals_seen.append(members["GlobalRules/AGENTS.md"])
        actual_records.append({"file": path.name, "bytes": path.stat().st_size, "sha256": build_release.sha256(path.read_bytes())})
    if len(set(globals_seen)) != 1:
        errors.append("GlobalRules differs across packages")
    checksums = "".join(f"{r['sha256']}  {r['file']}\n" for r in sorted(actual_records, key=lambda r: r["file"])).encode("utf-8")
    if not (dist / "SHA256SUMS").is_file() or (dist / "SHA256SUMS").read_bytes() != checksums:
        errors.append("SHA256SUMS mismatch")
    manifest_path = dist / "release-manifest.json"
    if not manifest_path.is_file():
        errors.append("release-manifest.json is missing")
    else:
        release = json.loads(manifest_path.read_text(encoding="utf-8"))
        if release.get("version") != build_release.read_version(root) or release.get("packages") != sorted(actual_records, key=lambda r: r["file"]):
            errors.append("release manifest mismatch")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--dist", type=Path)
    args = parser.parse_args()
    errors = validate_sources(ROOT)
    if not args.source_only:
        errors += validate_dist(ROOT, args.dist)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PAPOP v4 validation passed (source" + (" only)." if args.source_only else " and distributions)."))


if __name__ == "__main__":
    main()
