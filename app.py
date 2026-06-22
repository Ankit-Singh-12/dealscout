"""Hugging Face Spaces entrypoint for the DealScout demo.
Run locally with:  python app.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("DEALSCOUT_DEMO_MODE", "1")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "app"))

from app.dealscout_app import App

app = App()
demo = app.build()

if __name__ == "__main__":
    demo.launch()