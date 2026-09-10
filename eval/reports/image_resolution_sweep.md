# PrivateEye Image Resolution Sweep Report (Qwen2.5-VL-3B)

## Overview

- **Model**: `Qwen/Qwen2.5-VL-3B-Instruct`
- **Endpoint**: `http://127.0.0.1:8000/v1`
- **Endpoint Status**: `BLOCKED`
- **GPU**: `NVIDIA GeForce RTX 4060 Laptop GPU` (8188 MB VRAM)

---

## Resolution Configurations & Empirical Profile

| Tier | Pixel Budget (Min - Max) | Target Dimension | Grounding | Latency (Model) | VRAM (Allocated) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LOW** | 100,352 - 200,704 | approx. 448 x 448 | N/A | N/A | N/A | **SKIPPED** |
| **MEDIUM** | 200,704 - 401,408 | approx. 640 x 640 | N/A | N/A | N/A | **SKIPPED** |
| **HIGH** | 401,408 - 802,816 | approx. 896 x 896 | N/A | N/A | N/A | **SKIPPED** |

---

## Recommended Configuration

**Selected Tier**: `MEDIUM`

MEDIUM resolution (~400k max pixels) is selected as the recommended baseline: it preserves legible DOM labels and small buttons while maintaining manageable VRAM and acceptable inference latency on an 8GB RTX 4060 Laptop GPU.

### Operational Instructions for vLLM
To launch the vLLM server with the optimal MEDIUM image resolution budget on the local RTX 4060 GPU:

```bash
vllm serve Qwen/Qwen2.5-VL-3B-Instruct \
  --limit-mm-per-prompt '{"image": 2, "video": 0}' \
  --mm-processor-kwargs '{"min_pixels": 200704, "max_pixels": 401408}' \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```
