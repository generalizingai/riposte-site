#!/usr/bin/env python3
"""Render the social preview card and the favicon set from the Riposte brand.

The card is composed at 600x315 and rasterised at 2x to land on 1200x630, the size
X, LinkedIn and Facebook all crop from. Feeds downscale it to roughly 500px wide,
so the type is set large enough to survive that rather than sized for a monitor.
"""
import base64
import pathlib
import subprocess

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def card():
    wordmark = uri(ASSETS / "riposte-wordmark-dark.png")
    html = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;800&family=Sora:wght@300;400&display=swap">
<style>
  *,*::before,*::after{box-sizing:border-box}
  html,body{margin:0;width:600px;height:315px;overflow:hidden}
  body{background:#000;color:#f2f5f6;font-family:"Sora",-apple-system,sans-serif;
    -webkit-font-smoothing:antialiased;position:relative;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    text-align:center;padding:30px 46px}
  .grid{position:absolute;inset:0;pointer-events:none;
    background-image:linear-gradient(to right,rgba(255,255,255,.035) 1px,transparent 1px),
      linear-gradient(to bottom,rgba(255,255,255,.035) 1px,transparent 1px);
    background-size:34px 34px}
  .halo{position:absolute;top:-40%;left:50%;width:130%;height:90%;transform:translateX(-50%);
    pointer-events:none;
    background:radial-gradient(ellipse at center,rgba(74,158,255,.13),transparent 62%)}
  img{height:19px;display:block;margin-bottom:20px;position:relative;z-index:2}
  h1{position:relative;z-index:2;font-family:"JetBrains Mono",monospace;font-weight:800;
    font-size:31px;line-height:1.12;letter-spacing:-.04em;margin:0;max-width:17ch}
  .strip{position:relative;z-index:2;margin-top:24px;display:flex;gap:8px;
    font-family:"JetBrains Mono",monospace;font-size:11px;color:#9ba3aa}
  .strip span{border:1px solid rgba(255,255,255,.15);border-radius:999px;padding:6px 13px}
  .strip b{color:#f2f5f6;font-weight:500}
</style>
<div class="grid"></div><div class="halo"></div>
<img src="__WORDMARK__" alt="">
<h1>Grow your X account without typing a single comment.</h1>
<div class="strip">
  <span><b>12</b> rules</span><span><b>13</b> angles</span><span><b>$9.99</b> once</span>
</div>
""".replace("__WORDMARK__", wordmark)

    src = ASSETS / "_og.html"
    src.write_text(html)
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--window-size=600,315", "--force-device-scale-factor=2",
         "--virtual-time-budget=9000",
         f"--screenshot={ASSETS / 'social-card.png'}", src.as_uri()],
        capture_output=True, timeout=90,
    )
    src.unlink()


def favicons():
    disc = Image.open(ASSETS / "riposte-icon.png").convert("RGBA")

    for size in (16, 32, 180, 512):
        name = "apple-touch-icon.png" if size == 180 else f"favicon-{size}.png"
        out = disc.resize((size, size), Image.LANCZOS)
        if size == 180:
            # iOS ignores transparency and composites on white, so flatten onto the
            # brand black rather than letting it pick.
            flat = Image.new("RGB", (180, 180), (0, 0, 0))
            flat.paste(out, (0, 0), out)
            out = flat
        out.save(ASSETS / name)

    # Multi-resolution .ico for browsers and crawlers that still ask for one.
    disc.resize((64, 64), Image.LANCZOS).save(
        ASSETS / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )


if __name__ == "__main__":
    card()
    favicons()
    for f in sorted(ASSETS.glob("favicon*")) + [ASSETS / "apple-touch-icon.png", ASSETS / "social-card.png"]:
        im = Image.open(f)
        print(f"  {f.name:24} {im.size[0]}x{im.size[1]}  {round(f.stat().st_size / 1024)}KB")
