from pathlib import Path
import sys

# fastapi/ lives alongside api/ at the repo root
FASTAPI_DIR = Path(__file__).resolve().parent.parent / "fastapi"
if str(FASTAPI_DIR) not in sys.path:
    sys.path.insert(0, str(FASTAPI_DIR))

from backend.server import app
