# Changelog

## 1.0.0 (2026-11-18)

First release as an open-source web wallpaper, with its own site.

### The wallpaper
- Today's day of the week, full screen, in big heavy letters. It turns over at midnight by itself, so it stays right when left running for days.
- Breathing motion: each letter stretches and settles on its own slow rhythm. Tap the word to pause or resume it.
- Seven languages: English, French, German, Spanish, Japanese, Persian and Hebrew, each in a typeface made for its script, with right-to-left text handled properly.
- Any background and text colour, five display fonts (Inter, Poppins, Montserrat, Rubik Mono and Monoton) and a screen dimmer.
- A live clock and date in the top right, and a full screen button.

### Fixed
- **A preview no longer sticks.** Tapping another day used to be saved, so the wallpaper kept showing that day from then on. Previews now last until you reload, and it always opens on today.
- **Midnight.** The day was only worked out when the page opened, so a wallpaper left running showed yesterday. It now changes at midnight.
- **Long words on narrow screens.** Words like WEDNESDAY and MITTWOCH ran off both edges on phones and on an upright iPad. The word now shrinks to fit the width, with extra room while it breathes.
- **Persian while breathing.** Each letter was animated on its own, which broke the joins in Persian script. Persian words now breathe as a whole and stay joined, and Hebrew keeps its marks with their letters.
- **Off-centre breathing.** With breathing on, the word sat about half a letter right of centre. Each letter now breathes around its own middle.
- **Fonts.** They loaded from Google Fonts, so a first open without internet showed a fallback font, and the first frame could use the wrong font even online. The fonts are now built into the file and the word redraws as soon as its font is ready.
- **iPhone.** The full screen button threw an error on iPhone, which has no full screen for web pages. It's hidden there now, and works on iPad Safari.
- **Settings are easier to read.** Bigger, clearer text in the panel, a visible focus ring for keyboard users, and the closed panel is skipped by the Tab key and screen readers.
- **iPad and notched screens.** The panel fits the visible screen in Safari, and the buttons and clock keep clear of the notch and home bar.
- Tapping the word while Settings is open now just closes Settings, instead of also pausing the breathing.
- A damaged or old saved setting can no longer break the page.

### Site and repo
- A GitHub Pages site with a live preview, step-by-step setup for Mac (Plash) and Windows (Lively Wallpaper), and the wallpaper at `/wallpaper/`.
- A Check workflow that opens the wallpaper at phone, iPad and desktop sizes in every language, with breathing on and off.
- README with a banner and screenshots, a social preview image, a contributing guide, a security policy, Dependabot for the workflows, and scripts to rebuild the fonts and images.
- The Android app in `android/` is unchanged.
