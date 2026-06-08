# Wandermark — developer notes

Personal, shareable travel maps in **one HTML file**. No build step, no
framework, no bundler. Open `wandermark.html` in a browser and it runs.

This document is a map of the source so you can read and modify it confidently.
For the change history see [CHANGELOG.md](./CHANGELOG.md); for sharing/Drive
setup see `wandermark-drive-sharing-guide.md`.

---

## Files in this project

| File | What it is |
|------|------------|
| `wandermark.html` | The whole app: HTML + CSS + JS in one file. |
| `tabelog_hyakumeiten_to_wandermark.py` | Standalone scraper → Wandermark JSON. |
| `wandermark-drive-sharing-guide.md` | How to share via Google Drive. |
| `CHANGELOG.md` | Version history. |
| `README.md` | This file. |

## Running it

- **Locally:** double-click `wandermark.html`. Everything works in keyless
  OpenStreetMap mode; data persists in the browser's `localStorage`.
- **Google mode / Drive sync:** the hosted copy embeds a shared, referrer-
  restricted key (`CONFIG.apiKey`) so this just works there — no setup. It only
  works on the hosted origin, though (referrer-restricted); running the file
  locally falls back to OpenStreetMap, with a "bring your own key" fallback in
  🗂️ Map ▾ → Map style. Some Google features are also blocked inside sandboxed
  previews — use a real browser, ideally the hosted copy (see Roadmap).
- **Connecting to shared maps:** 🗂️ Map ▾ ("Your maps") is the front door —
  sign in there, then pick the shared folder visually with Google's real
  folder picker (no copying a link out of Drive). The old manual "paste a
  folder link + key" flow still exists as a fallback in the "Advanced: Drive
  connection settings" panel, for troubleshooting or pointing at a folder by
  hand.

## No external dependencies except via CDN

The only third-party code is loaded from `cdnjs.cloudflare.com`: **Leaflet**
(the OSM map), **JSZip** (lazy-loaded only when importing a `.kmz`), and Google
fonts. From Google itself: the **Maps JS API** (when you're in Google mode),
**Identity Services** (`accounts.google.com/gsi/client`, for Drive sign-in),
and the **Picker API** (`apis.google.com/js/api.js`, lazy-loaded only when a
signed-in user taps "choose folder from Drive" — a friendlier way to pick a
shared folder than pasting a link).

---

## How the file is laid out

The HTML is three blocks: a `<style>`, the `<body>` markup, then one big
`<script>` IIFE (`(function(){ ... })();`) holding all logic. The script is
divided by banner comments — search the file for these to jump around:

```
constants            palettes, default categories, day tables, language list
storage              Store: window.storage -> localStorage -> memory
maps (library)       multi-map model: LIB, activeMap, newMap, createMapFromData
helpers              esc, haversine, category guessing, opening-hours parsing
filter               getFiltered() — the single source of truth for "what shows"
popup                makePopupNode(), the per-place card
Leaflet engine       LeafletEngine — keyless OSM + Nominatim
Google engine        GoogleEngine — Google Maps + Places (needs key)
engine switching     startEngine()/teardownMap() swap engines at runtime
add place            addPlace()
search               the search box -> Engine.suggest -> resolve -> addPlace
rendering            renderAll() and the render* helpers
pin / address / geo  drop-a-pin, geolocation, geocoded distance anchor
modals               maps / drive / category / language / google / share / import
export / import      JSON & CSV; KML/KMZ (Google My Maps)
Drive sync           syncDrive() (pull) + driveSaveMap() (push, OAuth) +
                     scheduleAutoPush()/startDrivePolling() (auto-sync glue)
filters reset etc.   resetFilters, catAll, catNone
view                 map vs table tab switching
init                 wireUI() (event wiring) and boot() (load + migrate + start)
```

The mental model: **state changes → call `renderAll()`**. `renderAll()`
re-renders the category chips, the distance dropdown, the place list, the map
markers (via the active engine), the table if open, and then `save()`s. There's
no virtual DOM; it just rebuilds the relevant DOM each time. That's fine at this
scale (tens to low hundreds of places).

---

## Data model

Everything lives under two storage keys (see the `storage` section):

- `wandermark:data` — the whole library + app settings.
- `wandermark:gkey` — the Google Maps API key, kept **separate** so it is never
  included in exports or share codes.

### The library (`LIB`)

```js
LIB = {
  activeId: "<map id>",
  order:    ["<map id>", ...],   // display order
  maps:     { "<map id>": Map, ... }
}
```

`state` is a module-level variable that always **points at the active map**
(`state = LIB.maps[LIB.activeId]`). That's why most code can keep using
`state.places` / `state.categories` unchanged — switching maps just repoints
`state`.

### A map

```js
{
  id, name, kind,            // kind: "personal" | "curated" — cosmetic (⭐ icon) only
  mine,                      // do you own this map? (set at creation; drives the
                             // "Your maps" vs "Shared with you" grouping — like
                             // Google My Maps, every map lives on Drive, "mine"
                             // is always fully editable, "not mine" only if the
                             // owner granted Drive edit access)
  source?, driveId?,         // source:"drive" once the map is backed by a Drive file
  driveModifiedTime?, dirty?,// sync-state bookkeeping, independent of ownership
  places:     [ Place, ... ],
  categories: [ Category, ... ],
  createdAt
}
```

### A place

```js
{
  id, name, address, lat, lng,
  categoryId,                // -> one of this map's categories
  notes, hours,              // hours: human string (OSM) ...
  hoursByDay,                // ... or {Mo,Tu,We,Th,Fr,Sa,Su} (Google) for the grid
  website, photoUrl,         // from Google details
  googleUrl, placeId,        // placeId lets us re-fetch / re-translate
  createdAt
}
```

### A category

```js
{ id, name, color, emoji }
```

`DEFAULT_CATS` is the template; `freshCats()` deep-copies it for each new map.

### App settings (global, not per-map)

```js
appSettings = {
  lang: "native" | "en" | "ja" | ...,         // display language
  drive: { folderId, folderName, key, clientId, auto }  // Drive sync config
}
```

---

## The engine adapter (how OSM and Google coexist)

Both engines implement the **same interface**, and `var Engine` points at the
active one. To add a third map provider, implement these methods:

```
ready(cb)        async-load the lib, then call cb()
init(el)         create the map in element `el`
setView(v)       center {lat,lng,z}
getCenter()      -> {lat,lng}
refresh(list)    draw markers for `list` (+ the distance-anchor marker)
open(p)          pan to a place and open its popup
fit(places)      fit bounds to places
resize()         re-layout after the container changes size
geocode(addr,cb) cb({lat,lng}) or cb(null)
suggest(q,cb)    cb([{name,address,catId,resolve(done)}]) or cb([])/cb(null)
```

`suggest()` returns lightweight predictions; each has a `resolve(done)` that
does the expensive detail lookup and returns a full place object. This keeps
typing cheap and only pays for details when a result is chosen.

---

## Common changes (recipes)

- **Change default categories:** edit `DEFAULT_CATS` (the `constants` section).
- **Add a field to places:** add it in `normalizePlace()` so old data gets a
  default, then read it where places are rendered (`makePopupNode`,
  `renderPlaces`, `renderTable`) and write it where places are created
  (`placeFromDetails` for Google, the `suggest` resolver for OSM, importers).
- **Add a menu item:** add a `<button data-act="...">` in the `.pop-menu`
  markup, then handle that `act` in `wireUI()`'s menu click listener.
- **Add a language:** append to the `LANGS` array.
- **Bump the version:** edit `WANDERMARK_VERSION` and add a `CHANGELOG.md` entry
  (and the summary comment at the top of the HTML).

---

## Constraints worth knowing

- **CORS:** a browser page can't fetch arbitrary third-party sites (Tabelog,
  Eater, Michelin) — they don't allow cross-origin reads. That's why scraping
  lives in external scripts, not in the app. The Google **Drive API** *does*
  allow cross-origin reads with an API key, which is why Drive sync works
  in-browser.
- **`file://` vs hosted:** opening the file locally works for everything except
  things that need an OAuth origin (e.g. future Drive write-back). API keys can
  be referrer-restricted; a locally-opened file has no referrer, so use an
  unrestricted key locally or host the app.
- **No `localStorage` inside the Claude.ai artifact sandbox** — the `Store`
  layer treats it as a best-effort fallback and degrades to in-memory there.

---

## Roadmap (sharing with friends)

The MVP goal is sharing. Three stages, increasing in power and setup:

1. **Host it + version it (do this first).** Put the repo on **GitHub** and turn
   on **GitHub Pages** (free static hosting). This gives:
   - a stable `https://<you>.github.io/...` URL anyone can open (no download), and
   - real revision history (every change is a commit).
   This stage needs **no server**. It also unlocks stage 2.

2. **Google sign-in for Drive write-back.** With the app at a fixed URL you can
   add OAuth (Google Identity Services) and the Drive API *write* scope, so
   friends can **save** maps back to a shared Drive folder, not just read them.
   Google is the backend — still **no server of your own**. This delivers
   "several people maintain a shared set of maps" with last-writer-wins per file.

3. **A small backend (only if you want live, simultaneous editing).** A
   serverless function + a tiny database (e.g. **Netlify Functions** or
   **Cloudflare Workers** + KV, or **Firebase**) enables real-time shared maps
   and accounts. This is the big jump and the only stage that needs server-side
   code to maintain.

### GitHub Pages vs Netlify (since you asked)

Both host the single file for free and give an HTTPS URL.

- **GitHub Pages** — hosting built into a GitHub repo. Since you already have a
  GitHub account, this is the natural home: it stores the file, *is* your
  version history, and serves it. Best fit for stages 1–2.
- **Netlify** — a hosting platform with drag-and-drop deploys ("Netlify Drop")
  and built-in **serverless functions**. You'd reach for it (or Cloudflare
  Workers) at **stage 3**, when you want a bit of server-side logic without
  running a server yourself.

**Suggested next steps:** create the GitHub repo, drop these files in, enable
Pages (stage 1). Then decide between stage 2 (Drive write-back, no server — the
lightest way to hit the "friends can edit" MVP) and stage 3 (real-time, needs a
backend).
