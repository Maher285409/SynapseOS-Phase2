import os
import re
import math
import subprocess
import webbrowser
import pyautogui
import ctypes
from datetime import datetime, date


class CommandEngine:
    """
    SynapseOS voice command engine for Windows.

    Notes:
    - Website shortcuts are opened in dedicated Chrome app windows with
      separate SynapseOS browser profiles. This allows SynapseOS to close
      the window it launched without killing the user's normal Chrome session.
    - "close chrome" closes all Chrome windows, including windows the user
      opened manually.
    - Volume keys usually change Windows volume by about 2 percentage points
      per press. The exact step depends on the device/audio driver.
    """

    WEBSITES = {
        "youtube": ("YouTube", "https://www.youtube.com"),
        "google": ("Google", "https://www.google.com"),
        "amazon": ("Amazon", "https://www.amazon.in"),
        "flipkart": ("Flipkart", "https://www.flipkart.com"),
        "whatsapp": ("WhatsApp", "https://web.whatsapp.com"),
        "gmail": ("Gmail", "https://mail.google.com"),
        "github": ("GitHub", "https://github.com"),
        "chatgpt": ("ChatGPT", "https://chatgpt.com"),
        "instagram": ("Instagram", "https://www.instagram.com"),
        "facebook": ("Facebook", "https://www.facebook.com"),
        "netflix": ("Netflix", "https://www.netflix.com"),
        "spotify": ("Spotify", "https://open.spotify.com"),
    }

    def __init__(self):
        self.chrome_path = self._find_chrome()
        self.site_processes = {}
        self.speaker = None
        self._init_speech()
        print("[Command] Engine ready.")

    # --------------------------------------------------
    # INITIALIZATION / HELPERS
    # --------------------------------------------------

    @staticmethod
    def _find_chrome():
        candidates = [
            os.path.expandvars(
                r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
            ),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    def _init_speech(self):
        """Use pyttsx3 when installed; commands still work without it."""
        try:
            import pyttsx3
            self.speaker = pyttsx3.init()
            self.speaker.setProperty("rate", 175)
        except Exception:
            self.speaker = None
            print("[Command] Voice responses unavailable; install pyttsx3 to enable them.")

    def _say(self, message):
        print("[SynapseOS]", message)
        if self.speaker:
            try:
                self.speaker.say(message)
                self.speaker.runAndWait()
            except Exception as error:
                print("[Command] Speech error:", error)

    @staticmethod
    def _has_any(text, phrases):
        return any(phrase in text for phrase in phrases)

    @staticmethod
    def _extract_amount(text, default=10):
        match = re.search(r"\b(\d{1,3})\b", text)
        if not match:
            return default
        return max(1, min(100, int(match.group(1))))

    def _open_website(self, key):
        name, url = self.WEBSITES[key]

        # A dedicated profile keeps this app window separate from the
        # user's regular Chrome session and makes targeted closing safer.
        if self.chrome_path:
            profile_root = os.path.join(
                os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                "SynapseOS",
                "BrowserProfiles",
                key,
            )
            os.makedirs(profile_root, exist_ok=True)

            try:
                process = subprocess.Popen([
                    self.chrome_path,
                    "--app=" + url,
                    "--user-data-dir=" + profile_root,
                    "--no-first-run",
                    "--no-default-browser-check",
                ])
                self.site_processes[key] = process
                self._say("Opening " + name + ".")
                return
            except Exception as error:
                print("[Command] Chrome app-window error:", error)

        # Fallback if Chrome is not installed or could not be launched.
        webbrowser.open_new(url)
        self._say("Opening " + name + ".")

    def _close_website(self, key):
        name, _ = self.WEBSITES[key]
        process = self.site_processes.get(key)

        if process is None:
            self._say(
                name + " was not opened by SynapseOS in this session. "
                "I have not closed your other browser tabs."
            )
            return

        try:
            if process.poll() is None:
                # /T closes child processes belonging to this dedicated
                # Chrome app window. It does not target normal Chrome windows.
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            self.site_processes.pop(key, None)
            self._say("Closed the " + name + " window opened by SynapseOS.")
        except Exception as error:
            self._say("I could not close " + name + ".")
            print("[Command] Close website error:", error)

    def _launch_app(self, app_name):
        apps = {
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "paint": ["mspaint.exe"],
            "task manager": ["taskmgr.exe"],
            "file explorer": ["explorer.exe"],
        }
        try:
            subprocess.Popen(apps[app_name])
            self._say("Opening " + app_name + ".")
        except Exception as error:
            self._say("I could not open " + app_name + ".")
            print("[Command] App launch error:", error)

    # --------------------------------------------------
    # MAIN COMMAND HANDLER
    # --------------------------------------------------

    def execute(self, text):
        text = (text or "").lower().strip()
        text = re.sub(r"[,.!?]", "", text)
        text = re.sub(r"\s+", " ", text)

        if not text:
            return True

        print("[Command] Heard:", text)

        # Exit SynapseOS
        if text in ("exit", "quit", "stop synapse", "close synapseos",
                    "exit synapseos", "shutdown synapseos"):
            self._say("Closing SynapseOS.")
            return False

        # Lock Windows
        if self._has_any(text, (
            "lock computer", "lock my computer", "lock system",
            "lock windows", "lock synapse",
        )):
            self._say("Locking your computer.")
            try:
                ctypes.windll.user32.LockWorkStation()
            except Exception as error:
                print("[Command] Lock error:", error)
            return False

        # Time / date / day
        if self._has_any(text, (
            "what time", "tell me the time", "current time",
            "time now", "time is it",
        )) or text == "time":
            current_time = datetime.now().strftime("%I:%M %p").lstrip("0")
            self._say("The time is " + current_time + ".")
            return True

        if self._has_any(text, (
            "what is the date", "what's the date", "today's date",
            "today date", "date today", "current date",
        )) or text == "date":
            current_date = date.today().strftime("%A, %d %B %Y")
            self._say("Today is " + current_date + ".")
            return True

        if self._has_any(text, ("what day is it", "which day is it", "today's day")):
            self._say("Today is " + datetime.now().strftime("%A") + ".")
            return True

        # Volume: accepts phrases such as "increase volume by 30".
        if self._has_any(text, (
            "increase volume", "volume up", "turn up volume",
            "raise volume", "make it louder",
        )):
            amount = self._extract_amount(text, default=10)
            presses = max(1, math.ceil(amount / 2))
            for _ in range(presses):
                pyautogui.press("volumeup")
            self._say("Increasing volume by approximately " + str(amount) + " percent.")
            return True

        if self._has_any(text, (
            "decrease volume", "volume down", "turn down volume",
            "lower volume", "make it quieter",
        )):
            amount = self._extract_amount(text, default=10)
            presses = max(1, math.ceil(amount / 2))
            for _ in range(presses):
                pyautogui.press("volumedown")
            self._say("Decreasing volume by approximately " + str(amount) + " percent.")
            return True

        if self._has_any(text, ("unmute", "unmute volume")):
            # Windows mute is a toggle; this key may unmute or mute depending
            # on the current state, so use it only when explicitly requested.
            pyautogui.press("volumemute")
            self._say("Toggled mute.")
            return True

        if self._has_any(text, ("mute", "mute volume", "silence volume")):
            pyautogui.press("volumemute")
            self._say("Toggled mute.")
            return True

        # Open / close supported websites
        for key, (name, _) in self.WEBSITES.items():
            open_phrases = (
                "open " + key,
                "launch " + key,
                "start " + key,
                "go to " + key,
                "visit " + key,
            )
            close_phrases = (
                "close " + key,
                "exit " + key,
                "shut " + key,
                "quit " + key,
            )

            if self._has_any(text, open_phrases):
                self._open_website(key)
                return True

            if self._has_any(text, close_phrases):
                self._close_website(key)
                return True

        # Open Chrome itself
        if self._has_any(text, (
            "open chrome", "open google chrome", "launch chrome",
            "start chrome",
        )):
            if self.chrome_path:
                try:
                    subprocess.Popen([self.chrome_path])
                    self._say("Opening Google Chrome.")
                except Exception as error:
                    self._say("I could not open Chrome.")
                    print("[Command] Chrome error:", error)
            else:
                webbrowser.open_new("https://www.google.com")
                self._say("Chrome was not found. I opened your default browser.")
            return True

        # Close Chrome: explicitly closes all Chrome windows.
        if self._has_any(text, ("close chrome", "exit chrome", "quit chrome")):
            self._say("Closing all Google Chrome windows.")
            try:
                subprocess.run(
                    ["taskkill", "/IM", "chrome.exe", "/T", "/F"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except Exception as error:
                print("[Command] Close Chrome error:", error)
                self._say("I could not close Chrome.")
            return True

        # Google search
        search_match = re.match(
            r"^(?:search for|google|look up)\s+(.+)$", text
        )
        if search_match:
            query = search_match.group(1).strip()
            if query:
                webbrowser.open_new(
                    "https://www.google.com/search?q=" +
                    __import__("urllib.parse", fromlist=["quote"]).quote(query)
                )
                self._say("Searching Google for " + query + ".")
            return True

        # Open common Windows applications
        for app_name, phrases in {
            "notepad": ("open notepad", "launch notepad", "start notepad"),
            "calculator": ("open calculator", "open calc", "launch calculator"),
            "paint": ("open paint", "launch paint"),
            "task manager": ("open task manager", "launch task manager"),
            "file explorer": ("open file explorer", "open explorer"),
        }.items():
            if self._has_any(text, phrases):
                self._launch_app(app_name)
                return True

        # Screenshot
        if self._has_any(text, (
            "take screenshot", "capture screen", "take a screenshot",
        )):
            try:
                folder = os.path.join(
                    os.path.expanduser("~"), "Pictures", "SynapseOS"
                )
                os.makedirs(folder, exist_ok=True)
                filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
                path = os.path.join(folder, filename)
                pyautogui.screenshot().save(path)
                self._say("Screenshot saved in your Pictures SynapseOS folder.")
            except Exception as error:
                self._say("I could not take the screenshot.")
                print("[Command] Screenshot error:", error)
            return True

        # Help
        if self._has_any(text, (
            "help", "what can you do", "list commands", "available commands",
        )):
            self._say(
                "I can open or close supported websites, control volume, "
                "tell the time and date, search Google, open Windows apps, "
                "take screenshots, and lock the computer."
            )
            return True

        print("[Command] Unknown command:", text)
        self._say("Sorry, I don't know that command yet.")
        return True
