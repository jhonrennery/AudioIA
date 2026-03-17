from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INSTALL_DIR = Path.home() / ".local/share/audioia"
BIN_DIR = Path.home() / ".local/bin"
DESKTOP_DIR = Path.home() / ".local/share/applications"

EXCLUDED = {
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}


def ignore_filter(_dir: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        if name in EXCLUDED or name.endswith(".pyc"):
            ignored.add(name)
    return ignored


def write_launcher() -> None:
    launcher_path = BIN_DIR / "audioia"
    launcher_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'python3 "{INSTALL_DIR / "desktop_launcher.py"}"\n',
        encoding="utf-8",
    )
    launcher_path.chmod(launcher_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_desktop_file() -> None:
    desktop_path = DESKTOP_DIR / "audioia.desktop"
    desktop_path.write_text(
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=AudioIA\n"
        "Comment=Transcreve, reescreve e traduz audio\n"
        f'Exec={BIN_DIR / "audioia"}\n'
        "Terminal=false\n"
        "Categories=AudioVideo;Utility;\n",
        encoding="utf-8",
    )


def install() -> None:
    print(f"Instalando AudioIA em {INSTALL_DIR}")
    INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)

    shutil.copytree(ROOT, INSTALL_DIR, ignore=ignore_filter)

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "-r", str(INSTALL_DIR / "requirements.txt")],
        check=True,
    )

    write_launcher()
    write_desktop_file()

    print("Instalacao concluida.")
    print(f"Abra pelo comando: {BIN_DIR / 'audioia'}")
    print("Ou procure por AudioIA no menu de aplicativos.")


if __name__ == "__main__":
    install()
