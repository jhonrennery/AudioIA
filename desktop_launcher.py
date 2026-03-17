from __future__ import annotations

import os
import threading
import time
import webbrowser

from app.ui import build_app


def _open_browser(url: str) -> None:
    time.sleep(1.5)
    webbrowser.open(url)


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "7860"))
    url = f"http://{host}:{port}"

    threading.Thread(target=_open_browser, args=(url,), daemon=True).start()

    app = build_app()
    app.launch(
        server_name=host,
        server_port=port,
        inbrowser=False,
        prevent_thread_lock=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
