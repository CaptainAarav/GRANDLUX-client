import os
import tkinter as tk
import customtkinter as ctk
import requests
import webbrowser
from PIL import Image, ImageTk
from listener import XPlaneListener
from sender import DataSender
from auth import LoginListener, open_login


LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49005
API_BASE_URL = "https://grandlux-site-server.onrender.com"

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
        self.root.geometry("550x720")
        self.root.resizable(False, False)
        self.listener = None
        self.login_listener = None
        self.sender = None
        self.flight_id = None
        self.plan_id_by_label = {}
        self.sim_choice = tk.StringVar(value="xplane")

        self._icon_image = ImageTk.PhotoImage(Image.open(logo_file).convert("RGBA"))
        self.root.iconphoto(True, self._icon_image)
        self._build_header()
        self._build_login_section()
        self._build_sim_selector()
        self._build_stats_section()
        self._build_toggle_section()
        self._build_footer()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<FocusIn>", self._on_window_focus)
        self.root.after(2000, self._poll)

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

        self.token = token
        self.login_status_label.configure(text="Logged In!", text_color=green_colour)
        self.login_button.pack_forget()
        self.refresh_button.configure(state="normal")
        self._load_flight_plans()
        
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

    def _build_toggle_section(self) -> None:
        section = ctk.CTkFrame(self.root, fg_color=background_colour, corner_radius=0)
        section.pack(fill="x", padx=24, pady=(6, 10))

        header_row = ctk.CTkFrame(section, fg_color=background_colour)
        header_row.pack(fill="x")
        ctk.CTkLabel(header_row, text="FLIGHT PLAN", font=label_font, text_color=gold_colour, fg_color=background_colour).pack(side="left")
        self.refresh_button = ctk.CTkButton(
            header_row, text="Refresh",
            corner_radius=8, width=70, height=24,
            font=small_font,
            fg_color=grey_colour, hover_color=dark_colour, text_color="#ffffff",
            command=self._load_flight_plans,
            state="disabled",
        )
        self.refresh_button.pack(side="right")

        self.plan_menu = ctk.CTkOptionMenu(
            section, values=[],
            width=220, height=32, corner_radius=8,
            font=subtitle_font,
            fg_color=white_colour, button_color=red_colour, button_hover_color="#a81f24",
            text_color=dark_colour,
        )

        self.plan_empty_label = ctk.CTkLabel(section, text="Log in to load flight plans", font=subtitle_font, text_color=grey_colour, fg_color=background_colour)
        self.plan_empty_label.pack(pady=(6, 0))

        self.toggle_button = ctk.CTkButton(
            section, text="Start Flight",
            corner_radius=10,
            fg_color=red_colour,
            hover_color="#a81f24",
            text_color="#ffffff",
            font=button_font,
            width=150,
            height=35,
            command=self._on_toggle,
            state="disabled",
        )
        
        self.toggle_button.pack(pady=(14, 0))

        self.status_label = ctk.CTkLabel(section, text="● Stopped", font=subtitle_font, text_color=grey_colour, fg_color=background_colour)
        self.status_label.pack(pady=(10, 0))

    def _load_flight_plans(self) -> None:
        if self.token is None:
            return
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/flight-plans/mine",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5,
            )
            response.raise_for_status()
            plans = response.json()
            if not isinstance(plans, list):
                raise ValueError("unexpected flight-plans response")
        except (requests.exceptions.RequestException, ValueError):
            self.plan_empty_label.configure(text="Failed to load flight plans")
            self._show_plan_ui({})
            return

        plan_id_by_label = {
            f"{p.get('departure_icao')} → {p.get('arrival_icao')}": p["id"]
            for p in plans
        }
        self.plan_empty_label.configure(text="No flight plans — create one on the website")
        self._show_plan_ui(plan_id_by_label)

    def _show_plan_ui(self, plan_id_by_label: dict) -> None:
        self.plan_id_by_label = plan_id_by_label
        if not plan_id_by_label:
            self.plan_menu.pack_forget()
            self.plan_empty_label.pack(pady=(6, 0))
            self.toggle_button.configure(state="disabled")
            return

        self.plan_empty_label.pack_forget()
        self.plan_menu.configure(values=list(plan_id_by_label))
        previous = self.plan_menu.get()
        self.plan_menu.set(previous if previous in plan_id_by_label else next(iter(plan_id_by_label)))
        self.plan_menu.pack(pady=(6, 0))
        self.toggle_button.configure(state="normal")

    def _on_window_focus(self, event) -> None:
        if event.widget is self.root and getattr(self, "token", None) is not None and self.listener is None:
            self._load_flight_plans()

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self.root, fg_color=dark_colour, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        ctk.CTkLabel(footer, text="© 2026 GrandLux", font=small_font, text_color=grey_colour, fg_color=dark_colour).pack()

    def _on_toggle(self) -> None:
        if self.listener is None:
            if self.token is None:
                self.status_label.configure(text="● Log in first", text_color=red_colour)
                return

            plan_id = self.plan_id_by_label.get(self.plan_menu.get()) if self.plan_id_by_label else None
            if plan_id is None:
                self.status_label.configure(text="● No flight plan selected", text_color=red_colour)
                return

            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/flights/start",
                    json={"flight_plan_id": plan_id},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5,
                )
                response.raise_for_status()
            except requests.exceptions.RequestException:
                self.status_label.configure(text="● Failed to start flight", text_color=red_colour)
                return

            self.flight_id = response.json().get("flight_id")

            self.listener = XPlaneListener(LISTEN_IP, LISTEN_PORT)
            self.sender = DataSender(self.listener, f"{API_BASE_URL}/api/flights/ping", self.token, self.flight_id, interval=2)
            self.listener.start()
            self.sender.start()

            self.toggle_button.configure(text="Stop Flight", fg_color=dark_colour, hover_color="#000000")
            self.status_label.configure(text="● Tracking", text_color=gold_colour)
        else:
            try:
                requests.post(
                    f"{API_BASE_URL}/api/flights/end",
                    json={"flight_id": self.flight_id},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5,
                )
            except requests.exceptions.RequestException as e:
                print(f"End failed: {e}")

            self.sender.stop()
            self.listener.stop()
            self.listener = None
            self.sender = None
            self.flight_id = None

            self.toggle_button.configure(text="Start Flight", fg_color=red_colour, hover_color="#a81f24")
            self.status_label.configure(text="● Stopped", text_color=grey_colour)
            for label in self.stat_labels.values():
                label.configure(text="—")

            self._load_flight_plans()

    def _poll(self) -> None:
        if self.listener is not None:
            data = self.listener.get_latest()
            for key, label in self.stat_labels.items():
                if key in data:
                    value = data[key]
                    label.configure(text=f"{value:.4f}" if key in ("lat", "lon") else f"{value:.1f}")

        self.root.after(2000, self._poll)

    def _on_close(self) -> None:
        if self.listener is not None:
            self.listener.stop()
        if self.sender is not None:
            self.sender.stop()
        self.root.destroy()