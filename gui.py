import os
import tkinter as tk
from PIL import Image, ImageTk
from listener import XPlaneListener
from sender import DataSender


LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49005
API_URL = "https://your-api-here.com/api/flights/ping"


background_colour = "#F7F3EC"
dark_colour = "#1b1d22"
red_colour = "#c8262c"
gold_colour = "#c9a227"
grey_colour = "#55677a"
light_colour = "#f2f1ec"
white_colour = "#ffffff"

title_font = ("Georgia", 24, "bold")
subtitle_font = ("Helvetica", 10)
label_font = ("Helvetica", 10, "bold")
value_font = ("Helvetica", 13, "bold")
button_font = ("Helvetica", 12, "bold")
small_font = ("Helvetica", 9)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GrandLux Tracking Client")
        self.root.configure(bg=background_colour)
        self.root.geometry("380x600")
        self.root.resizable(False, False)
        self.listener = None
        self.sender = None
        self.sim_choice = tk.StringVar(value="xplane")
        self._build_header()
        self._build_login_section()
        self._build_sim_selector()
        self._build_stats_section()
        self._build_toggle_section()
        self._build_footer()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(2000, self._poll)
        
    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=dark_colour, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)