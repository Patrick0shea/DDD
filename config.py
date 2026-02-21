import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        val = input(f"Enter {key}: ").strip()
        if not val:
            raise ValueError(f"{key} is required")
        _offer_save(key, val)
    return val

def _offer_save(key: str, val: str):
    save = input(f"Save {key} to .env for future runs? [y/N]: ").strip().lower()
    if save == "y":
        env_path = Path(".env")
        with open(env_path, "a") as f:
            f.write(f"\n{key}={val}")
        print(f"Saved to .env")

ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
BAMBU_IP: str = _require("BAMBU_IP")
BAMBU_SERIAL: str = _require("BAMBU_SERIAL")
BAMBU_ACCESS_CODE: str = _require("BAMBU_ACCESS_CODE")
