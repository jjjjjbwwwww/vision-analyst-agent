
# scripts/stop_all.ps1
$ports = @(8006,8007,8010)
foreach ($p in $ports) {
  $c = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
  if ($c) {
    $pid = $c.OwningProcess
    Stop-Process -Id $pid -Force
    Write-Host "✅ killed port $p (pid=$pid)"
  } else {
    Write-Host "port $p not running"
  }
}
