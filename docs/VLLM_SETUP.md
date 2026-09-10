# PrivateEye Real VLM Deployment Guide (Qwen2.5-VL via vLLM)

This guide documents the exact, reproducible configuration for deploying **Qwen2.5-VL-3B-Instruct** (primary) and **Qwen2.5-VL-7B-Instruct** (secondary) using **vLLM** with OpenAI-compatible multimodal endpoints.

---

## 1. Pinned Software & Model Specifications

| Component | Pinned Version / Value | Rationale |
| :--- | :--- | :--- |
| **Primary Model** | `Qwen/Qwen2.5-VL-3B-Instruct` | Compact 3B parameter VLM with high visual grounding accuracy; runs comfortably in <=8GB VRAM |
| **Secondary Model** | `Qwen/Qwen2.5-VL-7B-Instruct` | Standard 7B parameter comparison baseline for evaluation |
| **Serving Framework** | `vllm>=0.7.0` | High-throughput PagedAttention, native OpenAI `/v1/chat/completions` API, and structured JSON output |
| **Python** | `3.11` / `3.12` / `3.13` | Modern Python runtime |
| **Transformers** | `transformers>=4.48.0` | Required for native Qwen2.5-VL architectural support |
| **Vision Utilities** | `qwen-vl-utils>=0.0.8` | Qwen official multimodal preprocessing |
| **CUDA Driver** | `CUDA 12.4` / `12.6` / `13.0` | GPU hardware acceleration |

---

## 2. Hardware Requirements

- **Qwen2.5-VL-3B-Instruct**:
  - Minimum GPU VRAM: **8 GB** (e.g., NVIDIA RTX 4060, RTX 3070, T4, A10G).
  - Quantization: Native `bfloat16` or `float16`.
- **Qwen2.5-VL-7B-Instruct**:
  - Minimum GPU VRAM: **16 GB** (e.g., NVIDIA RTX 4080/4090, A4000, A5000, A100).
  - Quantization: Native `bfloat16` or `AWQ 4-bit` for lower memory.

---

## 3. Launching the Model Server

### Option A: Linux / WSL2 Host (Recommended)
```bash
# 1. Install dependencies in your GPU environment
pip install "vllm>=0.7.0" "transformers>=4.48.0" "qwen-vl-utils>=0.0.8"

# 2. Start vLLM serving Qwen2.5-VL-3B-Instruct
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90 \
  --limit-mm-per-prompt '{"image": 2, "video": 0}' \
  --trust-remote-code
```

### Option B: Windows Native PowerShell
Use the provided launcher:
```powershell
.\scripts\start_vlm.ps1 -Model "Qwen/Qwen2.5-VL-3B-Instruct" -Port 8000
```

### Option C: Ollama Multimodal Serving
```bash
ollama run qwen2.5-vl:3b
# Serves an OpenAI-compatible endpoint on http://127.0.0.1:11434/v1
```

---

## 4. Validating Endpoint Health

Run PrivateEye's fail-closed health verifier:
```bash
python scripts/check_vlm.py --base-url http://127.0.0.1:8000/v1 --model Qwen/Qwen2.5-VL-3B-Instruct
```

Expected Output on Healthy Connection:
```json
{
  "status": "PASS",
  "endpoint": "http://127.0.0.1:8000/v1",
  "models_available": ["Qwen/Qwen2.5-VL-3B-Instruct"],
  "target_model": "Qwen/Qwen2.5-VL-3B-Instruct",
  "reason": "Endpoint reachable and model verified"
}
```

---

## 5. Connecting PrivateEye to the Real Model

Configure the environment variables:
```powershell
$env:PRIVATEEYE_VLM_MODE = "real"
$env:PRIVATEEYE_VLM_BASE_URL = "http://127.0.0.1:8000/v1"
$env:PRIVATEEYE_VLM_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
$env:PRIVATEEYE_VLM_TIMEOUT = "120"
```

Then run the evaluation harness:
```powershell
python -m eval.real_vlm_canary
python -m eval.real_vlm_experiment
python -m eval.context_ablation
python -m eval.model_comparison
```
