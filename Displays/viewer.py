# viewer.py
# Standalone viewer for StreamGame streams.
import argparse
import socket
import struct
import zlib

import pygame

_HEADER_FMT = "!III"   # width, height, payload_len
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed while receiving.")
        buf.extend(chunk)
    return bytes(buf)

def run_viewer(host: str, port: int, title: str = "StreamGame Viewer") -> None:
    pygame.init()
    screen = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((host, port))

    first_size = True
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            header = _recv_exact(sock, _HEADER_SIZE)
            w, h, payload_len = struct.unpack(_HEADER_FMT, header)
            payload = _recv_exact(sock, payload_len)
            raw = zlib.decompress(payload)
        except Exception:
            break

        try:
            frame = pygame.image.frombuffer(raw, (w, h), "RGB")
        except Exception:
            frame = pygame.image.fromstring(raw, (w, h), "RGB")

        if first_size:
            screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
            first_size = False

        win_w, win_h = screen.get_size()
        scale = min(win_w / w, win_h / h)
        disp_w, disp_h = max(1, int(w * scale)), max(1, int(h * scale))
        scaled = pygame.transform.smoothscale(frame, (disp_w, disp_h))

        screen.fill((10, 10, 12))
        screen.blit(scaled, ((win_w - disp_w) // 2, (win_h - disp_h) // 2))
        pygame.display.flip()
        clock.tick(120)

    try:
        sock.close()
    except Exception:
        pass
    pygame.quit()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Viewer for StreamGame streams.")
    ap.add_argument("--host", type=str, default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9999)
    args = ap.parse_args()
    run_viewer(args.host, args.port)
