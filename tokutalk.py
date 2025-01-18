import logging
import threading
import os
from pwnagotchi import plugins

class Tokutalk(plugins.Plugin):
    __author__ = 'd3nt4ku'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'Alternates between English and Japanese languages and fonts.'

    def __init__(self):
        super().__init__()
        self.interval = 600  # Switch every 10 minutes
        self.timer = None
        self.config_path = "/etc/pwnagotchi/config.toml"
        self.current_state = self.get_current_lang()  # Initialize based on current language
        self.current_mode = None  # Store the current mode (AUTO or MANU)
        self.log_path = "/etc/pwnagotchi/log/pwnagotchi.log"  # Path to the log file

    def get_current_lang(self):
        """
        Reads the current language from config.toml.
        Returns 0 for English, 1 for Japanese.
        """
        try:
            with open(self.config_path, "r") as f:
                for line in f:
                    if line.startswith("main.lang"):
                        if "ja" in line:
                            return 1  # Japanese
                        else:
                            return 0  # English
        except Exception as e:
            logging.error(f"Failed to read current language: {e}")
        return 0  # Default to English if unable to read

    def on_loaded(self):
        current_lang = "Japanese" if self.current_state == 1 else "English"
        logging.info(f"Tokutalk loaded. Now in {current_lang}. Alternating every 10 minutes.")
        self.schedule_switch()

    def on_unload(self):
        if self.timer:
            self.timer.cancel()

    def schedule_switch(self):
        self.timer = threading.Timer(self.interval, self.switch_language_and_font)
        self.timer.start()

    def switch_language_and_font(self):
        try:
            # Get the current mode (AUTO or MANU) from the log file
            self.current_mode = self.get_current_mode()
            logging.info(f"Current mode before switch: {self.current_mode}")

            # Toggle between English and Japanese
            if self.current_state == 0:
                new_lang = "ja"
                new_font = "fonts-japanese-gothic"
                current_lang = "Japanese"
                next_lang = "English"
            else:
                new_lang = "en"
                new_font = "DejaVuSansMono"
                current_lang = "English"
                next_lang = "Japanese"

            # Read the current config file
            with open(self.config_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if line.startswith("main.lang"):
                    new_lines.append(f'main.lang = "{new_lang}"\n')
                elif line.startswith("ui.font.name"):
                    new_lines.append(f'ui.font.name = "{new_font}"\n')
                else:
                    new_lines.append(line)

            # Write the updated config file
            with open(self.config_path, "w") as f:
                f.writelines(new_lines)

            logging.info(f"Switched to: lang={new_lang}, font={new_font}")
            logging.info(f"Now in {current_lang}.")

            # Restart the Pwnagotchi service to apply changes
            logging.info("Restarting Pwnagotchi service to apply changes.")
            self.restart_pwnagotchi()

            # Toggle the state for the next switch
            self.current_state = 1 - self.current_state
            logging.info(f"Next language: {next_lang}")

        except Exception as e:
            logging.error(f"Failed to switch language and font: {e}")
        finally:
            # Schedule the next switch
            self.schedule_switch()

    def get_current_mode(self):
        """
        Reads the current mode (AUTO or MANU) from the log file.
        Supports:
        - "entering auto mode"
        - "entering manual mode"
        """
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, "r") as f:
                    lines = f.readlines()
                    # Search for the last occurrence of mode-related phrases
                    for line in reversed(lines):
                        if "entering auto mode" in line:
                            return "AUTO"
                        elif "entering manual mode" in line:
                            return "MANU"
            logging.warning("Mode not found in log file. Defaulting to AUTO.")
            return "AUTO"  # Default to AUTO if no mode is found
        except Exception as e:
            logging.error(f"Failed to read current mode: {e}")
            return "AUTO"  # Default to AUTO if unable to read

    def restart_pwnagotchi(self):
        """
        Restarts the Pwnagotchi service in the correct mode.
        """
        if self.current_mode:
            try:
                # Set the mode using the touch command
                if self.current_mode == "AUTO":
                    os.system("touch /root/.pwnagotchi-auto && systemctl restart pwnagotch")
                elif self.current_mode == "MANU":
                    os.system("touch /root/.pwnagotchi-manu && systemctl restart pwnagotch")

                # Restart the service
                logging.info(f"Restarted Pwnagotchi in {self.current_mode} mode.")
            except Exception as e:
                logging.error(f"Failed to restart Pwnagotchi: {e}")
