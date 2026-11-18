"""Open the wallpaper in a headless browser and check it works everywhere.

For phone, tablet and desktop sizes, in every language, with breathing on
and off, it fails if the page throws an error, makes a network request, or
draws the word wider than the screen.

    pip install playwright && playwright install chromium
    python3 scripts/smoke-test.py
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = next(ROOT.glob("Animated-*-Live-Wallpaper.html"))
KEY = "wallpaper_weekdays_v1" if "Weekdays" in PAGE.name else "wallpaper_months_v1"
SIZES = {"phone": (390, 844), "phone sideways": (844, 390), "iPad": (820, 1180), "desktop": (1600, 900)}
LANGS = ["en", "fr", "de", "es", "ja", "fa", "he"]

# Width the word's ink actually covers, read back from the canvas pixels
INK_WIDTH = """() => {
  const c = document.getElementById('canvas'), x = c.getContext('2d');
  const { width: w, height: h } = c, d = x.getImageData(0, 0, w, h).data;
  const bg = [d[0], d[1], d[2]];
  let left = w, right = -1;
  for (let y = 0; y < h; y += 2) for (let i = 0; i < w; i++) {
    const p = (y * w + i) * 4;
    if (Math.abs(d[p] - bg[0]) + Math.abs(d[p + 1] - bg[1]) + Math.abs(d[p + 2] - bg[2]) > 60) {
      if (i < left) left = i; if (i > right) right = i;
    }
  }
  return { left, right, width: w };
}"""


async def main():
    failures = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for size, (w, h) in SIZES.items():
            for lang in LANGS:
                for animated in (False, True):
                    ctx = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
                    page = await ctx.new_page()
                    problems = []
                    page.on("pageerror", lambda e: problems.append(f"error: {e}"))
                    page.on("request", lambda r: problems.append(f"request: {r.url}")
                            if not r.url.startswith(("file:", "data:")) else None)
                    await page.goto(PAGE.as_uri())
                    state = {"currentLang": lang, "animated": animated}
                    await page.evaluate(f"localStorage.setItem('{KEY}', JSON.stringify({json.dumps(state)}))")
                    await page.reload()
                    await page.wait_for_timeout(1500)
                    ink = await page.evaluate(INK_WIDTH)
                    if ink["right"] < 0:
                        problems.append("nothing drawn")
                    elif ink["left"] <= 1 or ink["right"] >= ink["width"] - 2:
                        problems.append(f"word touches the edge ({ink['left']}-{ink['right']} of {ink['width']})")
                    label = f"{size:15} {lang} {'breathing' if animated else 'still'}"
                    print(("FAIL " if problems else "ok   ") + label, *problems)
                    failures += [label] if problems else []
                    await ctx.close()
        await browser.close()
    if failures:
        sys.exit(f"\n{len(failures)} failed")
    print("\nAll good")


if __name__ == "__main__":
    asyncio.run(main())
