"""Writes a 1280x400 banner, the README banners' look, with the Hardcharger bull.

    python3 scripts/banner.py OUT TITLE TAGLINE KICKER

The dark card (#0b1416 -> #101f26), the charging bull (src/assets/brand/hardcharger-mascot.webp:
the brand kit's standalone mascot, cropped, 480 px wide, WebP quality 90), the #f15a24 -> #31a8db
underline and kicker, and the speed streaks.
"""
import base64, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

out, title, tagline, kicker = sys.argv[1:5]
logo = base64.b64encode((ROOT / "src" / "assets" / "brand" / "hardcharger-mascot.webp").read_bytes()).decode()
font = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
size = 96 if len(title) <= 12 else 84
bar = min(560, int(len(title) * size * 0.56))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1280" height="400" viewBox="0 0 1280 400" role="img" aria-label="{title}: {tagline}. {kicker.title()}.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1416"/><stop offset="1" stop-color="#101f26"/></linearGradient>
    <linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f15a24"/><stop offset="1" stop-color="#31a8db"/></linearGradient>
    <linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f15a24" stop-opacity="0"/><stop offset="0.7" stop-color="#f15a24" stop-opacity="0.55"/><stop offset="1" stop-color="#31a8db" stop-opacity="0.9"/></linearGradient>
    <radialGradient id="glow" cx="0.22" cy="0.5" r="0.45"><stop offset="0" stop-color="#31a8db" stop-opacity="0.18"/><stop offset="1" stop-color="#31a8db" stop-opacity="0"/></radialGradient>
    <clipPath id="card"><rect width="1280" height="400" rx="28"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1280" height="400" fill="url(#bg)"/>
    <rect width="1280" height="400" fill="url(#glow)"/>
    <g transform="skewX(-24)">
      <rect x="620" y="58" width="760" height="6" rx="3" fill="url(#streak)" opacity="0.55"/>
      <rect x="820" y="84" width="600" height="3" rx="1.5" fill="url(#streak)" opacity="0.4"/>
      <rect x="760" y="318" width="700" height="4" rx="2" fill="url(#streak)" opacity="0.45"/>
      <rect x="960" y="340" width="520" height="2" rx="1" fill="url(#streak)" opacity="0.35"/>
    </g>
    <image x="52" y="124" width="258" height="165" href="data:image/webp;base64,{logo}"/>
    <text x="330" y="196" font-family="{font}" font-size="{size}" font-weight="800" letter-spacing="-2" fill="#f5f8f7">{title}</text>
    <rect x="334" y="218" width="{bar}" height="8" rx="4" fill="url(#brand)"/>
    <text x="334" y="270" font-family="{font}" font-size="30" font-weight="500" fill="#c9d6d4">{tagline}</text>
    <text x="334" y="312" font-family="{font}" font-size="22" font-weight="600" letter-spacing="3" fill="url(#brand)">{kicker.upper()}</text>
  </g>
</svg>
'''
pathlib.Path(out).write_text(svg)
