import time
import platform
from pynput.keyboard import Controller, Key, KeyCode
from typing import Dict, Any, Union, Optional, Callable

class KeyboardManager:

    def __init__(self) -> None:
        self.keyboard: Controller = Controller()
        self.modifier: Key = Key.cmd if platform.system() == "Darwin" else Key.ctrl_l

    def universal_copy(self) -> None:
        char: Union[str, KeyCode] = 'c' if platform.system() == "Darwin" else KeyCode.from_vk(67)

        with self.keyboard.pressed(self.modifier):
            time.sleep(0.1)
            self.keyboard.press(char)
            self.keyboard.release(char)
        time.sleep(0.1)

    def universal_insert(self) -> None:
        char: Union[str, KeyCode] = 'v' if platform.system() == "Darwin" else KeyCode.from_vk(86)

        with self.keyboard.pressed(self.modifier):
            time.sleep(0.1)
            self.keyboard.press(char)
            self.keyboard.release(char)
        time.sleep(0.1)

    def change_layout(self) -> None:
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press(Key.space)
            self.keyboard.release(Key.space)
        time.sleep(0.1)  

    def handle_commands(self, data: Dict[str, Any]) -> None:
        value: Optional[str] = data.get("value")

        if data["type"] == "text":
            self.keyboard.type(value)
        elif data["type"] == "systemCommand":
            special_command: dict = {
                "changeLayout": self.change_layout,
                "copy": self.universal_copy,
                "insert": self.universal_insert,
            }
            command_func: Optional[Callable] = special_command.get(value)
            if command_func:
                command_func()
        elif data["type"] == "key":
            special_keys: dict = {
                "backspace": Key.backspace,
                "enter": Key.enter,
                "tab": Key.tab,
                "esc": Key.esc,
                "volumeUp": Key.media_volume_up,
                "volumeDown": Key.media_volume_down,
                "nextMedia": Key.media_next,
                "prevMedia": Key.media_previous,
                "playPause": Key.media_play_pause,
                "arrowUp": Key.up,
                "arrowDown": Key.down,
                "arrowLeft": Key.left,
                "arrowRight": Key.right,
            }

            key: Optional[str] = special_keys.get(value)

            if key:
                self.keyboard.press(key)
                self.keyboard.release(key)