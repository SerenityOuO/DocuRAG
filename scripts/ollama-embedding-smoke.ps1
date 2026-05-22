param(
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
    [string]$InputText = "DocuRAG vector retrieval smoke test"
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

$baseUrl = $OllamaBaseUrl.TrimEnd("/")
$tagsUrl = "$baseUrl/api/tags"
$embedUrl = "$baseUrl/api/embed"

Write-Host "Ollama embedding smoke"
Write-Host "Tags: $tagsUrl"
Write-Host "Embed: $embedUrl"
Write-Host "Model: $EmbeddingModel"

try {
    $tags = Invoke-RestMethod -Method Get -Uri $tagsUrl
}
catch {
    throw "Ollama is unavailable at $tagsUrl. Start Ollama and pull $EmbeddingModel first. $($_.Exception.Message)"
}

$modelNames = @($tags.models | ForEach-Object { $_.name })
Assert-Condition ($modelNames -contains $EmbeddingModel) "Ollama model '$EmbeddingModel' was not found. Available models: $($modelNames -join ', ')"

$body = @{
    model = $EmbeddingModel
    input = $InputText
} | ConvertTo-Json

$embeddingResponse = Invoke-RestMethod -Method Post -Uri $embedUrl -ContentType "application/json" -Body $body
$embeddings = @($embeddingResponse.embeddings)
Assert-Condition ($embeddings.Count -eq 1) "Expected exactly one embedding from /api/embed."

$embedding = @($embeddings[0])
Assert-Condition ($embedding.Count -gt 0) "Embedding vector was empty."

Write-Host "Embedding OK"
Write-Host "Vector dimension: $($embedding.Count)"
