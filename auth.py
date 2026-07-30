import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

def open_login(port):
    webbrowser.open(f"https://grandlux.lu/login?redirect_port={port}")

class CallbackHandler(BaseHTTPRequestHandler):
    received_token = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        CallbackHandler.received_token = query.get("token", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>You're logged in - you can close this tab.</h1>")

    def log_message(self, format, *args):
        pass

class LoginListener:
    def __init__(self):
        self.port = None
        self.token = None
        self._lock = threading.Lock()
        self._running = False
        self._server = None

    def start(self) -> None:
        self._running = True
        self._server = HTTPServer(("127.0.0.1", 0), CallbackHandler)
        self.port = self._server.server_address[1]
        thread = threading.Thread(target=self._wait_for_callback, daemon=True)
        thread.start()

    def stop(self) -> None:
        self._running = False

    def _wait_for_callback(self) -> None:
        self._server.timeout = 0.5
        while self._running:
            self._server.handle_request()
            if CallbackHandler.received_token is not None:
                break
        with self._lock:
            self.token = CallbackHandler.received_token

    def get_token(self):
        with self._lock:
            return self.token