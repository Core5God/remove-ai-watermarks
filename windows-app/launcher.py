"""Start the local app and show it in the user's default browser."""

import threading
import webbrowser

from app import app


def open_browser() -> None:
    webbrowser.open_new("http://127.0.0.1:7860")


if __name__ == "__main__":
    threading.Timer(0.8, open_browser).start()
    app.run(host="127.0.0.1", port=7860, debug=False)
