"""
Host GPU, CUDA, WSL, and VLM Endpoint Diagnostic Tool.
Provides comprehensive environment profiling for Phase 5A real-VLM serving.
"""

import argparse
import json
import platform
import shutil
import subprocess
import sys
from typing import Any

from scripts.check_vlm import check_endpoint


def get_gpu_details() -> dict[str, Any]:
    """Query nvidia-smi for detailed GPU metrics."""
    result: dict[str, Any] = {
        "gpu_available": False,
        "gpu_name": "None",
        "vram_total_mb": 0,
        "vram_free_mb": 0,
        "vram_used_mb": 0,
        "driver_version": "N/A",
        "cuda_version": "N/A",
    }
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return result

    try:
        proc = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=name,memory.total,memory.free,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parts = [p.strip() for p in proc.stdout.strip().split(",")]
            if len(parts) >= 5:
                result["gpu_available"] = True
                result["gpu_name"] = parts[0]
                result["vram_total_mb"] = int(parts[1])
                result["vram_free_mb"] = int(parts[2])
                result["vram_used_mb"] = int(parts[3])
                result["driver_version"] = parts[4]

        # Check driver CUDA version from nvidia-smi banner
        banner_proc = subprocess.run(
            [nvidia_smi],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if banner_proc.returncode == 0:
            for line in banner_proc.stdout.splitlines():
                if "CUDA Version:" in line:
                    cuda_part = line.split("CUDA Version:")[1].strip().split()[0]
                    result["cuda_version"] = cuda_part
                    break
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass

    return result


def get_wsl_details() -> dict[str, Any]:
    """Check WSL2 availability and installed distributions."""
    result: dict[str, Any] = {
        "wsl_available": False,
        "distributions": [],
        "default_distro": "None",
    }
    wsl_bin = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl_bin:
        return result

    result["wsl_available"] = True
    try:
        proc = subprocess.run(
            [wsl_bin, "-l", "-v"],
            capture_output=True,
            text=False,
            timeout=5,
            check=False,
        )
        if proc.returncode == 0:
            try:
                text_out = proc.stdout.decode("utf-16le")
            except UnicodeDecodeError:
                text_out = proc.stdout.decode("utf-8", errors="replace")

            distros = []
            for line in text_out.splitlines():
                line = line.strip()
                if not line or "NAME" in line or "---" in line:
                    continue
                is_default = line.startswith("*")
                clean = line.lstrip("*").strip().split()
                if clean:
                    d_name = clean[0]
                    distros.append(d_name)
                    if is_default:
                        result["default_distro"] = d_name
            result["distributions"] = distros
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass

    return result


def diagnose_environment(
    endpoint_url: str = "http://127.0.0.1:8000/v1",
    target_model: str = "Qwen/Qwen2.5-VL-3B-Instruct",
) -> dict[str, Any]:
    """Compile comprehensive environment and serving diagnostic."""
    gpu = get_gpu_details()
    wsl = get_wsl_details()
    vlm = check_endpoint(base_url=endpoint_url, target_model=target_model)

    torch_available = False
    torch_cuda = False
    try:
        import torch  # type: ignore[import-untyped]

        torch_available = True
        torch_cuda = bool(torch.cuda.is_available())
    except ImportError:
        pass

    can_fit_3b = gpu["vram_total_mb"] >= 6500
    can_fit_7b = gpu["vram_total_mb"] >= 14000

    return {
        "os": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "gpu": gpu,
        "torch": {
            "installed": torch_available,
            "cuda_available": torch_cuda,
        },
        "wsl": wsl,
        "vllm_endpoint": vlm,
        "model_fit": {
            "qwen_3b_instruct": {
                "supported_by_vram": can_fit_3b,
                "vram_required_mb": 6500,
                "status": "SUPPORTED" if can_fit_3b else "INSUFFICIENT_VRAM",
            },
            "qwen_7b_instruct": {
                "supported_by_vram": can_fit_7b,
                "vram_required_mb": 14000,
                "status": "SUPPORTED" if can_fit_7b else "NOT AVAILABLE on current 8GB hardware",
            },
        },
        "ready_for_real_inference": vlm["status"] == "READY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose GPU and VLM serving environment")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/v1", help="VLM base URL")
    parser.add_argument(
        "--model", default="Qwen/Qwen2.5-VL-3B-Instruct", help="Target model identifier"
    )
    parser.add_argument("--json", action="store_true", help="Emit raw JSON")
    args = parser.parse_args()

    diag = diagnose_environment(endpoint_url=args.endpoint, target_model=args.model)

    if args.json:
        print(json.dumps(diag, indent=2))
        return 0

    print("=================================================================")
    print("           PrivateEye Host & VLM Serving Diagnostic             ")
    print("=================================================================")
    print(f"OS:                 {diag['os']} ({diag['architecture']})")
    print(f"Python:             {diag['python_version']}")
    print("-----------------------------------------------------------------")
    print(f"GPU Detected:       {diag['gpu']['gpu_name']}")
    print(
        f"VRAM:               {diag['gpu']['vram_total_mb']} MB total, {diag['gpu']['vram_free_mb']} MB free"
    )
    print(
        f"Driver / CUDA:      Driver {diag['gpu']['driver_version']} | CUDA {diag['gpu']['cuda_version']}"
    )
    print("-----------------------------------------------------------------")
    print(f"WSL2 Available:     {diag['wsl']['wsl_available']}")
    print(f"WSL Distros:        {', '.join(diag['wsl']['distributions']) or 'None'}")
    print("-----------------------------------------------------------------")
    print(
        f"Qwen2.5-VL-3B Fit:  {diag['model_fit']['qwen_3b_instruct']['status']} (~6.5GB required)"
    )
    print(f"Qwen2.5-VL-7B Fit:  {diag['model_fit']['qwen_7b_instruct']['status']} (~14GB required)")
    print("-----------------------------------------------------------------")
    print(f"Endpoint Status:    {diag['vllm_endpoint']['status']}")
    print(f"Endpoint Reason:    {diag['vllm_endpoint']['reason']}")
    print(f"Real Inference:     {'READY' if diag['ready_for_real_inference'] else 'BLOCKED'}")
    print("=================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
