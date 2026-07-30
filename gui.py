import os
import tkinter as tk
from PIL import Image, ImageTk
from listener import XPlaneListener
from sender import DataSender
from token_handlers import save_refresh_token, load_refresh_token


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

title_font = ("Georgia", 24)
subtitle_font = ("Helvetica", 10)
label_font = ("Helvetica", 10, "bold")
value_font = ("Helvetica", 13, "bold")
button_font = ("Helvetica", 12, "bold")
small_font = ("Helvetica", 9)

logo_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), "logo.png")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GrandLux Tracking Client")
        self.root.configure(bg=background_colour)
        self.root.geometry("550x600")
        self.root.resizable(False, False)
        self.listener = None
        self.login_listener = None
        self.sender = None
        self.sim_choice = tk.StringVar(value="xplane")
        
        self._build_header()

        if load_refresh_token() is None:
            self._build_login_section()
            
        # self._build_sim_selector()
        # self._build_stats_section()
        # self._build_toggle_section()
        # self._build_footer()
        # self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        # self.root.after(2000, self._poll)
        
    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=dark_colour, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        image = Image.open(logo_file).convert("RGBA")
        image.thumbnail((100, 100), Image.LANCZOS)
        self._logo_image = ImageTk.PhotoImage(image)
        
        tk.Label(header, image=self._logo_image, bg=dark_colour).pack(side="left", padx=(20, 12), pady=20)
        
        text_frame = tk.Frame(header, bg=dark_colour)
        text_frame.pack(side="left", pady=20)
        tk.Label(text_frame, text="GrandLux Tracking Client", font=title_font, fg=red_colour, bg=dark_colour).pack()
        
    def _build_login_section(self) -> None:
        section = tk.Frame(self.root, bg=background_colour)
        section.pack(fill="x", padx=24, pady=(20, 10))

        self.login_status_label = tk.Label(section, text="Not logged in", font=subtitle_font, fg=grey_colour, bg=background_colour)
        self.login_status_label.pack(anchor="w")

        self.login_button = tk.Label(
            section, text="Log In", font=button_font, fg="#ffffff", bg=red_colour,
            cursor="hand2", pady=8,
        )
        self.login_button.pack(fill="x", pady=(6, 0))
        self.login_button.bind("<Button-1>", lambda e: self._on_login_click())