# Phase 17 — Security & Privacy Adversarial Test Environment

## 1. Environment Baseline
- **Audit Date:** 2026-09-11
- **Repository Commit:** `f636ca122a557829c51316822e9175c0db41375d`
- **Operating System:** Windows 11 (build 26100)
- **Python Runtime:** Python 3.13.3 (`.venv\Scripts\python.exe`)
- **Dashboard Service:** FastAPI + Uvicorn
- **Server PID:** 29548 (listening on `127.0.0.1:8080`)
- **Base URL:** `http://127.0.0.1:8080`
- **Bound Interface:** Loopback (`127.0.0.1`)

## 2. Server Startup Procedure
```powershell
# In repository root c:\Users\krish\OneDrive\Desktop\BROWSER-AGENT
# Set environment
$env:PYTHONPATH = "."
# Start server
.venv\Scripts\python.exe demo.py
```

## 3. Server Teardown & Reset Procedure
```powershell
# Terminate listening process on port 8080
$proc = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($proc) {
    Stop-Process -Id $proc -Force
}

# Clear any dirty step state or residual test artifacts
# (Server restarts with clean demo_step_0 and demo_step_1 in memory)
```

## 4. Initial Sanitization Verification
- **F-01 Live Verification Result:** `PASS`
  - Probe: `POST /api/trigger {"domain": "../../etc/passwd", "port": 9999}`
  - Response: `HTTP 400 Bad Request`
  - Body: `{"detail":"Unknown domain '../../etc/passwd'. Must be one of: ['checkout', 'kyc', 'patient', 'sample_fixture']"}`
- **Test State:** Clean in-memory dictionary initialized with fixture demo steps 0 and 1.
