# Perun Weather 5.1.0

Release date: 2026-10-19

## Added

- Weather maps with WeatherAPI.com layer selection and an alternative
  Vaisala Xweather radar source.
- Map animation controls and a time slider for selecting individual frames.
- Bilingual map help covering source selection, navigation, Xweather
  credentials and map limitations.
- Map provider credits in the application footer and help.
- Leaflet information in the help and README.

## Changed

- WeatherAPI.com is the default map source for new settings.
  Existing saved source selections are preserved.
- Application version updated to 5.1.0.
- In-app history shows 5.1.0 and 5.0.0 outside the older-version
  collapsible section.
- README updated with map setup, attribution and release-note links.

## Fixed

- Windows: locally loaded application content is allowed to access
  remote map resources.

## Known limitations

- WeatherAPI.com layer legends are currently hidden.
- Map availability depends on the provider, connectivity and applicable
  account limits. Missing frames do not indicate an absence of precipitation.
- This release does not claim a fix for the outstanding gauge tick rendering
  or the sun/moon time-zone edge cases.
- Maps and forecasts do not replace official warnings.
