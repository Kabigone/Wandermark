#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tabelog_hyakumeiten_to_wandermark.py
====================================

Turn a Tabelog list — a 百名店 (Hyakumeiten) award page, an rstLst search, or a
PUBLIC saved list/map — into a Wandermark map file you can import via
⋯ menu -> "Import file" (it becomes its own "curated" map).

WHAT IT DOES
------------
1. Reads a Tabelog list URL (Hyakumeiten, search, or a public saved list).
2. Collects the restaurant detail-page links, following "next page" links.
3. Visits each restaurant page and pulls name + address + coordinates from
   the page's JSON-LD ("application/ld+json") structured data.
4. With --tags, also makes a best-effort guess at facility tags (テラス席, 朝食,
   ランチ, 個室 …) so you can use Wandermark's tag filters.

Note: a PRIVATE saved list (only visible when you're logged in) can't be read —
make the list public/shareable first, or it won't work.
4. If a page has no coordinates, it (optionally) geocodes the address with
   OpenStreetMap's free Nominatim service.
5. Writes  wandermark-<name>.json  ready to import.

PLEASE READ — be a good citizen
-------------------------------
* This is for PERSONAL use only, at small volume. Tabelog's Terms of Service
  and robots.txt govern what you may do. Check them and respect them. If a
  page or robots.txt disallows automated access, DON'T scrape it.
* The script is deliberately slow (a polite delay between requests). Do not
  remove the delays or hammer the site.
* It does NOT attempt to bypass logins, CAPTCHAs, rate limits, or any anti-bot
  measure, and you shouldn't add that.
* Tabelog changes its HTML from time to time. If results come back empty, the
  CSS selectors / JSON-LD shape below probably need a small tweak. This script
  has not been tested against the live site from here, so treat it as a
  starting point you may need to adjust.

REQUIREMENTS
------------
    pip install requests beautifulsoup4

USAGE
-----
    python3 tabelog_hyakumeiten_to_wandermark.py "https://award.tabelog.com/hyakumeiten/ramen_tokyo"
    python3 tabelog_hyakumeiten_to_wandermark.py "<list-url>" --name "Ramen Tokyo 100" --geocode --max 100
"""

import sys
import os
import re
import json
import time
import argparse
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing deps. Run:  pip install requests beautifulsoup4")

# A normal, identifiable User-Agent. Set this to something honest.
HEADERS = {
    "User-Agent": "Wandermark-personal-import/1.0 (personal use; contact: you@example.com)",
    "Accept-Language": "ja,en;q=0.8",
}
LIST_DELAY = 2.0      # seconds between list-page fetches
DETAIL_DELAY = 2.5    # seconds between restaurant-page fetches
GEOCODE_DELAY = 1.1   # Nominatim asks for <= 1 request/second


# --------------------------------------------------------------------------- #
#  HTTP                                                                        #
# --------------------------------------------------------------------------- #
def get(url):
    """Fetch a URL politely. Returns text or None."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"  ! HTTP {r.status_code} for {url}")
            return None
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.RequestException as e:
        print(f"  ! request failed: {e}")
        return None


# --------------------------------------------------------------------------- #
#  List pages -> restaurant detail URLs                                        #
# --------------------------------------------------------------------------- #
# Matches a Tabelog restaurant detail page, e.g. /tokyo/A1304/A130401/13012345/
RST_URL_RE = re.compile(r"https?://tabelog\.com/[^/]+/A\d+/A\d+/\d+/?$")


def find_next_page(soup, current_url, page):
    """Find the next list page. Works for Hyakumeiten, search (rstLst) and
    public saved lists, which paginate differently."""
    # 1) an explicit "next" pagination link
    for a in soup.find_all("a", href=True):
        cls = " ".join(a.get("class", [])).lower()
        rel = " ".join(a.get("rel", [])).lower() if a.get("rel") else ""
        label = a.get_text(strip=True)
        if "next" in cls or "next" in rel or label in ("次の20件", "次へ", "次のページ", ">"):
            return urljoin(current_url, a["href"])
    # 2) fall back to the Hyakumeiten-style /N/ suffix
    return urljoin(current_url.rstrip("/") + "/", str(page + 1) + "/")


def collect_restaurant_urls(list_url, max_count):
    """Walk a Tabelog list (Hyakumeiten award page, rstLst search, or a public
    saved list) and its pagination, gathering restaurant detail URLs.

    NOTE: private saved lists (visible only when logged in) cannot be read — this
    only works for pages that are publicly accessible without a login."""
    urls = []
    seen = set()
    page = 1
    page_url = list_url
    while True:
        print(f"- list page {page}: {page_url}")
        html = get(page_url)
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")

        found_here = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0]
            # Tabelog restaurant detail pages look like /tokyo/A1304/A130401/13012345/
            if RST_URL_RE.match(href) and href not in seen:
                seen.add(href)
                urls.append(href)
                found_here += 1
                if len(urls) >= max_count:
                    break

        print(f"    found {found_here} restaurant links (total {len(urls)})")
        if len(urls) >= max_count or found_here == 0:
            break
        page += 1
        if page > 15:  # safety stop
            break
        page_url = find_next_page(soup, page_url, page - 1)
        time.sleep(LIST_DELAY)
    return urls[:max_count]


# --------------------------------------------------------------------------- #
#  Detail page -> name / address / coordinates                                 #
# --------------------------------------------------------------------------- #
def parse_jsonld(soup):
    """Return the first Restaurant-ish JSON-LD object found, else {}."""
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text() or ""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else [data]
        for obj in candidates:
            if not isinstance(obj, dict):
                continue
            t = obj.get("@type", "")
            types = t if isinstance(t, list) else [t]
            if any("Restaurant" in str(x) or "FoodEstablishment" in str(x) or "LocalBusiness" in str(x)
                   for x in types):
                return obj
    return {}


def extract_tags(soup, obj):
    """Best-effort tags from a Tabelog detail page. HEURISTIC and brittle — the
    facilities table wording changes, so treat these as hints to review, not
    ground truth. Returns a list like ["テラス席", "ランチ", "朝食"]."""
    text = soup.get_text(" ", strip=True)
    tags = []

    def has(*needles):
        return any(n in text for n in needles)

    # Outdoor / terrace seating
    if has("テラス席あり", "テラス席"):
        # avoid "テラス席なし"
        if "テラス席なし" not in text:
            tags.append("テラス席")

    # Breakfast / morning service
    if has("モーニング", "朝食", "朝ごはん"):
        tags.append("朝食")

    # Lunch service (note: this flags "has lunch hours", NOT specifically a
    # weekday-only lunch *deal*, which Tabelog doesn't expose cleanly)
    if has("ランチ営業", "ランチ"):
        tags.append("ランチ")

    # A couple of other commonly-wanted facilities
    if has("個室あり", "完全個室"):
        tags.append("個室")
    if has("貸切可", "貸切"):
        tags.append("貸切")

    # de-dupe, keep order
    out = []
    for t in tags:
        if t not in out:
            out.append(t)
    return out


def extract_place(detail_url, want_tags=False):
    html = get(detail_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    obj = parse_jsonld(soup)

    name = obj.get("name")
    if not name:
        h = soup.find(["h2", "h1"])
        name = h.get_text(strip=True) if h else None

    # address
    address = ""
    addr = obj.get("address")
    if isinstance(addr, dict):
        parts = [addr.get("addressRegion"), addr.get("addressLocality"),
                 addr.get("streetAddress")]
        address = "".join(p for p in parts if p)
    elif isinstance(addr, str):
        address = addr

    # coordinates
    lat = lng = None
    geo = obj.get("geo")
    if isinstance(geo, dict):
        try:
            lat = float(geo.get("latitude"))
            lng = float(geo.get("longitude"))
        except (TypeError, ValueError):
            lat = lng = None

    return {
        "name": name or "(unknown)",
        "address": address,
        "lat": lat,
        "lng": lng,
        "website": detail_url,   # store the real Tabelog page in Wandermark's "website" field
        "tags": extract_tags(soup, obj) if want_tags else [],
    }


# --------------------------------------------------------------------------- #
#  Optional geocoding fallback (OpenStreetMap Nominatim)                       #
# --------------------------------------------------------------------------- #
def geocode(query):
    url = "https://nominatim.openstreetmap.org/search"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20,
                         params={"format": "jsonv2", "limit": 1, "q": query})
        if r.status_code == 200:
            arr = r.json()
            if arr:
                return float(arr[0]["lat"]), float(arr[0]["lon"])
    except (requests.RequestException, ValueError, KeyError):
        pass
    return None, None


# --------------------------------------------------------------------------- #
#  Build the Wandermark file                                                   #
# --------------------------------------------------------------------------- #
DEFAULT_CATEGORIES = [
    {"id": "eat",    "name": "Eat",    "color": "#e0533d", "emoji": "🍜"},
    {"id": "coffee", "name": "Coffee", "color": "#9a6b45", "emoji": "☕️"},
    {"id": "bakery", "name": "Bakery", "color": "#e08a2f", "emoji": "🥐"},
    {"id": "drinks", "name": "Drinks", "color": "#9a52c8", "emoji": "🍷"},
    {"id": "stay",   "name": "Stay",   "color": "#3d7bd1", "emoji": "🏨"},
    {"id": "see",    "name": "See",    "color": "#2f8f86", "emoji": "⛩️"},
    {"id": "shop",   "name": "Shop",   "color": "#d14f93", "emoji": "🛍️"},
    {"id": "other",  "name": "Other",  "color": "#6b7280", "emoji": "📍"},
]


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "tabelog").lower()).strip("-")
    return s[:40] or "tabelog"


def main():
    ap = argparse.ArgumentParser(description="Scrape a Tabelog list (Hyakumeiten award page, rstLst search, or a PUBLIC saved list) into a Wandermark map.")
    ap.add_argument("url", help="A Tabelog list URL — e.g. https://award.tabelog.com/hyakumeiten/ramen_tokyo, a rstLst search, or a public saved list. Private (login-only) lists won't work.")
    ap.add_argument("--name", default=None, help="Name for the resulting map (default: derived from URL)")
    ap.add_argument("--max", type=int, default=100, help="Max restaurants to fetch (default 100)")
    ap.add_argument("--geocode", action="store_true",
                   help="Geocode addresses with OpenStreetMap when a page has no coordinates")
    ap.add_argument("--tags", action="store_true",
                   help="Best-effort tags (テラス席 / 朝食 / ランチ / 個室 …) from each page. HEURISTIC — review before trusting.")
    ap.add_argument("--out", default=None, help="Output filename")
    args = ap.parse_args()

    map_name = args.name or urlparse(args.url).path.rstrip("/").split("/")[-1] or "Tabelog list"
    print(f"\nWandermark · Tabelog importer")
    print(f"List: {args.url}")
    print(f"Map name: {map_name}\n")

    detail_urls = collect_restaurant_urls(args.url, args.max)
    if not detail_urls:
        sys.exit("No restaurant links found. The list URL or the selectors may need adjusting.")

    print(f"\nFetching {len(detail_urls)} restaurant pages (slowly, please be patient)...\n")
    places = []
    for i, url in enumerate(detail_urls, 1):
        print(f"[{i}/{len(detail_urls)}] {url}")
        p = extract_place(url, want_tags=args.tags)
        if not p:
            continue

        if (p["lat"] is None or p["lng"] is None) and args.geocode and p["address"]:
            print("    geocoding address...")
            lat, lng = geocode(p["address"] + " Japan")
            p["lat"], p["lng"] = lat, lng
            time.sleep(GEOCODE_DELAY)

        if p["lat"] is None or p["lng"] is None:
            print(f"    (skipped — no coordinates for: {p['name']})")
            continue

        if p.get("tags"):
            print(f"    tags: {', '.join(p['tags'])}")

        places.append({
            "name": p["name"],
            "address": p["address"],
            "lat": p["lat"],
            "lng": p["lng"],
            "categoryId": "eat",
            "website": p["website"],
            "tags": p.get("tags", []),
            "notes": "",
        })
        time.sleep(DETAIL_DELAY)

    if not places:
        sys.exit("Got pages but no usable coordinates. Try re-running with --geocode.")

    out = {
        "v": 1,
        "name": map_name,
        "kind": "curated",            # shows up under "Curated / imported lists" in Wandermark
        "categories": DEFAULT_CATEGORIES,
        "places": places,
    }
    out_path = args.out or f"wandermark-{slugify(map_name)}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Wrote {len(places)} places to  {out_path}")
    print("  Import it in Wandermark:  ⋯ menu  ->  Import file  ->  pick this .json")
    print("  It will appear as its own curated map you can switch to and share.\n")


if __name__ == "__main__":
    main()
