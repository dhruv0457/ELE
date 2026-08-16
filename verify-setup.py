#!/usr/bin/env python3
"""Verify ELE Agent local setup"""
import sys
import subprocess
import os
from pathlib import Path

ROOT = Path(__file__).parent

def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd or ROOT, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    ok, out, _ = run_cmd("python --version")
    if ok:
        print(f"  [OK] Python: {out.strip()}")
        return True
    print(f"  [FAIL] Python not found")
    return False

def check_node():
    ok, out, _ = run_cmd("node --version")
    if ok:
        print(f"  [OK] Node.js: {out.strip()}")
        return True
    print(f"  [FAIL] Node.js not found")
    return False

def check_npm():
    ok, out, _ = run_cmd("npm --version")
    if ok:
        print(f"  [OK] npm: {out.strip()}")
        return True
    print(f"  [FAIL] npm not found")
    return False

def check_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        print(f"  [OK] .env file exists")
        return True
    print(f"  [FAIL] .env file missing (copy from .env.example)")
    return False

def check_backend():
    backend = ROOT / "backend"
    if not backend.exists():
        print(f"  [FAIL] backend/ directory missing")
        return False
    
    venv = backend / ".venv"
    if not venv.exists():
        print(f"  [WARN] backend/.venv not created (run install)")
        return False
    
    for f in ["app/main.py", "app/config.py", "pyproject.toml", "requirements.txt"]:
        if not (backend / f).exists():
            print(f"  [FAIL] Missing: {f}")
            return False
    
    print(f"  [OK] Backend structure OK")
    return True

def check_web():
    web = ROOT / "web"
    if not web.exists():
        print(f"  [FAIL] web/ directory missing")
        return False
    
    for f in ["package.json", "next.config.js", "tsconfig.json", "src/app/page.tsx"]:
        if not (web / f).exists():
            print(f"  [FAIL] Missing: {f}")
            return False
    
    print(f"  [OK] Web structure OK")
    return True

def check_desktop():
    desktop = ROOT / "desktop"
    if not desktop.exists():
        print(f"  [FAIL] desktop/ directory missing")
        return False
    
    for f in ["package.json", "src/main/main.ts", "src/preload/preload.ts", "src/renderer/App.tsx"]:
        if not (desktop / f).exists():
            print(f"  [FAIL] Missing: {f}")
            return False
    
    print(f"  [OK] Desktop structure OK")
    return True

def check_cli():
    cli = ROOT / "cli"
    if not cli.exists():
        print(f"  [FAIL] cli/ directory missing")
        return False
    
    for f in ["pyproject.toml", "src/app.py", "src/screens/chat.py"]:
        if not (cli / f).exists():
            print(f"  [FAIL] Missing: {f}")
            return False
    
    print(f"  [OK] CLI structure OK")
    return True

def check_extensions():
    ext = ROOT / "extensions"
    plugins = ["file-processor", "web-searcher", "code-assistant", "python-code-assistant"]
    all_ok = True
    for p in plugins:
        manifest = ext / p / "manifest.json"
        skill = ext / p / "skill.json"
        if not manifest.exists() and not skill.exists():
            print(f"  [FAIL] Missing plugin manifest: {p}")
            all_ok = False
    
    if all_ok:
        print(f"  [OK] Extensions OK")
    return all_ok

def check_docs():
    docs = ROOT / "docs"
    required = ["architecture.md", "api.md", "deployment.md", "user-guide.md", "ui-specs.md", "plugin-guide.md"]
    all_ok = True
    for d in required:
        if not (docs / d).exists():
            print(f"  [FAIL] Missing doc: {d}")
            all_ok = False
    
    if all_ok:
        print(f"  [OK] Documentation OK")
    return all_ok

def check_github():
    gh = ROOT / ".github" / "workflows"
    if not gh.exists():
        print(f"  [FAIL] .github/workflows missing")
        return False
    
    for w in ["ci.yml", "deploy.yml"]:
        if not (gh / w).exists():
            print(f"  [FAIL] Missing workflow: {w}")
            return False
    
    print(f"  [OK] GitHub workflows OK")
    return True

def main():
    print("=" * 50)
    print("ELE Agent Local Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Prerequisites", [
            ("Python 3.11+", check_python),
            ("Node.js 20+", check_node),
            ("npm", check_npm),
        ]),
        ("Configuration", [
            (".env file", check_env),
        ]),
        ("Backend", [
            ("Structure", check_backend),
        ]),
        ("Web Frontend", [
            ("Structure", check_web),
        ]),
        ("Desktop App", [
            ("Structure", check_desktop),
        ]),
        ("CLI/TUI", [
            ("Structure", check_cli),
        ]),
        ("Extensions", [
            ("Plugins", check_extensions),
        ]),
        ("Documentation", [
            ("Docs", check_docs),
        ]),
        ("CI/CD", [
            ("Workflows", check_github),
        ]),
    ]
    
    all_passed = True
    for category, items in checks:
        print(f"\n{category}:")
        for name, check_fn in items:
            if not check_fn():
                all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("[OK] All checks passed! Ready to run.")
        print("\nStart with:")
        print("  Windows:  .\\start-local.ps1")
        print("  Linux/Mac: ./start-local.sh")
        return 0
    else:
        print("[FAIL] Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())