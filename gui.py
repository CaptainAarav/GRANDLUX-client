import os
import tkinter as tk
import customtkinter as ctk
import webbrowser
from PIL import Image, ImageTk
from listener import XPlaneListener
from sender import DataSender
from token_handlers import save_refresh_token, load_refresh_token
from auth import LoginListener, open_login


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
green_colour = "#2e7d32"

title_font = ("Georgia", 36)
subtitle_font = ("Helvetica", 15)
label_font = ("Helvetica", 14, "bold")
value_font = ("Helvetica", 13, "bold")
button_font = ("Helvetica", 13, "bold")
small_font = ("Helvetica", 9)

logo_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), "logo.png")

ctk.set_appearance_mode("light")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GrandLux Tracking Client")
        self.root.configure(fg_color=background_colour)
        self.root.geometry("550x600")
        self.root.resizable(False, False)
        self.listener = None
        self.login_listener = None
        self.sender = None
        self.sim_choice = tk.StringVar(value="xplane")

        self._icon_image = ImageTk.PhotoImage(Image.open(logo_file).convert("RGBA"))
        self.root.iconphoto(True, self._icon_image)

        self._build_header()

        if load_refresh_token() is None:
            self._build_login_section()
            
        self._build_sim_selector()
        self._build_stats_section()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.root, fg_color=dark_colour, height=100, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        pil_image = Image.open(logo_file).convert("RGBA")
        self._logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(80, 80))

        ctk.CTkLabel(header, image=self._logo_image, text="", fg_color=dark_colour).pack(side="left", padx=(20, 12), pady=20)

        text_frame = ctk.CTkFrame(header, fg_color=dark_colour)
        text_frame.pack(side="left", pady=20)
        ctk.CTkLabel(text_frame, text="GrandLux Tracking Client", font=title_font, text_color=red_colour, fg_color=dark_colour).pack()

    def _build_login_section(self) -> None:
        section = ctk.CTkFrame(self.root, fg_color=background_colour, corner_radius=0)
        section.pack(fill="x", padx=24, pady=(20, 10))

        self.login_status_label = ctk.CTkLabel(section, text="Not logged in", font=subtitle_font, text_color=grey_colour, fg_color=background_colour)
        self.login_status_label.pack()

        self.login_button = ctk.CTkButton(
            section, text="Log In",
            corner_radius=10,
            fg_color=red_colour,
            hover_color="#a81f24",
            text_color="#ffffff",
            font=button_font,
            command=self._on_login_click,
            width=150,
            height=35
        )
        
        self.login_button.pack(pady=(10, 0))

    def _on_login_click(self) -> None:
        if self.login_listener is not None:
            return

        self.login_button.configure(text="Waiting for login...", state="disabled")
        self.login_listener = LoginListener()
        self.login_listener.start()
        open_login(self.login_listener.port)
        self.root.after(1000, self._check_login_status)

    def _check_login_status(self) -> None:
        token = self.login_listener.get_token()
        if token is None:
            self.root.after(1000, self._check_login_status)
            return

        save_refresh_token(token)
        self.login_status_label.configure(text="Logged In!", text_color=green_colour)
        self.login_button.pack_forget()
        
    def _build_sim_selector(self) -> None:
        section = ctk.CTkFrame(self.root, fg_color=background_colour, corner_radius=0)
        section.pack(fill="x", padx=24, pady=10)

        ctk.CTkLabel(section, text="SIMULATOR", font=label_font, text_color=gold_colour, fg_color=background_colour).pack(anchor="w")

        row = ctk.CTkFrame(section, fg_color=background_colour)
        row.pack(fill="x", pady=(6, 0))

        ctk.CTkRadioButton(
            row, text="X-Plane", variable=self.sim_choice, value="xplane",
            font=subtitle_font, fg_color=red_colour,
        ).pack(side="left")

        ctk.CTkRadioButton(
            row, text="MSFS (coming soon)", variable=self.sim_choice, value="msfs",
            font=subtitle_font, fg_color=red_colour, state="disabled",
        ).pack(side="left", padx=(16, 0))
        
    def _build_stats_section(self) -> None:
        card = ctk.CTkFrame(self.root, fg_color=white_colour, border_width=1, border_color=grey_colour, corner_radius=8)
        card.pack(fill="x", padx=24, pady=14)

        self.stat_labels = {}
        fields = [
            ("lat", "Latitude"),
            ("lon", "Longitude"),
            ("alt_msl", "Altitude (MSL)"),
            ("heading", "Heading"),
            ("speed", "Speed"),
        ]
        for i, (key, label) in enumerate(fields):
            row = ctk.CTkFrame(card, fg_color=white_colour)
            row.pack(fill="x", padx=16, pady=(12 if i == 0 else 6, 12 if i == len(fields) - 1 else 6))
            
            ctk.CTkLabel(row, text=label, font=subtitle_font, text_color=grey_colour, fg_color=white_colour).pack(side="left")
            value_label = ctk.CTkLabel(row, text="—", font=value_font, text_color=dark_colour, fg_color=white_colour)
            value_label.pack(side="right")
            self.stat_labels[key] = value_label