"""
~ BarakXYZ - XYZ Manager - 2024 - CS50x Final Project ~
The UserConfig class is used to manage the configuration files for the application.
It stores the shortcuts for manipulating windows, and some other settings.
It is WIP and needs to be refactored to be more modular and flexible.
"""

import configparser
from appdirs import AppDirs
import datetime
import os
import platform


class UserConfig:
    def __init__(self):

        self.GOD = {
            "config.ini": {
                "file": "Set in init",
                "path": "Set in init",
                "last_updated": "Set in runtime",
            },
            "preferences.ini": {
                "file": "Set in init",
                "path": "Set in init",
                "last_updated": "Set in runtime",
            },
            "cache.ini": {
                "file": "Set in init",
                "path": "Set in init",
                "last_updated": "Set in runtime",
            },
            "user": {
                "first_time": True,
                "username": "Set in init",
            },
            "state": {
                "regular": True,
                "whipser": False,
                "cv": False,
            },
            "general": {
                "app_name": "3Dreams",
                "author_name": "BarakXYZ",
            },
        }

        config_dir = AppDirs(
            self.GOD["general"]["app_name"], self.GOD["general"]["author_name"]
        ).user_config_dir

        config_path = os.path.join(config_dir, "config.ini")
        self.GOD["config.ini"]["path"] = config_path

        preferences_path = os.path.join(config_dir, "preferences.ini")
        self.GOD["preferences.ini"]["path"] = preferences_path

        cache_path = os.path.join(config_dir, "cache.ini")
        self.GOD["cache.ini"]["path"] = cache_path

        # Check if macOS
        if platform.system() == "Darwin":
            self.ctrl_name = "ctrl"
        else:
            self.ctrl_name = "ctrl_l"

        # Check if the configuration file already exists
        if not os.path.exists(config_path):

            # If files do not exist -> Create the default config.ini and preferences.ini files
            print("Configuration file not found. Setting up...")
            os.makedirs(config_dir, exist_ok=True)

            # Write the initial configuration file
            self.create_ini_file(
                "config.ini",
                config_path,
                {
                    "Last Updated": {"DateTime": str(datetime.datetime.now())},
                    "Window Test 1": {
                        "name": "Test 1",
                        "execution path": "something/else/here",
                    },
                    "Window Test 2": {
                        "name": "Test 2",
                        "execution path": "programs/there/else/whatever",
                    },
                },
            )
            self.create_ini_file(
                "preferences.ini",
                preferences_path,
                {
                    "User": {
                        "Username": "None",
                        "Password": "None",
                        "Email": "None",
                        "OS": platform.system(),
                    },
                    "Keyboard Shortcuts": {
                        "toggle always on top": f"{self.ctrl_name}+shift+a",
                        "configure window": f"{self.ctrl_name}+shift+'",
                        "cache windows data": f"{self.ctrl_name}+shift+0",
                        "ctrl window 1": f"{self.ctrl_name}+shift+1",
                        "open window 1": f"{self.ctrl_name}+shift+1+enter",
                        "close window 1": f"{self.ctrl_name}+shift+1+backspace",
                        "close all windows 1": f"{self.ctrl_name}+shift+1+delete",
                        "maximize window 1": f"{self.ctrl_name}+shift+1+plus",
                        "minimize window 1": f"{self.ctrl_name}+shift+1+-",
                        "ctrl window 2": f"{self.ctrl_name}+shift+2",
                        "open window 2": f"{self.ctrl_name}+shift+2+enter",
                        "close window 2": f"{self.ctrl_name}+shift+2+backspace",
                        "close all windows 2": f"{self.ctrl_name}+shift+2+delete",
                        "maximize window 2": f"{self.ctrl_name}+shift+2+plus",
                        "minimize window 2": f"{self.ctrl_name}+shift+2+-",
                        "ctrl window 3": f"{self.ctrl_name}+shift+3",
                        "open window 3": f"{self.ctrl_name}+shift+3+enter",
                        "close window 3": f"{self.ctrl_name}+shift+3+backspace",
                        "close all windows 3": f"{self.ctrl_name}+shift+3+delete",
                        "maximize window 3": f"{self.ctrl_name}+shift+3+plus",
                        "minimize window 3": f"{self.ctrl_name}+shift+3+-",
                        "ctrl window 4": f"{self.ctrl_name}+shift+4",
                        "open window 4": f"{self.ctrl_name}+shift+4+enter",
                        "close window 4": f"{self.ctrl_name}+shift+4+backspace",
                        "close all windows 4": f"{self.ctrl_name}+shift+4+delete",
                        "maximize window 4": f"{self.ctrl_name}+shift+4+plus",
                        "minimize window 4": f"{self.ctrl_name}+shift+4+-",
                        "ctrl window 5": f"{self.ctrl_name}+shift+5",
                        "open window 5": f"{self.ctrl_name}+shift+5+enter",
                        "close window 5": f"{self.ctrl_name}+shift+5+backspace",
                        "close all windows 5": f"{self.ctrl_name}+shift+5+delete",
                        "maximize window 5": f"{self.ctrl_name}+shift+5+plus",
                        "minimize window 5": f"{self.ctrl_name}+shift+5+-",
                        "open last active window": f"{self.ctrl_name}+shift+=",
                        "close active window": f"{self.ctrl_name}+shift+-",
                        "maximize active window": f"{self.ctrl_name}+shift+up",
                        "minimize active window": f"{self.ctrl_name}+shift+down",
                        "exit program": f"{self.ctrl_name}+shift+q",
                    },
                    "Window Names": {
                        "Window 1": "None",
                        "Window 2": "None",
                        "Window 3": "None",
                        "Window 4": "None",
                        "Window 5": "None",
                        "Window 6": "None",
                        "Window 7": "None",
                        "Window 8": "None",
                        "Window 9": "None",
                        "Window 10": "None",
                    },
                },
            )
            self.create_ini_file(
                "cache.ini",
                cache_path,
                {
                    "Last Updated": {"DateTime": str(datetime.datetime.now())},
                },
            )

            self.GOD["user"]["first_time"] = True

        else:
            print("Configuration file found. Loading settings...")
            # Read from the config file
            config_file = self.read_config_file(config_path)
            preferences_file = self.read_config_file(preferences_path)

            if config_file and preferences_file:
                self.GOD["first_time"] = False
                self.GOD["config.ini"]["file"] = config_file
                self.GOD["preferences.ini"]["file"] = preferences_file
            else:
                print("No configuration content to display.")

    # def create_ini_file(filename, config_path, sections, section_data):
    def create_ini_file(self, filename, config_path, config_data):
        try:
            """Create a configuration file with the given sections and data.

            Args:
                config_path (str): Path to the configuration file.
                sections (list): List of section names.
                section_data (list): List of dictionaries, each containing key-value pairs for a section.
            """
            config = configparser.ConfigParser()

            for section, data in config_data.items():
                if not config.has_section(section):
                    config.add_section(section)
                for key, value in data.items():
                    config.set(section, key, value)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Write the configuration file
            with open(config_path, "w") as configfile:
                config.write(configfile)

            self.GOD[filename]["file"] = config
            self.GOD[filename]["last_updated"] = str(datetime.datetime.now())

            print(f"Configuration written to {config_path}")
        except IOError as e:
            print(f"Failed to write to the configuration file: {e}")

    # TODO - Not sure if needed (seems to be pointless as the file is alread read in the init function)
    def read_config_file(self, config_path):
        """Read and return the content of a configuration file using configparser."""
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            return config  # You can return the whole config object for further use
        except configparser.Error as e:
            print(f"Failed to read the configuration file: {e}")
            return None

    # TODO - make the function be more modular by passing the path and file depending on the operation
    def update_ini_file(self, filename, updates):
        """
        Update an existing configuration file with new or updated settings.
        'updates' is a dictionary where keys are section names, and values are dictionaries
        of setting names and their values.
        """
        config = self.GOD["config.ini"]["file"]
        config_path = self.GOD["config.ini"]["path"]

        # Check if the file exists to read existing configurations
        if os.path.exists(config_path):
            config.read(config_path)
        else:
            print("Configuration file does not exist, creating a new one.")

        # Update or add the new settings
        for section, settings in updates.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in settings.items():
                config.set(section, key, value)
        config.set("Last Updated", "DateTime", str(datetime.datetime.now()))

        # Write the updated configuration back to the file
        with open(config_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)
            print(f"Configuration updated and written to {config_path}")
            self.GOD[filename]["file"] = config
            self.GOD[filename]["last_updated"] = str(datetime.datetime.now())


if __name__ == "__main__":
    user_config = UserConfig()
    print(user_config.GOD["config.ini"]["path"])
