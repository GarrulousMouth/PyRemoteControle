import asyncio
import cv2
import numpy as np
import mss
from pynput.mouse import Controller as MouseController
from fastapi import WebSocket

class ScreenStreamer:
    def __init__(self, quality: int = 75):
        self.encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
        self._is_running = False

        self.stream_enabled = False
        
        self.canvas_width = 400
        self.canvas_height = 400
        self.zoom = 1.0
        
        self.mouse = MouseController()
        
        with mss.mss() as sct:
            all_monitors = sct.monitors[0]
            self.virtual_left = all_monitors["left"]
            self.virtual_top = all_monitors["top"]
            self.virtual_width = all_monitors["width"]
            self.virtual_height = all_monitors["height"]

    def update_client_dimensions(self, width: int, height: int, zoom: float) -> None:
        self.canvas_width = max(100, width)
        self.canvas_height = max(100, height)
        self.zoom = max(0.2, min(5.0, 5.5-zoom))

    def set_stream_state(self, enabled: bool) -> None:
        self.stream_enabled = enabled

    def _draw_cursor(self, frame: np.ndarray, mouse_x: int, mouse_y: int, left: int, top: int) -> None:
        cursor_x = mouse_x - left
        cursor_y = mouse_y - top
        
        thickness = max(2, int(self.zoom * 2))
        cv2.arrowedLine(
            frame, 
            (cursor_x + int(12 * self.zoom), cursor_y + int(12 * self.zoom)), 
            (cursor_x, cursor_y), 
            (0, 0, 255), 
            thickness=thickness, 
            tipLength=0.4
        )

    async def start_stream(self, websocket: WebSocket) -> None:
        self._is_running = True
        
        with mss.mss() as sct:
            try:
                while self._is_running:
                    if not self.stream_enabled:
                        await asyncio.sleep(0.1)
                        continue

                    box_width = int(self.canvas_width * self.zoom)
                    box_height = int(self.canvas_height * self.zoom)
                    
                    mx, my = self.mouse.position
                    mouse_x, mouse_y = int(mx), int(my)

                    left = mouse_x - (box_width // 2)
                    top = my - (box_height // 2)

                    left = max(self.virtual_left, min(left, self.virtual_left + self.virtual_width - box_width))
                    top = max(self.virtual_top, min(top, self.virtual_top + self.virtual_height - box_height))

                    monitor = {"top": top, "left": left, "width": box_width, "height": box_height}

                    sct_img = sct.grab(monitor)
                    img_np = np.array(sct_img)
                    frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

                    self._draw_cursor(frame, mouse_x, mouse_y, left, top)

                    algo = cv2.INTER_AREA if self.zoom > 1.0 else cv2.INTER_LINEAR
                    frame = cv2.resize(frame, (self.canvas_width, self.canvas_height), interpolation=algo)

                    success, encoded_image = cv2.imencode('.webp', frame, self.encode_param)
                    if success:
                        await websocket.send_bytes(encoded_image.tobytes())

                    await asyncio.sleep(0.02)
                    
            except Exception as e:
                print(f"Ошибка стримера: {e}")
            finally:
                self._is_running = False

    def stop(self) -> None:
        self._is_running = False
