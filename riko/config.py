"""Loads character_config.yaml and the API keys from .env."""
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent  # the project folder
load_dotenv(ROOT / ".env")


def load_config():
    with open(ROOT / "character_config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def need_key(name, why):
    """Stop at startup with a clear message if an API key is missing."""
    if not os.getenv(name):
        sys.exit(f"[setup] {name} is missing. Add it to .env (needed for {why}).")
    print(f"[setup] {name} found ({why})")
