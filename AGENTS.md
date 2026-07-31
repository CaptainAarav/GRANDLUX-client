# AGENTS.md

Python desktop GUI client (customtkinter) that tracks a flight simulator and uploads position data to the GrandLux backend. No tests, lint, typecheck, or CI configured — don't invent commands for them.

## Run

- Use the project venv: `.venv/bin/python main.py` (Python 3.14; deps in `requirements.txt`).
- `assets/logo.png` is required — the app crashes on startup if it's missing.
- The app is a GUI (needs a display). All modules are plain top-level `.py` files; no package structure.

## Architecture

- `main.py` — entrypoint, creates the `ctk.CTk()` root and `gui.App`.
- `gui.py` — all UI. Defines color/font constants at module top. Hardcodes `API_BASE_URL = http://localhost:4000`, `LISTEN_PORT = 49005`. Has Departure/Arrival ICAO entries; on Start it POSTs `{departure_icao, arrival_icao}` to `/api/flights/start`, stores the returned `flight_id`, and on Stop POSTs `{flight_id}` to `/api/flights/end`. Builds endpoint paths as `f"{API_BASE_URL}/api/flights/ping"`.
- `listener.py` — `XPlaneListener`: binds a UDP socket on `0.0.0.0:49005` and parses X-Plane `DATA` packets. Each packet is `b"DATA"` followed by repeated 36-byte chunks unpacked as `<i8f`. Data indices: `20` → lat/lon/alt_msl/alt_agl, `17` → heading, `3` → speed, `4` → vvi_fpm.
- `sender.py` — `DataSender`: polls the listener every `interval` seconds and POSTs `{lat, lon, alt_msl, alt_agl, heading, speed, vvi_fpm, flight_id}` as JSON with a `Bearer` token. Logs failures via `print`, never throws.
- `auth.py` — login flow: starts an HTTP server on an ephemeral localhost port, opens `http://localhost:5173/login?redirect_port=<port>` in the browser, and captures `?token=` from the callback.
- `token_handlers.py` — **dead code**. Persisted refresh-token storage (`client_config.json`) left over from before the "no persistent login" change; nothing imports it.

## External dependencies

The backend (login page on `localhost:5173`, API on `localhost:4000`) is a separate service not in this repo. Login and tracking only work when it's running locally.

## Gotchas

- `__pycache__/*.pyc` files are tracked in git (committed before `.gitignore` added the dir). A regenerated `.pyc` shows up as modified in `git status` — don't stage it.
- `client_config.json` is gitignored and generated at runtime (if `token_handlers.py` is ever used again).
- The MSFS radio button is disabled/placeholder; `sim_choice` is not consulted by the tracking toggle.
- `vvi_fpm` (row 4) requires X-Plane's own Settings → Data Output → Data Set → network UDP output checkbox for row 4. If the sim hasn't enabled it, `vvi_fpm` is simply absent from parsed data — a client-side code change can't fix it.
