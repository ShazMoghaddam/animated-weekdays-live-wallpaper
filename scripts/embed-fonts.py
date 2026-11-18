"""Build the wallpaper's fonts into the HTML file itself.

Each font is cut down to the characters the page actually uses, so the file
works offline and makes no requests to Google Fonts. Run it again after
changing any text in the wallpaper (a new language, a new label).

    npm install --prefix /tmp/fonts @fontsource-variable/inter @fontsource/poppins \
        @fontsource/montserrat @fontsource/rubik-mono-one @fontsource/monoton \
        @fontsource/reem-kufi @fontsource/noto-sans-hebrew @fontsource/noto-sans-jp
    pip install fonttools brotli
    python3 scripts/embed-fonts.py /tmp/fonts/node_modules

The fonts are all under the SIL Open Font License, which allows embedding.
"""
import base64
import glob
import io
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
HTML = next(ROOT.glob("Animated-*-Live-Wallpaper.html"))
START, END = "/* fonts:start */", "/* fonts:end */"

# Which characters each kind of font is for: Latin fonts take Latin, script
# fonts take only their own script (plus spaces and joiners), so the Japanese
# slices that merely repeat ASCII are left out.
LATIN = lambda c: c < 0x0250 or 0x2000 <= c < 0x2070
PERSIAN = lambda c: 0x0600 <= c < 0x0700 or c in (0x20, 0x200C, 0x200D)
HEBREW = lambda c: 0x0590 <= c < 0x0600 or c == 0x20
CJK = lambda c: 0x3000 <= c < 0xA000

# family, CSS weight, files inside node_modules, characters it covers
FONTS = [
    ("Inter", "100 900", "@fontsource-variable/inter/files/inter-latin-wght-normal.woff2", LATIN),
    ("Inter", "100 900", "@fontsource-variable/inter/files/inter-latin-ext-wght-normal.woff2", LATIN),
    ("Poppins", "900", "@fontsource/poppins/files/poppins-latin-900-normal.woff2", LATIN),
    ("Montserrat", "900", "@fontsource/montserrat/files/montserrat-latin-900-normal.woff2", LATIN),
    ("Rubik Mono One", "400", "@fontsource/rubik-mono-one/files/rubik-mono-one-latin-400-normal.woff2", LATIN),
    ("Monoton", "400", "@fontsource/monoton/files/monoton-latin-400-normal.woff2", LATIN),
    ("Reem Kufi", "700", "@fontsource/reem-kufi/files/reem-kufi-arabic-700-normal.woff2", PERSIAN),
    ("Noto Sans Hebrew", "900", "@fontsource/noto-sans-hebrew/files/noto-sans-hebrew-hebrew-900-normal.woff2", HEBREW),
    # Japanese comes in many numbered slices; only the ones holding our characters are kept
    ("Noto Sans JP", "900", "@fontsource/noto-sans-jp/files/noto-sans-jp-[0-9]*-900-normal.woff2", CJK),
]


def used_characters(html: str) -> set[int]:
    """Every character on the page, plus printable ASCII for safety."""
    text = re.sub(re.escape(START) + ".*?" + re.escape(END), "", html, flags=re.S)
    chars = {ord(c) for c in text if ord(c) > 0x20}
    chars |= set(range(0x20, 0x7F))
    chars |= {0x200C, 0x200D}  # zero-width joiners used in Persian
    return chars


def unicode_range(cps: list[int]) -> str:
    """Compact CSS unicode-range, e.g. U+20-7E,U+E9."""
    out, cps = [], sorted(cps)
    i = 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        out.append(f"U+{cps[i]:X}" if i == j else f"U+{cps[i]:X}-{cps[j]:X}")
        i = j + 1
    return ",".join(out)


def cut(path: str, wanted: set[int]):
    font = TTFont(path)
    keep = sorted(wanted & set(font.getBestCmap()))
    if not keep:
        return None, []
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]  # keep Persian joining, kerning and the rest
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=keep)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return buf.getvalue(), keep


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    modules = Path(sys.argv[1])
    html = HTML.read_text(encoding="utf-8")
    wanted = used_characters(html)

    faces, total = [], 0
    for family, weight, pattern, scope in FONTS:
        files = sorted(glob.glob(str(modules / pattern)))
        if not files:
            sys.exit(f"Missing {pattern}: install the packages listed at the top of this script.")
        for f in files:
            data, keep = cut(f, {c for c in wanted if scope(c)})
            if not data:
                continue
            total += len(data)
            b64 = base64.b64encode(data).decode()
            faces.append(
                f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
                f"font-display:block;unicode-range:{unicode_range(keep)};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
            )

    block = START + "\n" + "\n".join(faces) + "\n" + END
    html = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, html, flags=re.S)
    HTML.write_text(html, encoding="utf-8")
    print(f"Embedded {len(faces)} font files, {total / 1024:.0f} KB, into {HTML.name}")


if __name__ == "__main__":
    main()
