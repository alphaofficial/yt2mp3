from __future__ import annotations

import os
import platform
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import get_yt2mp3_home

DEFAULT_REPO = "alphaofficial/yt2mp3"


class LifecycleError(RuntimeError):
    pass


@dataclass(frozen=True)
class LifecycleResult:
    success: bool
    message: str
    path: Optional[Path] = None
    artifact: Optional[str] = None


def default_install_path(home: Optional[Path] = None) -> Path:
    return (home or get_yt2mp3_home()) / "bin" / "yt2mp3"


def _platform_os() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    if system == "linux":
        return "linux"
    raise LifecycleError(f"Unsupported OS: {platform.system()}")


def _platform_arch() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "amd64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    raise LifecycleError(f"Unsupported architecture: {platform.machine()}")


def artifact_name() -> str:
    return f"yt2mp3-{_platform_os()}-{_platform_arch()}"


def _download_url(repo: str, artifact: str) -> str:
    return f"https://github.com/{repo}/releases/latest/download/{artifact}"


def _chmod_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _clear_macos_quarantine(path: Path) -> None:
    if platform.system().lower() == "darwin":
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(path)], check=False)


def upgrade(*, home: Optional[Path] = None, repo: str = DEFAULT_REPO) -> LifecycleResult:
    install_path = default_install_path(home)
    install_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = artifact_name()
    url = _download_url(repo, artifact)

    fd, tmp_name = tempfile.mkstemp(prefix="yt2mp3-upgrade-", dir=str(install_path.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        subprocess.run(["curl", "-fsSL", url, "-o", str(tmp_path)], check=True)
        _chmod_executable(tmp_path)
        os.replace(tmp_path, install_path)
        _clear_macos_quarantine(install_path)
        try:
            subprocess.run([str(install_path), "--version"], check=False, capture_output=True, text=True)
        except Exception:
            pass
    except Exception as exc:
        tmp_path.unlink(missing_ok=True)
        raise LifecycleError(f"Upgrade failed: {exc}") from exc

    return LifecycleResult(True, f"Upgraded yt2mp3 at {install_path}", install_path, artifact)


def _is_safe_home(home: Path) -> bool:
    resolved = home.expanduser().resolve()
    return resolved.name == ".yt2mp3" and resolved != Path("/") and len(resolved.parts) >= 3


def uninstall(*, home: Optional[Path] = None, yes: bool = False) -> LifecycleResult:
    target = home or get_yt2mp3_home()
    target = target.expanduser()
    if not _is_safe_home(target):
        raise LifecycleError(f"Refusing to remove suspicious path: {target}")
    if not yes:
        raise LifecycleError("Pass --yes to confirm uninstall")
    if target.exists():
        shutil.rmtree(target)
    return LifecycleResult(True, f"Removed {target}", target)
