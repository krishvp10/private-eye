<#
.SYNOPSIS
    PrivateEye Real VLM Server Supervisor (Windows PowerShell)

.DESCRIPTION
    Launches or configures an OpenAI-compatible Vision-Language Model endpoint
    using vLLM or Ollama for Qwen2.5-VL-3B-Instruct (primary) or Qwen2.5-VL-7B-Instruct.
    Sets necessary PrivateEye environment variables.

.PARAMETER Model
    The HuggingFace or Ollama model identifier to serve. Default: Qwen/Qwen2.5-VL-3B-Instruct
.PARAMETER Backend
    Serving engine: 'vllm' or 'ollama'. Default: vllm
.PARAMETER Port
    Port for the OpenAI-compatible API. Default: 8000
.PARAMETER Hostname
    Host interface to bind. Default: 127.0.0.1
.PARAMETER GpuMemoryUtilization
    Fraction of GPU VRAM to allocate to vLLM (0.0 to 1.0). Default: 0.90
.PARAMETER MaxModelLen
    Maximum model context length in tokens. Default: 4096

.EXAMPLE
    .\scripts\start_vlm.ps1 -Model "Qwen/Qwen2.5-VL-3B-Instruct"
    .\scripts\start_vlm.ps1 -Model "Qwen/Qwen2.5-VL-7B-Instruct" -GpuMemoryUtilization 0.92
#>

[CmdletBinding()]
param(
    [string]$Model = "Qwen/Qwen2.5-VL-3B-Instruct",
    [ValidateSet("vllm", "ollama")]
    [string]$Backend = "vllm",
    [string]$Hostname = "127.0.0.1",
    [int]$Port = 8000,
    [double]$GpuMemoryUtilization = 0.90,
    [int]$MaxModelLen = 4096
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PrivateEye Real VLM Server Launcher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Model:                  $Model" -ForegroundColor Yellow
Write-Host "Backend:                $Backend" -ForegroundColor Yellow
Write-Host "Endpoint:               http://${Hostname}:${Port}/v1" -ForegroundColor Yellow
Write-Host "GPU Memory Ratio:       $GpuMemoryUtilization" -ForegroundColor Yellow
Write-Host "Max Context Tokens:     $MaxModelLen" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Set environment variables for PrivateEye processes
$env:PRIVATEEYE_VLM_MODE = "real"
$env:PRIVATEEYE_VLM_BASE_URL = "http://${Hostname}:${Port}/v1"
$env:PRIVATEEYE_VLM_MODEL = $Model

Write-Host "`nEnvironment configured:" -ForegroundColor Green
Write-Host "  `$env:PRIVATEEYE_VLM_MODE     = '$($env:PRIVATEEYE_VLM_MODE)'"
Write-Host "  `$env:PRIVATEEYE_VLM_BASE_URL = '$($env:PRIVATEEYE_VLM_BASE_URL)'"
Write-Host "  `$env:PRIVATEEYE_VLM_MODEL    = '$($env:PRIVATEEYE_VLM_MODEL)'"

if ($Backend -eq "vllm") {
    Write-Host "`nLaunching vLLM OpenAI-compatible server..." -ForegroundColor Cyan
    $vllmCmd = @(
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", $Model,
        "--host", $Hostname,
        "--port", $Port,
        "--max-model-len", $MaxModelLen,
        "--gpu-memory-utilization", $GpuMemoryUtilization,
        "--limit-mm-per-prompt", '{"image": 2, "video": 0}',
        "--trust-remote-code"
    )

    try {
        & python @vllmCmd
    } catch {
        Write-Warning "Could not start vLLM directly: $_"
        Write-Host "`nIf vLLM is installed on WSL2 / Linux host, start it with:" -ForegroundColor Yellow
        Write-Host "  python -m vllm.entrypoints.openai.api_server --model $Model --host 0.0.0.0 --port $Port --limit-mm-per-prompt '{\`"image\`": 2, \`"video\`": 0}'" -ForegroundColor White
        Write-Host "`nThen verify health with:" -ForegroundColor Yellow
        Write-Host "  python scripts/check_vlm.py --base-url http://${Hostname}:${Port}/v1 --model $Model" -ForegroundColor White
    }
} elseif ($Backend -eq "ollama") {
    Write-Host "`nConfiguring for Ollama..." -ForegroundColor Cyan
    Write-Host "Run in a separate terminal: ollama run qwen2.5-vl:3b" -ForegroundColor Yellow
    Write-Host "Verify with: python scripts/check_vlm.py --base-url http://127.0.0.1:11434/v1" -ForegroundColor White
}
