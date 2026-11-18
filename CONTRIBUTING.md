# Contributing to Animated Weekdays

Thanks for helping. Bug reports, new languages and new fonts are all welcome.

## Setup

The wallpaper is one page, `Animated-Weekdays-Live-Wallpaper.html`. Open it in any desktop browser and reload after each change; there's no build step for the code.

To see the site as GitHub Pages serves it, with the wallpaper at `/wallpaper/`:

```sh
sh scripts/build-site.sh serve
```

The site's own files are in `site/`.

## Adding a language

1. Add the seven day names to `DAYS_ALL`, keyed `0` (Sunday) to `6` (Saturday), and a chip to the Language row in the panel.
2. If the language has its own script, add it to `SCRIPT_LANGS`, give it a font in `LANG_FONT`, and add that font to `scripts/embed-fonts.py`. Right-to-left languages also go in `isRTL()`.
3. If its letters join up (like Persian), make `breathingUnits()` treat each word as one unit, so the letters stay joined while breathing.
4. Rebuild the fonts (below) and run the smoke test.

## Adding a display font

Add a chip to the Font row and the name to `FONTS`, then add the font to `scripts/embed-fonts.py` and rebuild. Use a font under the SIL Open Font License.

## Rebuilding the fonts

The fonts are built into the page, cut down to the characters it uses. After changing any text, rebuild them:

```sh
npm install --prefix /tmp/fonts @fontsource-variable/inter @fontsource/poppins @fontsource/montserrat \
  @fontsource/rubik-mono-one @fontsource/monoton @fontsource/reem-kufi @fontsource/noto-sans-hebrew @fontsource/noto-sans-jp
pip install fonttools brotli
python3 scripts/embed-fonts.py /tmp/fonts/node_modules
```

## Checking your change

```sh
pip install playwright && playwright install chromium
python3 scripts/smoke-test.py
```

This opens the wallpaper at phone, iPad and desktop sizes in every language, with breathing on and off, and fails on any error, any network request, or a word that doesn't fit. The same check runs on every pull request.

## Guidelines

- No external requests: the page must keep working offline as a single file.
- Keep the `wallpaper_weekdays_v1` storage key, so saved settings survive updates.
- If a change is visible, refresh the README images with `python3 docs/capture.py`.
- Add a line to `CHANGELOG.md` under a new version heading.
