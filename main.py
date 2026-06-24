import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from typing import Any, Dict
import socket

from mouse import MouseManager
from keyboard import KeyboardManager
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
    try:
        while True:
            data: Dict[str, Any] = await websocket.receive_json()
            if data["input"] == "mouse":
                mouse_controller.handle_commands(data)
            elif data["input"] == "keyboard":
                keyboard_controller.handle_commands(data)
    except WebSocketDisconnect:
        print(f"Client disconnected")

if __name__ == "__main__":
    print(f"Remote control start: http://{_get_real_local_ip()}:8000")
    uvicorn.run("main:app", host=Config.WS_SERVER, port=Config.PORT, reload=True)