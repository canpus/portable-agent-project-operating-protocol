$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Utf8 = New-Object System.Text.UTF8Encoding($false, $true)
$CoreFiles = @('goal.md','plan.md','decisions.md','history.md','current_state.md','snapshots.md')
$Required = @(
  'SCHEMA','TASK_ID','SESSION_ID','STAGE_ID','GOVERNANCE_MODE','PHASE','EXECUTION_STATUS',
  'AUTHORIZATION_STATUS','AGENT_COMPLETION','ACCEPTANCE_STATUS','REQUIREMENTS_REF',
  'REQUIREMENTS_DECISION_REF','GOAL_REF','PROPOSED_GOAL_REF','GOAL_DECISION_REF',
  'ACTIVE_PLAN_REF','PROPOSED_PLAN_REF','PLAN_DECISION_REF','TASK_AUTHORIZATION_REF',
  'DELIVERY_REF','ACCEPTANCE_REF','CURRENT_STEP','STATE_REVISION','LAST_EVENT_ID',
  'LAST_SNAPSHOT_ID','LAST_EVENT_TYPE','EVENT_STATUS','EVENT_KEYWORDS','EVENT_SUBJECT',
  'EVENT_SUMMARY','RELATED_PLAN_REFS','RELATED_DECISION_REFS','RELATED_CASE_REFS',
  'RELATED_INPUT_REFS','INCIDENT_SIGNATURE','ROOT_CAUSE_KEY','ROOT_CAUSE_EVIDENCE',
  'ROOT_CAUSE_OCCURRENCE','EVENT_CHANGE','EVENT_EVIDENCE','NEXT_ACTION','UPDATED_AT'
)

function Fail([string]$Message) { throw $Message }
function Bytes([string]$Text) { return ,$Utf8.GetBytes($Text) }
function Read-Bytes([string]$Path) { return ,([IO.File]::ReadAllBytes($Path)) }
function Hash-Bytes([byte[]]$Data) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($sha.ComputeHash($Data))).Replace('-','').ToLowerInvariant() }
  finally { $sha.Dispose() }
}
function Join-Bytes([object[]]$Parts) {
  $chunks = @(); $length = 0
  foreach ($part in $Parts) {
    if ($null -eq $part) { continue }
    [byte[]]$chunk = @($part)
    if ($chunk.Length -eq 0) { continue }
    $chunks += ,$chunk
    $length += $chunk.Length
  }
  $result = New-Object byte[] $length; $offset = 0
  foreach ($chunk in $chunks) { [Array]::Copy($chunk,0,$result,$offset,$chunk.Length); $offset += $chunk.Length }
  return ,$result
}
function Equal-Bytes([byte[]]$A,[byte[]]$B) {
  if ($A.Length -ne $B.Length) { return $false }
  for ($i=0; $i -lt $A.Length; $i++) { if ($A[$i] -ne $B[$i]) { return $false } }
  return $true
}
function Count-LF([byte[]]$Data,[int]$Limit = -1) {
  if ($Limit -lt 0 -or $Limit -gt $Data.Length) { $Limit = $Data.Length }
  $count=0; for ($i=0; $i -lt $Limit; $i++) { if ($Data[$i] -eq 10) { $count++ } }; return $count
}
function Index-Bytes([byte[]]$Haystack,[byte[]]$Needle,[int]$Start=0) {
  if ($Needle.Length -eq 0) { return $Start }
  for ($i=$Start; $i -le $Haystack.Length-$Needle.Length; $i++) {
    $ok=$true; for ($j=0; $j -lt $Needle.Length; $j++) { if ($Haystack[$i+$j] -ne $Needle[$j]) { $ok=$false; break } }
    if ($ok) { return $i }
  }; return -1
}
function Parse-Fields([byte[]]$Data) {
  $text=$Utf8.GetString($Data); $map=@{}
  foreach ($line in ($text -split "`n")) {
    $line=$line.TrimEnd("`r")
    if ($line.StartsWith('#') -or $line -eq '----- SNAPSHOT_CONTENT_BEGIN -----') { break }
    if ($line -match '^([A-Z][A-Z0-9_]*):[ ]*(.*)$') {
      if ($map.ContainsKey($Matches[1])) { Fail "duplicate field: $($Matches[1])" }
      $map[$Matches[1]]=$Matches[2].Trim()
    }
  }; return $map
}
function Get-Option([string[]]$InputArgs,[string]$Name) {
  for ($i=0; $i -lt $InputArgs.Length-1; $i++) { if ($InputArgs[$i] -eq $Name) { return $InputArgs[$i+1] } }
  Fail "missing option: $Name"
}
function Resolve-Existing([string]$Path) { return (Get-Item -LiteralPath $Path -Force).FullName }
function Workspace-Of([string]$TaskRoot) { return (Get-Item -LiteralPath (Join-Path (Split-Path -Parent $TaskRoot) '..') -Force).FullName }
function Ensure-Ignore([string]$Path,[string[]]$Rules) {
  [byte[]]$old=@();if([IO.File]::Exists($Path)){$old=[IO.File]::ReadAllBytes($Path)}
  if($old.Length -ge 3 -and $old[0]-eq 239 -and $old[1]-eq 187 -and $old[2]-eq 191){Fail "BOM in .gitignore: $Path"}
  $text=if($old.Length){$Utf8.GetString($old)}else{''};$lines=@($text -split "`r?`n")
  $missing=@();foreach($rule in $Rules){if($lines -notcontains $rule){$missing+=$rule}}
  if(-not$missing.Count){return}
  $prefix=if($old.Length -and $old[$old.Length-1]-ne 10){Bytes "`n"}else{[byte[]]@()}
  $payload=Bytes (($missing -join "`n")+"`n")
  [IO.File]::WriteAllBytes($Path,(Join-Bytes -Parts @($old,$prefix,$payload)))
}
function Validate-Layout([string]$TaskRoot) {
  $task=Get-Item -LiteralPath $TaskRoot -Force
  if($task.Attributes-band[IO.FileAttributes]::ReparsePoint){Fail 'Task reparse point rejected'}
  if (-not $task.PSIsContainer -or $task.Name -notmatch '^task[1-9][0-9]*_[0-9]{8}_[^<>:"/\\|?*]+$' -or (Split-Path -Leaf $task.Parent.FullName) -ne 'tasks') { Fail 'invalid Task root' }
  $state=Join-Path $task.FullName '.agent-state'; if (-not (Test-Path -LiteralPath $state -PathType Container)) { Fail 'missing .agent-state' }
  $names=@(Get-ChildItem -LiteralPath $state -Force | ForEach-Object Name | Sort-Object)
  $expected=@($CoreFiles + 'cases' | Sort-Object)
  if (($names -join "`n") -ne ($expected -join "`n")) { Fail '.agent-state must contain six ledgers and cases/' }
  $cases=Join-Path $state 'cases'; if (-not (Test-Path -LiteralPath (Join-Path $cases 'index.md') -PathType Leaf)) { Fail 'missing cases/index.md' }
  foreach($path in @($state,$cases)+($CoreFiles|ForEach-Object{Join-Path $state $_})+(Join-Path $cases 'index.md')){if((Get-Item -LiteralPath $path -Force).Attributes-band[IO.FileAttributes]::ReparsePoint){Fail "state reparse point rejected: $path"}}
  foreach ($entry in Get-ChildItem -LiteralPath $cases -Force) { if (-not $entry.PSIsContainer -and ($entry.Name -eq 'index.md' -or $entry.Name -match '^C-[0-9]{4}\.md$')) { continue }; Fail "unexpected Case entry: $($entry.Name)" }
  return $state
}
function Append-LF([string]$Path,[byte[]]$Payload) {
  $old=Read-Bytes $Path
  if ($old.Length -gt 0 -and $old[$old.Length-1] -ne 10) { Fail "append-only file lacks LF: $Path" }
  $prefix=if($old.Length -gt 0){Bytes "`n"}else{[byte[]]@()}
  $stream=New-Object IO.FileStream($Path,[IO.FileMode]::Append,[IO.FileAccess]::Write,[IO.FileShare]::Read)
  try { $data=Join-Bytes -Parts @($prefix,$Payload,(Bytes "`n")); $stream.Write($data,0,$data.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}
function Find-Block([string]$Path,[string]$Kind,[string]$Key,[string]$Value) {
  $data=Read-Bytes $Path; if($data.Length -eq 0){return $null}; $text=$Utf8.GetString($data)
  $pattern='(?ms)^<!-- '+[regex]::Escape($Kind)+'_BEGIN -->\n.*?^<!-- '+[regex]::Escape($Kind)+'_END -->'
  $hits=@()
  foreach($block in [regex]::Matches($text,$pattern)) {
    if($block.Value -match ('(?m)^'+[regex]::Escape($Key)+': '+[regex]::Escape($Value)+'$')) { $hits += $block }
  }
  if($hits.Count -gt 1){Fail "duplicate $Key`: $Value"}; if($hits.Count -eq 0){return $null}; return Bytes $hits[0].Value
}
function Require-Record([string]$Path,[string]$Field,[string]$Ref) {
  if($Ref -eq 'NONE'){return}; $text=$Utf8.GetString((Read-Bytes $Path)); if($text -notmatch ('(?m)^'+[regex]::Escape($Field)+': '+[regex]::Escape($Ref)+'$')){Fail "missing $Field`: $Ref"}
}
function Decision-Allows([string]$Path,[string]$Ref,[string[]]$Kinds,[string]$Target) {
  if($Ref -eq 'NONE'){return $false}; $text=$Utf8.GetString((Read-Bytes $Path))
  $block=[regex]::Match($text,'(?ms)^<!-- DECISION_BEGIN -->\n.*?^DECISION_ID: '+[regex]::Escape($Ref)+'\n.*?^<!-- DECISION_END -->')
  if(-not $block.Success){return $false}; $f=Parse-Fields (Bytes $block.Value)
  return ($Kinds -contains $f['DECISION_TYPE'] -and $f['TARGET_REF'] -eq $Target -and $f['SOURCE'] -eq 'USER_MESSAGE')
}
function Require-Decision([string]$Path,[string]$Ref,[string[]]$Kinds,[string]$Target) {
  if(-not(Decision-Allows $Path $Ref $Kinds $Target)){Fail "Decision $Ref does not authorize $Target"}
}
function Validate-State([string]$TaskRoot,[string]$StateRoot,[byte[]]$Data) {
  if($Data.Length -eq 0 -or $Data[$Data.Length-1] -ne 10){Fail 'next-state must end with LF'}
  foreach($b in $Data){if($b -eq 13){Fail 'next-state contains CR'}}
  if($Data.Length -ge 3 -and $Data[0]-eq 239 -and $Data[1]-eq 187 -and $Data[2]-eq 191){Fail 'next-state contains BOM'}
  $s=Parse-Fields $Data; foreach($name in $Required){if(-not $s.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($s[$name])){Fail "missing field: $name"}}
  if($s['SCHEMA'] -ne 'PAPOP-CURRENT-5' -or $s['TASK_ID'] -ne (Split-Path -Leaf $TaskRoot)){Fail "schema or TASK_ID mismatch: schema=$($s['SCHEMA']) task=$($s['TASK_ID']) root=$(Split-Path -Leaf $TaskRoot)"}
  if(@('STRICT_APPROVAL','AUTONOMOUS') -notcontains $s['GOVERNANCE_MODE']){Fail 'invalid GOVERNANCE_MODE'}
  if($s['SESSION_ID'] -notmatch '^SES-[0-9]{4}$' -or $s['STAGE_ID'] -notmatch '^STG-[0-9]{4}$' -or $s['LAST_EVENT_ID'] -notmatch '^E-[0-9]{6}$' -or $s['LAST_SNAPSHOT_ID'] -notmatch '^SNP-[0-9]{6}$'){Fail 'invalid identifier'}
  [int]$rev=0; [int]$occ=0; if(-not [int]::TryParse($s['STATE_REVISION'],[ref]$rev) -or $rev -lt 1){Fail 'invalid STATE_REVISION'}; if(-not [int]::TryParse($s['ROOT_CAUSE_OCCURRENCE'],[ref]$occ) -or $occ -lt 0){Fail 'invalid ROOT_CAUSE_OCCURRENCE'}
  if(($s['ROOT_CAUSE_KEY'] -eq 'NONE') -ne ($occ -eq 0)){Fail 'root cause key/count mismatch'}
  if($s['ROOT_CAUSE_KEY'] -ne 'NONE' -and ($s['INCIDENT_SIGNATURE'] -eq 'NONE' -or $s['ROOT_CAUSE_EVIDENCE'] -eq 'NONE')){Fail 'confirmed root cause requires incident signature and evidence'}
  $goal=Join-Path $StateRoot 'goal.md'; $plan=Join-Path $StateRoot 'plan.md'; $dec=Join-Path $StateRoot 'decisions.md'
  Require-Record $goal 'GOAL_REF' $s['GOAL_REF']; Require-Record $goal 'GOAL_REF' $s['PROPOSED_GOAL_REF']; Require-Record $plan 'PLAN_REF' $s['ACTIVE_PLAN_REF']; Require-Record $plan 'PLAN_REF' $s['PROPOSED_PLAN_REF']
  if($s['GOVERNANCE_MODE'] -eq 'STRICT_APPROVAL'){
    $p=$s['PHASE']
    if(@('GOAL_DRAFTING','AWAITING_GOAL_APPROVAL','PLAN_DRAFTING','AWAITING_PLAN_APPROVAL','IMPLEMENTATION','VERIFYING','AWAITING_DELIVERY_ACCEPTANCE','REWORKING','STAGE_CLOSED') -contains $p){Require-Decision $dec $s['REQUIREMENTS_DECISION_REF'] @('REQUIREMENTS_CONFIRMED') $s['REQUIREMENTS_REF']}
    if(@('PLAN_DRAFTING','AWAITING_PLAN_APPROVAL','IMPLEMENTATION','VERIFYING','AWAITING_DELIVERY_ACCEPTANCE','REWORKING','STAGE_CLOSED') -contains $p){Require-Decision $dec $s['GOAL_DECISION_REF'] @('GOAL_APPROVED') $s['GOAL_REF']}
    if(@('IMPLEMENTATION','VERIFYING','AWAITING_DELIVERY_ACCEPTANCE','REWORKING','STAGE_CLOSED') -contains $p){Require-Decision $dec $s['PLAN_DECISION_REF'] @('PLAN_APPROVED') $s['ACTIVE_PLAN_REF']}
    if($p -eq 'STAGE_CLOSED'){if($s['DELIVERY_REF'] -eq 'NONE'){Fail 'closed Stage lacks Delivery'}; Require-Decision $dec $s['ACCEPTANCE_REF'] @('DELIVERY_ACCEPTED') $s['DELIVERY_REF']}
  } elseif(@('IMPLEMENTATION','VERIFYING','AWAITING_DELIVERY_ACCEPTANCE','REWORKING','STAGE_CLOSED') -contains $s['PHASE']) { Require-Decision $dec $s['TASK_AUTHORIZATION_REF'] @('TASK_AUTHORIZED') $s['TASK_ID'] }
  return $s
}
function Snapshot-Bytes($S,[byte[]]$State,[string]$Recorded){
  $hash=Hash-Bytes $State
  $head="<!-- SNAPSHOT_BEGIN -->`nSCHEMA: PAPOP-SNAPSHOT-5`nSNAPSHOT_ID: $($S['LAST_SNAPSHOT_ID'])`nTASK_ID: $($S['TASK_ID'])`nEVENT_ID: $($S['LAST_EVENT_ID'])`nSTATE_REVISION: $($S['STATE_REVISION'])`nSTATE_SHA256: $hash`nCONTENT_BYTES: $($State.Length)`nRECORDED_AT: $Recorded`n----- SNAPSHOT_CONTENT_BEGIN -----`n"
  return Join-Bytes -Parts @((Bytes $head),$State,(Bytes "----- SNAPSHOT_CONTENT_END -----`n<!-- SNAPSHOT_END -->"))
}
function History-Bytes($S,[byte[]]$State,[byte[]]$Snapshot,[string]$Recorded,[int]$Start,[int]$End){
  $stateHash=Hash-Bytes $State; $blockHash=Hash-Bytes $Snapshot
  $text="<!-- HISTORY_ENTRY_BEGIN -->`nSCHEMA: PAPOP-HISTORY-5`nEVENT_ID: $($S['LAST_EVENT_ID'])`nTASK_ID: $($S['TASK_ID'])`nSESSION_ID: $($S['SESSION_ID'])`nSTAGE_ID: $($S['STAGE_ID'])`nPHASE: $($S['PHASE'])`nEVENT_TYPE: $($S['LAST_EVENT_TYPE'])`nEVENT_STATUS: $($S['EVENT_STATUS'])`nREQUIREMENTS_REF: $($S['REQUIREMENTS_REF'])`nGOAL_REF: $($S['GOAL_REF'])`nPLAN_REFS: $($S['RELATED_PLAN_REFS'])`nDECISION_REFS: $($S['RELATED_DECISION_REFS'])`nCASE_REFS: $($S['RELATED_CASE_REFS'])`nINPUT_REFS: $($S['RELATED_INPUT_REFS'])`nINCIDENT_SIGNATURE: $($S['INCIDENT_SIGNATURE'])`nROOT_CAUSE_KEY: $($S['ROOT_CAUSE_KEY'])`nROOT_CAUSE_EVIDENCE: $($S['ROOT_CAUSE_EVIDENCE'])`nROOT_CAUSE_OCCURRENCE: $($S['ROOT_CAUSE_OCCURRENCE'])`nSNAPSHOT_ID: $($S['LAST_SNAPSHOT_ID'])`nSNAPSHOT_START_LINE: $Start`nSNAPSHOT_END_LINE: $End`nSNAPSHOT_BLOCK_SHA256: $blockHash`nSTATE_REVISION: $($S['STATE_REVISION'])`nSTATE_SHA256: $stateHash`nRECORDED_AT: $Recorded`nKEYWORDS: $($S['EVENT_KEYWORDS'])`nSUBJECT: $($S['EVENT_SUBJECT'])`nSUMMARY: $($S['EVENT_SUMMARY'])`nACTION: $($S['EVENT_CHANGE'])`nEVIDENCE: $($S['EVENT_EVIDENCE'])`nNEXT: $($S['NEXT_ACTION'])`n<!-- HISTORY_ENTRY_END -->"
  return Bytes $text
}
