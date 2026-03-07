#!/usr/bin/env python3
"""
MUIOGO Cross-Platform Development Uninstall Script

Reverses the local state created by setup_dev.py:
  1. Removes the Python virtual environment (.venvs/muiogo)
  2. Removes installed demo data using the marker file
  3. Reverts setup-created entries in the repository .env file
  4. Removes Windows manual solver fallback installs and user PATH entries
  5. (Opt-in) Uninstalls package-manager installed solvers

Usage:
    python scripts/uninstall_dev.py
    python scripts/uninstall_dev.py --uninstall-solvers
    python scripts/uninstall_dev.py --venv-dir ~/my-envs/muiogo
    python scripts/uninstall_dev.py --yes
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENV_DIR = (Path.home() / ".venvs" / "muiogo").resolve()
SYSTEM = platform.system()
DATA_STORAGE_DIR = PROJECT_ROOT / "WebAPP" / "DataStorage"
DEMO_DATA_MARKER = DATA_STORAGE_DIR / ".demo_data_installed.json"
DOTENV_FILE = PROJECT_ROOT / ".env"

BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

if not sys.stdout.isatty():
    BOLD = GREEN = YELLOW = RED = RESET = ""


def _print_header(msg: str) -> None:
    print(f"\n{BOLD}{'=' * 60}")
    print(f"  {msg}")
    print(f"{'=' * 60}{RESET}\n")

def _print_pass(label: str, detail: str = "") -> None:
    suffix = f"  ({detail})" if detail else ""
    print(f"  {GREEN}[Removed]{RESET} {label}{suffix}")

def _print_skip(label: str, detail: str = "") -> None:
    suffix = f"  ({detail})" if detail else ""
    print(f"  {YELLOW}[Skipped]{RESET} {label}{suffix}")

def _print_fail(label: str, detail: str = "") -> None:
    suffix = f"  ({detail})" if detail else ""
    print(f"  {RED}[Failed]{RESET} {label}{suffix}")

def _print_warn(label: str, detail: str = "") -> None:
    suffix = f"  ({detail})" if detail else ""
    print(f"  {YELLOW}[WARN]{RESET} {label}{suffix}")

def _confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    if not sys.stdin.isatty():
        _print_warn("Non-interactive mode requires --yes to proceed", prompt)
        return False
    print()
    answer = input(f"  {YELLOW}{prompt} [y/N]{RESET}: ").strip().lower()
    return answer in ("y", "yes")

def _resolve_venv_dir(venv_dir_arg: str | None) -> Path:
    if venv_dir_arg:
        return Path(venv_dir_arg).expanduser().resolve()
    env_override = os.environ.get("MUIOGO_VENV_DIR", "").strip()
    if env_override:
        return Path(env_override).expanduser().resolve()
    return DEFAULT_VENV_DIR

def _which(name: str) -> str | None:
    return shutil.which(name)

def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, **kwargs)

# ──────────────────────────────────────────────────────────────────────────────
# Uninstall Steps
# ──────────────────────────────────────────────────────────────────────────────

def remove_venv(venv_dir: Path, yes: bool) -> bool:
    _print_header("Step 1: Virtual Environment")
    if not venv_dir.exists():
        _print_skip("Virtual environment not found", str(venv_dir))
        return True

    if not _confirm(f"Remove virtual environment at {venv_dir}?", yes):
        _print_skip("Virtual environment removal cancelled", str(venv_dir))
        return False

    try:
        shutil.rmtree(venv_dir)
        _print_pass("Virtual environment removed", str(venv_dir))
        return True
    except Exception as exc:
        _print_fail("Failed to remove virtual environment", str(exc))
        return False

def remove_demo_data(yes: bool) -> bool:
    _print_header("Step 2: Demo Data")
    if not DEMO_DATA_MARKER.exists():
        _print_skip("Demo data marker not found", "No installed demo data detected")
        return True
    
    try:
        marker_data = json.loads(DEMO_DATA_MARKER.read_text(encoding="utf-8"))
    except Exception as exc:
        _print_fail("Failed to read demo data marker", str(exc))
        return False

    installed_paths = marker_data.get("installed_paths", [])
    if not installed_paths:
        _print_skip("No paths recorded in demo data marker")
        DEMO_DATA_MARKER.unlink(missing_ok=True)
        return True

    targets = []
    for rel_path in installed_paths:
        p = (PROJECT_ROOT / rel_path).resolve()
        if p.exists() and str(p).startswith(str(PROJECT_ROOT)):
            targets.append(p)
    
    if not targets:
        _print_skip("Demo data targets already missing")
        DEMO_DATA_MARKER.unlink(missing_ok=True)
        return True

    print("  The following demo data targets will be removed:")
    for t in targets:
        print(f"    - {t}")
    
    if not _confirm("Remove demo data?", yes):
        _print_skip("Demo data removal cancelled")
        return False

    success = True
    for t in targets:
        try:
            if t.is_dir():
                shutil.rmtree(t)
            else:
                t.unlink()
            _print_pass("Removed demo data target", detail=t.name)
        except Exception as exc:
            _print_fail(f"Failed to remove {t.name}", str(exc))
            success = False

    if success:
        DEMO_DATA_MARKER.unlink(missing_ok=True)
        _print_pass("Demo data marker removed")
    
    return success

def clean_dot_env(yes: bool) -> bool:
    _print_header("Step 3: Repository .env File")
    if not DOTENV_FILE.exists():
        _print_skip(".env file not found")
        return True

    lines = DOTENV_FILE.read_text(encoding="utf-8").splitlines()
    setup_keys = ("GLPK_ROOT", "CBC_ROOT", "GLPK_DIR", "CBC_DIR", "MUIOGO_SETUP")
    
    cleaned_lines = []
    removed_lines = []
    for line in lines:
        if any(line.strip().startswith(f"{k}=") or line.strip().startswith(f"export {k}=") for k in setup_keys):
            removed_lines.append(line)
        else:
            cleaned_lines.append(line)

    if not removed_lines:
        _print_skip("No setup-created entries found in .env")
        return True

    print("  The following entries will be removed from .env:")
    for line in removed_lines:
        print(f"    - {line}")

    if not _confirm("Remove these .env entries?", yes):
        _print_skip(".env cleanup cancelled")
        return False

    try:
        DOTENV_FILE.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
        _print_pass("Setup-created entries removed from .env")
        return True
    except Exception as exc:
        _print_fail("Failed to clean .env", str(exc))
        return False

def remove_windows_manual_solvers(yes: bool) -> bool:
    if SYSTEM != "Windows":
        return True

    _print_header("Step 4: Windows Manual Solvers (Fallback)")
    
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local_app_data.is_dir():
        _print_skip("LOCALAPPDATA not found")
        return True

    glpk_dir = local_app_data / "glpk"
    cbc_dir = local_app_data / "cbc"
    
    targets = []
    if glpk_dir.exists(): targets.append(glpk_dir)
    if cbc_dir.exists(): targets.append(cbc_dir)

    if targets:
        print("  The following manual local solver installations will be removed:")
        for t in targets:
            print(f"    - {t}")
        
        if _confirm("Remove local solver directories?", yes):
            for t in targets:
                try:
                    shutil.rmtree(t)
                    _print_pass("Removed local solver", str(t))
                except Exception as exc:
                    _print_fail("Failed to remove local solver", str(t))
        else:
            _print_skip("Local solver removal cancelled")
    else:
        _print_skip("No manual local solver directories found")

    # Remove User PATH entries via Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            path_val, _ = winreg.QueryValueEx(key, "PATH")
        except OSError:
            path_val = ""
        
        path_parts = path_val.split(";")
        new_parts = []
        removed = []
        for p in path_parts:
            if not p.strip(): continue
            p_upper = p.upper()
            if "LOCALAPPDATA" in p_upper and ("GLPK" in p_upper or "CBC" in p_upper):
                removed.append(p)
            elif str(glpk_dir).upper() in p_upper or str(cbc_dir).upper() in p_upper:
                removed.append(p)
            else:
                new_parts.append(p)
        
        if removed:
            print("  The following user PATH entries will be removed:")
            for r in removed:
                print(f"    - {r}")
            if _confirm("Remove user PATH entries?", yes):
                new_path_val = ";".join(new_parts)
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path_val)
                _print_pass("User PATH updated")
                # Broadcast environment change
                import ctypes
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x001A
                SMTO_ABORTIFHUNG = 0x0002
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
                    SMTO_ABORTIFHUNG, 5000, None
                )
            else:
                _print_skip("User PATH removal cancelled")
        else:
            _print_skip("No setup-created solver paths found in user PATH")
            
        winreg.CloseKey(key)
        
        # Also clean GLPK_ROOT or CBC_ROOT env vars if present
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        for val_name in ["GLPK_ROOT", "CBC_ROOT"]:
            try:
                winreg.QueryValueEx(key, val_name)
                print(f"  Found user environment variable: {val_name}")
                if _confirm(f"Remove user environment variable {val_name}?", yes):
                    winreg.DeleteValue(key, val_name)
                    _print_pass(f"Removed '{val_name}'")
            except OSError:
                pass
        winreg.CloseKey(key)

    except Exception as exc:
        _print_warn("Failed to check or update Windows Registry for PATH/Env Vars", str(exc))

    return True

def remove_system_solvers(uninstall_solvers: bool, yes: bool) -> bool:
    _print_header("Step 5: System Solvers (Package Managers)")
    
    if not uninstall_solvers:
        _print_skip("System solver uninstall not requested", "Use --uninstall-solvers to opt-in")
        return True

    print(f"  {YELLOW}Warning: Package manager solvers (brew/apt/choco) may be used by outside projects.{RESET}")
    if not _confirm("Are you sure you want to uninstall system-wide solvers?", yes):
        _print_skip("System solver uninstall cancelled")
        return False

    success = True
    if SYSTEM == "Darwin" and _which("brew"):
        for pkg in ["glpk", "cbc"]:
            r = _run(["brew", "uninstall", pkg], capture_output=True, text=True)
            if r.returncode == 0:
                _print_pass("Uninstalled", pkg)
            else:
                _print_skip("Brew uninstall skipped or failed", f"{pkg} ({r.stderr.strip()})")

    elif SYSTEM == "Linux":
        if _which("apt-get"):
            for pkg in ["glpk-utils", "coinor-cbc"]:
                r = _run(["sudo", "apt-get", "remove", "-y", pkg], capture_output=True, text=True)
                if r.returncode == 0:
                    _print_pass("Uninstalled", pkg)
                else:
                    _print_skip("Apt remove skipped or failed", pkg)
        elif _which("dnf"):
            for pkg in ["glpk-utils", "coin-or-Cbc"]:
                r = _run(["sudo", "dnf", "remove", "-y", pkg], capture_output=True, text=True)
                if r.returncode == 0:
                    _print_pass("Uninstalled", pkg)
        elif _which("pacman"):
            for pkg in ["glpk", "coin-or-cbc"]:
                r = _run(["sudo", "pacman", "-R", "--noconfirm", pkg], capture_output=True, text=True)
                if r.returncode == 0:
                    _print_pass("Uninstalled", pkg)

    elif SYSTEM == "Windows" and _which("choco"):
        for pkg in ["glpk", "coinor-cbc"]:
            r = _run(["choco", "uninstall", pkg, "-y"], capture_output=True, text=True)
            if r.returncode == 0:
                _print_pass("Uninstalled via Chocolatey", pkg)
            else:
                _print_skip("Choco uninstall skipped or failed", f"{pkg} ({r.stderr.strip()})")
    
    return success

def main() -> int:
    parser = argparse.ArgumentParser(description="MUIOGO Cross-Platform Uninstall Script")
    parser.add_argument("--venv-dir", help="Virtual environment directory path.")
    parser.add_argument("--uninstall-solvers", action="store_true", help="Opt-in to uninstall system solvers via package managers.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts.")
    args = parser.parse_args()

    print(f"\n{BOLD}MUIOGO Development Environment Uninstaller{RESET}")
    
    venv_dir = _resolve_venv_dir(args.venv_dir)

    remove_venv(venv_dir, args.yes)
    remove_demo_data(args.yes)
    clean_dot_env(args.yes)
    
    if SYSTEM == "Windows":
        remove_windows_manual_solvers(args.yes)
        
    remove_system_solvers(args.uninstall_solvers, args.yes)

    print(f"\n{GREEN}{BOLD}Uninstall complete.{RESET}")
    print("You can run `./scripts/setup.sh` or `scripts\\setup.bat` to reinstall a fresh environment.\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
