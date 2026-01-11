#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

os.chdir(Path(__file__).parent)
os.makedirs("data", exist_ok=True)

# Install deps
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

print("🚀 Smart AI PM Tool LIVE → http://localhost:8000")
subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
