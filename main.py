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

    mouse_controller = MouseManager()
    keyboard_controller = KeyboardManager()
    streamer = ScreenStreamer()

    handlers = {
    "mouse": lambda payload: mouse_controller.handle_commands(payload),
    "keyboard": lambda payload: keyboard_controller.handle_commands(payload),
    "stream_state": lambda payload: streamer.set_stream_state(bool(payload)),
    "dimensions": lambda payload: streamer.update_client_dimensions(
        width=int(payload.get("canvas_width", 0)),
        height=int(payload.get("canvas_height", 0)),
        zoom=float(payload.get("zoom", 1.0))
    )
}

    async def receive_loop():
        try:
            while True:
                data: Dict[str, Any] = await websocket.receive_json()

                packet_type = data.get("input")

                if packet_type == "settings":
                    if "mouse" in data:
                        for d in data["mouse"]:
                            handlers["mouse"](d)
                    if "stream" in data: handlers["stream_state"](data["stream"])
                    if "settingStream" in data:
                        # Собираем данные в один объект для хендлера
                        geo_data = data["settingStream"]
                        if "zoom" not in geo_data:
                            geo_data["zoom"] = 2.0
                        handlers["dimensions"](geo_data)
                elif packet_type in handlers:
                    handlers[packet_type](data)
                elif "stream" in data:
                    handlers["stream_state"](data["stream"])
                elif "canvas_width" in data and "canvas_height" in data:
                    handlers["dimensions"](data)
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