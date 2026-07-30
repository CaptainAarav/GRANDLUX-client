import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client_config.json")

def save_refresh_token(token: str) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump({"refresh_token": token}, f)

def load_refresh_token() -> str | None:
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    return data.get("refresh_token")