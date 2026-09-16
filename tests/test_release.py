from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import build_release, validate_release


def base_state(**updates: str) -> dict[str, str]:
    state = {
        "SCHEMA": "PAPOP-CURRENT-4",
        "TASK_ID": "T-20260916-test",
        "GOVERNANCE_MODE": "PLAN_APPROVAL",
        "STATUS": "EXECUTING",
        "WORKFLOW_PHASE": "IMPLEMENTATION",
        "AUTHORIZATION_STATUS": "PLAN_AUTHORIZED",
        "AGENT_COMPLETION": "IN_PROGRESS",
        "ACCEPTANCE_STATUS": "NOT_REQUESTED",
        "SUBJECT": "合成约束测试",
        "TAGS": "test",
        "PLAN_REF": "P-0001-R0001",
        "PROPOSED_PLAN_REF": "NONE",
        "ACTIVE_STEP": "S-001",
        "REQUIREMENTS_CONFIRMATION_REF": "D-000001",
        "PLAN_APPROVAL_REF": "D-000002",
        "TASK_AUTHORIZATION_REF": "NONE",
        "DELIVERY_REF": "NONE",
        "ACCEPTANCE_REF": "NONE",
        "LAST_DECISION_REF": "D-000002",
        "LAST_EVENT_ID": "E-000004",
        "LAST_EVENT_TYPE": "PLAN_ACTIVATED",
        "LAST_SNAPSHOT": ".agent-work/tasks/T-20260916-test/snapshots/E-000004.md",
        "RESUME_MODE": "NORMAL",
        "UPDATED_AT": "UNKNOWN",
    }
    state.update(updates)
    return state


def user_decision(kind: str, target: str, **updates: str) -> dict[str, str]:
    item = {
        "TASK_ID": "T-20260916-test",
        "DECISION_TYPE": kind,
        "DECISION_SOURCE": "USER_MESSAGE",
        "TARGET_REF": target,
        "USER_EVIDENCE": "合成测试中的明确用户决定",
    }
    item.update(updates)
    return item


class SourceAndPackagingTests(unittest.TestCase):
    def test_source_validation(self) -> None:
        self.assertEqual([], validate_release.validate_sources())

    def test_exact_three_packages_and_modes(self) -> None:
        packages = build_release.package_entries()
        self.assertEqual(3, len(packages))
        plan = next(entries for name, entries in packages.items() if name.endswith("-plan-approval.zip"))
        delegation = next(entries for name, entries in packages.items() if name.endswith("-task-delegation.zip"))
        global_only = next(entries for name, entries in packages.items() if name.endswith("-global-rules-only.zip"))
        self.assertIn(b"GOVERNANCE_MODE: PLAN_APPROVAL", plan["ProjectRules/AGENTS.md"])
        self.assertIn(b"RECORD_MODE: TRACKED", plan["ProjectRules/AGENTS.md"])
        self.assertIn(b"GOVERNANCE_MODE: TASK_DELEGATION", delegation["ProjectRules/AGENTS.md"])
        self.assertIn(b"RECORD_MODE: AUTO", delegation["ProjectRules/AGENTS.md"])
        self.assertFalse(any(name.startswith("ProjectRules/") for name in global_only))

    def test_zip_is_reproducible_and_manifest_matches(self) -> None:
        for entries in build_release.package_entries().values():
            first = build_release.zip_bytes(entries)
            second = build_release.zip_bytes(entries)
            self.assertEqual(first, second)
            with zipfile.ZipFile(__import__("io").BytesIO(first)) as archive:
                members = {name: archive.read(name) for name in archive.namelist()}
            manifest = json.loads(members["MANIFEST.json"])
            expected = {name: build_release.sha256(data) for name, data in sorted(members.items()) if name != "MANIFEST.json"}
            self.assertEqual(expected, manifest["files"])

    def test_generated_distribution_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build_release.build(output=output)
            self.assertEqual([], validate_release.validate_dist(dist=output))

    def test_different_existing_artifact_is_not_silently_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            records = build_release.build(output=output)
            (output / records[0]["file"]).write_bytes(b"user artifact")
            with self.assertRaises(FileExistsError):
                build_release.build(output=output)

    def test_zip_member_validation(self) -> None:
        for unsafe in ("../escape", "/absolute", "C:/drive", "a\\b", "a/./b"):
            self.assertFalse(build_release.valid_member(unsafe), unsafe)
        self.assertTrue(build_release.valid_member("ProjectRules/.agent-protocol/SCHEMA.md"))


class GovernanceConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plans = {
            "P-0001-R0001": {
                "TASK_ID": "T-20260916-test",
                "REQUIREMENTS_CONFIRMATION_REF": "D-000001",
            },
            "P-0001-R0002": {
                "TASK_ID": "T-20260916-test",
                "REQUIREMENTS_CONFIRMATION_REF": "D-000001",
            },
        }
        self.decisions = {
            "D-000001": user_decision("REQUIREMENTS_CONFIRMED", "T-20260916-test"),
            "D-000002": user_decision("PLAN_APPROVED", "P-0001-R0001"),
        }

    def check(self, state: dict[str, str], decisions: dict[str, dict] | None = None, plans: dict[str, dict] | None = None, **kwargs) -> list[str]:
        return validate_release.validate_state_fixture(state, decisions or self.decisions, plans or self.plans, **kwargs)

    def test_valid_approved_plan_can_execute(self) -> None:
        self.assertEqual([], self.check(base_state()))

    def test_old_revision_approval_cannot_activate_new_revision(self) -> None:
        errors = self.check(base_state(PLAN_REF="P-0001-R0002"))
        self.assertTrue(any("targets" in error for error in errors), errors)

    def test_plan_approval_waits_for_acceptance(self) -> None:
        waiting = base_state(
            STATUS="WAITING_USER", WORKFLOW_PHASE="AWAITING_ACCEPTANCE", AGENT_COMPLETION="COMPLETE",
            ACCEPTANCE_STATUS="AWAITING", DELIVERY_REF="B-0001", ACTIVE_STEP="NONE",
            LAST_EVENT_TYPE="DELIVERY_READY",
        )
        self.assertEqual([], self.check(waiting))
        invalid = dict(waiting, STATUS="DONE", WORKFLOW_PHASE="CLOSED")
        errors = self.check(invalid)
        self.assertTrue(any("human acceptance" in error for error in errors), errors)

    def test_acceptance_is_bound_to_current_delivery(self) -> None:
        decisions = dict(self.decisions)
        decisions["D-000003"] = user_decision("DELIVERY_ACCEPTED", "B-0001")
        done = base_state(
            STATUS="DONE", WORKFLOW_PHASE="CLOSED", AGENT_COMPLETION="COMPLETE", ACCEPTANCE_STATUS="ACCEPTED",
            DELIVERY_REF="B-0001", ACCEPTANCE_REF="D-000003", LAST_DECISION_REF="D-000003", ACTIVE_STEP="NONE",
            LAST_EVENT_TYPE="TASK_COMPLETED",
        )
        self.assertEqual([], self.check(done, decisions=decisions))
        stale = dict(done, DELIVERY_REF="B-0002")
        errors = self.check(stale, decisions=decisions)
        self.assertTrue(any("targets" in error for error in errors), errors)

    def test_delegation_can_close_without_claiming_human_acceptance(self) -> None:
        decisions = {"D-000001": user_decision("TASK_AUTHORIZED", "T-20260916-test")}
        state = base_state(
            GOVERNANCE_MODE="TASK_DELEGATION", STATUS="DONE", WORKFLOW_PHASE="CLOSED",
            AUTHORIZATION_STATUS="TASK_AUTHORIZED", AGENT_COMPLETION="COMPLETE", ACCEPTANCE_STATUS="NOT_REQUIRED",
            REQUIREMENTS_CONFIRMATION_REF="NONE", PLAN_APPROVAL_REF="NONE", TASK_AUTHORIZATION_REF="D-000001",
            LAST_DECISION_REF="D-000001", ACTIVE_STEP="NONE",
        )
        self.assertEqual([], self.check(state, decisions=decisions))

    def test_pending_user_gate_stops_covered_action(self) -> None:
        gate = {"GATE_ID": "G-001", "TARGET": "S-001", "GATE_STATUS": "PENDING"}
        errors = self.check(base_state(), gates=[gate])
        self.assertTrue(any("pending gate" in error for error in errors), errors)

    def test_unknown_source_cannot_authorize(self) -> None:
        decisions = dict(self.decisions)
        decisions["D-000002"] = dict(decisions["D-000002"], DECISION_SOURCE="UNKNOWN")
        errors = self.check(base_state(), decisions=decisions)
        self.assertTrue(any("no valid user source" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
