# Glass Panel

A minimal KDE Plasma 6 desktop theme: Breeze, with frosted-glass panels,
popups and tooltips. It is designed to match the glass look of the
[SysDash](https://github.com/zhelly0/sysdash) and
[DeskClock](https://github.com/zhelly0/deskclock) widgets.

Only three graphics are replaced; everything else falls back to Breeze:

| Graphic | Used for |
|---|---|
| `widgets/panel-background` | Panels (taskbar, top bar) |
| `dialogs/background` | Popups: application launcher, KRunner, calendar, system tray, notifications, OSDs |
| `widgets/tooltip` | Hover tooltips |

Each is a rounded (12 px) frame with a thin outline and a tint of your colour
scheme's background, so it follows light/dark schemes. KWin blurs what is
behind it. The tint is strong enough to keep light text readable even when a
white window is behind the glass (KWin 6 no longer has the background-contrast
effect that older themes relied on for this).

## Install

The folder name must match the theme id:

```sh
git clone https://github.com/zhelly0/glass-panel-theme ~/.local/share/plasma/desktoptheme/zhelly0-glass
plasma-apply-desktoptheme zhelly0-glass
```

Programs that were already running (e.g. KRunner) pick it up after a restart:
`systemctl --user restart plasma-plasmashell plasma-krunner`.

Revert with `plasma-apply-desktoptheme default`.

## Tweaking

Edit the values at the top of `generate.py` (tint, outline, corner radius,
padding), then regenerate and re-apply:

```sh
python3 generate.py
plasma-apply-desktoptheme default && plasma-apply-desktoptheme zhelly0-glass
```

## Recommended companion settings

These aren't part of a Plasma theme, but complete the look:

- **Smooth blur without grain** (measured to match the widgets' glass):
  `kwriteconfig6 --file kwinrc --group Effect-blur --key BlurStrength 3`,
  `kwriteconfig6 --file kwinrc --group Effect-blur --key NoiseStrength 0`, then
  `qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.reconfigureEffect blur`
- **Translucent app menus** (Breeze): System Settings → Colors & Themes →
  Application Style → Breeze → Transparency, about halfway
  (`breezerc`: `[Style] MenuOpacity=50`)

## License

GPL-3.0, see [LICENSE](LICENSE).
