"""Render the README images, banner and social preview from the real wallpaper.

    pip install playwright && playwright install chromium
    python3 docs/capture.py

Writes docs/wallpaper.png, docs/settings.png, docs/languages.png,
docs/banner.png and docs/social-preview.png. The clock is pinned to a
Wednesday morning and the breathing is frozen on one frame, so the images
are the same every time.
"""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "Animated-Weekdays-Live-Wallpaper.html").as_uri()
OUT = ROOT / "docs"
KEY = "wallpaper_weekdays_v1"
WEDNESDAY = datetime(2026, 11, 18, 9, 41, 0, tzinfo=timezone.utc)
ACCENT = "#D4FF3A"


async def open_wallpaper(browser, width, height, state=None, frame=None, scale=1):
    ctx = await browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=scale,
        timezone_id="Europe/London",
        locale="en-GB",
    )
    page = await ctx.new_page()
    await page.clock.install(time=WEDNESDAY)
    await page.goto(PAGE)
    await page.evaluate(f"localStorage.setItem('{KEY}', JSON.stringify({json.dumps(state or {})}))")
    await page.reload()
    await page.clock.run_for(1500)
    if frame is not None:  # freeze the breathing on one moment
        await page.evaluate(f"animated = true; animTime = {frame}; paused = true; dirty = true;")
        await page.clock.run_for(200)
    return ctx, page


# Text laid over the wallpaper for the banner and social preview
CARD = """({ kicker, title, line, pad, size }) => {
  const box = document.createElement('div');
  box.innerHTML = `
    <p style="margin:0 0 10px;font:700 ${size * .5}px/1 Inter;letter-spacing:.18em;text-transform:uppercase;color:%s">${kicker}</p>
    <p style="margin:0;font:900 ${size}px/1 Inter;letter-spacing:-.03em;color:#fff">${title}</p>`;
  Object.assign(box.style, { position: 'fixed', left: pad + 'px', top: pad + 'px', zIndex: 50 });
  const foot = document.createElement('p');
  foot.textContent = line;
  Object.assign(foot.style, { position: 'fixed', left: pad + 'px', bottom: pad + 'px', margin: 0, zIndex: 50,
    font: `500 ${size * .55}px/1 Inter`, letterSpacing: '.02em', color: 'rgba(255,255,255,.62)' });
  document.body.append(box, foot);
  for (const id of ['settingsBtn', 'fullscreenBtn', 'datetime']) document.getElementById(id).style.display = 'none';
}""" % ACCENT


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))

        # The wallpaper, as it looks on a desktop
        ctx, page = await open_wallpaper(browser, 1600, 900, frame=10.5)
        await page.screenshot(path=OUT / "wallpaper.png")
        await ctx.close()

        # Settings open, with a custom colour and font
        ctx, page = await open_wallpaper(browser, 1280, 720, {"BG": "#101820", "FG": "#d4ff3a", "fontName": "Poppins"})
        await page.click("#settingsBtn")
        await page.clock.run_for(600)
        await page.screenshot(path=OUT / "settings.png")
        await ctx.close()

        # Persian, Japanese and Hebrew side by side
        shots = []
        for lang in ("fa", "ja", "he"):
            ctx, page = await open_wallpaper(browser, 800, 450, {"currentLang": lang}, frame=2.1)
            await page.evaluate("for (const id of ['settingsBtn','fullscreenBtn','datetime']) document.getElementById(id).style.display='none'")
            shots.append(await page.screenshot())
            await ctx.close()
        ctx = await browser.new_context(viewport={"width": 1600, "height": 300})
        page = await ctx.new_page()
        imgs = "".join(
            f'<img src="data:image/png;base64,{__import__("base64").b64encode(s).decode()}" '
            f'style="width:528px;height:297px;border-radius:10px">' for s in shots)
        await page.set_content(f'<body style="margin:0;background:#0B0B0C;display:flex;gap:8px;padding:0 0 0 0">{imgs}</body>')
        await page.screenshot(path=OUT / "languages.png", clip={"x": 0, "y": 0, "width": 1600, "height": 297})
        await ctx.close()

        # README banner and social preview: the wallpaper itself, with a title
        for name, (w, h), size, pad in (("banner", (1280, 400), 34, 40), ("social-preview", (1280, 640), 46, 56)):
            ctx, page = await open_wallpaper(browser, w, h, frame=21.0)
            await page.evaluate(CARD, {
                "kicker": "Live wallpaper · Shaz Moghaddam",
                "title": "Animated Weekdays",
                "line": "Seven languages · Mac, Windows and any screen · Free and open source",
                "pad": pad, "size": size,
            })
            await page.clock.run_for(200)
            await page.screenshot(path=OUT / f"{name}.png")
            await ctx.close()

        await browser.close()
        print("Wrote", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))


if __name__ == "__main__":
    asyncio.run(main())
