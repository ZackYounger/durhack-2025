# stream_game.py
# Library-only: StreamGame class. No CLI, no viewer.
import socket
import struct
import threading
import time
import zlib
from typing import List

import pygame

_HEADER_FMT = "!III"   # width, height, payload_len (u32, network byte order)
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)

class StreamGame:

    """
    Stream Pygame surfaces (frames) to multiple TCP clients.

    Protocol per frame:
      header (12 bytes): width:uint32, height:uint32, payload_len:uint32 (big-endian)
      payload: zlib-compressed RGB bytes (len = w*h*3 before compression)
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 9999, max_clients: int = 3, target_fps: int = 20):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.target_fps = max(1, int(target_fps))
        self._min_frame_interval = 1.0 / float(self.target_fps)

        self._server_sock: socket.socket | None = None
        self._accept_thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._clients: List[socket.socket] = []
        self._clients_lock = threading.Lock()
        self._last_sent_time = 0.0

    @property
    def client_count(self) -> int:
        with self._clients_lock:
            return len(self._clients)

    # ---- lifecycle ----
    def start_server(self) -> None:
        if self._server_sock is not None:
            return
        self._stop_flag.clear()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(self.max_clients)
        self._server_sock = s

        t = threading.Thread(target=self._accept_loop, name="StreamGameAccept", daemon=True)
        t.start()
        self._accept_thread = t

    def stop_server(self) -> None:
        self._stop_flag.set()
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None

        with self._clients_lock:
            for c in self._clients[:]:
                try:
                    c.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    c.close()
                except Exception:
                    pass
            self._clients.clear()

        if self._accept_thread and self._accept_thread.is_alive():
            self._accept_thread.join(timeout=1.0)
        self._accept_thread = None

    # ---- internals ----
    def _accept_loop(self) -> None:
        while not self._stop_flag.is_set():
            try:
                self._server_sock.settimeout(0.5)
                client, _ = self._server_sock.accept()
            except socket.timeout:
                continue
            except Exception:
                if self._stop_flag.is_set():
                    break
                else:
                    continue

            with self._clients_lock:
                if len(self._clients) >= self.max_clients:
                    try:
                        client.close()
                    except Exception:
                        pass
                    continue
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._clients.append(client)

    # ---- streaming ----
    def stream_surface(self, surface: "pygame.Surface") -> None:

        # control the rate of streaming
        now = time.time()
        if now - self._last_sent_time < self._min_frame_interval:
            return
        self._last_sent_time = now


        # extract pygame surface
        w, h = surface.get_size()
        #24 bit rgb format
        rgb_surface = surface.convert(24)

        # [R,G,B][R,G,B]    
        raw_bytes = pygame.image.tostring(rgb_surface, "RGB")
        # compress (lvl 3 - good balance between speed and size)
        payload = zlib.compress(raw_bytes, level=3)


        header = struct.pack(_HEADER_FMT, w, h, len(payload))
        packet = header + payload

        dead = []
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.sendall(packet)
                except Exception:
                    dead.append(c)
            for c in dead:
                try:
                    self._clients.remove(c)
                except ValueError:
                    pass
                try:
                    c.close()
                except Exception:
                    pass
