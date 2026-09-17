#!/bin/sh
set -eu
set -f
LC_ALL=C
export LC_ALL

fail() { printf '%s\n' "CHECKPOINT_ERROR: $*" >&2; exit 1; }
field() { awk -F ': ' -v key="$2" '$1==key{sub(/^[^:]*:[ \t]*/,"");print;exit}' "$1"; }
sha_file() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum < "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 < "$1" | awk '{print $1}'
  elif command -v openssl >/dev/null 2>&1; then openssl dgst -sha256 < "$1" | awk '{print $NF}'
  else fail 'no SHA-256 provider found'; fi
}
bytes() { wc -c < "$1" | tr -d ' '; }
lines() { wc -l < "$1" | tr -d ' '; }
block_lines() { awk 'END{print NR}' "$1"; }
arg() { key=$1; shift; while [ "$#" -gt 1 ]; do [ "$1" = "$key" ] && { printf '%s\n' "$2"; return; }; shift; done; fail "missing option: $key"; }
task_name_ok() { printf '%s\n' "$1" | grep -Eq '^task[1-9][0-9]*_[0-9]{8}_.+$' && ! printf '%s\n' "$1" | grep -Eq '[<>:"\\|?*]'; }
canon_dir() { (cd "$1" 2>/dev/null && pwd -P) || fail "directory not found: $1"; }
workspace_of() { dirname "$(dirname "$1")"; }
state_of() { printf '%s/.agent-state\n' "$1"; }
ensure_ignore() {
  file=$1; shift; [ -e "$file" ] || : > "$file"
  for rule in "$@"; do
    if ! grep -Fqx "$rule" "$file"; then
      if [ -s "$file" ] && ! tail -c 1 "$file" | od -An -tu1 | grep -Eq '[[:space:]]10[[:space:]]*$'; then printf '\n' >> "$file"; fi
      printf '%s\n' "$rule" >> "$file"
    fi
  done
}

validate_layout() {
  task=$(canon_dir "$1"); [ "$(basename "$(dirname "$task")")" = tasks ] || fail 'Task must be under tasks/'
  state=$(state_of "$task"); [ -d "$state/cases" ] && [ -f "$state/cases/index.md" ] || fail 'invalid .agent-state layout'
  [ ! -L "$task" ] && [ ! -L "$state" ] && [ ! -L "$state/cases" ] && [ ! -L "$state/cases/index.md" ] || fail 'state symlink rejected'
  for f in goal.md plan.md decisions.md history.md current_state.md snapshots.md; do [ -f "$state/$f" ] || fail "missing ledger: $f"; done
  for f in goal.md plan.md decisions.md history.md current_state.md snapshots.md; do [ ! -L "$state/$f" ] || fail "ledger symlink rejected: $f"; done
  find "$state" -mindepth 1 -maxdepth 1 -printf '%f\n' 2>/dev/null | sort > "${TMPDIR:-/tmp}/papop-layout.$$" || {
    for p in "$state"/* "$state"/.[!.]*; do [ -e "$p" ] && basename "$p"; done | sort > "${TMPDIR:-/tmp}/papop-layout.$$"
  }
  expected='cases
current_state.md
decisions.md
goal.md
history.md
plan.md
snapshots.md'
  [ "$(cat "${TMPDIR:-/tmp}/papop-layout.$$")" = "$expected" ] || { rm -f "${TMPDIR:-/tmp}/papop-layout.$$"; fail '.agent-state has unexpected entries'; }
  rm -f "${TMPDIR:-/tmp}/papop-layout.$$"
  printf '%s\n' "$state"
}
check_text() {
  [ -s "$1" ] || fail 'state is empty'
  tail -c 1 "$1" | od -An -tu1 | grep -Eq '[[:space:]]10[[:space:]]*$' || fail 'state must end with LF'
  cr=$(printf '\r'); grep -q "$cr" "$1" && fail 'state contains CR'
  first=$(od -An -tx1 -N3 "$1" | tr -d ' \n'); [ "$first" != efbbbf ] || fail 'state contains BOM'
}
require_field() { value=$(field "$1" "$2"); [ -n "$value" ] || fail "missing field: $2"; }
require_ref() { [ "$3" = NONE ] && return 0; grep -Fqx "$2: $3" "$1" || fail "missing $2: $3"; }
decision_matches() {
  file=$1 id=$2 kinds=$3 target=$4; [ "$id" != NONE ] || fail "missing decision for $target"
  # index() keeps id/target/kind as literals, matching checkpoint-core.ps1's escaped regexes.
  awk -v id="$id" -v kinds="$kinds" -v target="$target" '
    /^<!-- DECISION_BEGIN -->/{b="";on=1} on{b=b $0 "\n"} /^<!-- DECISION_END -->/{
      if(index(b,"DECISION_ID: " id "\n") && index(b,"TARGET_REF: " target "\n") && index(b,"SOURCE: USER_MESSAGE\n")){n=split(kinds,a,"|");for(i=1;i<=n;i++)if(index(b,"DECISION_TYPE: " a[i] "\n"))ok=1} on=0
    } END{exit ok?0:1}' "$file"
}
decision_ok() {
  decision_matches "$1" "$2" "$3" "$4" || fail "Decision $2 does not authorize $4"
}
validate_state() {
  task=$1 state=$2 next=$3; check_text "$next"
  required='SCHEMA TASK_ID SESSION_ID STAGE_ID GOVERNANCE_MODE PHASE EXECUTION_STATUS AUTHORIZATION_STATUS AGENT_COMPLETION ACCEPTANCE_STATUS REQUIREMENTS_REF REQUIREMENTS_DECISION_REF GOAL_REF PROPOSED_GOAL_REF GOAL_DECISION_REF ACTIVE_PLAN_REF PROPOSED_PLAN_REF PLAN_DECISION_REF TASK_AUTHORIZATION_REF DELIVERY_REF ACCEPTANCE_REF CURRENT_STEP STATE_REVISION LAST_EVENT_ID LAST_SNAPSHOT_ID LAST_EVENT_TYPE EVENT_STATUS EVENT_KEYWORDS EVENT_SUBJECT EVENT_SUMMARY RELATED_PLAN_REFS RELATED_DECISION_REFS RELATED_CASE_REFS RELATED_INPUT_REFS INCIDENT_SIGNATURE ROOT_CAUSE_KEY ROOT_CAUSE_EVIDENCE ROOT_CAUSE_OCCURRENCE EVENT_CHANGE EVENT_EVIDENCE NEXT_ACTION UPDATED_AT'
  for key in $required; do require_field "$next" "$key"; done
  [ "$(field "$next" SCHEMA)" = PAPOP-CURRENT-5 ] || fail 'schema mismatch'; [ "$(field "$next" TASK_ID)" = "$(basename "$task")" ] || fail 'TASK_ID mismatch'
  mode=$(field "$next" GOVERNANCE_MODE); [ "$mode" = STRICT_APPROVAL ] || [ "$mode" = AUTONOMOUS ] || fail 'invalid mode'
  printf '%s\n' "$(field "$next" SESSION_ID)" | grep -Eq '^SES-[0-9]{4}$' || fail 'invalid SESSION_ID'
  printf '%s\n' "$(field "$next" STAGE_ID)" | grep -Eq '^STG-[0-9]{4}$' || fail 'invalid STAGE_ID'
  printf '%s\n' "$(field "$next" LAST_EVENT_ID)" | grep -Eq '^E-[0-9]{6}$' || fail 'invalid LAST_EVENT_ID'
  printf '%s\n' "$(field "$next" LAST_SNAPSHOT_ID)" | grep -Eq '^SNP-[0-9]{6}$' || fail 'invalid LAST_SNAPSHOT_ID'
  printf '%s\n' "$(field "$next" STATE_REVISION)" | grep -Eq '^[1-9][0-9]*$' || fail 'invalid STATE_REVISION'
  printf '%s\n' "$(field "$next" ROOT_CAUSE_OCCURRENCE)" | grep -Eq '^[0-9]+$' || fail 'invalid ROOT_CAUSE_OCCURRENCE'
  root=$(field "$next" ROOT_CAUSE_KEY); occurrence=$(field "$next" ROOT_CAUSE_OCCURRENCE)
  if [ "$root" = NONE ]; then [ "$occurrence" -eq 0 ] || fail 'root cause key/count mismatch'
  else [ "$occurrence" -gt 0 ] && [ "$(field "$next" INCIDENT_SIGNATURE)" != NONE ] && [ "$(field "$next" ROOT_CAUSE_EVIDENCE)" != NONE ] || fail 'confirmed root cause requires incident signature and evidence'; fi
  require_ref "$state/goal.md" GOAL_REF "$(field "$next" GOAL_REF)"; require_ref "$state/goal.md" GOAL_REF "$(field "$next" PROPOSED_GOAL_REF)"
  require_ref "$state/plan.md" PLAN_REF "$(field "$next" ACTIVE_PLAN_REF)"; require_ref "$state/plan.md" PLAN_REF "$(field "$next" PROPOSED_PLAN_REF)"
  phase=$(field "$next" PHASE); dec="$state/decisions.md"
  if [ "$mode" = STRICT_APPROVAL ]; then
    case "$phase" in GOAL_DRAFTING|AWAITING_GOAL_APPROVAL|PLAN_DRAFTING|AWAITING_PLAN_APPROVAL|IMPLEMENTATION|VERIFYING|AWAITING_DELIVERY_ACCEPTANCE|REWORKING|STAGE_CLOSED) decision_ok "$dec" "$(field "$next" REQUIREMENTS_DECISION_REF)" REQUIREMENTS_CONFIRMED "$(field "$next" REQUIREMENTS_REF)";; esac
    case "$phase" in PLAN_DRAFTING|AWAITING_PLAN_APPROVAL|IMPLEMENTATION|VERIFYING|AWAITING_DELIVERY_ACCEPTANCE|REWORKING|STAGE_CLOSED) decision_ok "$dec" "$(field "$next" GOAL_DECISION_REF)" GOAL_APPROVED "$(field "$next" GOAL_REF)";; esac
    case "$phase" in IMPLEMENTATION|VERIFYING|AWAITING_DELIVERY_ACCEPTANCE|REWORKING|STAGE_CLOSED) decision_ok "$dec" "$(field "$next" PLAN_DECISION_REF)" PLAN_APPROVED "$(field "$next" ACTIVE_PLAN_REF)";; esac
    if [ "$phase" = STAGE_CLOSED ]; then [ "$(field "$next" DELIVERY_REF)" != NONE ] || fail 'closed Stage lacks Delivery'; decision_ok "$dec" "$(field "$next" ACCEPTANCE_REF)" DELIVERY_ACCEPTED "$(field "$next" DELIVERY_REF)"; fi
  else case "$phase" in IMPLEMENTATION|VERIFYING|AWAITING_DELIVERY_ACCEPTANCE|REWORKING|STAGE_CLOSED) decision_ok "$dec" "$(field "$next" TASK_AUTHORIZATION_REF)" TASK_AUTHORIZED "$(field "$next" TASK_ID)";; esac; fi
}
extract_block() {
  file=$1 kind=$2 key=$3 value=$4 out=$5
  awk -v begin="<!-- ${kind}_BEGIN -->" -v end="<!-- ${kind}_END -->" -v key="$key: $value" '
    $0==begin{b="";on=1;hit=0} on{b=b $0 "\n";if($0==key)hit=1} $0==end{if(hit){count++;sub(/\n$/, "", b);printf "%s",b}on=0} END{if(count>1)exit 2;if(count==0)exit 1}' "$file" > "$out"
}
append_block() { file=$1 payload=$2; if [ -s "$file" ]; then tail -c 1 "$file" | od -An -tu1 | grep -q 10 || fail 'append ledger lacks LF'; printf '\n' >> "$file"; fi; cat "$payload" >> "$file"; printf '\n' >> "$file"; }
verify_task() {
  task=$(canon_dir "$1"); state=$(validate_layout "$task"); current="$state/current_state.md"
  if [ ! -s "$current" ]; then [ ! -s "$state/history.md" ] && [ ! -s "$state/snapshots.md" ] || fail 'empty Current has generated records'; printf '%s\n' "TASK_STATE_VALID $(basename "$task") EMPTY"; return; fi
  (validate_state "$task" "$state" "$current"); sid=$(field "$current" LAST_SNAPSHOT_ID); eid=$(field "$current" LAST_EVENT_ID); tmp="$(workspace_of "$task")/.agent-work/.txn/verify.$$"; mkdir -p "$(dirname "$tmp")"
  extract_block "$state/snapshots.md" SNAPSHOT SNAPSHOT_ID "$sid" "$tmp.snap" || fail 'missing Snapshot'; extract_block "$state/history.md" HISTORY_ENTRY EVENT_ID "$eid" "$tmp.hist" || fail 'missing History'
  sed -n '/^----- SNAPSHOT_CONTENT_BEGIN -----$/,/^----- SNAPSHOT_CONTENT_END -----$/p' "$tmp.snap" | sed '1d;$d' > "$tmp.current"; cmp -s "$tmp.current" "$current" || { rm -f "$tmp".*; fail 'Snapshot does not reproduce Current'; }
  start=$(awk -v id="SNAPSHOT_ID: $sid" 'BEGIN{on=0} /^<!-- SNAPSHOT_BEGIN -->/{s=NR;on=1} on&&$0==id{hit=1} /^<!-- SNAPSHOT_END -->/{if(on&&hit){print s;exit}on=0;hit=0}' "$state/snapshots.md")
  end=$(awk -v id="SNAPSHOT_ID: $sid" 'BEGIN{on=0} /^<!-- SNAPSHOT_BEGIN -->/{on=1} on&&$0==id{hit=1} /^<!-- SNAPSHOT_END -->/{if(on&&hit){print NR;exit}on=0;hit=0}' "$state/snapshots.md")
  [ "$(field "$tmp.hist" SNAPSHOT_START_LINE)" = "$start" ] && [ "$(field "$tmp.hist" SNAPSHOT_END_LINE)" = "$end" ] || { rm -f "$tmp".*; fail 'History line pointer mismatch'; }
  [ "$(field "$tmp.hist" SNAPSHOT_BLOCK_SHA256)" = "$(sha_file "$tmp.snap")" ] || { rm -f "$tmp".*; fail 'Snapshot block hash mismatch'; }
  rm -f "$tmp".*; printf '%s\n' "TASK_STATE_VALID $(field "$current" TASK_ID) $eid $sid"
}
init_task() {
  root=$1 mode=$2; [ "$mode" = STRICT_APPROVAL ] || [ "$mode" = AUTONOMOUS ] || fail 'invalid mode'; parent=$(dirname "$root"); [ "$(basename "$parent")" = tasks ] || fail 'Task must be under tasks/'; task_name_ok "$(basename "$root")" || fail 'invalid Task name'
  [ ! -L "$root" ] && [ ! -L "$root/.agent-state" ] && [ ! -L "$root/.agent-state/cases" ] || fail 'Task state symlink rejected'
  mkdir -p "$root/.agent-state/cases"; for f in goal.md plan.md decisions.md history.md current_state.md snapshots.md; do [ -e "$root/.agent-state/$f" ] || : > "$root/.agent-state/$f"; done; [ -e "$root/.agent-state/cases/index.md" ] || : > "$root/.agent-state/cases/index.md"
  workspace=$(dirname "$parent"); mkdir -p "$workspace/.agent-work/.txn" "$workspace/.agent-work/locks"
  ensure_ignore "$workspace/.gitignore" '.agent-work/' 'tasks/*/.agent-state/'
  ensure_ignore "$root/.gitignore" '.agent-state/'
  validate_layout "$root" >/dev/null; printf '%s\n' "TASK_INITIALIZED $(basename "$root") $mode"
}
commit_task() {
  task=$(canon_dir "$1"); state=$(validate_layout "$task"); workspace=$(workspace_of "$task"); next=$2; [ -f "$next" ] || fail 'next-state missing'; next_dir=$(canon_dir "$(dirname "$next")"); [ "$next_dir" = "$workspace/.agent-work/.txn" ] || fail 'next-state outside transaction directory'
  lock="$workspace/.agent-work/locks/$(basename "$task").lock"; mkdir "$lock" 2>/dev/null || fail 'Task lock is held'; trap 'rmdir "$lock" 2>/dev/null || true' EXIT HUP INT TERM
  (validate_state "$task" "$state" "$next"); current="$state/current_state.md"; rev=$(field "$next" STATE_REVISION); eid=$(field "$next" LAST_EVENT_ID); sid=$(field "$next" LAST_SNAPSHOT_ID)
  if [ ! -s "$current" ]; then [ "$rev" = 1 ] && [ "$eid" = E-000001 ] && [ "$sid" = SNP-000001 ] || fail 'invalid first sequence'
  elif ! cmp -s "$current" "$next"; then
    oldrev=$(field "$current" STATE_REVISION); olde=$(field "$current" LAST_EVENT_ID|sed 's/^E-//;s/^0*//'); olds=$(field "$current" LAST_SNAPSHOT_ID|sed 's/^SNP-//;s/^0*//'); [ -n "$olde" ] || olde=0; [ -n "$olds" ] || olds=0
    expected_e=$(printf 'E-%06d' $((olde+1))); expected_s=$(printf 'SNP-%06d' $((olds+1)))
    [ "$rev" -eq $((oldrev+1)) ] && [ "$eid" = "$expected_e" ] && [ "$sid" = "$expected_s" ] || fail 'checkpoint sequence mismatch'
  fi
  if [ -s "$current" ]; then
    old_mode=$(field "$current" GOVERNANCE_MODE); new_mode=$(field "$next" GOVERNANCE_MODE); decisions="$state/decisions.md"
    if [ "$old_mode" != "$new_mode" ]; then
      target="GOVERNANCE_MODE:$old_mode->$new_mode"; approved=0
      for ref in $(printf '%s\n' "$(field "$next" RELATED_DECISION_REFS)"|tr ',;' '  '); do [ "$ref" = NONE ] && continue; if decision_matches "$decisions" "$ref" MODE_SWITCH_APPROVED "$target"; then approved=1; break; fi; done
      [ "$approved" -eq 1 ] || fail "mode switch lacks approval: $target"
    fi
    old_goal=$(field "$current" GOAL_REF); new_goal=$(field "$next" GOAL_REF)
    if [ "$old_goal" != NONE ] && [ "$old_goal" != "$new_goal" ]; then decision_ok "$decisions" "$(field "$next" GOAL_DECISION_REF)" GOAL_APPROVED "$new_goal"; fi
  fi
  existing_hist="$workspace/.agent-work/.txn/.existing-history.$$"; history_exists=0
  if extract_block "$state/history.md" HISTORY_ENTRY EVENT_ID "$eid" "$existing_hist"; then history_exists=1; fi
  root=$(field "$next" ROOT_CAUSE_KEY); occurrence=$(field "$next" ROOT_CAUSE_OCCURRENCE)
  if [ "$root" != NONE ]; then
    prior=$(awk -v value="ROOT_CAUSE_KEY: $root" '$0==value{n++}END{print n+0}' "$state/history.md")
    expected=$((prior+1)); [ "$history_exists" -eq 0 ] || expected=$prior
    [ "$occurrence" -eq "$expected" ] || fail 'root cause occurrence mismatch'
  fi
  recorded=$(field "$next" UPDATED_AT); snap="$workspace/.agent-work/.txn/.snapshot.$$"; statehash=$(sha_file "$next")
  { printf '%s\n' '<!-- SNAPSHOT_BEGIN -->' 'SCHEMA: PAPOP-SNAPSHOT-5' "SNAPSHOT_ID: $sid" "TASK_ID: $(field "$next" TASK_ID)" "EVENT_ID: $eid" "STATE_REVISION: $rev" "STATE_SHA256: $statehash" "CONTENT_BYTES: $(bytes "$next")" "RECORDED_AT: $recorded" '----- SNAPSHOT_CONTENT_BEGIN -----'; cat "$next"; printf '%s\n' '----- SNAPSHOT_CONTENT_END -----'; printf '%s' '<!-- SNAPSHOT_END -->'; } > "$snap"
  existing="$workspace/.agent-work/.txn/.existing-snapshot.$$"; snapshot_exists=0
  if extract_block "$state/snapshots.md" SNAPSHOT SNAPSHOT_ID "$sid" "$existing"; then
    snapshot_exists=1; cmp -s "$existing" "$snap" || fail 'Snapshot ID conflict'
    start=$(awk -v id="SNAPSHOT_ID: $sid" 'BEGIN{on=0}/^<!-- SNAPSHOT_BEGIN -->/{s=NR;on=1}on&&$0==id{hit=1}/^<!-- SNAPSHOT_END -->/{if(hit){print s;exit}on=0}' "$state/snapshots.md")
  else before=$(lines "$state/snapshots.md"); [ -s "$state/snapshots.md" ] && start=$((before+2)) || start=1; fi
  end=$((start+$(block_lines "$snap")-1))
  hist="$workspace/.agent-work/.txn/.history.$$"; blockhash=$(sha_file "$snap")
  { printf '%s\n' '<!-- HISTORY_ENTRY_BEGIN -->' 'SCHEMA: PAPOP-HISTORY-5' "EVENT_ID: $eid" "TASK_ID: $(field "$next" TASK_ID)" "SESSION_ID: $(field "$next" SESSION_ID)" "STAGE_ID: $(field "$next" STAGE_ID)" "PHASE: $(field "$next" PHASE)" "EVENT_TYPE: $(field "$next" LAST_EVENT_TYPE)" "EVENT_STATUS: $(field "$next" EVENT_STATUS)" "REQUIREMENTS_REF: $(field "$next" REQUIREMENTS_REF)" "GOAL_REF: $(field "$next" GOAL_REF)" "PLAN_REFS: $(field "$next" RELATED_PLAN_REFS)" "DECISION_REFS: $(field "$next" RELATED_DECISION_REFS)" "CASE_REFS: $(field "$next" RELATED_CASE_REFS)" "INPUT_REFS: $(field "$next" RELATED_INPUT_REFS)" "INCIDENT_SIGNATURE: $(field "$next" INCIDENT_SIGNATURE)" "ROOT_CAUSE_KEY: $(field "$next" ROOT_CAUSE_KEY)" "ROOT_CAUSE_EVIDENCE: $(field "$next" ROOT_CAUSE_EVIDENCE)" "ROOT_CAUSE_OCCURRENCE: $(field "$next" ROOT_CAUSE_OCCURRENCE)" "SNAPSHOT_ID: $sid" "SNAPSHOT_START_LINE: $start" "SNAPSHOT_END_LINE: $end" "SNAPSHOT_BLOCK_SHA256: $blockhash" "STATE_REVISION: $rev" "STATE_SHA256: $statehash" "RECORDED_AT: $recorded" "KEYWORDS: $(field "$next" EVENT_KEYWORDS)" "SUBJECT: $(field "$next" EVENT_SUBJECT)" "SUMMARY: $(field "$next" EVENT_SUMMARY)" "ACTION: $(field "$next" EVENT_CHANGE)" "EVIDENCE: $(field "$next" EVENT_EVIDENCE)" "NEXT: $(field "$next" NEXT_ACTION)"; printf '%s' '<!-- HISTORY_ENTRY_END -->'; } > "$hist"
  if [ "$history_exists" -eq 1 ]; then cmp -s "$existing_hist" "$hist" || fail 'Event ID conflict'; fi
  if ! cmp -s "$current" "$next"; then tmp="$workspace/.agent-work/.txn/.current.$$"; cp "$next" "$tmp"; mv -f "$tmp" "$current"; fi
  [ "$snapshot_exists" -eq 1 ] || append_block "$state/snapshots.md" "$snap"
  [ "$history_exists" -eq 1 ] || append_block "$state/history.md" "$hist"
  (verify_task "$task"); rm -f "$next" "$snap" "$hist" "$existing" "$existing_hist"; printf '%s\n' "CHECKPOINT_COMMITTED $(basename "$task") $eid $sid"
  occ=$(field "$current" ROOT_CAUSE_OCCURRENCE); [ "$occ" -lt 3 ] || [ "$(field "$current" RELATED_CASE_REFS)" != NONE ] || printf '%s\n' "CASE_RECOMMENDATION_REQUIRED $(field "$current" ROOT_CAUSE_KEY) $occ"
  rmdir "$lock"; trap - EXIT HUP INT TERM
}

[ "$#" -ge 1 ] || fail 'usage: checkpoint <init|commit|verify>'
command_name=$1; shift
case "$command_name" in
  init) root=$(arg --task-root "$@"); mode=$(arg --mode "$@"); init_task "$root" "$mode";;
  commit) root=$(arg --task-root "$@"); next=$(arg --next-state "$@"); commit_task "$root" "$next";;
  verify) root=$(arg --task-root "$@"); verify_task "$root";;
  *) fail "unknown command: $command_name";;
esac
