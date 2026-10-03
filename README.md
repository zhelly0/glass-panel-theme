# Glass Panel

A minimal KDE Plasma 6 desktop theme: Breeze, with frosted-glass panels,
popups and tooltips. It is designed to match the glass look of the
[SysDash](https://github.com/zhelly0/sysdash) and
[DeskClock](https://github.com/zhelly0/deskclock) widgets.

![Glass Panel: KRunner, the taskbar and the SysDash/DeskClock widgets](docs/screenshot.png)

Glass versions of these graphics replace Breeze's; everything else falls back
to Breeze:

| Graphic | Used for |
|---|---|
| `widgets/panel-background` | Panels (taskbar, top bar) |
| `dialogs/background` | Popups: application launcher, KRunner, calendar, system tray, notifications, OSDs |
| `widgets/tooltip` | Hover tooltips |
| `widgets/background`, `widgets/translucentbackground` | Widget backgrounds |
| `widgets/lineedit` | Text fields, e.g. the KRunner and launcher search boxes |
| `widgets/viewitem` | List highlights (hover / selected) in KRunner, the launcher, the tray |
| `widgets/tasks` | Taskbar buttons: normal, hover, focused, needs attention, minimized, progress |
| `widgets/plasmoidheading` | Popup headers and footers (a thin separator instead of a shaded bar) |
| `widgets/frame`, `widgets/tabbar`, `widgets/menubaritem` | Frames, active tabs, menu bar items |

The control graphics are derived from Breeze's own files: frame names and
padding hints are copied verbatim, so sizes and alignment match Breeze and only
the drawing changes.

Surfaces are rounded (12 px) frames with a thin outline and a tint of your
colour scheme's background; controls use 6 px corners and your accent colour for
highlights. Everything follows your colour scheme. KWin blurs what is
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
