Write-Host "Running backend tests" -ForegroundColor Cyan

pushd backend
try {
    python -m pytest
}
finally {
    popd
}