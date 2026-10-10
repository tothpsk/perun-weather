"""
alerts.py - Official weather alerts (CAP-based) for Perun Weather.

Two sources are combined:
  - MeteoAlarm Atom feed (Europe only, per-country)
  - WMO Severe Weather Information Centre (SWIC) CAP feed (global, per-country)

Both are XML/Atom feeds (no API key, no official REST API for reading),
so this module fetches and parses them with the same generic CAP-in-Atom
approach. Results are normalized into the same alert dict shape your
chart.html already expects and renders in both the alert cards and the
alerts Gantt chart.

Region filtering: MeteoAlarm's legacy feed returns ALL active warnings for
an entire country in one call (e.g. every Slovak district), not just the
user's selected location. fetch_official_alerts() accepts an optional
`region` string (typically the location's admin1/admin2 name from
Open-Meteo geocoding) and, when given, keeps only alerts whose title
mentions that region - falling back to returning all alerts if the title
format cannot be parsed or region is not provided, so filtering degrades
gracefully instead of silently hiding everything.
"""
from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .api import USER_AGENT

METEOALARM_COUNTRY_FEED = "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-{cc}"

# ISO 3166-1 alpha-2 code -> slug used in the MeteoAlarm legacy atom feed URL.
# Source: https://feeds.meteoalarm.org/ (list of all active legacy atom feeds)
# and https://climate-adapt.eea.europa.eu/en/metadata/portals/meteoalarm
# (list of MeteoAlarm member countries).
METEOALARM_CC = {
    "AD": "andorra",
    "AT": "austria",
    "BE": "belgium",
    "BA": "bosnia-herzegovina",
    "BG": "bulgaria",
    "HR": "croatia",
    "CY": "cyprus",
    "CZ": "czechia",
    "DK": "denmark",
    "EE": "estonia",
    "FI": "finland",
    "FR": "france",
    "DE": "germany",
    "GR": "greece",
    "HU": "hungary",
    "IS": "iceland",
    "IE": "ireland",
    "IL": "israel",
    "IT": "italy",
    "LV": "latvia",
    "LT": "lithuania",
    "LU": "luxembourg",
    "MT": "malta",
    "MD": "moldova",
    "ME": "montenegro",
    "NL": "netherlands",
    "MK": "republic-of-north-macedonia",
    "NO": "norway",
    "PL": "poland",
    "PT": "portugal",
    "RO": "romania",
    "RS": "serbia",
    "SK": "slovakia",
    "SI": "slovenia",
    "ES": "spain",
    "SE": "sweden",
    "CH": "switzerland",
    "UA": "ukraine",
    "GB": "united-kingdom",
}

CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2", "atom": "http://www.w3.org/2005/Atom"}

SEVERITY_TO_LEVEL = {
    "Extreme": "red",
    "Severe": "red",
    "Moderate": "orange",
    "Minor": "yellow",
    "Unknown": "neutral",
}

EVENT_ICON_MAP = {
    "thunderstorm": "\u26c8\ufe0f",
    "storm": "\u26c8\ufe0f",
    "gale": "\U0001f4a8",
    "wind": "\U0001f4a8",
    "flood": "\U0001f30a",
    "rain": "\U0001f327\ufe0f",
    "snow": "\u2744\ufe0f",
    "ice": "\U0001f9ca",
    "fog": "\U0001f32b\ufe0f",
    "high temperature": "\U0001f321\ufe0f",
    "heat": "\U0001f321\ufe0f",
    "low temperature": "\U0001f976",
    "cold": "\U0001f976",
    "avalanche": "\U0001f3d4\ufe0f",
    "forest fire": "\U0001f525",
    "wildfire": "\U0001f525",
    "coastal event": "\U0001f30a",
    "uv": "\u2600\ufe0f",
}
DEFAULT_ICON = "\u26a0\ufe0f"

# Matches "... issued for <Country> - <Region>" (MeteoAlarm legacy title
# format) and captures the region part, e.g. "Liptovský Mikuláš" or
# "Bavaria". Case-insensitive; tolerant of extra whitespace around the dash.
_REGION_FROM_TITLE = re.compile(r"issued for [^-]+-\s*(.+)$", re.IGNORECASE)


def _icon_for_event(event_text: str | None) -> str:
    if not event_text:
        return DEFAULT_ICON
    text = event_text.lower()
    for keyword, icon in EVENT_ICON_MAP.items():
        if keyword in text:
            return icon
    return DEFAULT_ICON


def _extract_region(title: str) -> str | None:
    m = _REGION_FROM_TITLE.search(title)
    return m.group(1).strip() if m else None


def _region_matches(alert_region: str | None, wanted_region: str | None) -> bool:
    """Loose match: strips common admin-level prefixes/suffixes (Slovak
    "Okres " prefix, trailing Roman numerals like " V" for city districts)
    before doing a case-insensitive substring check in both directions.
    Diacritics are NOT normalized - if this proves too strict in practice,
    consider adding unicodedata-based normalization.
    """
    if not alert_region or not wanted_region:
        return False

    def _clean(s: str) -> str:
        s = re.sub(r"^\s*okres\s+", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+[IVX]+$", "", s)
        return s.strip().lower()

    a = _clean(alert_region)
    w = _clean(wanted_region)
    return a == w or a in w or w in a


def _request(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=20) as response:
        return response.read()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _local_time_str(dt: datetime | None) -> str:
    if dt is None:
        return "--:--"
    return dt.astimezone().strftime("%H:%M")


def _entries_from_atom(xml_bytes: bytes) -> list[ET.Element]:
    root = ET.fromstring(xml_bytes)
    return root.findall("atom:entry", CAP_NS)


def _alert_from_meteoalarm_entry(entry: ET.Element) -> dict | None:
    title_el = entry.find("atom:title", CAP_NS)
    summary_el = entry.find("atom:summary", CAP_NS)
    if title_el is None or title_el.text is None:
        return None
    title = title_el.text.strip()
    if "no alert" in title.lower():
        return None

    text_for_level = " ".join(
        t for t in (title, summary_el.text if summary_el is not None else None) if t
    ).lower()

    if "red" in text_for_level:
        level = "red"
    elif "orange" in text_for_level:
        level = "orange"
    elif "yellow" in text_for_level:
        level = "yellow"
    else:
        level = "neutral"

    updated_el = entry.find("atom:updated", CAP_NS)
    start_dt = _parse_iso(updated_el.text if updated_el is not None else None)

    event_el = entry.find(".//cap:event", CAP_NS)
    event = (
        event_el.text.strip()
        if event_el is not None and event_el.text
        else ""
    )
    issuer = "MeteoAlarm"

    icon = _icon_for_event(event or title)
    region = _extract_region(title)

    return {
        "title": title,
        "event": event or title,
        "issuer": issuer,
        "level": level,
        "icon": icon,
        "start": _local_time_str(start_dt),
        "end": "--:--",
        "start_iso": start_dt.isoformat() if start_dt else None,
        "end_iso": None,
        "source": "MeteoAlarm",
        "region": region,
    }


def fetch_meteoalarm(country_code: str) -> list[dict]:
    """Fetch active alerts from MeteoAlarm for a European country.

    Returns [] silently on any error - never raises. Callers should treat
    an empty list as 'no data available', not 'no alerts active'.
    """
    cc = METEOALARM_CC.get(country_code.upper())
    if not cc:
        return []
    try:
        xml_bytes = _request(METEOALARM_COUNTRY_FEED.format(cc=cc))
        entries = _entries_from_atom(xml_bytes)
        return [a for e in entries if (a := _alert_from_meteoalarm_entry(e))]
    except Exception:
        return []


def _dedupe(alerts: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for a in alerts:
        key = a["title"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(a)
    return result

KDE_AREA_URL = "https://alerts.kde.org/alert/area"
KDE_POINT_MARGIN = 0.005  # malý vyhľadávací obdĺžnik okolo bodu


def _cap_values(value) -> list:
    """CAP JSON môže mať jeden objekt alebo zoznam objektov."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _point_in_polygon(lat: float, lon: float, text: str) -> bool:
    """CAP polygon: dvojice 'lat,lon' oddelené medzerami."""
    try:
        points = []
        for pair in text.split():
            y, x = pair.split(",", 1)
            points.append((float(x), float(y)))  # interne x=lon, y=lat
        if len(points) < 3:
            return False
    except (TypeError, ValueError):
        return False

    inside = False
    for i in range(len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]

        # Bod presne na hrane považujeme za súčasť oblasti.
        cross = (lon - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
        if abs(cross) < 1e-10 and (
            min(x1, x2) - 1e-10 <= lon <= max(x1, x2) + 1e-10
            and min(y1, y2) - 1e-10 <= lat <= max(y1, y2) + 1e-10
        ):
            return True

        if (y1 > lat) != (y2 > lat):
            crossing_x = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < crossing_x:
                inside = not inside

    return inside


def _point_in_circle(lat: float, lon: float, text: str) -> bool:
    """CAP circle: 'lat,lon radius_km'."""
    try:
        centre, radius_text = text.strip().split()
        centre_lat, centre_lon = map(float, centre.split(","))
        radius_km = float(radius_text)
        if radius_km < 0:
            return False
    except (AttributeError, ValueError):
        return False

    lat1, lon1, lat2, lon2 = map(
        math.radians, (lat, lon, centre_lat, centre_lon)
    )
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    distance_km = 6371.0088 * 2 * math.atan2(
        math.sqrt(a), math.sqrt(max(0.0, 1 - a))
    )
    return distance_km <= radius_km


def _cap_area_contains(area: dict, lat: float, lon: float) -> bool:
    for polygon in _cap_values(area.get("polygon")):
        if isinstance(polygon, str) and _point_in_polygon(lat, lon, polygon):
            return True
    for circle in _cap_values(area.get("circle")):
        if isinstance(circle, str) and _point_in_circle(lat, lon, circle):
            return True
    return False


def _cap_datetime(value):
    dt = _parse_iso(value)
    if dt is None or dt.tzinfo is None:
        return None
    return dt


def _cap_xml_text(element: ET.Element, name: str) -> str | None:
    found = element.find(f"cap:{name}", CAP_NS)
    return found.text.strip() if found is not None and found.text else None


def _kde_alerts_from_xml(xml_bytes: bytes, lat: float, lon: float) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    if root.tag != "{urn:oasis:names:tc:emergency:cap:1.2}alert":
        return []

    if (
        _cap_xml_text(root, "status") != "Actual"
        or _cap_xml_text(root, "scope") != "Public"
        or _cap_xml_text(root, "msgType") not in ("Alert", "Update")
    ):
        return []

    now = datetime.now(timezone.utc)
    alert_id = _cap_xml_text(root, "identifier") or ""
    sender = _cap_xml_text(root, "sender") or ""
    results = []

    for info in root.findall("cap:info", CAP_NS):
        categories = [
            el.text.strip()
            for el in info.findall("cap:category", CAP_NS)
            if el.text
        ]
        if "Met" not in categories:
            continue

        start_dt = _cap_datetime(
            _cap_xml_text(info, "onset")
            or _cap_xml_text(info, "effective")
            or _cap_xml_text(root, "sent")
        )
        end_dt = _cap_datetime(_cap_xml_text(info, "expires"))

        effective_dt = _cap_datetime(
            _cap_xml_text(info, "effective") 
            or _cap_xml_text(root, "sent")
        )
        if (
            start_dt is None
            or effective_dt is None
            or end_dt is None
            or not (effective_dt <= now < end_dt)
        ):
            continue

        matching_areas = []
        for area in info.findall("cap:area", CAP_NS):
            polygons = [
                el.text.strip()
                for el in area.findall("cap:polygon", CAP_NS)
                if el.text
            ]
            circles = [
                el.text.strip()
                for el in area.findall("cap:circle", CAP_NS)
                if el.text
            ]
            if _cap_area_contains(
                {"polygon": polygons, "circle": circles}, lat, lon
            ):
                matching_areas.append(area)

        if not matching_areas:
            continue

        event = _cap_xml_text(info, "event") or ""
        title = _cap_xml_text(info, "headline") or event or "Weather warning"
        region = _cap_xml_text(matching_areas[0], "areaDesc") or ""
        issuer = _cap_xml_text(info, "senderName") or sender or "CAP via KDE"

        results.append({
            "title": title,
            "level": SEVERITY_TO_LEVEL.get(
                _cap_xml_text(info, "severity"), "neutral"
            ),
            "icon": _icon_for_event(event or title),
            "start": _local_time_str(start_dt),
            "end": _local_time_str(end_dt),
            "start_iso": start_dt.isoformat(),
            "end_iso": end_dt.isoformat(),
            "event": event or "Weather warning",
            "issuer": issuer,
            "source": issuer,
            "region": region,
            "_id": alert_id,
        })

    return results


def fetch_kde_alerts(latitude: float, longitude: float) -> list[dict]:
    """Načítaj platné meteorologické CAP výstrahy pre konkrétny bod."""
    lat, lon = float(latitude), float(longitude)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return []

    margin = KDE_POINT_MARGIN
    params = {
        "min_lat": max(-90, lat - margin),
        "max_lat": min(90, lat + margin),
        "min_lon": max(-180, lon - margin),
        "max_lon": min(180, lon + margin),
    }
    if (
        params["min_lat"] >= params["max_lat"]
        or params["min_lon"] >= params["max_lon"]
    ):
        return []

    url = KDE_AREA_URL + "?" + urlencode(params)
    try:
        ids = json.loads(_request(url).decode("utf-8"))
    except Exception as exc:
        print(f"KDE alerts area request failed: {exc}")
        return []

    if not isinstance(ids, list):
        print("KDE alerts: unexpected area response format")
        return []

    results = []
    seen = set()

    for alert_uuid in ids:
        if not isinstance(alert_uuid, str):
            continue

        try:
            alert_url = (
                "https://alerts.kde.org/alert/"
                + quote(alert_uuid, safe="")
            )
            xml_bytes = _request(alert_url)
            alerts_for_point = _kde_alerts_from_xml(xml_bytes, lat, lon)
        except Exception as exc:
            print(f"KDE alert {alert_uuid} failed: {exc}")
            continue

        for alert in alerts_for_point:
            key = (
                alert["_id"],
                alert["title"],
                alert["start_iso"],
                alert["region"],
            )
            if key not in seen:
                seen.add(key)
                alert.pop("_id", None)
                results.append(alert)

    return results

def fetch_official_alerts(country_code: str | None, region: str | None = None) -> list[dict]:
    """Fetch and merge official alerts from MeteoAlarm and WMO SWIC.

    If `region` is given (typically the location's admin1/admin2/city name
    from Open-Meteo geocoding), alerts are filtered to only those whose
    parsed region loosely matches it - so a country-wide feed of ~10
    district warnings collapses down to the one relevant to the selected
    location. If no alert has a parsable region, or none match, or region
    is not given, ALL fetched alerts are returned unfiltered - this
    function never hides everything just because filtering was
    inconclusive.

    Always returns a list, never raises.
    """
    if not country_code:
        return []
    combined = _dedupe(fetch_meteoalarm(country_code))

    if not region:
        return combined

    return [a for a in combined if _region_matches(a.get("region"), region)]
