# Perun Weather 5.2.0

Release date: 2026-10-24

## Added

- LibreWXR as a weather map source: radar with a nowcast up to 60 minutes
  ahead, NOAA GMGSI satellite imagery and optional overlays for lightning,
  precipitation motion arrows, storm cells and alerts, with a legend for each
  layer.
- Beaufort scale colours and names for wind speed and gusts, and a text
  description of cloud cover in "Weather at a glance".
- Precipitation nowcast for the next hour (LibreWXR radar or the Open-Meteo
  15-minute model). The Precipitation tile and a new Nowcast card appear only
  when precipitation is expected.
- "Storms nearby" card with a mini radar of nearby storm cells, their movement
  and recent lightning.
- Bilingual help, footer credits and licence notes for LibreWXR.

## Changed

- LibreWXR is the default map source for new settings.
  Existing saved source selections are preserved.
- Application version updated to 5.2.0.
- In-app history shows 5.2.0 and 5.1.0 outside the older-version
  collapsible section.
- README updated with the new map source, attribution and release-note links.

## Known limitations

- Rainfall amounts derived from radar reflectivity are rough estimates, not
  measurements. The Open-Meteo source provides modelled amounts.
- The nowcast runs only while weather maps are enabled with LibreWXR as the
  source.
- Storm movement and arrival times are linear estimates and depend on the
  motion data provided by the server.
- Maps and forecasts do not replace official warnings.

## Downloads

| Platform | File |
|---|---|
| Fedora 44 (RPM) | [perun-weather-5.2.0-1.fc44.noarch.rpm](https://github.com/tothpsk/perun-weather/releases/download/v5.2.0/perun-weather-5.2.0-1.fc44.noarch.rpm) |
| Debian 13 (DEB) | [perun-weather_5.2.0-1_all.deb](https://github.com/tothpsk/perun-weather/releases/download/v5.2.0/perun-weather_5.2.0-1_all.deb) |
| Windows | [PerunWeather-5.2.0-windows.zip](https://github.com/tothpsk/perun-weather/releases/download/v5.2.0/PerunWeather-5.2.0-windows.zip) |

## Installation

### Fedora

```bash
sudo dnf install ./perun-weather-5.2.0-1.fc44.noarch.rpm
```

### Debian

```bash
sudo apt install ./perun-weather_5.2.0-1_all.deb
```

Use `apt install` with the `./` prefix so that dependencies are installed automatically.

### Windows

Extract the whole ZIP folder and run `PerunWeather.exe`.
Keep all files in the folder together.
No separate installation of Python or Qt is needed.

### Linux requirements

Python 3.12 or newer, GTK 4, libadwaita and WebKitGTK 6.
Dependencies are installed automatically with the package.

---

**Full changelog:** [v5.1.0...v5.2.0](https://github.com/tothpsk/perun-weather/compare/v5.1.0...v5.2.0)
