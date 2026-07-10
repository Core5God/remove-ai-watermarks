"""Start the local app and show it in the user's default browser."""

import os
import socket
import threading
import webbrowser

from app import app


def choose_available_port(preferred: int = 7860) -> int:
    """Use the preferred port when free, otherwise ask Windows for a free one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            probe.bind(("127.0.0.1", 0))
            return int(probe.getsockname()[1])


def open_browser(url: str) -> None:
    webbrowser.open_new(url)


if __name__ == "__main__":
    preferred_port = int(os.environ.get("WATERMARK_HELPER_PORT", "7860"))
    port = choose_available_port(preferred_port)
    url = f"http://127.0.0.1:{port}"
    if os.environ.get("WATERMARK_HELPER_NO_BROWSER") != "1":
        threading.Timer(0.8, open_browser, args=(url,)).start()
    app.run(host="127.0.0.1", port=port, debug=False)
