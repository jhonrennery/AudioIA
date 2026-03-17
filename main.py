import os

from app.ui import build_app


app = build_app()


if __name__ == "__main__":
    app.launch(
        server_name=os.getenv("HOST", "0.0.0.0"),
        server_port=int(os.getenv("PORT", "7860")),
    )
