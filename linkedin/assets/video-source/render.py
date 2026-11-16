"""Render scene.html to PNG frames (30 FPS) with Playwright. Usage: python3 render.py <out_dir> [start_frame end_frame]"""
import sys, pathlib
from playwright.sync_api import sync_playwright
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
b = int(sys.argv[3]) if len(sys.argv) > 3 else 1800
src = (pathlib.Path(__file__).parent / "scene.html").resolve().as_uri()
with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(src); pg.wait_for_timeout(500)
    for f in range(a, b):
        pg.evaluate(f"render({f/30})")
        pg.screenshot(path=str(out / f"f{f:05d}.jpg"), type="jpeg", quality=92)
    br.close()
