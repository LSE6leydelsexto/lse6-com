from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TRACKS = [
    ("ley-del-sexto", "pdcQBdp-xhg"),
    ("zona-gris", "Re5mvPwaoG4"),
    ("clones-y-fantasmas", "jdpOHKF_dXQ"),
    ("nada-me-borra", "9wk6CUoYwFo"),
    ("libre-prisionero", "M0N5CoOKyEY"),
    ("lse6", "v40hHkTtdig"),
    ("error-404", "Fafu9xC-npY"),
]
errors = []
index = (ROOT / "index.html").read_text(encoding="utf-8-sig")
redirects = (ROOT / "_redirects").read_text(encoding="utf-8-sig")
if "https://lse6.org/" not in index or "LSEØ_ARCHIVO" not in index:
    errors.append("Missing visible LSE6.ORG link")

for slug, video_id in TRACKS:
    route_url = f"https://lse6.com/{slug}/"
    direct = f"/{slug}/ https://youtube.com/watch?v={video_id} 302"
    if direct not in redirects:
        errors.append(f"Missing direct YouTube redirect: {slug}")
    if f'href="/{slug}/"' not in index:
        errors.append(f"Missing homepage link: {slug}")
    if f"lse6.com/{slug}" not in index:
        errors.append(f"Missing visible short URL: {slug}")
    route = ROOT / slug / "index.html"
    if not route.exists():
        errors.append(f"Missing route file: {slug}")
        continue
    page = route.read_text(encoding="utf-8-sig")
    required = [route_url, video_id, "ABRIR EN LA APP DE YOUTUBE", "androidIntent", "youtube://watch?v=", "https://youtube.com/watch?v="]
    for token in required:
        if token not in page:
            errors.append(f"{slug}: missing {token}")
    for forbidden in ("https://youtu.be/", "https://www.youtube.com/watch", "youtube://www.youtube.com/watch", "intent://www.youtube.com/watch"):
        if forbidden in page:
            errors.append(f"{slug}: forbidden redirect target {forbidden}")
    thumb = ROOT / "lse6-assets" / "youtube-thumbnails" / f"{video_id}.jpg"
    if not thumb.exists() or thumb.stat().st_size < 10000:
        errors.append(f"Invalid thumbnail: {video_id}")

data = json.loads((ROOT / "music-links.json").read_text(encoding="utf-8-sig"))
if len(data.get("tracks", [])) != 7:
    errors.append("music-links.json does not contain 7 tracks")

root = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locations = {node.text for node in root.findall("s:url/s:loc", ns)}
for slug, _ in TRACKS:
    if f"https://lse6.com/{slug}/" not in locations:
        errors.append(f"Sitemap missing {slug}")
if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("VALIDATION PASSED")
print("routes=7 thumbnails=7 sitemap=7 org_link=1")
