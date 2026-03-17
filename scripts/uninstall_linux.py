from __future__ import annotations

import shutil
from pathlib import Path


INSTALL_DIR = Path.home() / ".local/share/audioia"
BIN_PATH = Path.home() / ".local/bin/audioia"
DESKTOP_PATH = Path.home() / ".local/share/applications/audioia.desktop"


def uninstall() -> None:
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    if BIN_PATH.exists():
        BIN_PATH.unlink()
    if DESKTOP_PATH.exists():
        DESKTOP_PATH.unlink()

    print("AudioIA removido do computador.")


if __name__ == "__main__":
    uninstall()
