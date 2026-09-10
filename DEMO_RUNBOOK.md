# PrivateEye Demo Runbook

## One-command launch

```powershell
python demo.py
```

Select a configured fixture with:

```powershell
python demo.py --domain kyc
python demo.py --domain checkout
python demo.py --domain patient
python demo.py --domain sample_fixture
```

Use `--no-browser` for CI or a headless smoke check.

## Configuration

The supervisor reads safe local defaults from `shared/config.py`. Override
without source edits:

```powershell
$env:PRIVATEEYE_HOST="127.0.0.1"
$env:PRIVATEEYE_DEMO_PORT="9001"
$env:PRIVATEEYE_SERVER_PORT="8000"
$env:PRIVATEEYE_DASHBOARD_PORT="8080"
```

The VLM boundary remains explicit:

```powershell
$env:PRIVATEEYE_VLM_MODE="mock"
# or PRIVATEEYE_VLM_MODE=real when a reachable endpoint exists
```

## What to inspect

1. Open the dashboard shown by the supervisor.
2. Click **Run Agent**.
3. Use the timeline chips or Previous/Next controls to replay a step.
4. Compare local raw imagery with the sanitized wire image.
5. Inspect detections, redactions, action target, validation, execution, and
   latency metadata.
6. Open the generated privacy report under `eval/reports/`.

Raw screenshots are retained only in local dashboard memory. They are not sent
to the reasoning server. Reports contain no vault values.

## Shutdown

Press Ctrl+C in the supervisor terminal. It terminates the supervised process
tree and reports any service that exited unexpectedly.
