import socket
import threading
import struct

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49005
ROW_POSITION = 20
ROW_HEADING = 17
ROW_SPEED = 3

class XPlaneListener:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.parsed_values = {}
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        self._running = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()

    def _listen_loop(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))

        while self._running:
            data, addr = sock.recvfrom(1024)
            # Add data to the parsed_values dictionary



