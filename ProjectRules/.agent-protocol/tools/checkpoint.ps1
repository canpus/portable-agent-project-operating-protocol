. (Join-Path $PSScriptRoot 'checkpoint-core.ps1')

function Verify([string]$TaskRoot){
  $stateRoot=Validate-Layout $TaskRoot; $current=Read-Bytes (Join-Path $stateRoot 'current_state.md')
  if($current.Length -eq 0){if((Read-Bytes (Join-Path $stateRoot 'history.md')).Length -or (Read-Bytes (Join-Path $stateRoot 'snapshots.md')).Length){Fail 'empty Current has generated records'}; Write-Output "TASK_STATE_VALID $(Split-Path -Leaf $TaskRoot) EMPTY"; return}
  $s=Validate-State $TaskRoot $stateRoot $current; $snap=Find-Block (Join-Path $stateRoot 'snapshots.md') 'SNAPSHOT' 'SNAPSHOT_ID' $s['LAST_SNAPSHOT_ID']; $hist=Find-Block (Join-Path $stateRoot 'history.md') 'HISTORY_ENTRY' 'EVENT_ID' $s['LAST_EVENT_ID']
  if($null -eq $snap -or $null -eq $hist){Fail 'missing Snapshot or History'}; $sf=Parse-Fields $snap; $hf=Parse-Fields $hist
  $begin=Bytes "----- SNAPSHOT_CONTENT_BEGIN -----`n"; $end=Bytes '----- SNAPSHOT_CONTENT_END -----'; $a=Index-Bytes $snap $begin; $b=Index-Bytes $snap $end ($a+$begin.Length)
  if($a -lt 0 -or $b -lt 0){Fail 'invalid Snapshot framing'}; $content=New-Object byte[] ($b-$a-$begin.Length); [Array]::Copy($snap,$a+$begin.Length,$content,0,$content.Length)
  if(-not (Equal-Bytes $content $current) -or $sf['STATE_SHA256'] -ne (Hash-Bytes $current)){Fail 'Snapshot does not reproduce Current'}
  $all=Read-Bytes (Join-Path $stateRoot 'snapshots.md'); $off=Index-Bytes $all $snap; $start=(Count-LF $all $off)+1; $finish=$start+(Count-LF $snap)
  if($hf['SNAPSHOT_START_LINE'] -ne [string]$start -or $hf['SNAPSHOT_END_LINE'] -ne [string]$finish -or $hf['SNAPSHOT_BLOCK_SHA256'] -ne (Hash-Bytes $snap)){Fail 'History Snapshot pointer mismatch'}
  Write-Output "TASK_STATE_VALID $($s['TASK_ID']) $($s['LAST_EVENT_ID']) $($s['LAST_SNAPSHOT_ID'])"
}
function Init([string]$TaskRoot,[string]$Mode){
  if(@('STRICT_APPROVAL','AUTONOMOUS') -notcontains $Mode){Fail 'invalid mode'}
  $full=[IO.Path]::GetFullPath($TaskRoot); if((Split-Path -Leaf (Split-Path -Parent $full)) -ne 'tasks' -or (Split-Path -Leaf $full) -notmatch '^task[1-9][0-9]*_[0-9]{8}_[^<>:"/\\|?*]+$'){Fail 'invalid Task path'}
  foreach($candidate in @($full,(Join-Path $full '.agent-state'),(Join-Path $full '.agent-state/cases'))){if(Test-Path -LiteralPath $candidate){if((Get-Item -LiteralPath $candidate -Force).Attributes-band[IO.FileAttributes]::ReparsePoint){Fail "Task state reparse point rejected: $candidate"}}}
  [IO.Directory]::CreateDirectory($full)|Out-Null; $state=Join-Path $full '.agent-state'; [IO.Directory]::CreateDirectory($state)|Out-Null; [IO.Directory]::CreateDirectory((Join-Path $state 'cases'))|Out-Null
  foreach($name in $CoreFiles){$p=Join-Path $state $name;if(-not [IO.File]::Exists($p)){[IO.File]::WriteAllBytes($p,([byte[]]@()))}}; $idx=Join-Path $state 'cases/index.md';if(-not [IO.File]::Exists($idx)){[IO.File]::WriteAllBytes($idx,([byte[]]@()))}
  $workspace=Workspace-Of $full; [IO.Directory]::CreateDirectory((Join-Path $workspace '.agent-work/.txn'))|Out-Null; [IO.Directory]::CreateDirectory((Join-Path $workspace '.agent-work/locks'))|Out-Null
  Ensure-Ignore (Join-Path $workspace '.gitignore') @('.agent-work/','tasks/*/.agent-state/')
  Ensure-Ignore (Join-Path $full '.gitignore') @('.agent-state/')
  [void](Validate-Layout $full)
  Write-Output "TASK_INITIALIZED $(Split-Path -Leaf $full) $Mode"
}
function Commit([string]$TaskRoot,[string]$NextPath){
  $task=Resolve-Existing $TaskRoot; $stateRoot=Validate-Layout $task; $workspace=Workspace-Of $task; $next=Resolve-Existing $NextPath
  $txn=(Get-Item -LiteralPath (Join-Path $workspace '.agent-work/.txn') -Force).FullName; if((Split-Path -Parent $next) -ne $txn){Fail 'next-state must be a direct child of .agent-work/.txn'}
  $lock=Join-Path $workspace ".agent-work/locks/$((Split-Path -Leaf $task)).lock"
  try{$lockStream=New-Object IO.FileStream($lock,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)}catch{Fail 'Task lock is held'}
  try{
    $data=Read-Bytes $next; $s=Validate-State $task $stateRoot $data; $currentPath=Join-Path $stateRoot 'current_state.md'; $old=Read-Bytes $currentPath
    if($old.Length -eq 0){if($s['STATE_REVISION'] -ne '1' -or $s['LAST_EVENT_ID'] -ne 'E-000001' -or $s['LAST_SNAPSHOT_ID'] -ne 'SNP-000001'){Fail 'invalid first sequence'}}
    elseif(-not(Equal-Bytes $old $data)){$o=Parse-Fields $old; $er='E-{0:d6}' -f (([int]$o['LAST_EVENT_ID'].Substring(2))+1); $sr='SNP-{0:d6}' -f (([int]$o['LAST_SNAPSHOT_ID'].Substring(4))+1); if([int]$s['STATE_REVISION'] -ne ([int]$o['STATE_REVISION']+1) -or $s['LAST_EVENT_ID'] -ne $er -or $s['LAST_SNAPSHOT_ID'] -ne $sr){Fail 'checkpoint sequence mismatch'}}
    if($old.Length -gt 0){
      $o=Parse-Fields $old;$decisions=Join-Path $stateRoot 'decisions.md'
      if($o['GOVERNANCE_MODE'] -ne $s['GOVERNANCE_MODE']){$target="GOVERNANCE_MODE:$($o['GOVERNANCE_MODE'])->$($s['GOVERNANCE_MODE'])";$approved=$false;foreach($ref in ($s['RELATED_DECISION_REFS'] -split '[,; ]+')){if(Decision-Allows $decisions $ref @('MODE_SWITCH_APPROVED') $target){$approved=$true;break}};if(-not$approved){Fail "mode switch lacks approval: $target"}}
      if($o['GOAL_REF'] -ne 'NONE' -and $o['GOAL_REF'] -ne $s['GOAL_REF']){Require-Decision $decisions $s['GOAL_DECISION_REF'] @('GOAL_APPROVED') $s['GOAL_REF']}
    }
    $historyPath=Join-Path $stateRoot 'history.md'; $existingHistory=Find-Block $historyPath 'HISTORY_ENTRY' 'EVENT_ID' $s['LAST_EVENT_ID']
    if($s['ROOT_CAUSE_KEY'] -ne 'NONE'){$htext=$Utf8.GetString((Read-Bytes $historyPath));$prior=([regex]::Matches($htext,'(?m)^ROOT_CAUSE_KEY: '+[regex]::Escape($s['ROOT_CAUSE_KEY'])+'$')).Count;$expected=if($null-ne$existingHistory){$prior}else{$prior+1};if([int]$s['ROOT_CAUSE_OCCURRENCE']-ne$expected){Fail 'root cause occurrence mismatch'}}
    $recorded=$s['UPDATED_AT']; $snapshot=Snapshot-Bytes $s $data $recorded; $snapshotPath=Join-Path $stateRoot 'snapshots.md'; $existing=Find-Block $snapshotPath 'SNAPSHOT' 'SNAPSHOT_ID' $s['LAST_SNAPSHOT_ID']
    if($null-eq$existing){$before=Read-Bytes $snapshotPath;$start=if($before.Length){(Count-LF $before)+2}else{1};$end=$start+(Count-LF $snapshot)}else{if(-not(Equal-Bytes $existing $snapshot)){Fail 'Snapshot ID conflict'};$all=Read-Bytes $snapshotPath;$off=Index-Bytes $all $snapshot;$start=(Count-LF $all $off)+1;$end=$start+(Count-LF $snapshot)}
    $history=History-Bytes $s $data $snapshot $recorded $start $end
    if($null-ne$existingHistory -and -not(Equal-Bytes $existingHistory $history)){Fail 'Event ID conflict'}
    if(-not(Equal-Bytes $old $data)){$tmp=Join-Path $txn ('.current.'+[guid]::NewGuid().ToString('N')+'.tmp');$backup=Join-Path $txn ('.current.'+[guid]::NewGuid().ToString('N')+'.bak');[IO.File]::WriteAllBytes($tmp,$data);[IO.File]::Replace($tmp,$currentPath,$backup);[IO.File]::Delete($backup)}
    if($null-eq$existing){Append-LF $snapshotPath $snapshot}
    if($null-eq$existingHistory){Append-LF $historyPath $history}
    Verify $task; Remove-Item -LiteralPath $next -Force; Write-Output "CHECKPOINT_COMMITTED $($s['TASK_ID']) $($s['LAST_EVENT_ID']) $($s['LAST_SNAPSHOT_ID'])"
    if([int]$s['ROOT_CAUSE_OCCURRENCE'] -ge 3 -and $s['RELATED_CASE_REFS'] -eq 'NONE'){Write-Output "CASE_RECOMMENDATION_REQUIRED $($s['ROOT_CAUSE_KEY']) $($s['ROOT_CAUSE_OCCURRENCE'])"}
  } finally {$lockStream.Dispose();if(Test-Path -LiteralPath $lock){Remove-Item -LiteralPath $lock -Force}}
}

try {
  if($args.Length -lt 1){Fail 'usage: checkpoint <init|commit|verify> ...'}; $command=$args[0]
  if($command -eq 'init'){Init (Get-Option $args '--task-root') (Get-Option $args '--mode')}
  elseif($command -eq 'commit'){Commit (Get-Option $args '--task-root') (Get-Option $args '--next-state')}
  elseif($command -eq 'verify'){Verify (Resolve-Existing (Get-Option $args '--task-root'))}
  else{Fail "unknown command: $command"}
} catch { [Console]::Error.WriteLine("CHECKPOINT_ERROR: $($_.Exception.Message) [$($_.InvocationInfo.ScriptLineNumber)]"); exit 1 }
