import json
import urllib.request

url = "https://api.github.com/repos/krishvp10/private-eye/actions/runs?per_page=4"
req = urllib.request.Request(url, headers={"User-Agent": "PrivateEye-CI-Checker"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    runs = data.get("workflow_runs", [])
    for r in runs:
        print(f"Run {r['id']}: {r['name']} | Status: {r['status']} | Conclusion: {r['conclusion']} | SHA: {r['head_commit']['id'][:7]}")
except Exception as e:
    print(f"Error checking GitHub Actions: {e}")
