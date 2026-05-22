param(
    [string]$QdrantUrl = "http://127.0.0.1:6333",
    [string]$Collection = "docurag_chunks_v1",
    [int]$VectorSize = 1024
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Get-ErrorStatusCode {
    param([object]$ErrorRecord)

    $response = $ErrorRecord.Exception.Response
    if ($null -eq $response) {
        return $null
    }

    if ($response.PSObject.Properties.Name -contains "StatusCode") {
        return [int]$response.StatusCode
    }

    return $null
}

function Get-VectorConfig {
    param([object]$CollectionResponse)

    $vectors = $CollectionResponse.result.config.params.vectors
    return @{
        Size = [int]$vectors.size
        Distance = [string]$vectors.distance
    }
}

$baseUrl = $QdrantUrl.TrimEnd("/")
$collectionUrl = "$baseUrl/collections/$Collection"

Write-Host "Qdrant collection smoke"
Write-Host "Endpoint: $collectionUrl"
Write-Host "Expected vector size: $VectorSize"

$collectionExists = $false
try {
    $existing = Invoke-RestMethod -Method Get -Uri $collectionUrl
    $collectionExists = $true
}
catch {
    $statusCode = Get-ErrorStatusCode $_
    if ($statusCode -ne 404) {
        throw "Qdrant is unavailable at $baseUrl. Start Docker Compose Qdrant first. $($_.Exception.Message)"
    }
}

if (-not $collectionExists) {
    Write-Host "Collection not found. Creating $Collection."
    $body = @{
        vectors = @{
            size = $VectorSize
            distance = "Cosine"
        }
    } | ConvertTo-Json -Depth 5

    Invoke-RestMethod -Method Put -Uri $collectionUrl -ContentType "application/json" -Body $body | Out-Null
    $existing = Invoke-RestMethod -Method Get -Uri $collectionUrl
}

$vectorConfig = Get-VectorConfig $existing
Assert-Condition ($vectorConfig.Size -eq $VectorSize) "Qdrant collection '$Collection' vector size is $($vectorConfig.Size); expected $VectorSize."
Assert-Condition ($vectorConfig.Distance -eq "Cosine") "Qdrant collection '$Collection' distance is $($vectorConfig.Distance); expected Cosine."

Write-Host "Qdrant collection OK"
Write-Host "Collection: $Collection"
Write-Host "Vector size: $($vectorConfig.Size)"
Write-Host "Distance: $($vectorConfig.Distance)"
