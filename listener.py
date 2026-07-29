import socket
import threading
import struct

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
            parsed = self._parse_packet(data)
            
            if parsed:
                with self._lock:
                    self.parsed_values.update(parsed)

    def _parse_packet(self, data: bytes) -> dict:
        if data[:4] != b"DATA":
            return {}

        body = data[5:]
        result = {}

        for byte in range(0, len(body), 36):
            chunk = body[byte:byte + 36]
            index, *floats = struct.unpack("<i8f", chunk)

            if index == 20:
                result["lat"] = floats[0]
                result["lon"] = floats[1]
                result["alt_msl"] = floats[2]
            elif index == 17:
                result["heading"] = floats[2]
            elif index == 3:
                result["speed"] = floats[0]
                
        return result
    
    def get_latest(self) -> dict:
        with self._lock:
            return self.parsed_values.copy()
                