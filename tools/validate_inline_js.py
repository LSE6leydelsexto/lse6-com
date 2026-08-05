from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html"] + [
    ROOT / slug / "index.html" for slug in (
        "ley-del-sexto", "zona-gris", "clones-y-fantasmas",
        "nada-me-borra", "libre-prisionero", "lse6", "error-404",
    )
]
errors = []
with tempfile.TemporaryDirectory() as temp_dir:
    temp = Path(temp_dir)
    count = 0
    for page in PAGES:
        html = page.read_text(encoding="utf-8-sig")
        blocks = re.findall(r"<script([^>]*)>(.*?)</script>", html, re.I | re.S)
        for number, (attrs, script) in enumerate(blocks, 1):
            lowered = attrs.lower()
            if "src=" in lowered or "application/ld+json" in lowered:
                continue
            count += 1
            js_file = temp / f"{page.parent.name}-{number}.js"
            js_file.write_text(script, encoding="utf-8")
            result = subprocess.run(["node", "--check", str(js_file)], capture_output=True, text=True)
            if result.returncode:
                errors.append(f"{page.relative_to(ROOT)} script {number}: {result.stderr.strip()}")

if errors:
    print("JAVASCRIPT VALIDATION FAILED")
    for error in errors:
        print(error)
    raise SystemExit(1)

print(f"JAVASCRIPT VALIDATION PASSED scripts={count}")
