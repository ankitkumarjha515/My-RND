$py = "C:\Users\ankit kumar jha\Desktop\all folder inside this\cool-project\Reach-out\avo-lab\vendor\arcvenv\Scripts\python.exe"
$actions = Get-Content plan.txt | Where-Object { $_ -match '\S' }
foreach ($a in $actions) {
  $out = & $py driver.py client ACT $a
  $n = (Get-ChildItem grids -Filter "s*.txt" | Measure-Object).Count + 1
  $name = "grids\s{0:d3}_{1}.txt" -f $n, $a.Trim()
  $out | Set-Content $name
  Copy-Item $name grids\cur.txt -Force
  Copy-Item $name grids\prev.txt -Force
  $meta = $out | Select-String "step=|ERROR|state="
  Write-Output ("{0}: {1}" -f $a.Trim(), ($meta -join " | "))
}
