"""Run all offline tests (no Ollama needed). `python code/run_tests.py`"""
import subprocess, sys
from pathlib import Path
here = Path(__file__).parent
for t in ["test_solver.py", "test_reference.py", "test_pipeline_mock.py"]:
    print(f"\n=== {t}")
    r = subprocess.run([sys.executable, t], cwd=here, capture_output=True, text=True)
    print(next((l for l in r.stdout.splitlines() if l.startswith('OK')), r.stdout + r.stderr) if r.returncode == 0 else r.stdout + r.stderr)
    if r.returncode: sys.exit(f"FAILED: {t}")
print("\nTodos los tests pasaron.")
