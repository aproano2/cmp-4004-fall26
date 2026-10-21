"""Environment check. Run this before you ask for help.

    python -m aicourse.doctor

Exit code 0 means every REQUIRED check passed. Optional tools (SWI-Prolog,
Ollama) report as warnings, not failures -- the manual LLM backend and the
week 1-7 material work without them.
"""

from __future__ import annotations

import importlib
import platform
import shutil
import subprocess
import sys

from .cache import Cache
from .llm import LLM, backends_available

OK, WARN, FAIL = "✔", "!", "✗"

REQUIRED = [("numpy", "1.24"), ("matplotlib", "3.7"), ("pytest", "7.4")]
OPTIONAL_PY = [("pandas", "2.0"), ("sklearn", "1.3"),
               ("networkx", "3.1"), ("pyperplan", None)]


def _ver(mod):
    for attr in ("__version__", "version", "VERSION"):
        v = getattr(mod, attr, None)
        if isinstance(v, str):
            return v
    return "?"


def _tuple(v):
    out = []
    for part in v.split("."):
        digits = "".join(c for c in part if c.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def check_python():
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 10)
    print(f"{OK if ok else FAIL} Python {platform.python_version()}"
          f"{'' if ok else '  — need 3.10 or newer'}")
    return ok


def check_packages():
    all_ok = True
    found = []
    for name, minv in REQUIRED:
        try:
            mod = importlib.import_module(name)
        except ImportError:
            print(f"{FAIL} {name} is missing — pip install -r requirements.txt")
            all_ok = False
            continue
        v = _ver(mod)
        if minv and v != "?" and _tuple(v) < _tuple(minv):
            print(f"{WARN} {name} {v} (want >= {minv})")
        found.append(f"{name} {v}")
    if found:
        print(f"{OK} " + ", ".join(found))

    opt = []
    for name, minv in OPTIONAL_PY:
        try:
            mod = importlib.import_module(name)
            opt.append(f"{name} {_ver(mod)}")
        except ImportError:
            opt.append(f"{name} MISSING")
    print(f"{OK} optional: " + ", ".join(opt))
    return all_ok


def check_prolog():
    exe = shutil.which("swipl")
    if not exe:
        print(f"{WARN} SWI-Prolog not found — needed for weeks 8-9 only")
        print("    brew install swi-prolog   /   sudo apt install swi-prolog")
        return True                     # not a hard failure
    try:
        out = subprocess.run([exe, "--version"], capture_output=True,
                             text=True, timeout=10)
        print(f"{OK} {out.stdout.strip() or 'SWI-Prolog present'}")
    except Exception as exc:            # noqa: BLE001
        print(f"{WARN} swipl found but would not run: {exc}")
    return True


def check_llm():
    avail = backends_available()
    for name, status in avail.items():
        mark = OK if name in ("manual", "echo") or "serving (" in status else WARN
        print(f"{mark} backend {name:<7} {status}")

    llm = LLM(backend="auto")
    if llm.backend == "manual":
        print(f"{OK} LLM backend: manual — this is a PASS, not a failure.")
        print("    Every lab is completable this way. Note your reduced n in reports.")
        return True

    print(f"  probing {llm.backend} ({llm.model}) ...")
    r = llm.complete("Reply with exactly the word: ready", use_cache=False)
    if r.error:
        print(f"{WARN} {llm.backend} failed: {r.error}")
        print("    Falling back to the manual backend is fine.")
        return True
    preview = r.text.strip().replace("\n", " ")[:60]
    print(f"{OK} LLM backend: {llm.backend} ({llm.model}) — "
          f"responded in {r.elapsed:.1f} s: {preview!r}")
    return True


def check_cache():
    c = Cache()
    if not c.writable():
        print(f"{FAIL} .llm_cache/ is not writable in {c.root.absolute()}")
        return False
    print(f"{OK} .llm_cache/ writable ({len(c)} entr{'y' if len(c)==1 else 'ies'})")
    return True


def main(argv=None):
    print("CMP-4004 environment check")
    print("-" * 58)
    results = [
        check_python(),
        check_packages(),
        check_prolog(),
        check_llm(),
        check_cache(),
    ]
    print("-" * 58)
    if all(results):
        print("→ Ready.")
        return 0
    print("→ Some REQUIRED checks failed (marked ✗). Fix those first.")
    print("  Lines marked ! are warnings and will not block you this week.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
