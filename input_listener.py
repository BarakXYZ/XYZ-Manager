"""
~ BarakXYZ - XYZ Manager - 2024 - CS50x Final Project ~
The input listener catches the keyboard and mouse events and emits signals to the main application.
It is also incharge of executing the actions based on the keyboard shortcuts.
It is designed in a non-blocking way, so that the main application can run smoothly.
This is done by using Qt threads and signals.
"""

from PySide6.QtCore import QObject, Signal
from pynput import keyboard, mouse
import configparser
import time


class KeyboardListener(QObject):
    finished = Signal()
    quit_requested = Signal()
    key_print = Signal(
        str
    )  # str is the type of data that will be emitted, the signal will be connected to a slot that will receive this data
    key_release_print = Signal(str)
    user_response = Signal(bool)
    configure_window = Signal()
    window_action = Signal(int, str)
    window_number_assignment = Signal(int)

    def __init__(self, config_file):
        super().__init__()
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(config_file)
        self.user_shortcuts = {}

        print("Config file memory adderess: ", config_file)
        self.create_user_shortcuts(config_file)

        # self.config.read("config.ini")
        self.pressed_since_released = False
        self.hotkey_listener = True
        self.waiting_for_specific_input = False
        self.listen_pynput = True
        self.can_run = True
        self.waiting_for_number_assignment = False

        self.outcast_keys_map = {
            "Þ": "'",
            "Ü": "|",
            "¿": "?",
            "¾": ">",
            "¼": "<",
            "Ý": "}",
            "Û": "{",
            "º": ":",
            "»": "+",
        }
        self.outcast_keys_regular_map = {"▲": "6", r"\x1f": "-"}
        self.symbol_to_number = {
            "!": "1",  # Shift+1 is !
            "@": "2",  # Shift+2 is @
            "#": "3",  # Shift+3 is #
            "$": "4",  # Shift+4 is $
            "%": "5",  # Shift+5 is %
            "^": "6",  # Shift+6 is ^
            "&": "7",  # Shift+7 is &
            "*": "8",  # Shift+8 is *
            "(": "9",  # Shift+9 is (
            ")": "0",  # Shift+0 is )
            "<": ",",  # Shift+, is <
            ">": ".",  # Shift+. is >
            "?": "/",  # Shift+/ is ?
            ":": ";",  # Shift+; is :
            '"': "'",  # Shift+' is "
            "{": "[",  # Shift+[ is {
            "}": "]",  # Shift+] is }
            "|": "\\",  # Shift+\ is |
            "_": "-",  # Shift+- is _
            "+": "=",  # Shift+= is +
            "~": "`",  # Shift+` is ~
            r"'\x1f'": "-",
        }
        self.pressed_keys = {}
        self.listener_loop = 0.25
        self.is_active = 0

        # self.COMBOS = {"<49>": "Action1"}
        # Define your key combinations as frozensets for immutability and efficient comparison

    def create_user_shortcuts(self, config_file):
        print("Reading config file...")
        # Initialize user_shortcuts if it's not already
        self.user_shortcuts = {}

        # Read "Keyboard Shortcuts" section
        for key, value in config_file.items("Keyboard Shortcuts"):
            # Split the value by '+' and replace 'plus' with '+'
            values = [v if v != "plus" else "+" for v in value.split("+")]
            self.user_shortcuts[key] = values
        print(f"User Shortcuts: {self.user_shortcuts}")

    def start_listener(self):
        self.listen_pynput = True

    def stop_listener(self):
        self.listen_pynput = False

    def get_listener_status(self):
        return self.listen_pynput

    def on_keyboard_events_pynput(self):
        with keyboard.Events() as events:
            while self.can_run:
                if not self.listen_pynput:
                    time.sleep(1)
                else:
                    event = events.get(self.listener_loop)
                    # print("Listener Loop")
                    if event is None:
                        # print("EVENT IS NONE")
                        # print(f"Is Active: {self.is_active}")
                        if self.is_active < 3:
                            self.is_active += 1
                        else:
                            self.pressed_keys = {}
                            self.listener_loop = 0.25
                            self.is_active = 0

                        continue
                    else:
                        # print("EVENT IS NOT NONE")
                        self.listener_loop = 0.15
                        self.is_active = 0

                    if not self.waiting_for_specific_input:
                        # if self.waiting_for_number_assignment:
                        #     return
                        if (
                            isinstance(event, keyboard.Events.Press)
                            and event.key not in self.pressed_keys
                            and not event.key == keyboard.Key.esc
                        ):
                            key = event.key
                            self.pressed_since_released = True

                            # Check if the key is a KeyCode (which can have a char attribute)
                            if hasattr(key, "char") and key.char:
                                # If the key's char is a control unicode, convert it
                                if self.is_ctrl_unicode(key.char):
                                    char = self.character_from_ctrl_unicode(
                                        self.get_unicode_order_from_char(key.char)
                                    )
                                    print(f"Control key pressed: {char}")
                                    self.key_print.emit(char)

                                    self.pressed_keys[key] = char
                                    # print(f"Pressed Keys: {self.pressed_keys[key]}")
                                    # You can now use `char` as the representation of the control key
                                else:
                                    if hasattr(key, "vk"):
                                        if key.vk == 50 or key.vk == 54:
                                            key_regular = chr(key.vk)
                                        else:
                                            key_regular = key.char.lower()
                                    else:
                                        key_regular = key.char.lower()
                                    # print(f"Regular Key pressed: {key_regular}")
                                    if not key_regular.isalnum():
                                        key_regular = self.symbol_to_number.get(
                                            key_regular, None
                                        )
                                        print("SYMBOL TO NUMBER: ", key_regular)
                                    # print(f"Regular Value: {key.vk}")
                                    print(f"Regular Key pressed: {key_regular}")

                                    self.key_print.emit(key_regular)
                                    if self.waiting_for_number_assignment:
                                        try:
                                            key_regular = int(key_regular)
                                        except:
                                            key_regular = 99
                                        self.window_number_assignment.emit(key_regular)
                                    else:
                                        if key_regular == None:
                                            key_regular = self.symbol_to_number.get(
                                                str(key), None
                                            )

                                        self.pressed_keys[key] = key_regular
                                    # print(f"Pressed Keys: {self.pressed_keys}")
                            else:
                                if hasattr(key, "vk"):
                                    key_chr = chr(key.vk)
                                    if key_chr in self.outcast_keys_map:
                                        key_chr = self.outcast_keys_map[key_chr]
                                    # key_value = key.value
                                    # print(f"Key Value: {key_value}")
                                    print(f"Key pressed (vk): {key_chr}")
                                    self.key_print.emit(key_chr)
                                    self.pressed_keys[key] = key_chr
                                    # print(f"Pressed Keys: {self.pressed_keys}")
                                else:
                                    print(f"Special Key pressed: {key}")
                                    special_key = format(key).split(".")[1]
                                    self.key_print.emit(special_key)
                                    self.pressed_keys[key] = special_key
                                    # print(f"Pressed Keys: {self.pressed_keys}")
                            # If we want this on pressed, but the problem is that the user might have both ctrl+shift+1 and ctrl+shift+1+up (which in this case hee can never reach the second one)
                            # if detected_combo := self.detect_combinations():
                            #     self.execute_action(detected_combo)

                            print(f"Pressed Keys: {self.pressed_keys}")

                        elif (
                            isinstance(event, keyboard.Events.Release)
                            and event.key in self.pressed_keys
                        ):
                            if self.pressed_since_released:
                                if detected_combo := self.detect_combinations():
                                    self.execute_action(detected_combo)
                                else:
                                    del self.pressed_keys[event.key]
                                    self.pressed_since_released = False
                            else:
                                del self.pressed_keys[event.key]
                                self.pressed_since_released = False

                        elif (
                            isinstance(event, keyboard.Events.Release)
                            and event.key == keyboard.Key.esc
                        ):
                            print("Esc pressed. Exiting...")
                            self.stop_listener()
                            self.quit_requested.emit()
                            break
                    else:
                        if (
                            isinstance(event, keyboard.Events.Press)
                            and not event.key == keyboard.Key.esc
                        ):
                            if event.key == keyboard.Key.enter:
                                self.user_response.emit(True)
                                self.pressed_keys = {}
                                print("User response received.")
                        elif (
                            isinstance(event, keyboard.Events.Release)
                            and event.key == keyboard.Key.esc
                        ):
                            print("Esc pressed. Exiting...")
                            self.stop_listener()
                            self.quit_requested.emit()
                            break

    def detect_combinations(self):
        detected_combination = None
        # print(f"Pressed Keys: {self.pressed_keys}")
        for label, combination in self.user_shortcuts.items():
            # Debug:
            # print(f"Checking combination: {combination}")
            # for key in combination:
            #     print(type(key))

            values = list(self.pressed_keys.values())
            if combination == values:
                # print(f"len combination: {len(combination)}, len pressed_keys: {len(self.pressed_keys)}")
                print(f"Combination detected (Direct): {label}")
                detected_combination = label
                self.key_release_print.emit(
                    f"Combination detected: {values} Action: {label}"
                )
                self.pressed_keys = {}
                break
        # Debug:
        # print(f"Passed Keys: {self.pressed_keys.values()}")
        # for value in self.pressed_keys.values():
        #     print(type(value))

        return detected_combination

    def execute_action(self, detected_combination):

        match detected_combination:
            case "configure window":
                print("Configuring window...")
                self.configure_window.emit()
            case "toggle always on top":
                self.window_action.emit(1, "toggle_on_top")
            case "exit program":
                self.close_app()
            case "ctrl window 1":
                self.window_action.emit(1, "ctrl")
            case "open window 1":
                self.window_action.emit(1, "open")
            case "close window 1":
                self.window_action.emit(1, "close")
            case "close all windows 1":
                self.window_action.emit(1, "close_all")
            case "maximize window 1":
                self.window_action.emit(1, "maximize")
            case "minimize window 1":
                self.window_action.emit(1, "minimize")

            case "ctrl window 2":
                self.window_action.emit(2, "ctrl")
            case "open window 2":
                self.window_action.emit(2, "open")
            case "close window 2":
                self.window_action.emit(2, "close")
            case "close all windows 2":
                self.window_action.emit(2, "close_all")
            case "maximize window 2":
                self.window_action.emit(2, "maximize")
            case "minimize window 2":
                self.window_action.emit(2, "minimize")

            case "ctrl window 3":
                self.window_action.emit(3, "ctrl")
            case "open window 3":
                self.window_action.emit(3, "open")
            case "close window 3":
                self.window_action.emit(3, "close")
            case "close all windows 3":
                self.window_action.emit(3, "close_all")
            case "maximize window 3":
                self.window_action.emit(3, "maximize")
            case "minimize window 3":
                self.window_action.emit(3, "minimize")

            case "ctrl window 4":
                self.window_action.emit(4, "ctrl")
            case "open window 4":
                self.window_action.emit(4, "open")
            case "close window 4":
                self.window_action.emit(4, "close")
            case "close all windows 4":
                self.window_action.emit(4, "close_all")
            case "maximize window 4":
                self.window_action.emit(4, "maximize")
            case "minimize window 4":
                self.window_action.emit(4, "minimize")

            case "ctrl window 5":
                self.window_action.emit(5, "ctrl")
            case "open window 5":
                self.window_action.emit(5, "open")
            case "close window 5":
                self.window_action.emit(5, "close")
            case "close all windows 5":
                self.window_action.emit(5, "close_all")
            case "maximize window 5":
                self.window_action.emit(5, "maximize")
            case "minimize window 5":
                self.window_action.emit(5, "minimize")

    def close_app(self):
        print("Closing the app...")
        self.stop_listener()
        self.quit_requested.emit()

    def open_window_1(self):
        print("Opening window 1...")

    def open_window_2(self):
        print("Opening window 2...")

    def is_ctrl_unicode(self, code: str) -> bool:
        """Check if the given unicode character is a control character."""
        return len(code) == 1 and 0 < ord(code) <= 26

    def get_unicode_order_from_char(self, char: str) -> int:
        """Get the unicode order (ordinal) of a character."""
        if len(char) != 1:
            return -1
        return ord(char)

    def character_from_ctrl_unicode(self, order: int) -> str:
        """Get the corresponding character from a control unicode."""
        if not 0 < order <= 26:  # Adjusted to include 26
            return ""
        pool = "abcdefghijklmnopqrstuvwxyz"
        return pool[order - 1]


class MouseListener(QObject):
    mouse_finished = Signal()
    mouse_quit_requested = Signal()
    emit_mouse_moved = Signal(int, int)
    emit_mouse_left_click = Signal()

    def __init__(self):
        super().__init__()

        self.mouse_listen_pynput = False
        self.listen_mouse_pynput = True
        self.can_mouse_run = True
        self.listen_to_mouse_clicks = False

    def stop_mouse_listener(self, terminate=False):
        self.mouse_listen_pynput = False
        if terminate:
            self.can_mouse_run = False

    def on_mouse_events_pynput(self):
        # The event listener will be running in this block
        self.mouse_listen_pynput = True
        with mouse.Events() as events:
            # Block at most one second
            while self.can_mouse_run:
                if not self.listen_mouse_pynput:
                    time.sleep(1)
                else:
                    event = events.get(1.0)
                    if event is None:
                        # print('You did not interact with the mouse within one second')
                        continue
                    else:
                        # print('Received event {}'.format(event))
                        if isinstance(event, mouse.Events.Move):
                            self.emit_mouse_moved.emit(event.x, event.y)
                        elif (
                            isinstance(event, mouse.Events.Click)
                            and self.listen_to_mouse_clicks
                        ):
                            # print(f"Mouse clicked: {event}")
                            if event.button == mouse.Button.left and event.pressed:
                                print("Left button clicked")
                                self.emit_mouse_left_click.emit()
                                # theoretically, we can also control self.mouse_listen_pynput here (if we wanna stop the listener)
