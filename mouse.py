from pynput.mouse import Controller, Button
from typing import Dict, Any, Optional

from config import Config

class MouseManager:

    def __init__(self) -> None:
        self.mouse: Controller = Controller()

    def handle_commands(self, data: Dict[str, Any]) -> None:
        action: Optional[str] = data.get("type")

        if action == "move":
            x: int = data.get("x", 0)
            y: int = data.get("y", 0)
            self.move_mouse(x, y)
        elif action == "clickLeft":
            self.click_left()
            print("clickLeft")
        elif action == "clickRight":
            self.click_right()
        elif action == "clickMiddle":
            self.click_middle()
        elif action == "dragAndDrop":
            command: Optional[str] = data.get("command")
            if command:
                self.drag_and_drop(command)
        elif action == "scroll":
            y: int = data.get("y")
            self.scroll_mouse(y)

    def click_left(self) -> None:
        self.mouse.click(Button.left)

    def move_mouse(self, x: int, y: int) -> None:
        self.mouse.move(x * Config.MOUSE_SENSITIVITY, y * Config.MOUSE_SENSITIVITY)

    def drag_and_drop(self, action: str) -> None:
        if action == "press":
            self.mouse.press(Button.left)
            print("press")
        elif action == "release":
            self.mouse.release(Button.left)
            print("release")

    def scroll_mouse(self, y: int) -> None:
        self.mouse.scroll(0, y * Config.SCROLL_FACTOR)

    def click_middle(self) -> None:
        self.mouse.click(Button.middle)

    def click_right(self) -> None:
        self.mouse.click(Button.right)