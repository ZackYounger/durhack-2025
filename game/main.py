import pygame
import random
from . import level_manager
from . import player as player_module
import sys
import json
import subprocess
import os
import socket
import struct
import threading
import time
import zlib
from typing import List
from Coord.find2 import coords


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

def game_loop(screen, is_streaming=False, controllers={}):
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60
    clock = pygame.time.Clock()

    streamer1 = None
    streamer2 = None
    if is_streaming:
        streamer1 = StreamGame(port=9999)
        streamer1.start_server()
        print("[Game] Streaming server 1 started on port 9999.")

        streamer2 = StreamGame(port=10000)
        streamer2.start_server()
        print("[Game] Streaming server 2 started on port 10000.")

    def corners_to_pygame_rect(corner1, corner2, corner3, corner4):
        """
        Converts four corner coordinates of a rectangle into a pygame.Rect object.

        Args:
            corner1 (tuple): (x, y) coordinates of the first corner.
            corner2 (tuple): (x, y) coordinates of the second corner.
            corner3 (tuple): (x, y) coordinates of the third corner.
            corner4 (tuple): (x, y) coordinates of the fourth corner.

        Returns:
            pygame.Rect: A pygame.Rect object representing the bounding box of the four corners.
        """
        # Extract all x and y coordinates
        x_coords = [corner1[0], corner2[0], corner3[0], corner4[0]]
        y_coords = [corner1[1], corner2[1], corner3[1], corner4[1]]

        # Find the top-left corner (minimum x and y)
        min_x = min(x_coords)
        min_y = min(y_coords)

        # Find the bottom-right corner (maximum x and y) to determine width and height
        max_x = max(x_coords)
        max_y = max(y_coords)

        # Calculate width and height
        width = max_x - min_x
        height = max_y - min_y

        # Create and return the pygame.Rect object
        return pygame.Rect(min_x, min_y, width, height)

    # temporarily hardcode for testing
    # data = {
    #     "red": [(0,0),(100,0),(0, 100),(100,100)],
    #     "green": [(200, 200), (300, 200), (200, 300), (300, 300)],
    #     "blue": [(50, 250), (150, 250), (50, 350), (150, 350)]
    # }
    data = coords()
    print(data)

    screen_rects = [corners_to_pygame_rect(*corners) for corners in data.values() if corners != 0]
    colours = data.keys()
    print(screen_rects)

    gravity = 0.5

    level = level_manager.Level()
    level.create_new_level(screen_rects)
    level_surface = pygame.Surface((level.world_size[0], level.world_size[1]))

    player_instance = player_module.Player(level.start_pos, level.block_width, level.border_walls, "SteamMan")

    overview = False
    tick = 0
    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                running = False

        level.draw(level_surface)
        player_instance.update(tick, keys, gravity)
        player_instance.draw(level_surface)

        # Blit the main game surface to the screen
        # screen.blit(level_surface, (0, 0))

        for colour, rect in zip(colours, screen_rects):
            extracted_surface = level_surface.subsurface(rect)

            if is_streaming:
                if streamer1 and colour == "red":
                    streamer1.stream_surface(extracted_surface)
                    print(extracted_surface.get_size(), screen.get_size())

                if streamer2 and colour == "green":
                    streamer2.stream_surface(extracted_surface)
                    print(extracted_surface.get_size(), screen.get_size())
            if colour == "blue":
                screen.blit(extracted_surface, (0,0))

        pygame.display.flip()
        tick += 1

    if is_streaming:
        if streamer1:
            streamer1.stop_server()
            print("[Game] Streaming server 1 stopped.")
        if streamer2:
            streamer2.stop_server()
            print("[Game] Streaming server 2 stopped.")

# This part is for testing the game module directly
if __name__ == "__main__":
    pygame.init()
    info = pygame.display.Info()
    main_screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Game Test")
    
    # Example of calling the loop
    game_loop(main_screen, is_streaming=True)
    
    pygame.quit()
    sys.exit()
