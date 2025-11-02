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
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    running = True
    first_size = True

    def draw_waiting():
        screen.fill((10, 10, 12))
        font = pygame.font.SysFont(None, 72)
        small = pygame.font.SysFont(None, 36)
        msg = font.render("Waiting for host to start…", True, (220, 220, 220))
        # sub = small.render(f"{host}:{port}. Press ESC to quit", True, (180, 180, 180))
        rect = msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        # rect2 = sub.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40))
        screen.blit(msg, rect)
        # screen.blit(sub, rect2)
        pygame.display.flip()

    while running:
        # ---- WAIT & CONNECT PHASE ----
        # show waiting screen and keep trying to connect
        connected_sock = None
        while running and connected_sock is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            draw_waiting()

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(2.5)  # quick retry cadence
                sock.connect((host, port))
                sock.settimeout(None)
                connected_sock = sock
                print(f"[Viewer] Connected to {host}:{port}")
                first_size = True
            except Exception:
                pygame.time.delay(500)
                continue

        if not running:
            break

        # ---- STREAM PHASE ----
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False

                header = _recv_exact(connected_sock, _HEADER_SIZE)
                w, h, payload_len = struct.unpack(_HEADER_FMT, header)
                payload = _recv_exact(connected_sock, payload_len)
                raw = zlib.decompress(payload)

                try:
                    frame = pygame.image.frombuffer(raw, (w, h), "RGB")
                except Exception:
                    frame = pygame.image.fromstring(raw, (w, h), "RGB")

                # Keep fullscreen; first frame just adjusts internal scaling
                if first_size:
                    first_size = False

                win_w, win_h = screen.get_size()
                scale = min(win_w / w, win_h / h)
                disp_w, disp_h = max(1, int(w * scale)), max(1, int(h * scale))
                scaled = pygame.transform.smoothscale(frame, (disp_w, disp_h))

                screen.fill((10, 10, 12))
                screen.blit(scaled, ((win_w - disp_w) // 2, (win_h - disp_h) // 2))
                pygame.display.flip()
                clock.tick(120)

        except Exception:
            # Lost connection — loop back to waiting
            try:
                connected_sock.close()
            except Exception:
                pass
            continue

    pygame.quit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Viewer for StreamGame streams.")
    ap.add_argument("--host", type=str, default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9999)
    args = ap.parse_args()
    run_viewer(args.host, args.port)
