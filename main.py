"""
~ BarakXYZ - XYZ Manager - 2024 - CS50x Final Project ~
In this main.py file, we have the main window of the application.
Using Qt for the GUI, and its threading capabilities to run the keyboard and mouse listeners in separate threads.
All the modules are imported and the necessary classes are created.
There's also a Transparent (glass-like) window that shows instructions to the user.
It follows the cursor and guides the user on the configuration process.
"""

from PySide6.QtCore import (
    QSize,
    Qt,
    QThread,
    QTimer,
    QPoint,
    QPropertyAnimation,
)
from PySide6.QtGui import (
    QIcon,
    QCursor,
    QColor,
    QPainter,
    QPen,
    QPainterPath,
    QFontDatabase,
    QFont,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QTextBrowser,
    QTabWidget,
    QLabel,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
import sys
import os
import logging

# My imports
from input_listener import KeyboardListener, MouseListener
from config import UserConfig
from window_detector import WindowDetector


class GuidanceWindow(QLabel):
    def __init__(
        self,
        text1="",
        text2="",
        text3="",
        fade_in=750,
        fade_out=750,
        coordinates=(0, 0),
        font="arial",
    ):
        super().__init__()
        self.move(coordinates[0], coordinates[1])
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.text1 = text1  # Instruction 1
        self.text2 = text2  # Usually the window name
        self.text3 = text3  # Instruction 2
        self.custom_font = font
        self.initUI()
        self.initFadeInEffect()

    def initUI(self):
        self.setFont(self.custom_font)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        self.setFixedSize(750, 150)  # Adjust the size to accommodate additional text

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(1, 1)
        shadow.setBlurRadius(3)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def initFadeInEffect(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.fadeInAnimation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fadeInAnimation.setDuration(self.fade_in)
        self.fadeInAnimation.setStartValue(0)
        self.fadeInAnimation.setEndValue(1)
        self.fadeInAnimation.start()

    def closeWindow(self):
        self.fadeOutAnimation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fadeOutAnimation.setDuration(self.fade_out)
        self.fadeOutAnimation.setStartValue(1)
        self.fadeOutAnimation.setEndValue(0)
        self.fadeOutAnimation.finished.connect(self.close)
        self.fadeOutAnimation.start()

    def setText(self, text):
        self.text = text
        self.update()

    def setAdditionalText(self, text):
        self.additional_text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = self.font()

        # Draw text 1
        additional_path = QPainterPath()
        additional_path.addText(
            20, 40, font, self.text1
        )  # Adjust positioning as needed
        outlinePen = QPen(QColor("black"))
        outlinePen.setWidth(2)
        painter.setPen(outlinePen)
        painter.drawPath(additional_path)
        painter.fillPath(additional_path, QColor("white"))

        # Draw text 2
        path = QPainterPath()
        path.addText(20, 70, font, self.text2)  # Adjust positioning as needed
        painter.drawPath(path)
        painter.fillPath(path, QColor("white"))

        # Draw text 3
        path = QPainterPath()
        path.addText(20, 100, font, self.text3)  # Adjust positioning as needed
        painter.drawPath(path)
        painter.fillPath(path, QColor("white"))


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app  # Store the app instance
        self.app.setStyle("Fusion")
        self.setWindowTitle("XYZ Manager")
        self.setGeometry(800, 800, 800, 600)
        logging.basicConfig(level=logging.DEBUG)  # Set up basic logging
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Make the window always on top
        self.custom_font = self.get_custom_font(size=16)
        self.custom_font_main_ui = self.get_custom_font(size=12)
        self.app.setFont(self.custom_font_main_ui)
        # Guidance Window
        self.guidanceWindow = None

        self.user_config = UserConfig()
        if config_file := self.user_config.GOD["preferences.ini"]["file"]:
            print("Config File Found")
            print(f"Config Path: {self.user_config.GOD['config.ini']['path']}")
        else:
            sys.exit("Config file could not be created. Exiting...")

        self.last_active_window = None
        self.can_control_windows = False
        self.all_windows = [
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
            {
                "window_object": None,
                "window_title": None,
                "exe_path": None,
                "window_handle": None,
            },
        ]
        self.mouse_left_clicks_counter = 0
        self.selected_window = None

        self.keyboard_pynput_thread = QThread()
        self.mouse_pynput_thread = QThread()
        self.window_detector_thread = QThread()

        self.keyboard_pynput_worker = KeyboardListener(config_file)
        self.mouse_pynput_worker = MouseListener()
        self.window_detector_worker = WindowDetector()

        self.mouse_pynput_worker.moveToThread(self.mouse_pynput_thread)
        self.keyboard_pynput_worker.moveToThread(self.keyboard_pynput_thread)
        self.window_detector_worker.moveToThread(self.window_detector_thread)

        self.keyboard_pynput_thread.started.connect(
            self.keyboard_pynput_worker.on_keyboard_events_pynput
        )
        self.mouse_pynput_thread.started.connect(
            self.mouse_pynput_worker.on_mouse_events_pynput
        )

        self.keyboard_pynput_worker.quit_requested.connect(self.quit_app)
        self.keyboard_pynput_worker.key_print.connect(self.print_key)
        self.keyboard_pynput_worker.key_release_print.connect(self.print_release_key)
        self.keyboard_pynput_worker.configure_window.connect(self.configure_window)
        self.keyboard_pynput_worker.window_action.connect(self.control_window)
        self.keyboard_pynput_worker.window_number_assignment.connect(
            self.configure_window
        )

        self.mouse_pynput_worker.emit_mouse_moved.connect(self.on_mouse_move)
        self.mouse_pynput_worker.emit_mouse_left_click.connect(self.get_active_window)

        self.keyboard_pynput_thread.start()
        self.mouse_pynput_thread.start()
        self.window_detector_thread.start()

        # Save path cross-platform
        icon_path = os.path.join(os.path.dirname(__file__), "images/app_icon.ico")
        # Set title bar icon
        self.setWindowIcon(QIcon(icon_path))
        # Change to dark theme (os specific)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # central_widget.setMouseTracking(True)

        # Menubar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        # menu_bar.setStyleSheet("background-color: #F472B6; color: black;")

        # Quit Action
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)

        # Help Action
        help_action = file_menu.addAction("Help")
        help_action.triggered.connect(
            lambda: QMessageBox.information(
                self,
                "Help",
                """Hey there!\n
                XYZ Manager is a tool that allows you to control\n
                multiple windows with keyboard shortcuts.\n\n
                To configure a window, press ctrl+shift+"\n
                and click on the window you want to configure.\n
                After configuring a window, you can call it\n
                by pressing ctrl+shift+[number] assigned to it.\n
                You can:\n
                Minimize - Ctrl+Shift+[Number]+Minus\n
                Maximiize - Ctrl+Shift+[Number]+Plus\n
                Close - Ctrl+Shift+[Number]+Backspace\n
                Open Ctrl+Shift+[Number]+Enter\n""",
            )
        )

        # Toolbars
        toolbar = QToolBar("Main Toolbar")
        # toolbar.setStyleSheet("background-color: #A5B4FC; color: black;")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)  # Adding the toolbar to the main window
        toolbar.addAction(
            quit_action
        )  # Essentially, can handle the already existing action for the toolbar as well
        toolbar.addAction(help_action)

        core_layout = QVBoxLayout()
        # Change padding of layout between buttons
        core_layout.setSpacing(12)
        central_widget.setLayout(core_layout)

        tab_widget = QTabWidget()
        core_layout.addWidget(tab_widget)

        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)  # Create a layout for each tab
        tab_widget.addTab(main_tab, "Main Tab")

        windows_tab = QWidget()
        windows_tab_layout = QVBoxLayout(windows_tab)  # Create a layout for each tab
        tab_widget.addTab(windows_tab, "Keyboard Shortcuts")

        # Create text box for logging information
        self.debug_terminal = QTextBrowser()
        self.debug_terminal.setStyleSheet("background-color: #78716C; color: #FAFAF9;")
        main_layout.addWidget(self.debug_terminal)

        sub_button_layout = QHBoxLayout()
        sub_button_layout.setSpacing(6)
        main_layout.addLayout(sub_button_layout)

        button_get_active_window = QPushButton('Configure Window [Ctrl+Shift+"]')
        sub_button_layout.addWidget(button_get_active_window)
        button_get_active_window.pressed.connect(self.configure_window)

        window_buttons_vertical_box = QVBoxLayout()
        windows_tab_layout.addLayout(window_buttons_vertical_box)

        info_label = QLabel(
            "Here's an example of how to control a window.\nFeel free to assign more windows to more keys\nand to control them in a similar way!"
        )
        info_label.setFont(self.custom_font)
        # win1_vbox.addWidget(info_label)
        window_buttons_vertical_box.addWidget(info_label)

        win1_vbox = QVBoxLayout()
        window_buttons_vertical_box.addLayout(win1_vbox)
        win1_vbox.setSpacing(6)

        win1_text = QPushButton("Window 1 [Ctrl+Shift+1]")
        win1_vbox.addWidget(win1_text)
        win1_hbox = QHBoxLayout()
        win1_vbox.addLayout(win1_hbox)
        win2_hbox = QHBoxLayout()
        win1_vbox.addLayout(win2_hbox)

        btn1_win1 = QPushButton("Maximize [Ctrl+Shift+1+Plus]")
        btn1_win1.pressed.connect(lambda: self.control_window(1, "maximize"))
        win1_hbox.addWidget(btn1_win1)

        btn2_win1 = QPushButton("Minimize [Ctrl+Shift+1+Minus]")
        btn2_win1.pressed.connect(lambda: self.control_window(1, "minimize"))
        win1_hbox.addWidget(btn2_win1)

        btn3_win1 = QPushButton("Open [Ctrl+Shift+1+Enter]")
        btn3_win1.pressed.connect(lambda: self.control_window(1, "open"))
        win2_hbox.addWidget(btn3_win1)

        btn4_win1 = QPushButton("Close [Ctrl+Shift+1+Backspace]")
        btn4_win1.pressed.connect(lambda: self.control_window(1, "close"))
        win2_hbox.addWidget(btn4_win1)

        # Status bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().setStyleSheet("background-color: #FFF1F2; color: #0C0A09;")
        self.statusBar().setFont("Arial")  # TODO Change font to RobotoMono

    def configure_window(self, assignment_index=None, configure_stage=0):
        if assignment_index:
            if assignment_index > 9:
                self.debug_terminal.append(
                    "Invalid Assignment Index\n Please choose a number between 0-9"
                )
                configure_stage = 0
            else:
                configure_stage = 3
                self.debug_terminal.append(f"Assignment Index: {assignment_index}")

        if configure_stage == 0:
            self.mouse_pynput_worker.listen_to_mouse_clicks = True
            self.create_guidance_window(
                window_text2="Press on the window you want to configure"
            )
        elif configure_stage == 1:
            self.keyboard_pynput_worker.waiting_for_number_assignment = True
            self.create_guidance_window(
                window_text1="Your current selection is:",
                window_text2=f"{self.selected_window.title}",
                window_text3="Press a number key to control this window (0-9)",
                window_fade_out=250,
            )
        elif configure_stage == 2:
            self.keyboard_pynput_worker.waiting_for_number_assignment = False
            self.create_guidance_window(
                window_text1="No window found",
                window_text2="Please try again",
                window_fade_out=250,
            )
        elif configure_stage == 3:
            if not self.selected_window:
                self.configure_window(configure_stage=2)
                return

            self.create_guidance_window(
                window_text1="Success!",
                window_text2=f"{self.selected_window.title}",
                window_text3=f"Assigned to {assignment_index}",
                window_fade_out=250,
                show_and_destroy=True,
            )
            self.all_windows[assignment_index]["window_object"] = self.selected_window
            self.all_windows[assignment_index][
                "window_title"
            ] = self.selected_window.title
            self.all_windows[assignment_index][
                "window_handle"
            ] = self.selected_window.getHandle()
            self.all_windows[assignment_index]["exe_path"] = (
                self.window_detector_worker.get_exe_path_from_window_handle(
                    self.all_windows[assignment_index]["window_handle"]
                )
            )

            # Clean-up:
            self.selected_window = None
            self.keyboard_pynput_worker.waiting_for_number_assignment = False
            self.mouse_pynput_worker.listen_to_mouse_clicks = False
            # Print exe path
            print(f"Exe Path: {self.all_windows[assignment_index]['exe_path']}")

    def get_active_window(self, direct_assign_window=False, assignment_index=None):
        self.debug_terminal.append("Get Active Window Reached")
        if not direct_assign_window:
            self.selected_window = (
                self.window_detector_worker.get_active_window_simple()
            )
            if self.selected_window:
                self.debug_terminal.append(
                    f"Selected Window: {self.selected_window.title}"
                )
                self.debug_terminal.append(
                    f"Selected Window Handle: {self.selected_window.getHandle()}"
                )
                self.debug_terminal.append(f"Window Object: {self.selected_window}")
                self.configure_window(configure_stage=1)
            else:
                self.configure_window(configure_stage=2)
        else:
            self.all_windows[assignment_index][
                "window_object"
            ] = self.window_detector_worker.get_active_window_simple()

    def control_window(self, window_index, action):
        print("Control Window Reached")
        print(f"Window Index: {window_index}")
        print(f"Action: {action}")
        # Toggle the control of windows
        match action:
            case "ctrl":
                if self.all_windows[window_index]["window_object"]:
                    self.window_detector_worker.ctrl_window(
                        self.all_windows[window_index]["window_object"]
                    )
                elif self.all_windows[window_index]["exe_path"]:
                    self.all_windows[window_index]["window_object"] = (
                        self.window_detector_worker.open_window(
                            self.all_windows[window_index]["exe_path"],
                            self.all_windows[window_index]["window_title"],
                        )
                    )
                else:
                    self.debug_terminal.append("CTRL:")
                    self.debug_terminal.append(
                        "No window found for this index, please configure it first <3"
                    )
            case "open":
                if self.all_windows[window_index]["exe_path"]:
                    self.all_windows[window_index]["window_object"] = (
                        self.window_detector_worker.open_window(
                            self.all_windows[window_index]["exe_path"],
                            self.all_windows[window_index]["window_title"],
                        )
                    )
                elif self.all_windows[window_index]["window_object"]:
                    self.all_windows[window_index]["exe_path"] = (
                        self.window_detector_worker.get_exe_path_from_window_handle(
                            self.all_windows[window_index]["window_handle"]
                        )
                    )
                    if self.all_windows[window_index]["exe_path"]:
                        self.all_windows[window_index]["window_object"] = (
                            self.window_detector_worker.open_window(
                                self.all_windows[window_index]["exe_path"],
                                self.all_windows[window_index]["window_title"],
                            )
                        )
                else:
                    # Clear all properties for this index window
                    self.all_windows[window_index]["window_object"] = None
                    self.all_windows[window_index]["window_handle"] = None
                    self.all_windows[window_index]["exe_path"] = None
                    self.all_windows[window_index]["window_title"] = None

                    self.debug_terminal.append("OPEN:")
                    self.debug_terminal.append(
                        "No window found for this index, please configure it first <3"
                    )
            case "close":
                if self.all_windows[window_index]["window_object"]:
                    self.window_detector_worker.close_window(
                        self.all_windows[window_index]["window_object"]
                    )
                    self.all_windows[window_index]["window_object"] = None
                    self.all_windows[window_index]["window_handle"] = None
            case "close_all":
                if self.all_windows[window_index]["window_title"]:
                    self.window_detector_worker.close_all_windows(
                        self.all_windows[window_index]["window_title"]
                    )
                    self.all_windows[window_index]["window_object"] = None
                    self.all_windows[window_index]["window_handle"] = None
                else:
                    self.debug_terminal.append("CLOSE-ALL:")
                    self.debug_terminal.append(
                        "No window title found for this index, please configure it first <3"
                    )
            case "maximize":
                if self.all_windows[window_index]["window_object"]:
                    self.window_detector_worker.maximize_window(
                        self.all_windows[window_index]["window_object"]
                    )
                    self.debug_terminal.append("Maximize Window")
                else:
                    self.debug_terminal.append("MAXIMIZE:")
                    self.debug_terminal.append(
                        "No window found for this index, please configure it first <3"
                    )
            case "minimize":
                if self.all_windows[window_index]["window_object"]:
                    self.window_detector_worker.minimize_window(
                        self.all_windows[window_index]["window_object"]
                    )
                    self.debug_terminal.append("Minimize Window")
                else:
                    self.debug_terminal.append("MINIMIZE:")
                    self.debug_terminal.append(
                        "No window found for this index, please configure it first <3"
                    )
            case "toggle_on_top":
                # Check if the window is already on top
                if self.windowFlags() & Qt.WindowStaysOnTopHint:
                    # If it's already on top, remove the flag to not stay on top
                    self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
                else:
                    # If it's not on top, set the flag to make it stay on top
                    self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

                # Reapply the widget/window settings for changes to take effect
                self.show()

    def on_mouse_move(self, x, y):
        if self.guidanceWindow:
            delta = QCursor.pos() - QPoint(0, 50)
            # self.debug_terminal.append(f"Mouse Position: {QCursor.pos()}")  # Debugging
            self.guidanceWindow.move(delta)
        else:
            pass

    def create_guidance_window(
        self,
        window_text1="",
        window_text2="",
        window_text3="",
        window_fade_in=750,
        window_fade_out=750,
        show_and_destroy=False,
    ):
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() - 0
        y = cursor_pos.y() - 50
        print("Cursor Position: ", x, y)
        if show_and_destroy:
            self.guidanceWindow.closeWindow()
            self.guidanceWindow = None
            self.guidanceWindow = GuidanceWindow(
                text1=window_text1,
                text2=window_text2,
                text3=window_text3,
                coordinates=(x, y),
                fade_in=window_fade_in,
                fade_out=window_fade_out,
                font=self.custom_font,
            )  # Create a new window with new text
            self.guidanceWindow.show()
            self.timer = QTimer()
            self.timer.timeout.connect(self.guidanceWindow.closeWindow)
            print("Timer Started")
            self.timer.start(2000)

        elif self.guidanceWindow:
            self.guidanceWindow.closeWindow()  # Close and destroy the current window
            self.guidanceWindow = None
            self.guidanceWindow = GuidanceWindow(
                text1=window_text1,
                text2=window_text2,
                text3=window_text3,
                coordinates=(x, y),
                fade_in=window_fade_in,
                fade_out=window_fade_out,
                font=self.custom_font,
            )  # Create a new window with new text
            self.guidanceWindow.show()
        else:
            self.guidanceWindow = GuidanceWindow(
                text1=window_text1,
                text2=window_text2,
                text3=window_text3,
                coordinates=(x, y),
                fade_in=window_fade_in,
                fade_out=window_fade_out,
                font=self.custom_font,
            )
            self.guidanceWindow.show()

    def kill_process_by_name(self, process_name):
        self.window_detector_worker.kill_process_by_name(process_name.lower())
        # Depracated (but for the future)

    def open_last_active_window(self):
        if self.last_active_window:
            self.window_detector_worker.ctrl_window(self.last_active_window)
        else:
            self.debug_terminal.append(
                "No last active window found, please get one first <3"
            )

    def print_key(self, key):
        self.statusBar().showMessage(f"Key Pressed: {key}", 2500)

    def print_release_key(self, key):
        self.debug_terminal.append(f"Key Pressed: {key}")

    def toolbar_action_1(self):
        # Control the keyboard listener
        if self.keyboard_pynput_worker.get_listener_status():
            self.keyboard_pynput_worker.stop_listener()
        else:
            self.keyboard_pynput_worker.start_listener()

    def get_custom_font(self, size=16):
        font_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "fonts/static/RobotoMono-Regular.ttf",
        )
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font_family = font_families[0]
            custom_font = QFont(custom_font_family, size)
            # self.debug_terminal.append("Font Loaded")
            return custom_font
        else:
            self.debug_terminal.append("Failed to load font")

    def quit_app(self):
        print("Stopping Pynput Listener")
        self.keyboard_pynput_worker.stop_listener()
        self.keyboard_pynput_worker.can_run = False
        print("Quitting Thread")
        self.keyboard_pynput_thread.quit()
        print("Waiting for Keyboard Thread")
        self.keyboard_pynput_thread.wait(deadline=2500)

        print("Stopping Mouse Pynput Listener")
        self.mouse_pynput_worker.stop_mouse_listener(terminate=True)
        self.mouse_pynput_worker.can_mouse_run = False
        print("Quitting Mouse Thread")
        self.mouse_pynput_thread.quit()
        print("Waiting for Mouse Thread")
        self.mouse_pynput_thread.wait(deadline=2500)

        print("Quit Window Detector Thread")
        self.window_detector_thread.quit()
        print("Waiting for Window Detector Thread")
        self.window_detector_thread.wait(deadline=2500)

        print("Quitting App")
        self.app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())
