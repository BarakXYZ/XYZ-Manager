"""
~ BarakXYZ - XYZ Manager - 2024 - CS50x Final Project ~
The window detector uses the pywinctl library to interact with windows.
In nature, this library is cross-platform, but macOS isn't working so well (from my testings).
The window detector can be used to open, close, maximize, minimize, and control windows.
It can also detect the execution path of a window (.exe) and open a file after it was closed.
But some of the feature are still not as robust (WIP).
"""

from PySide6.QtCore import QObject
import pywinctl as pwc
import psutil
import re
import os
import platform
import subprocess
import sys
import win32process
import time


class WindowDetector(QObject):
    def __init__(self):
        super().__init__()

        self.windows = {}

        # Check if macOS
        if platform.system() == "Darwin":
            self.platform = "macOS"
        else:
            self.platform = None

    def get_active_window_simple(self):
        if window := pwc.getActiveWindow():
            return window
        else:
            return None

    def ctrl_window(self, window):
        if window.isMinimized:
            window.restore()
        else:
            window.minimize()

    def open_window(self, exe_path, window_title, timeout=10):
        # os.startfile(exe_path)  # Simple method
        if sys.platform.startswith("darwin"):
            subprocess.run(["open", exe_path])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", exe_path])
        elif sys.platform.startswith("win32"):
            subprocess.run(f'start "" "{exe_path}"', shell=True)
        # Wait for the window to appear
        start_time = time.time()
        while True:
            new_windows = pwc.getWindowsWithTitle(
                window_title, condition=pwc.Re.CONTAINS, flags=pwc.Re.IGNORECASE
            )
            if new_windows:
                print(f"Windows Found: {new_windows}")
                return new_windows[0]  # Returns a list of all matching windows
            elif time.time() - start_time > timeout:
                print("Timeout waiting for window to appear.")
                return None
            time.sleep(0.5)

    def close_window(self, window):
        if window:
            window.close()

    def close_all_windows(self, window_title):
        windows_to_delete = pwc.getWindowsWithTitle(
            window_title, condition=pwc.Re.CONTAINS, flags=pwc.Re.IGNORECASE
        )
        if windows_to_delete:
            print(f"Windows Found: {windows_to_delete}")
            for window in windows_to_delete:
                window.close()

    def maximize_window(self, window):
        if window:
            window.maximize()

    def minimize_window(self, window):
        if window:
            window.minimize()

    def detect_active_window(self):
        if self.platform:
            print("Permissions: ", pwc.checkPermissions())

            if active_window := pwc.getActiveWindow():
                return (
                    active_window,
                    active_window.title,
                    pwc.getAllAppsWindowsTitles(),
                )
            else:
                return (None, None)
        else:
            if active_window := pwc.getActiveWindow():
                if apps_names := pwc.getAllAppsNames():
                    return (active_window, pwc.getActiveWindow(), apps_names)
                return (active_window, pwc.getActiveWindowTitle(), None)
            else:
                return (None, None)

    def get_apps(self):
        print("Getting apps...")
        apps = {}
        apps_names = pwc.getAllAppsNames()  # List of useful app names
        all_windows = pwc.getAllWindows()  # List of Win32Window objects
        all_apps_windows_titles = pwc.getAllAppsWindowsTitles()
        # print("Apps names: ", apps_names)
        # print("All windows: ", all_windows)

        for window in all_windows:
            if (
                window_title := window.title
            ):  # Accessing the title of the Win32Window object
                for app_name in apps_names:
                    app_name = app_name.split(".exe")[
                        0
                    ]  # Remove the ".exe" extension from the app name
                    # Escape regex special characters in app name and compile regex pattern
                    pattern = re.compile(
                        r"\b" + re.escape(app_name) + r"\b", re.IGNORECASE
                    )
                    # print("App name: ", app_name)
                    # print("Window Title: ", window_title)
                    if re.search(pattern, window_title):
                        apps[app_name] = window_title
        return apps, apps_names, all_windows, all_apps_windows_titles

    def parse_active_windows(self):
        self.windows = pwc.getAllWindows()

    def extract_app_name(self, window_title):
        # Define the regex pattern to split by "-", "—", or spaces around them
        pattern = r"\s*[\-–—]+\s*"

        # Split the title using the defined pattern
        parts = re.split(pattern, window_title)

        # Return the last part if there are multiple parts, or the original title if no delimiter is found
        if len(parts) > 1:
            return parts[
                -1
            ].strip()  # Using .strip() to remove any leading/trailing spaces
        else:
            return (
                window_title.strip()
            )  # Return the original title with leading/trailing spaces removed

    def detect_all_processes(self):
        processes = []
        for process in psutil.process_iter(attrs=["pid", "name", "exe"]):
            try:
                processes.append(
                    {
                        "pid": process.info["pid"],
                        "name": process.info["name"],
                        "exe": process.info["exe"],
                    }
                )
            except (psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except psutil.NoSuchProcess:
                continue
        print("All processes fetched.")
        return processes

    def find_procs_by_name(self, name):
        """
        Return a list of dictionaries with process information matching 'name'.
        Each dictionary contains 'pid', 'name', and 'exe'.
        """
        assert name, "Name parameter is required"
        matching_procs = []

        for process in psutil.process_iter(attrs=["pid", "name", "exe"]):
            try:
                proc_name = process.info["name"]
                proc_exe = process.info["exe"]
                # Adjust the condition to check for both 'name' and 'name.exe'
                if (
                    proc_name.lower() == name.lower()
                    or proc_name.lower() == f"{name.lower()}.exe"
                    or (proc_exe and os.path.basename(proc_exe).lower() == name.lower())
                    or (
                        proc_exe
                        and os.path.basename(proc_exe).lower() == f"{name.lower()}.exe"
                    )
                ):
                    matching_procs.append(
                        {"pid": process.info["pid"], "name": proc_name, "exe": proc_exe}
                    )
            except (psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except psutil.NoSuchProcess:
                continue

        print("Matching processes: ", matching_procs)
        return matching_procs

    # Find .exe by title
    def find_process_by_title(self, target_title):
        # Iterate over all running processes
        for proc in psutil.process_iter(attrs=["pid", "name", "exe", "cmdline"]):
            # Try to access process details
            try:
                # Ensure cmdline is iterable (i.e., a list) before joining
                cmdline = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                # Check if the target title is part of the process' cmdline or name
                if (
                    target_title.lower() in cmdline.lower()
                    or target_title.lower() in (proc.info["name"] or "").lower()
                ):
                    # Print .exe path
                    print(proc.info["exe"])
                    return proc.info["exe"]
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None

    def get_exe_path_from_window_handle(self, hwnd):
        # Get the process ID associated with the window handle
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # Find the process using psutil
        try:
            p = psutil.Process(pid)
            # Return the executable path
            return p.exe()
        except psutil.NoSuchProcess:
            return None

    def kill_process_by_name(self, name):
        # Loop through all running processes
        for process in psutil.process_iter():
            # Check if process name matches the desired one (e.g., "notepad.exe" for Notepad on Windows)
            try:
                if name in process.name().lower():
                    process.terminate()  # Terminate the process
                    print("Process terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        print("Function Finished.")
