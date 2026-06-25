import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from typing import Any, Dict
import socket

from mouse import MouseManager
from keyboard import KeyboardManager
from streamer import ScreenStreamer
from config import Config

app = FastAPI()
mouse_controller = MouseManager()
keyboard_controller = KeyboardManager()

def _get_real_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        real_ip = s.getsockname()[0]
    except Exception:
        real_ip = '127.0.0.1'
    finally:
        s.close()
    return real_ip

@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse("templates/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    streamer = ScreenStreamer()
    # streamer.update_box_size(1000)
    async def receive_loop():
        try:
            while True:
                data: Dict[str, Any] = await websocket.receive_json()
                print(data)
                if "stream" in data:
                    print(data["stream"])
                    streamer.set_stream_state(bool(data["stream"]))
                
                elif "canvas_width" in data and "canvas_height" in data and "zoom" in data:
                    streamer.update_client_dimensions(
                        width=int(data['canvas_width']),
                        height=int(data["canvas_height"]),
                        zoom=float(data["zoom"])
                    )
                elif data["input"] == "mouse":
                    mouse_controller.handle_commands(data)
                elif data["input"] == "keyboard":
                    keyboard_controller.handle_commands(data)
        except Exception:
            pass


    receive_task = asyncio.create_task(receive_loop())
    send_video_task = asyncio.create_task(streamer.start_stream(websocket))

    try:
        await asyncio.wait(
            [receive_task, send_video_task],
            return_when=asyncio.FIRST_COMPLETED
        )
    except WebSocketDisconnect:
        print(f"Client disconnected")
    finally:
        streamer.stop()
        receive_task.cancel()
        send_video_task.cancel()
        

if __name__ == "__main__":
    print(f"Remote control start: http://{_get_real_local_ip()}:8000")
    uvicorn.run("main:app", host=Config.WS_SERVER, port=Config.PORT, reload=True)