from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lse6-assets" / "youtube-thumbnails"
OUT.mkdir(parents=True, exist_ok=True)
VIDEOS = [
    "pdcQBdp-xhg", "Re5mvPwaoG4", "jdpOHKF_dXQ",
    "9wk6CUoYwFo", "M0N5CoOKyEY", "v40hHkTtdig", "Fafu9xC-npY",
]

def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "LSE6-Thumbnail-Sync/1.0"})
    with urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
        if response.status != 200 or not content_type.startswith("image/"):
            raise ValueError(f"Invalid thumbnail response: {response.status} {content_type}")
        return data
changed = 0
for video_id in VIDEOS:
    target = OUT / f"{video_id}.jpg"
    data = None
    for quality in ("maxresdefault", "hqdefault"):
        try:
            data = download(f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg")
            break
        except (HTTPError, URLError, ValueError):
            continue
    if data is None:
        raise RuntimeError(f"Could not download thumbnail for {video_id}")
    old = target.read_bytes() if target.exists() else b""
    if hashlib.sha256(old).digest() != hashlib.sha256(data).digest():
        target.write_bytes(data)
        changed += 1
        print(f"UPDATED {video_id}")
    else:
        print(f"UNCHANGED {video_id}")

print(f"SYNC COMPLETE changed={changed} total={len(VIDEOS)}")
