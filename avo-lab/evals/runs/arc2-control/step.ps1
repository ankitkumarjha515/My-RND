param([string]$Action)
$py = "C:\Users\ankit kumar jha\Desktop\all folder inside this\cool-project\Reach-out\avo-lab\vendor\arcvenv\Scripts\python.exe"
$out = & $py driver.py client ACT $Action
$n = (Get-ChildItem grids -Filter "s*.txt" | Measure-Object).Count + 1
$name = "grids\s{0:d3}_{1}.txt" -f $n, $Action
$out | Set-Content $name
Copy-Item $name grids\cur.txt -Force
if (Test-Path grids\prev.txt) {
  Write-Output "=== DIFF vs previous ==="
  & $py gridtool.py grids\prev.txt grids\cur.txt
}
Copy-Item $name grids\prev.txt -Force
Write-Output "=== META ==="
$out | Select-Object -Last 5
