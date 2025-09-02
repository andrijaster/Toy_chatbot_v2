import os
import logging
from pathlib import Path
from settings import get_settings, Settings

# === Configuration ===
settings: Settings = get_settings()
CURR_DIR = Path(__file__).parent
STATIC_DIR = CURR_DIR / "static"

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("kids-story-bot")

LANDING_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AI Voice Assistant — Start</title>
  <style>
    body {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; display:flex;
           height:100vh; margin:0; align-items:center; justify-content:center; background:#0f172a; color:#f8fafc; }}
    .card {{ width:90%; max-width:720px; padding:28px; border-radius:12px; background:rgba(255,255,255,0.04);
            box-shadow: 0 6px 30px rgba(2,6,23,0.6); text-align:left; }}
    h1 {{ margin:0 0 8px 0; font-size:24px; text-align:center; }}
    label {{ display:block; margin-top:12px; font-weight:600; color:#e6eef6; }}
    input[type="text"], input[type="number"], textarea {{ width:100%; padding:8px; margin-top:6px; border-radius:8px;
            border:1px solid rgba(255,255,255,0.06); background:rgba(255,255,255,0.02); color:inherit; }}
    .row {{ display:flex; gap:12px; }}
    .btn {{ display:inline-block; margin-top:16px; padding:10px 16px; border-radius:10px; background:#06b6d4; color:#022;
           text-decoration:none; font-weight:700; border:none; cursor:pointer; }}
    .small {{ margin-top:10px; font-size:13px; color:#94a3b8; text-align:center; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Welcome — set up your session</h1>
    <form action="/start" method="post">
      <label for="name">Name</label>
      <input id="name" name="name" type="text" placeholder="Your name" required />

      <label for="age">Age</label>
      <input id="age" name="age" type="number" min="0" placeholder="Your age" required />

      <label for="guidelines">Guidelines / Notes</label>
      <textarea id="guidelines" name="guidelines" rows="4" placeholder="Tell the assistant anything useful (tone, constraints, background)"></textarea>

      <div style="text-align:center;">
        <button class="btn" type="submit">Start conversation</button>
      </div>
    </form>
    <div class="small">
      You will be redirected to the assistant UI. Your session info is saved locally (in-memory + <code>profiles.json</code>).
    </div>
  </div>
</body>
</html>
"""