param(
    [string]$BindHost = "0.0.0.0",
    [int]$Port = 8000
)

Write-Host ("Starting backend on http://{0}:{1}" -f $BindHost, $Port) -ForegroundColor Cyan

uvicorn backend.app.main:app --host $BindHost --port $Port --reload