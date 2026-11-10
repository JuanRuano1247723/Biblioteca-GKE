param([string]$Base = "http://localhost:8000")
$h = @{ "Content-Type" = "application/json" }

Write-Host "== healthz"; Invoke-RestMethod "$Base/healthz" | ConvertTo-Json

Write-Host "== CREATE"
$p = Invoke-RestMethod -Method Post "$Base/api/prestamos" -Headers $h -Body '{"ejemplar_id":1,"prestatario":"Prueba Debora"}'
$p | ConvertTo-Json
$id = $p.id

Write-Host "== READ"; Invoke-RestMethod "$Base/api/prestamos/$id" | ConvertTo-Json

Write-Host "== UPDATE"
Invoke-RestMethod -Method Put "$Base/api/prestamos/$id" -Headers $h -Body '{"ejemplar_id":1,"prestatario":"Prueba Debora","fecha_devolucion":"2026-11-09"}' | ConvertTo-Json

Write-Host "== LIST"; Invoke-RestMethod "$Base/api/prestamos" | ConvertTo-Json

Write-Host "== ERROR 400 (ejemplar inexistente)"
try { Invoke-RestMethod -Method Post "$Base/api/prestamos" -Headers $h -Body '{"ejemplar_id":9999,"prestatario":"X"}' }
catch { "-> $($_.Exception.Response.StatusCode.value__) $($_.ErrorDetails.Message)" }

Write-Host "== DELETE"
$r = Invoke-WebRequest -Method Delete "$Base/api/prestamos/$id" -UseBasicParsing
"-> $($r.StatusCode)"

Write-Host "== READ tras DELETE (404)"
try { Invoke-RestMethod "$Base/api/prestamos/$id" } catch { "-> $($_.Exception.Response.StatusCode.value__)" }