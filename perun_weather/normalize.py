from __future__ import annotations

ALERT_THRESHOLDS = {
    "thunderstorm_codes": {95, 96, 99},
    "wind_gust_kmh": 60.0,
    "heavy_rain_mm": 10.0,
    "extreme_heat_c": 35.0,
    "extreme_cold_c": -15.0,
}


def _nearest_time_index(times: list[str], target_iso: str | None) -> int | None:
    """Map an arbitrary ISO timestamp (e.g. from a CAP feed) onto the
    closest index in the hourly `times` array, so official alerts can be
    plotted on the same Gantt chart axis as local threshold-based alerts.
    Returns None if times is empty or target_iso cannot be parsed.
    """
    if not times or not target_iso:
        return None
    from datetime import datetime
    try:
        target = datetime.fromisoformat(target_iso)
    except ValueError:
        return None
    best_idx, best_diff = None, None
    for i, t in enumerate(times):
        try:
            candidate = datetime.fromisoformat(t)
        except ValueError:
            continue
        c = candidate.replace(tzinfo=target.tzinfo) if candidate.tzinfo is None else candidate
        diff = abs(c.timestamp() - target.timestamp())
        if best_diff is None or diff < best_diff:
            best_idx, best_diff = i, diff
    return best_idx


def _merge_official_alerts(times: list[str], official_alerts: list[dict] | None) -> list[dict]:
    """Convert official (MeteoAlarm/WMO SWIC) alerts into the same shape
    _build_alerts() produces: {"level", "icon", "title", "start", "end"},
    where start/end are entries from the `times` array (ISO strings) -
    exactly what the alerts Gantt chart in chart.html already consumes.
    """
    if not official_alerts or not times:
        return []
    merged = []
    for a in official_alerts:
        start_idx = _nearest_time_index(times, a.get("start_iso"))
        end_idx = _nearest_time_index(times, a.get("end_iso")) if a.get("end_iso") else None
        if start_idx is None:
            continue
        if end_idx is None:
            # No official end time (e.g. MeteoAlarm legacy feed) - show a
            # short marker instead of a full bar, matching how _build_alerts()
            # pads local alerts (start + a fixed lookahead window).
            end_idx = min(start_idx + 6, len(times) - 1)
        merged.append({
            "level": a["level"],
            "icon": a["icon"],
            "title": f"{a['title']} ({a['source']})",
            "event": a.get("event") or a["title"],
            "issuer": a.get("issuer") or a["source"],
            "start": times[start_idx],
            "end": times[end_idx],
            "source": a["source"],
        })
    return merged


def _get(source: dict, key: str) -> list:
    return source.get(key, []) or []


def _build_alerts(w: dict, units: str) -> list[dict]:
    times = _get(w, "time")
    codes = _get(w, "weather_code")
    gusts = _get(w, "wind_gusts_10m")
    precip = _get(w, "precipitation")
    temps = _get(w, "temperature_2m")

    alerts: list[dict] = []

    def first_index(predicate, arr):
        for i, v in enumerate(arr):
            if v is not None and predicate(v):
                return i
        return None

    idx = first_index(lambda c: c in ALERT_THRESHOLDS["thunderstorm_codes"], codes)
    if idx is not None and idx < len(times):
        alerts.append({
            "level": "red", "icon": "⛈", "title": "Thunderstorm risk", "issuer": "Local estimate",
            "start": times[idx], "end": times[min(idx + 6, len(times) - 1)] if times else "",
            "source": "Local estimate",
        })

    gust_limit = ALERT_THRESHOLDS["wind_gust_kmh"]
    if units == "imperial":
        gust_limit = gust_limit / 1.60934
    elif units == "ms":
        gust_limit = gust_limit / 3.6
    elif units == "knots":
        gust_limit = gust_limit / 1.852
    idx = first_index(lambda v: v >= gust_limit, gusts)
    if idx is not None and idx < len(times):
        alerts.append({
            "level": "orange", "icon": "💨", "title": "Strong wind gusts", "issuer": "Local estimate",
            "start": times[idx], "end": times[min(idx + 12, len(times) - 1)] if times else "",
            "source": "Local estimate",
        })

    rain_limit = ALERT_THRESHOLDS["heavy_rain_mm"]
    if units == "imperial":
        rain_limit = rain_limit / 25.4
    idx = first_index(lambda v: v >= rain_limit, precip)
    if idx is not None and idx < len(times):
        alerts.append({
            "level": "orange", "icon": "🌧", "title": "Heavy precipitation", "issuer": "Local estimate",
            "start": times[idx], "end": times[min(idx + 6, len(times) - 1)] if times else "",
            "source": "Local estimate",
        })

    heat_limit = ALERT_THRESHOLDS["extreme_heat_c"]
    cold_limit = ALERT_THRESHOLDS["extreme_cold_c"]
    if units == "imperial":
        heat_limit = heat_limit * 9 / 5 + 32
        cold_limit = cold_limit * 9 / 5 + 32
    idx = first_index(lambda v: v >= heat_limit, temps)
    if idx is not None and idx < len(times):
        alerts.append({
            "level": "yellow", "icon": "🌡", "title": "Extreme heat", "issuer": "Local estimate",
            "start": times[idx], "end": times[min(idx + 24, len(times) - 1)] if times else "",
            "source": "Local estimate",
        })
    idx = first_index(lambda v: v <= cold_limit, temps)
    if idx is not None and idx < len(times):
        alerts.append({
            "level": "yellow", "icon": "❄", "title": "Extreme cold", "issuer": "Local estimate",
            "start": times[idx], "end": times[min(idx + 24, len(times) - 1)] if times else "",
            "source": "Local estimate",
        })

    return alerts


def prepare(location, weather, air, units: str = "metric", official_alerts: list[dict] | None = None) -> dict:
    """Normalize API data for the frontend."""
    w = weather.get("hourly", {})
    a = air.get("hourly", {}) if air else {}
    d = weather.get("daily", {})

    local_alerts = _build_alerts(w, units)
    remote_alerts = _merge_official_alerts(_get(w, "time"), official_alerts)
    alerts = remote_alerts + local_alerts

    return {
        "name": location.name,
        "latitude": location.latitude,
        "longitude": location.longitude,
        # Seconds east of UTC for this location's local time, as returned by
        # Open-Meteo. The front end uses this to compute "now" correctly in
        # the displayed location's own local time, instead of the browser's
        # local time, so the current-time marker lands on the visible axis
        # for every location regardless of timezone offset.
        "utc_offset_seconds": weather.get("utc_offset_seconds", 0),
        "uv_sources": weather.get("uv_sources", []),
        "alerts": alerts,
        "daily": {
            "time": _get(d, "time"),
            "sunrise": _get(d, "sunrise"),
            "sunset": _get(d, "sunset"),
            },
        "hourly": {
            "time": _get(w, "time"),
            "temperature_2m": _get(w, "temperature_2m"),
            "apparent_temperature": _get(w, "apparent_temperature"),
            "uv_index": _get(w, "uv_index"),
            "precipitation": _get(w, "precipitation"),
            "rain": _get(w, "rain"),
            "showers": _get(w, "showers"),
            "snowfall": _get(w, "snowfall"),
            "cloud_cover": _get(w, "cloud_cover"),
            "cloud_cover_low": _get(w, "cloud_cover_low"),
            "cloud_cover_mid": _get(w, "cloud_cover_mid"),
            "cloud_cover_high": _get(w, "cloud_cover_high"),
            "wind_speed_10m": _get(w, "wind_speed_10m"),
            "wind_direction_10m": _get(w, "wind_direction_10m"),
            "wind_gusts_10m": _get(w, "wind_gusts_10m"),
            "weather_code": _get(w, "weather_code"),
            "pressure_msl": _get(w, "pressure_msl"),
        },
        "air": {
            "hourly": {
                "european_aqi": _get(a, "european_aqi"),
                "us_aqi": _get(a, "us_aqi"),
                "pm2_5": _get(a, "pm2_5"),
                "pm10": _get(a, "pm10"),
                "ozone": _get(a, "ozone"),
                "nitrogen_dioxide": _get(a, "nitrogen_dioxide"),
                "sulphur_dioxide": _get(a, "sulphur_dioxide"),
                "carbon_monoxide": _get(a, "carbon_monoxide"),
                "ammonia": _get(a, "ammonia"),
                "dust": _get(a, "dust"),
                "aerosol_optical_depth": _get(a, "aerosol_optical_depth"),
                "alder_pollen": _get(a, "alder_pollen"),
                "birch_pollen": _get(a, "birch_pollen"),
                "grass_pollen": _get(a, "grass_pollen"),
                "mugwort_pollen": _get(a, "mugwort_pollen"),
                "olive_pollen": _get(a, "olive_pollen"),
                "ragweed_pollen": _get(a, "ragweed_pollen"),
            }
        } if air else {"hourly": {}},
    }
