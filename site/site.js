// Animated Weekdays site: scales the live preview and copies the wallpaper link.

// The preview renders the wallpaper at 1600 x 900 and scales it to the frame,
// so it looks like a real desktop at any width.
const screen = document.querySelector('.preview__screen');
const frame = document.querySelector('.preview__frame');
if (screen && frame) {
  const fit = () => {
    frame.style.transform = `scale(${screen.clientWidth / 1600})`;
  };
  fit();
  new ResizeObserver(fit).observe(screen);
}

// "Copy link" buttons: copy the text of the element they point at.
document.querySelectorAll('[data-copy]').forEach((btn) => {
  const source = document.getElementById(btn.dataset.copy);
  if (!source || !navigator.clipboard) return;
  const label = btn.textContent;
  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(source.textContent.trim());
      btn.textContent = 'Copied';
    } catch (e) {
      btn.textContent = 'Press Cmd or Ctrl + C';
      getSelection().selectAllChildren(source);
    }
    setTimeout(() => { btn.textContent = label; }, 2000);
  });
});
