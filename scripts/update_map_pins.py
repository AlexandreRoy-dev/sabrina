#!/usr/bin/env python3
"""Build / refresh transaction map pins for index.html.

- Keeps historical street-level pins (no civic numbers)
- Adds sold listings from data/properties.json as street-name-only pins
- Geocodes via Nominatim (cached) so pins land on the right street
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PROPERTIES = ROOT / "data" / "properties.json"
PINS_OUT = ROOT / "data" / "transaction_pins.json"
HISTORICAL_SEED = ROOT / "data" / "historical_transaction_pins.json"
CACHE_PATH = ROOT / "data" / "geocode_cache.json"
USER_AGENT = "SabrinaLagasseSiteMapPins/1.0 (vendreavecsabrina.ca)"

AREA_CITY = {
    "Lévis": "Lévis, Québec",
    "Longueuil": "Longueuil, Québec",
    "Parcours du Cerf": "Longueuil, Québec",
    "Saint-Hubert": "Saint-Hubert, Longueuil, Québec",
    "Centre": "Longueuil, Québec",
    "Le Vieux-Longueuil": "Longueuil, Québec",
    "Saint-Roch-de-Richelieu": "Saint-Roch-de-Richelieu, Québec",
    "Saint-Joseph-de-Sorel": "Saint-Joseph-de-Sorel, Québec",
    "Sorel-Tracy": "Sorel-Tracy, Québec",
    "Tracy": "Sorel-Tracy, Québec",
    "Yamaska": "Yamaska, Québec",
    "Hinchinbrooke": "Hinchinbrooke, Québec",
    "Beloeil": "Beloeil, Québec",
    "Chambly": "Chambly, Québec",
    "Brossard": "Brossard, Québec",
    "Boucherville": "Boucherville, Québec",
    "Saint-Hyacinthe": "Saint-Hyacinthe, Québec",
    "Mont-Saint-Hilaire": "Mont-Saint-Hilaire, Québec",
    "Varennes": "Varennes, Québec",
    "La Prairie": "La Prairie, Québec",
    "Candiac": "Candiac, Québec",
    "Sir-Wilfrid-Laurier": "Longueuil, Québec",
    "Québec": "Québec, Québec",
}

ROAD_CLASSES = {"highway"}
ROAD_TYPES = {
    "residential",
    "unclassified",
    "tertiary",
    "secondary",
    "primary",
    "living_street",
    "service",
    "road",
    "trunk",
}

# Drop failed historical geocodes
DROP_TITLES = {"Cadastre du Québec"}

# Normalize abbreviated street titles for better geocoding
STREET_ALIASES = {
    "Boul. Ste-Anne": "Boulevard Sainte-Anne",
    "Boul Taché Ouest": "Boulevard Taché Ouest",
    "Av. Taniata": "Avenue Taniata",
    "Ave des Jésuites": "Avenue des Jésuites",
    "Av. Nordique": "Avenue Nordique",
    "Av. Maguire": "Avenue Maguire",
    "Av. Joffre": "Avenue Joffre",
    "Av. Royale": "Avenue Royale",
    "Av. du Golf-de-Bélair": "Avenue du Golf-de-Bélair",
    "Av. de la Rivière-Jaune": "Avenue de la Rivière-Jaune",
    "Ch. d'Azur": "Chemin d'Azur",
    "Ch. du Sault": "Chemin du Sault",
}

# Rough QuebecCity/Lévis metro bounds – reject far outliers (e.g. Montreal)
QC_BOUNDS = {
    "min_lat": 44.8,
    "max_lat": 47.8,
    "min_lng": -75.0,
    "max_lng": -69.5,
}



def street_name_only(address: str) -> str:
    """Remove civic / unit numbers; keep street name only."""
    if not address:
        return ""
    parts = [p.strip() for p in address.split(",") if p.strip()]
    kept: list[str] = []
    for part in parts:
        # Pure/unit civic numbers: 1618, 1093A, 360-L6, 2106, 305, apt styles
        if re.fullmatch(r"\d+[A-Za-z]?(?:-\w+)?", part):
            continue
        if re.fullmatch(r"(?:app|apt|unit|suite|#)\s*\.?\s*\d+\w*", part, re.I):
            continue
        # Leading civic still glued: "1618 Rue Aladin"
        part = re.sub(r"^\d+[A-Za-z]?(?:-\w+)?\s+", "", part).strip()
        if part:
            kept.append(part)
    return ", ".join(kept) if kept else address.strip()


def area_from_listing(listing: dict) -> str:
    label = (listing.get("cityLabel") or "").strip()
    m = re.search(r"\(([^)]+)\)", label)
    if m:
        return m.group(1).strip()
    if label:
        return label
    city = (listing.get("city") or "").replace("-", " ").strip()
    return city.title() if city else "Québec"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_index_pins(html: str) -> list[dict]:
    match = re.search(r"var properties = (\[.*?\]);", html, re.S)
    if not match:
        return []
    return json.loads(match.group(1))


def nominatim_search(session: requests.Session, query: str) -> list[dict]:
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "countrycodes": "ca",
    }
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    time.sleep(1.05)
    return resp.json()


def pick_result(results: list[dict], street: str, area: str) -> dict | None:
    street_l = street.lower()
    tokens = [t for t in re.split(r"[\s\-'.]+", street_l) if len(t) > 2]
    stop = {
        "rue",
        "avenue",
        "ave",
        "av",
        "boulevard",
        "boul",
        "chemin",
        "ch",
        "route",
        "montée",
        "montee",
        "carré",
        "carre",
        "des",
        "de",
        "du",
        "la",
        "le",
        "les",
    }
    tokens = [t for t in tokens if t not in stop]
    area_tok = area.lower().split(",")[0].strip()

    scored: list[tuple[float, dict]] = []
    for item in results:
        display = (item.get("display_name") or "").lower()
        score = 0.0
        if item.get("class") in ROAD_CLASSES:
            score += 5
        if item.get("type") in ROAD_TYPES:
            score += 3
        if item.get("class") == "place":
            score -= 4
        if "cadastre" in display:
            score -= 10
        for tok in tokens:
            if tok in display:
                score += 2
        if area_tok and area_tok in display:
            score += 2
        if "québec" in display or "quebec" in display or "lévis" in display or "levis" in display:
            score += 0.5
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] < 3:
        return None
    return scored[0][1]


def photon_search(session: requests.Session, query: str) -> list[dict]:
    """Fallback geocoder (OSM-based) when Nominatim is rate-limited."""
    params = {"q": query, "limit": 5, "lang": "fr"}
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(params)
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    time.sleep(0.35)
    features = resp.json().get("features") or []
    converted = []
    for feat in features:
        props = feat.get("properties") or {}
        coords = (feat.get("geometry") or {}).get("coordinates") or [None, None]
        lng, lat = coords[0], coords[1]
        if lat is None or lng is None:
            continue
        parts = [
            props.get("name"),
            props.get("street"),
            props.get("city") or props.get("locality"),
            props.get("state"),
            props.get("country"),
        ]
        display = ", ".join(p for p in parts if p)
        osm_key = props.get("osm_key") or ""
        osm_value = props.get("osm_value") or ""
        converted.append(
            {
                "lat": lat,
                "lon": lng,
                "display_name": display,
                "class": osm_key,
                "type": osm_value,
            }
        )
    return converted


def in_qc_bounds(lat: float, lng: float) -> bool:
    return (
        QC_BOUNDS["min_lat"] <= lat <= QC_BOUNDS["max_lat"]
        and QC_BOUNDS["min_lng"] <= lng <= QC_BOUNDS["max_lng"]
    )


def geocode_title(title: str) -> str:
    return STREET_ALIASES.get(title, title)


def geocode(
    session: requests.Session,
    cache: dict,
    title: str,
    area: str,
    *,
    force: bool = False,
) -> tuple[float, float] | None:
    key = f"{title}|{area}"
    if not force and key in cache and cache[key]:
        cached = cache[key]
        if in_qc_bounds(float(cached["lat"]), float(cached["lng"])):
            return float(cached["lat"]), float(cached["lng"])

    city = AREA_CITY.get(area, f"{area}, Québec")
    search_title = geocode_title(title)
    queries = [
        f"{search_title}, {city}, Canada",
        f"{search_title}, {city}",
        f"{search_title}, Québec, QC, Canada",
    ]

    for query in queries:
        try:
            results = photon_search(session, query)
        except requests.RequestException as exc:
            print(f"  WARN photon error ({query}): {exc}")
            results = []
        # Prefer in-bounds quebec results
        filtered = []
        for item in results:
            try:
                lat, lng = float(item["lat"]), float(item["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            if in_qc_bounds(lat, lng):
                filtered.append(item)
        picked = pick_result(filtered or results, search_title, area) if results else None
        if picked:
            lat, lng = float(picked["lat"]), float(picked["lon"])
            if not in_qc_bounds(lat, lng):
                continue
            cache[key] = {"lat": lat, "lng": lng, "query": query, "source": "photon"}
            return lat, lng

    for query in queries:
        try:
            results = nominatim_search(session, query)
        except requests.RequestException as exc:
            print(f"  WARN nominatim error ({query}): {exc}")
            continue
        filtered = []
        for item in results:
            try:
                lat, lng = float(item["lat"]), float(item["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            if in_qc_bounds(lat, lng):
                filtered.append(item)
        picked = pick_result(filtered or results, search_title, area)
        if picked:
            lat, lng = float(picked["lat"]), float(picked["lon"])
            if not in_qc_bounds(lat, lng):
                continue
            cache[key] = {"lat": lat, "lng": lng, "query": query, "source": "nominatim"}
            return lat, lng

    cache[key] = None
    return None


def pin_key(pin: dict) -> tuple[str, str]:
    return (pin.get("title") or "").strip().lower(), (pin.get("area") or "").strip().lower()


def load_pin_sources() -> list[dict]:
    """Merge seed + current JSON + leftover index.html pins. Seed wins last-write on coords? No: first seen wins, later sources fill gaps."""
    existing: list[dict] = []
    if HISTORICAL_SEED.exists():
        existing.extend(load_json(HISTORICAL_SEED, {}).get("pins") or [])
    if PINS_OUT.exists():
        existing.extend(load_json(PINS_OUT, {}).get("pins") or [])
    if INDEX.exists():
        existing.extend(extract_index_pins(INDEX.read_text(encoding="utf-8")))
    return existing


def build_pins(session: requests.Session, cache: dict, *, regeocode: bool = False) -> list[dict]:
    existing = load_pin_sources()

    pins: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for raw in existing:
        title = street_name_only(raw.get("title") or "")
        area = (raw.get("area") or "").strip()
        if not title or title in DROP_TITLES:
            continue
        key = (title.lower(), area.lower())
        if key in seen:
            continue
        seen.add(key)

        if regeocode:
            coords = geocode(session, cache, title, area)
            if coords:
                lat, lng = coords
            else:
                lat, lng = float(raw["lat"]), float(raw["lng"])
                print(f"  KEEP OLD coords for {title} / {area}")
        else:
            lat, lng = float(raw["lat"]), float(raw["lng"])

        pins.append(
            {
                "lat": round(lat, 5),
                "lng": round(lng, 5),
                "title": title,
                "area": area,
                "status": raw.get("status") or "transaction",
            }
        )

    # Sold listings from sync → street-only pins (always refresh coords)
    props = load_json(PROPERTIES, {})
    for listing in props.get("listings") or []:
        if not listing.get("sold"):
            continue
        title = street_name_only(listing.get("address") or "")
        area = area_from_listing(listing)
        if not title:
            continue
        key = (title.lower(), area.lower())

        if key in seen and not regeocode:
            for existing_pin in pins:
                if pin_key(existing_pin) == key:
                    existing_pin["status"] = "vendu"
                    if listing.get("uls"):
                        existing_pin["uls"] = listing.get("uls")
                    break
            continue

        print(f"Geocoding sold: {title} ({area})...")
        coords = geocode(session, cache, title, area, force=regeocode)
        if not coords:
            print(f"  FAIL: could not geocode {title} / {area}")
            continue
        lat, lng = coords
        pin = {
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "title": title,
            "area": area,
            "status": "vendu",
            "uls": listing.get("uls"),
        }
        if key in seen:
            for i, existing_pin in enumerate(pins):
                if pin_key(existing_pin) == key:
                    pins[i] = pin
                    break
        else:
            seen.add(key)
            pins.append(pin)
        print(f"  -> {lat:.5f}, {lng:.5f}")

    return pins


MAP_SECTION_HTML = """
    <section id="transactions-map-section" class="relative py-24 bg-[#151515] overflow-hidden">
      <div class="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
        <div class="grid lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          <div class="lg:col-span-4">
            <p class="text-brand font-bold uppercase tracking-[0.2em] text-xs mb-3">Portfolio</p>
            <h2 class="font-serif italic text-3xl md:text-4xl text-brand mb-2">Transactions</h2>
            <h3 class="font-black text-4xl md:text-5xl text-white uppercase tracking-tighter leading-[0.9] mb-6">Réussies</h3>
            <p class="text-gray-300 text-base leading-relaxed mb-8">
              Explorez mes transactions à travers la Montérégie et les environs. Chaque point représente un projet accompli.
            </p>
            <a href="proprietes.html" class="inline-flex items-center gap-2 bg-brand text-white px-6 py-3 rounded-full text-sm font-bold uppercase tracking-wider hover:bg-white hover:text-black transition-all">
              Voir mes propriétés
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </a>
          </div>
          <div class="lg:col-span-8">
            <div class="w-full h-[420px] md:h-[500px] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl bg-white/5">
              <div id="transactionsMap" class="w-full h-full"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
"""

MAP_HEAD_LINKS = """
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
  <style>
    .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large { background-color: rgba(208,16,58,0.25) !important; }
    .marker-cluster-small div, .marker-cluster-medium div, .marker-cluster-large div {
      background-color: #d0103a !important; color: #fff !important; font-weight: 700;
    }
    #transactionsMap .leaflet-popup-content-wrapper { border-radius: 12px; }
  </style>
"""

MAP_SCRIPT = """
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
  <script>
  document.addEventListener("DOMContentLoaded", function() {
    var el = document.getElementById('transactionsMap');
    if (!el || typeof L === 'undefined') return;
    var map = L.map('transactionsMap').setView([45.55, -73.35], 9);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    var markers = L.markerClusterGroup({ maxClusterRadius: 40 });
    var redIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });
    fetch('data/transaction_pins.json')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        var properties = (data && data.pins) ? data.pins : [];
        properties.forEach(function(prop) {
          var badge = prop.status === 'vendu' ? 'VENDU' : 'TRANSACTION RÉUSSIE';
          var marker = L.marker([prop.lat, prop.lng], {icon: redIcon})
            .bindPopup(
              '<div style="text-align:center;font-family:inherit;min-width:140px;">'
              + '<div style="color:#d0103a;text-transform:uppercase;font-weight:700;font-size:10px;letter-spacing:1px;margin-bottom:4px;">' + (prop.area || '') + '</div>'
              + '<div style="font-weight:700;color:#111;font-size:14px;margin-bottom:8px;">' + (prop.title || '') + '</div>'
              + '<div style="display:inline-block;background:#d0103a;color:#fff;padding:6px 10px;border-radius:6px;font-size:11px;font-weight:700;">' + badge + '</div>'
              + '</div>'
            );
          markers.addLayer(marker);
        });
        map.addLayer(markers);
        if (properties.length) {
          try { map.fitBounds(markers.getBounds().pad(0.2)); } catch (e) {}
        }
      })
      .catch(function(err) { console.error('Map pins load failed', err); });
  });
  </script>
"""


def write_index_loader(pin_count: int) -> None:
    """Ensure index.html has a transactions map that loads data/transaction_pins.json."""
    html = INDEX.read_text(encoding="utf-8")

    if "transaction_pins.json" in html and "transactionsMap" in html:
        print(f"index.html already has transactions map ({pin_count} pins)")
        return

    if "leaflet@" not in html:
        html = html.replace("</head>", MAP_HEAD_LINKS + "\n</head>", 1)

    if "transactions-map-section" not in html:
        # Insert before FAQ section when present, else before footer
        if '<section id="faq"' in html:
            html = html.replace(
                '<section id="faq"',
                MAP_SECTION_HTML + '\n    <section id="faq"',
                1,
            )
        elif "<footer" in html:
            html = html.replace("<footer", MAP_SECTION_HTML + "\n    <footer", 1)
        else:
            html = html.replace("</body>", MAP_SECTION_HTML + "\n</body>", 1)

    if "leaflet.markercluster.js" not in html:
        html = html.replace("</body>", MAP_SCRIPT + "\n</body>", 1)

    INDEX.write_text(html, encoding="utf-8")
    print(f"Added transactions map to index.html ({pin_count} pins)")


def run(*, regeocode: bool = False) -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    cache = load_json(CACHE_PATH, {})

    print("Building transaction pins...")
    pins = build_pins(session, cache, regeocode=regeocode)
    save_json(CACHE_PATH, cache)
    payload = {
        "generatedFrom": "scripts/update_map_pins.py",
        "pinCount": len(pins),
        "pins": pins,
    }
    save_json(PINS_OUT, payload)
    seed_pins = []
    seen_seed: set[tuple[str, str]] = set()
    if HISTORICAL_SEED.exists():
        for raw in load_json(HISTORICAL_SEED, {}).get("pins") or []:
            key = pin_key(raw)
            if key in seen_seed:
                continue
            seen_seed.add(key)
            seed_pins.append(raw)
    for pin in pins:
        key = pin_key(pin)
        if key in seen_seed:
            continue
        seen_seed.add(key)
        seed_pins.append(
            {
                "lat": pin["lat"],
                "lng": pin["lng"],
                "title": pin["title"],
                "area": pin.get("area") or "",
                "status": pin.get("status") or "transaction",
                **({"uls": pin["uls"]} if pin.get("uls") else {}),
            }
        )
    save_json(
        HISTORICAL_SEED,
        {
            "comment": "Append-only seed of completed transactions. update_map_pins.py always merges this file and never deletes these pins.",
            "pins": seed_pins,
        },
    )
    print(f"Wrote {PINS_OUT} ({len(pins)} pins)")
    write_index_loader(len(pins))
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Update transaction map pins")
    parser.add_argument(
        "--regeocode",
        action="store_true",
        help="Re-geocode historical pins (slow; uses Photon/Nominatim)",
    )
    args = parser.parse_args()
    return run(regeocode=args.regeocode)


if __name__ == "__main__":
    raise SystemExit(main())
