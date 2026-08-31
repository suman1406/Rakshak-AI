param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$OutputDirectory = ".local-proof"
)

$ErrorActionPreference = "Stop"
$proofRoot = Join-Path (Get-Location) $OutputDirectory
New-Item -ItemType Directory -Force -Path $proofRoot | Out-Null

function Save-ProofResponse {
    param([string]$Name, [string]$Method, [string]$Uri, [hashtable]$Headers = @{}, [object]$Body = $null)
    $requestHeaders = @{}
    foreach ($key in $Headers.Keys) {
        $requestHeaders[$key] = if ($key -eq "Authorization") { "Bearer [REDACTED]" } else { $Headers[$key] }
    }
    $request = @{ method = $Method; url = $Uri; headers = $requestHeaders; body = $Body }
    $curlArgs = @("--silent", "--show-error", "--include", "--request", $Method, $Uri)
    foreach ($key in $Headers.Keys) { $curlArgs += @("--header", "${key}: $($Headers[$key])") }
    $payloadPath = $null
    if ($null -ne $Body) {
        $payloadPath = Join-Path $proofRoot "$Name-request.json"
        $Body | ConvertTo-Json -Compress | Set-Content -NoNewline -Encoding utf8 $payloadPath
        $curlArgs += @("--header", "Content-Type: application/json", "--data-binary", "@$payloadPath")
    }
    $raw = (& curl.exe @curlArgs) -join "`n"
    if ($payloadPath) { Remove-Item -LiteralPath $payloadPath -Force }
    $safeRaw = $raw -replace '"(access_token|refresh_token)":"[^"]+"', '"$1":"[REDACTED]"'
    @{ request = $request; raw_http_response = $safeRaw } | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $proofRoot "$Name.json")
    return $raw
}

$login = Save-ProofResponse "01-login" "POST" "$BaseUrl/api/v1/auth/login" @{} @{ email_or_phone = "rajan.patil@example.com"; password = "Farmer@1234" }
$tokenMatch = [regex]::Match($login, '"access_token":"([^"]+)"')
$token = $tokenMatch.Groups[1].Value
if (-not $token) { throw "Seed login failed. Inspect $proofRoot\\01-login.json" }
$auth = @{ Authorization = "Bearer $token" }
Save-ProofResponse "02-video-status" "GET" "$BaseUrl/api/v1/videos/00000000-0007-0007-0007-000000000002/status" $auth
Save-ProofResponse "03-video-analysis" "GET" "$BaseUrl/api/v1/videos/00000000-0007-0007-0007-000000000002/analysis" $auth
Write-Host "Proof written to $proofRoot (tokens are redacted)."
