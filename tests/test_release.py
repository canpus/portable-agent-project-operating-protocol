from __future__ import annotations
import io,json,os,shutil,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from scripts import build_release,validate_release

ROOT=Path(__file__).resolve().parents[1]
CHECKPOINT=ROOT/"ProjectRules/.agent-protocol/tools/checkpoint.ps1"
CHECKPOINT_CMD=ROOT/"ProjectRules/.agent-protocol/tools/checkpoint.cmd"
CHECKPOINT_SH=ROOT/"ProjectRules/.agent-protocol/tools/checkpoint.sh"
INTAKE=ROOT/"ProjectRules/.agent-protocol/tools/intake.ps1"
INTAKE_CMD=ROOT/"ProjectRules/.agent-protocol/tools/intake.cmd"
INTAKE_SH=ROOT/"ProjectRules/.agent-protocol/tools/intake.sh"
PS=shutil.which("pwsh") or shutil.which("powershell")
SH=os.environ.get("PAPOP_SH") or shutil.which("sh")

def run_ps(script:Path,*args:str,ok:bool=True)->subprocess.CompletedProcess[str]:
    command=[PS,"-NoLogo","-NoProfile"]
    if Path(PS).name.lower().startswith("powershell"): command += ["-ExecutionPolicy","Bypass"]
    command += ["-File",str(script),*map(str,args)]
    raw=subprocess.run(command,capture_output=True)
    result=subprocess.CompletedProcess(raw.args,raw.returncode,raw.stdout.decode("utf-8",errors="replace"),raw.stderr.decode("utf-8",errors="replace"))
    if ok and result.returncode: raise AssertionError(result.stdout+result.stderr)
    return result

def run_cmd(script:Path,*args:str,ok:bool=True)->subprocess.CompletedProcess[str]:
    raw=subprocess.run(["cmd.exe","/d","/c",str(script),*map(str,args)],capture_output=True,timeout=20)
    result=subprocess.CompletedProcess(raw.args,raw.returncode,raw.stdout.decode("utf-8",errors="replace"),raw.stderr.decode("utf-8",errors="replace"))
    if ok and result.returncode: raise AssertionError(result.stdout+result.stderr)
    return result

def run_windows_ps(script:Path,*args:str,ok:bool=True)->subprocess.CompletedProcess[str]:
    raw=subprocess.run(["C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe","-NoLogo","-NoProfile","-ExecutionPolicy","Bypass","-File",str(script),*map(str,args)],capture_output=True,timeout=20)
    result=subprocess.CompletedProcess(raw.args,raw.returncode,raw.stdout.decode("utf-8",errors="replace"),raw.stderr.decode("utf-8",errors="replace"))
    if ok and result.returncode: raise AssertionError(result.stdout+result.stderr)
    return result

def run_sh(script:Path,*args:str|Path,ok:bool=True)->subprocess.CompletedProcess[str]:
    def convert(value:str|Path)->str:
        if isinstance(value,Path) and os.name=="nt":
            cygpath=Path(SH).resolve().parents[1]/"usr/bin/cygpath.exe"
            if cygpath.is_file(): return subprocess.check_output([cygpath,"-u",str(value.resolve())],encoding="utf-8").strip()
        return str(value)
    env=os.environ.copy()
    if os.name=="nt": env["PATH"]=str(Path(SH).resolve().parents[1]/"usr/bin")+os.pathsep+str(Path(SH).resolve().parent)+os.pathsep+env.get("PATH","")
    raw=subprocess.run([SH,convert(script),*(convert(arg) for arg in args)],capture_output=True,env=env)
    result=subprocess.CompletedProcess(raw.args,raw.returncode,raw.stdout.decode("utf-8",errors="replace"),raw.stderr.decode("utf-8",errors="replace"))
    if ok and result.returncode: raise AssertionError(result.stdout+result.stderr)
    return result

def state(task:str,revision:int=1,phase:str="TASK_ONBOARDING",root_key:str="NONE",occ:int=0)->bytes:
    signature="NONE" if root_key=="NONE" else "SIG-fixture"
    evidence="NONE" if root_key=="NONE" else "fixture-evidence"
    return f"""SCHEMA: PAPOP-CURRENT-5
TASK_ID: {task}
SESSION_ID: SES-0001
STAGE_ID: STG-0001
GOVERNANCE_MODE: STRICT_APPROVAL
PHASE: {phase}
EXECUTION_STATUS: NOT_STARTED
AUTHORIZATION_STATUS: PENDING_REQUIREMENTS
AGENT_COMPLETION: NOT_STARTED
ACCEPTANCE_STATUS: NOT_REQUESTED
REQUIREMENTS_REF: NONE
REQUIREMENTS_DECISION_REF: NONE
GOAL_REF: NONE
PROPOSED_GOAL_REF: NONE
GOAL_DECISION_REF: NONE
ACTIVE_PLAN_REF: NONE
PROPOSED_PLAN_REF: NONE
PLAN_DECISION_REF: NONE
TASK_AUTHORIZATION_REF: NONE
DELIVERY_REF: NONE
ACCEPTANCE_REF: NONE
CURRENT_STEP: NONE
STATE_REVISION: {revision}
LAST_EVENT_ID: E-{revision:06d}
LAST_SNAPSHOT_ID: SNP-{revision:06d}
LAST_EVENT_TYPE: TEST_EVENT
EVENT_STATUS: SUCCESS
EVENT_KEYWORDS: test,checkpoint
EVENT_SUBJECT: fixture
EVENT_SUMMARY: revision {revision}
RELATED_PLAN_REFS: NONE
RELATED_DECISION_REFS: NONE
RELATED_CASE_REFS: NONE
RELATED_INPUT_REFS: NONE
INCIDENT_SIGNATURE: {signature}
ROOT_CAUSE_KEY: {root_key}
ROOT_CAUSE_EVIDENCE: {evidence}
ROOT_CAUSE_OCCURRENCE: {occ}
EVENT_CHANGE: test
EVENT_EVIDENCE: fixture
NEXT_ACTION: continue
UPDATED_AT: 2026-09-17T10:0{revision}:00+08:00

## State
revision {revision}
""".encode()

def with_fields(data:bytes,**values:str)->bytes:
    lines=data.decode().splitlines()
    for index,line in enumerate(lines):
        key=line.split(":",1)[0]
        if key in values: lines[index]=f"{key}: {values[key]}"
    return ("\n".join(lines)+"\n").encode()

def decision(task:str,decision_id:str,kind:str,target:str)->bytes:
    return f"""<!-- DECISION_BEGIN -->
SCHEMA: PAPOP-DECISION-5
TASK_ID: {task}
SESSION_ID: SES-0001
DECISION_ID: {decision_id}
DECISION_TYPE: {kind}
TARGET_REF: {target}
SOURCE: USER_MESSAGE
DECIDED_AT: 2026-09-17T10:00:00+08:00
SUBJECT: fixture
<!-- DECISION_END -->
""".encode()

def decision_sectioned(task:str,decision_id:str,kind:str,target:str)->bytes:
    # 真实 decisions.md 的块在字段之后带井号标题区段；解析器在该处停止读取字段。
    return decision(task,decision_id,kind,target).replace(b"<!-- DECISION_END -->",b"## fixture\n\nfixture\n<!-- DECISION_END -->")

def two_decisions(task:str,first:tuple[str,str,str],second:tuple[str,str,str])->bytes:
    return b"\n".join(decision_sectioned(task,*item) for item in (first,second))

class Packaging(unittest.TestCase):
    def test_sources(self): self.assertEqual([],validate_release.validate_sources())
    def test_three_packages(self):
        packages=build_release.package_entries();self.assertEqual(3,len(packages));self.assertTrue(any(n.endswith("strict-approval.zip") for n in packages));self.assertTrue(any(n.endswith("autonomous.zip") for n in packages))
        for entries in packages.values():
            a=build_release.zip_bytes(entries);self.assertEqual(a,build_release.zip_bytes(entries))
            with zipfile.ZipFile(io.BytesIO(a)) as z:m={n:z.read(n) for n in z.namelist()}
            manifest=json.loads(m["MANIFEST.json"]);self.assertEqual(manifest["files"],{n:build_release.sha256(d) for n,d in sorted(m.items()) if n!="MANIFEST.json"})
    def test_byte_policy_covers_mmd_and_gitignore(self):
        self.assertEqual([],validate_release.byte_errors("docs/diagrams/x.mmd",b"a\nb\n"));self.assertNotEqual([],validate_release.byte_errors("docs/diagrams/x.mmd",b"a\r\nb\r\n"))
        self.assertEqual([],validate_release.byte_errors(".gitignore",b"a\n"));self.assertNotEqual([],validate_release.byte_errors(".gitignore",b"a\r\n"))
        self.assertNotEqual([],validate_release.byte_errors("docs/diagrams/x.mmd",b"a\r\nb")) # 末尾 CR 亦须报错
    def test_dist(self):
        with tempfile.TemporaryDirectory() as d:build_release.build(output=Path(d));self.assertEqual([],validate_release.validate_dist(dist=Path(d)))

@unittest.skipUnless(PS,"PowerShell unavailable")
class PowerShellTools(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)/"Workspace 空格 &!%";self.tasks=self.base/"tasks";self.tasks.mkdir(parents=True);self.task=self.tasks/"task1_20260917_fixture"
        run_ps(CHECKPOINT,"init","--task-root",self.task,"--mode","STRICT_APPROVAL");self.txn=self.base/".agent-work/.txn";self.ledger=self.task/".agent-state"
    def tearDown(self):self.tmp.cleanup()
    def commit(self,data:bytes,name:str):p=self.txn/name;p.write_bytes(data);return run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",p)
    def test_checkpoint_and_single_snapshot(self):
        self.commit(state(self.task.name),"one.md");self.commit(state(self.task.name,2),"two.md");out=run_ps(CHECKPOINT,"verify","--task-root",self.task)
        self.assertIn("TASK_STATE_VALID",out.stdout);text=(self.ledger/"snapshots.md").read_text(encoding="utf-8");self.assertEqual(2,text.count("<!-- SNAPSHOT_BEGIN -->"));self.assertFalse((self.ledger/"snapshots").exists())
        history=(self.ledger/"history.md").read_text(encoding="utf-8");self.assertIn("SNAPSHOT_START_LINE:",history);self.assertIn("SNAPSHOT_BLOCK_SHA256:",history)
    def test_init_merges_gitignore_without_duplicates(self):
        run_ps(CHECKPOINT,"init","--task-root",self.task,"--mode","STRICT_APPROVAL")
        workspace=(self.base/".gitignore").read_text(encoding="utf-8");task=(self.task/".gitignore").read_text(encoding="utf-8")
        self.assertEqual(1,workspace.splitlines().count(".agent-work/"));self.assertEqual(1,workspace.splitlines().count("tasks/*/.agent-state/"));self.assertEqual([".agent-state/"],task.splitlines())
    def test_case_recommendation_on_third_confirmed_root_cause(self):
        self.commit(state(self.task.name,1,root_key="RC-fixture",occ=1),"one.md");self.commit(state(self.task.name,2,root_key="RC-fixture",occ=2),"two.md");out=self.commit(state(self.task.name,3,root_key="RC-fixture",occ=3),"three.md")
        self.assertIn("CASE_RECOMMENDATION_REQUIRED RC-fixture 3",out.stdout)
    def test_snapshot_conflict_does_not_replace_current(self):
        first=state(self.task.name);self.commit(first,"one.md");(self.ledger/"snapshots.md").write_bytes((self.ledger/"snapshots.md").read_bytes()+b"\n<!-- SNAPSHOT_BEGIN -->\nSNAPSHOT_ID: SNP-000002\n<!-- SNAPSHOT_END -->\n")
        candidate=self.txn/"two.md";candidate.write_bytes(state(self.task.name,2));result=run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",candidate,ok=False)
        self.assertNotEqual(0,result.returncode);self.assertEqual(first,(self.ledger/"current_state.md").read_bytes())
    def test_mode_switch_requires_exact_user_decision(self):
        first=state(self.task.name);self.commit(first,"one.md");second=with_fields(state(self.task.name,2),GOVERNANCE_MODE="AUTONOMOUS",RELATED_DECISION_REFS="D-000001")
        candidate=self.txn/"two.md";candidate.write_bytes(second);result=run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",candidate,ok=False);self.assertIn("mode switch lacks approval",result.stderr);self.assertEqual(first,(self.ledger/"current_state.md").read_bytes())
        (self.ledger/"decisions.md").write_bytes(decision(self.task.name,"D-000001","MODE_SWITCH_APPROVED","GOVERNANCE_MODE:STRICT_APPROVAL->AUTONOMOUS"));candidate.write_bytes(second);self.commit(second,"two.md");self.assertEqual(second,(self.ledger/"current_state.md").read_bytes())
    def test_second_decision_block_authorizes_its_target(self):
        self.commit(state(self.task.name),"one.md")
        confirmed=with_fields(state(self.task.name,2,phase="GOAL_DRAFTING"),REQUIREMENTS_REF="REQ-0002",REQUIREMENTS_DECISION_REF="D-000002")
        (self.ledger/"decisions.md").write_bytes(two_decisions(self.task.name,("D-000001","REQUIREMENTS_CONFIRMED","REQ-0001"),("D-000002","REQUIREMENTS_CONFIRMED","REQ-0002")))
        self.commit(confirmed,"two.md");self.assertEqual(confirmed,(self.ledger/"current_state.md").read_bytes())
        forged=with_fields(state(self.task.name,3,phase="GOAL_DRAFTING"),REQUIREMENTS_REF="REQ-0002",REQUIREMENTS_DECISION_REF="D-000009")
        candidate=self.txn/"three.md";candidate.write_bytes(forged);r=run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",candidate,ok=False)
        self.assertNotEqual(0,r.returncode);self.assertEqual(confirmed,(self.ledger/"current_state.md").read_bytes())
        mismatched=with_fields(state(self.task.name,3,phase="GOAL_DRAFTING"),REQUIREMENTS_REF="REQ-0003",REQUIREMENTS_DECISION_REF="D-000002")
        candidate.write_bytes(mismatched);r=run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",candidate,ok=False)
        self.assertNotEqual(0,r.returncode);self.assertEqual(confirmed,(self.ledger/"current_state.md").read_bytes())
    def test_task_authorization_target_matches_literally(self):
        # Task 目录名允许 . 与 + 等正则元字符；target 若按正则匹配会放宽判定，只差一字符的决策也会被接受。
        dotted=self.tasks/"task1_20260917_a.b";run_ps(CHECKPOINT,"init","--task-root",dotted,"--mode","AUTONOMOUS");ledger=dotted/".agent-state"
        first=with_fields(state(dotted.name),GOVERNANCE_MODE="AUTONOMOUS");candidate=self.txn/"one.md";candidate.write_bytes(first);run_ps(CHECKPOINT,"commit","--task-root",dotted,"--next-state",candidate)
        gated=with_fields(state(dotted.name,2,phase="IMPLEMENTATION"),GOVERNANCE_MODE="AUTONOMOUS",TASK_AUTHORIZATION_REF="D-000001")
        (ledger/"decisions.md").write_bytes(decision_sectioned(dotted.name,"D-000001","TASK_AUTHORIZED","task1_20260917_axb"))
        candidate=self.txn/"two.md";candidate.write_bytes(gated);r=run_ps(CHECKPOINT,"commit","--task-root",dotted,"--next-state",candidate,ok=False)
        self.assertNotEqual(0,r.returncode);self.assertEqual(first,(ledger/"current_state.md").read_bytes())
        (ledger/"decisions.md").write_bytes(decision_sectioned(dotted.name,"D-000001","TASK_AUTHORIZED",dotted.name))
        candidate.write_bytes(gated);run_ps(CHECKPOINT,"commit","--task-root",dotted,"--next-state",candidate);self.assertEqual(gated,(ledger/"current_state.md").read_bytes())
    def test_partial_current_recovery(self):
        self.commit(state(self.task.name),"one.md");second=state(self.task.name,2);(self.ledger/"current_state.md").write_bytes(second);self.commit(second,"two.md");self.assertEqual(2,(self.ledger/"history.md").read_text().count("<!-- HISTORY_ENTRY_BEGIN -->"))
    def test_invalid_transition_does_not_replace_current(self):
        p=self.txn/"bad.md";p.write_bytes(state(self.task.name,phase="PLAN_DRAFTING"));r=run_ps(CHECKPOINT,"commit","--task-root",self.task,"--next-state",p,ok=False);self.assertNotEqual(0,r.returncode);self.assertEqual(b"",(self.ledger/"current_state.md").read_bytes())
    def test_intake_internal_and_external(self):
        source=self.base/"用户 输入.txt";source.write_bytes(b"hello\n");r=run_ps(INTAKE,"copy","--workspace-root",self.base,"--task-root",self.task,"--source",source);self.assertIn("DELETE_SOURCE_OPTION_AVAILABLE",r.stdout);self.assertTrue(source.exists())
        outside=Path(self.tmp.name)/"outside.bin";outside.write_bytes(b"outside");r=run_ps(INTAKE,"copy","--workspace-root",self.base,"--task-root",self.task,"--source",outside);self.assertIn("SOURCE_PRESERVED",r.stdout);self.assertNotIn("DELETE_SOURCE_OPTION_AVAILABLE",r.stdout);self.assertTrue(outside.exists())

@unittest.skipUnless(SH,"POSIX sh unavailable")
class PosixTools(unittest.TestCase):
    def test_posix_checkpoint_matches_powershell(self):
        with tempfile.TemporaryDirectory() as d:
            roots=[]
            for name,runner,script in (("shell",run_sh,CHECKPOINT_SH),("powershell",run_ps,CHECKPOINT)):
                workspace=Path(d)/name;task=workspace/"tasks/task1_20260917_中文任务";task.parent.mkdir(parents=True);runner(script,"init","--task-root",task,"--mode","STRICT_APPROVAL")
                for revision in (1,2): candidate=workspace/f".agent-work/.txn/{revision}.md";candidate.write_bytes(state(task.name,revision));runner(script,"commit","--task-root",task,"--next-state",candidate)
                roots.append(task/".agent-state")
            for name in ("current_state.md","snapshots.md","history.md"):
                self.assertEqual((roots[0]/name).read_bytes(),(roots[1]/name).read_bytes(),name)
    def test_posix_second_decision_block_authorizes_its_target(self):
        with tempfile.TemporaryDirectory() as d:
            workspace=Path(d)/"workspace";task=workspace/"tasks/task1_20260917_中文任务";task.parent.mkdir(parents=True);run_sh(CHECKPOINT_SH,"init","--task-root",task,"--mode","STRICT_APPROVAL");ledger=task/".agent-state"
            candidate=workspace/".agent-work/.txn/one.md";candidate.write_bytes(state(task.name));run_sh(CHECKPOINT_SH,"commit","--task-root",task,"--next-state",candidate)
            (ledger/"decisions.md").write_bytes(two_decisions(task.name,("D-000001","REQUIREMENTS_CONFIRMED","REQ-0001"),("D-000002","REQUIREMENTS_CONFIRMED","REQ-0002")))
            confirmed=with_fields(state(task.name,2,phase="GOAL_DRAFTING"),REQUIREMENTS_REF="REQ-0002",REQUIREMENTS_DECISION_REF="D-000002")
            candidate.write_bytes(confirmed);run_sh(CHECKPOINT_SH,"commit","--task-root",task,"--next-state",candidate);self.assertEqual(confirmed,(ledger/"current_state.md").read_bytes())
            forged=with_fields(state(task.name,3,phase="GOAL_DRAFTING"),REQUIREMENTS_REF="REQ-0002",REQUIREMENTS_DECISION_REF="D-000009")
            candidate.write_bytes(forged);r=run_sh(CHECKPOINT_SH,"commit","--task-root",task,"--next-state",candidate,ok=False)
            self.assertNotEqual(0,r.returncode);self.assertEqual(confirmed,(ledger/"current_state.md").read_bytes())
    def test_posix_task_authorization_target_matches_literally(self):
        with tempfile.TemporaryDirectory() as d:
            workspace=Path(d)/"workspace";dotted=workspace/"tasks/task1_20260917_a.b";dotted.parent.mkdir(parents=True);run_sh(CHECKPOINT_SH,"init","--task-root",dotted,"--mode","AUTONOMOUS");ledger=dotted/".agent-state"
            first=with_fields(state(dotted.name),GOVERNANCE_MODE="AUTONOMOUS");candidate=workspace/".agent-work/.txn/one.md";candidate.write_bytes(first);run_sh(CHECKPOINT_SH,"commit","--task-root",dotted,"--next-state",candidate)
            gated=with_fields(state(dotted.name,2,phase="IMPLEMENTATION"),GOVERNANCE_MODE="AUTONOMOUS",TASK_AUTHORIZATION_REF="D-000001")
            (ledger/"decisions.md").write_bytes(decision_sectioned(dotted.name,"D-000001","TASK_AUTHORIZED","task1_20260917_axb"))
            candidate.write_bytes(gated);r=run_sh(CHECKPOINT_SH,"commit","--task-root",dotted,"--next-state",candidate,ok=False)
            self.assertNotEqual(0,r.returncode);self.assertEqual(first,(ledger/"current_state.md").read_bytes())
            (ledger/"decisions.md").write_bytes(decision_sectioned(dotted.name,"D-000001","TASK_AUTHORIZED",dotted.name))
            candidate.write_bytes(gated);run_sh(CHECKPOINT_SH,"commit","--task-root",dotted,"--next-state",candidate);self.assertEqual(gated,(ledger/"current_state.md").read_bytes())
    def test_posix_intake(self):
        with tempfile.TemporaryDirectory() as d:
            workspace=Path(d)/"workspace";task=workspace/"tasks/task1_20260917_fixture";task.parent.mkdir(parents=True);run_sh(CHECKPOINT_SH,"init","--task-root",task,"--mode","AUTONOMOUS")
            source=workspace/"input.txt";source.write_bytes(b"input\n");result=run_sh(INTAKE_SH,"copy","--workspace-root",workspace,"--task-root",task,"--source",source);self.assertIn("INPUT_IMPORT_VERIFIED",result.stdout);self.assertIn("DELETE_SOURCE_OPTION_AVAILABLE",result.stdout);self.assertTrue(source.exists())

@unittest.skipUnless(Path("C:/Windows/System32/cmd.exe").is_file() and os.environ.get("PAPOP_WINDOWS_INTEGRATION")=="1","set PAPOP_WINDOWS_INTEGRATION=1 for Windows integration tests")
class WindowsCmdWrapper(unittest.TestCase):
    def test_pwsh_and_cmd_wrapper_generate_identical_ledgers(self):
        with tempfile.TemporaryDirectory() as d:
            roots=[]
            for name,runner,script in (("pwsh",run_ps,CHECKPOINT),("ps51",run_cmd,CHECKPOINT_CMD)):
                workspace=Path(d)/name;task=workspace/"tasks/task1_20260917_fixture";task.parent.mkdir(parents=True);runner(script,"init","--task-root",task,"--mode","STRICT_APPROVAL");candidate=workspace/".agent-work/.txn/one.md";candidate.write_bytes(state(task.name));runner(script,"commit","--task-root",task,"--next-state",candidate);roots.append(task/".agent-state")
            for name in ("current_state.md","snapshots.md","history.md"):
                self.assertEqual((roots[0]/name).read_bytes(),(roots[1]/name).read_bytes(),name)
    def test_intake_cmd_wrapper_with_unicode_space_path(self):
        with tempfile.TemporaryDirectory() as d:
            workspace=Path(d)/"工作区 空格";task=workspace/"tasks/task1_20260917_中文任务";task.parent.mkdir(parents=True);run_cmd(CHECKPOINT_CMD,"init","--task-root",task,"--mode","STRICT_APPROVAL")
            source=workspace/"用户 输入.txt";source.write_bytes(b"input\n");result=run_cmd(INTAKE_CMD,"copy","--workspace-root",workspace,"--task-root",task,"--source",source);self.assertIn("INPUT_IMPORT_VERIFIED",result.stdout);self.assertTrue(source.exists())
    def test_windows_powershell_51_direct_handles_percent_path(self):
        with tempfile.TemporaryDirectory() as d:
            workspace=Path(d)/"工作区 % &!^ 路径";task=workspace/"tasks/task1_20260917_中文任务";task.parent.mkdir(parents=True);result=run_windows_ps(CHECKPOINT,"init","--task-root",task,"--mode","STRICT_APPROVAL")
            self.assertIn("TASK_INITIALIZED",result.stdout);self.assertTrue((task/".agent-state/current_state.md").is_file())

if __name__=="__main__":unittest.main()
