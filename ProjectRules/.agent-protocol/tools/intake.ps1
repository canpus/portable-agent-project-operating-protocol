$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$Excluded=@('.git','.agent-state','.agent-work','.agent-protocol','tasks')
function Fail([string]$m){throw $m}
function Opt([string[]]$a,[string]$n){for($i=0;$i-lt$a.Length-1;$i++){if($a[$i]-eq$n){return $a[$i+1]}};Fail "missing option: $n"}
function Full([string]$p){return (Get-Item -LiteralPath $p -Force).FullName}
function Inside([string]$child,[string]$parent){$c=[IO.Path]::GetFullPath($child).TrimEnd('\')+'\';$p=[IO.Path]::GetFullPath($parent).TrimEnd('\')+'\';return $c.StartsWith($p,[StringComparison]::OrdinalIgnoreCase)}
function Hash([string]$p){$s=[Security.Cryptography.SHA256]::Create();$f=[IO.File]::OpenRead($p);try{return([BitConverter]::ToString($s.ComputeHash($f))).Replace('-','').ToLowerInvariant()}finally{$f.Dispose();$s.Dispose()}}
function Files([string]$root){
  $item=Get-Item -LiteralPath $root -Force;if($item.Attributes-band[IO.FileAttributes]::ReparsePoint){Fail "reparse point rejected: $($item.FullName)"};if(-not$item.PSIsContainer){return ,$item}
  $result=@();$stack=New-Object Collections.Stack;$stack.Push($item)
  while($stack.Count){$dir=$stack.Pop();foreach($x in Get-ChildItem -LiteralPath $dir.FullName -Force){if($x.Attributes-band[IO.FileAttributes]::ReparsePoint){Fail "reparse point rejected: $($x.FullName)"};if($x.PSIsContainer){if($Excluded-notcontains$x.Name){$stack.Push($x)}}else{$result+=$x}}};return $result
}
function Relative([string]$base,[string]$path){$b=[Uri](([IO.Path]::GetFullPath($base).TrimEnd('\')+'\'));$p=[Uri][IO.Path]::GetFullPath($path);return[Uri]::UnescapeDataString($b.MakeRelativeUri($p).ToString()).Replace('/','\')}
function Compare-Trees([string]$source,[string]$dest){
  $sitem=Get-Item -LiteralPath $source -Force;$s=@{};$d=@{}
  if($sitem.PSIsContainer){foreach($f in Files $source){$s[(Relative $source $f.FullName)]=@($f.Length,(Hash $f.FullName))};foreach($f in Files $dest){$d[(Relative $dest $f.FullName)]=@($f.Length,(Hash $f.FullName))}}
  else{$s[$sitem.Name]=@($sitem.Length,(Hash $sitem.FullName));$df=Join-Path $dest $sitem.Name;$di=Get-Item -LiteralPath $df;$d[$sitem.Name]=@($di.Length,(Hash $df))}
  $sk=@($s.Keys|Sort-Object);$dk=@($d.Keys|Sort-Object)
  if(($sk-join"`n") -ne ($dk-join"`n")){Fail 'tree path diff is not empty'}
  foreach($k in $s.Keys){if($s[$k][0]-ne$d[$k][0]-or$s[$k][1]-ne$d[$k][1]){Fail "copy hash mismatch: $k"}}
  return $s.Count
}
function Copy-Input([string]$workspace,[string]$task,[string]$source){
  $w=Full $workspace;$t=Full $task;$s=Full $source;if((Get-Item -LiteralPath $w -Force).Attributes-band[IO.FileAttributes]::ReparsePoint){Fail 'workspace reparse point rejected'};if((Get-Item -LiteralPath $t -Force).Attributes-band[IO.FileAttributes]::ReparsePoint){Fail 'Task reparse point rejected'};if(-not(Inside $t $w)){Fail 'Task is outside workspace'};if(Inside $s $t){Write-Output "INPUT_ALREADY_IN_TASK $s";return}
  $si=Get-Item -LiteralPath $s -Force;if($si.Attributes-band[IO.FileAttributes]::ReparsePoint){Fail 'source reparse point rejected'}
  if($si.PSIsContainer -and $Excluded -contains $si.Name){Fail "protected source directory rejected: $($si.Name)"}
  $input=Join-Path $t 'UserInput';[IO.Directory]::CreateDirectory($input)|Out-Null;$max=0;foreach($x in Get-ChildItem -LiteralPath $input -Directory -Filter 'I-*' -ErrorAction SilentlyContinue){if($x.Name-match'^I-([0-9]{4})$'){$n=[int]$Matches[1];if($n-gt$max){$max=$n}}};$id='I-{0:d4}'-f($max+1);$batch=Join-Path $input $id;[IO.Directory]::CreateDirectory($batch)|Out-Null
  if($si.PSIsContainer){$dest=Join-Path $batch $si.Name;[IO.Directory]::CreateDirectory($dest)|Out-Null;foreach($f in Files $s){$rel=Relative $s $f.FullName;$to=Join-Path $dest $rel;[IO.Directory]::CreateDirectory((Split-Path -Parent $to))|Out-Null;[IO.File]::Copy($f.FullName,$to,$false)};$count=Compare-Trees $s $dest}
  else{[IO.File]::Copy($s,(Join-Path $batch $si.Name),$false);$dest=$batch;$count=Compare-Trees $s $batch}
  $scope=if(Inside $s $w){'WORKSPACE'}else{'EXTERNAL'};Write-Output "INPUT_IMPORT_VERIFIED $id";Write-Output "SOURCE_SCOPE: $scope";Write-Output "SOURCE: $s";Write-Output "DESTINATION: $dest";Write-Output "FILE_COUNT: $count";if($scope-eq'WORKSPACE'){Write-Output 'DELETE_SOURCE_OPTION_AVAILABLE'}else{Write-Output 'SOURCE_PRESERVED'}
}
function Delete-Source([string]$workspace,[string]$task,[string]$source,[string]$copy){
  $w=Full $workspace;$t=Full $task;$s=Full $source;$c=Full $copy;if(-not(Inside $s $w)-or(Inside $s $t)){Fail 'only workspace-internal, Task-external sources may be deleted'};[void](Compare-Trees $s $c)
  $item=Get-Item -LiteralPath $s -Force;if($item.PSIsContainer){Remove-Item -LiteralPath $s -Recurse -Force}else{Remove-Item -LiteralPath $s -Force};if(Test-Path -LiteralPath $s){Fail 'source deletion incomplete'};Write-Output "INPUT_SOURCE_DELETED $s"
}
try{if($args.Length-lt1){Fail 'usage: intake <copy|delete>'};$cmd=$args[0];if($cmd-eq'copy'){Copy-Input (Opt $args '--workspace-root') (Opt $args '--task-root') (Opt $args '--source')}elseif($cmd-eq'delete'){Delete-Source (Opt $args '--workspace-root') (Opt $args '--task-root') (Opt $args '--source') (Opt $args '--copy')}else{Fail 'unknown command'}}catch{[Console]::Error.WriteLine("INTAKE_ERROR: $($_.Exception.Message)");exit 1}
