# Changelog

All notable changes to Wandermark. This project uses loose [semantic
versioning](https://semver.org/) while pre-1.0 (expect rough edges; the data
format may still shift).

The version that ships in the app is the `WANDERMARK_VERSION` constant near the
top of the `<script>` in `wandermark.html`, and it's shown at the bottom of the
⋯ menu.

---

## [0.9.1] — Embeddable shared config ("just works" for friends)

### Added
- A `CONFIG` block at the top of the script. Fill in a referrer-restricted Maps
  key, a referrer-restricted Drive key + shared folder ID, and the OAuth Client
  ID, and anyone who opens the hosted URL gets Google mode + the shared maps with
  nothing to enter. A person's own entered values always override CONFIG.
- Clearer toast when the Maps key is blocked by a website restriction (points at
  the `https://kabigone.github.io/*` wildcard fix).

### Sharing model (summary)
- To share: give people the **URL**. With CONFIG filled, Google mode and the
  shared folder just work. To let someone **edit**, add them as an OAuth **test
  user** and share the Drive folder with them as **Editor**; they sign in with
  their own Google account.
- Only embed **referrer-restricted** browser keys (restricted to the site). The
  Client ID is public by design. Never embed an unrestricted key.

---

## [0.9.0] — Collaborative editing of shared maps

### Changed
- OAuth scope widened from `drive.file` to full **`drive`**, so a signed-in
  collaborator can edit **any map they have Drive edit-access to**, not only
  ones they created. The owner shares the folder as **Editor**; Drive itself
  enforces who can write what.
- **Publish / Update on Drive** now appears on every map (including shared ones).
- **Last-writer-wins**, like Google My Maps. A **●** marks a map with local
  edits you haven't pushed; a sync won't overwrite a map while it has unpushed
  edits (push first, then it syncs normally).

### Trade-off (be aware)
- Full `drive` scope is a "restricted" Google scope, so while the OAuth app is
  in **testing** it shows an "unverified app" screen — added **test users** can
  click *Advanced → continue*. Going fully public later would need Google's
  verification. Fine for a friend group; documented so it's not a surprise.

---

## [0.8.0] — Drive write-back (save your maps from the app)

### Added
- **Google sign-in (OAuth, `drive.file` scope)** using an OAuth **Client ID**
  (separate from the read API key). Stored locally like the other credentials.
- **Publish / Update on Drive** buttons on your own maps (in the 🗂️ maps panel):
  publishing creates the map's JSON file in the shared folder; updating
  overwrites the file you created — no manual upload step.
- The model: everyone still *reads* the whole folder via the API key; *writing*
  is per-person via `drive.file`, so you can only change maps **you** published.
  Keep separate files if two people need to edit the "same" map.

### Changed
- Read-sync no longer overwrites or deletes maps you've published yourself.

### Notes
- Needs the app hosted at a fixed origin (your GitHub Pages URL) — OAuth won't
  work from a local file. With the consent screen in "testing", sign-in expires
  every few days; just sign in again.

## [0.7.1] – [0.7.3] — Drive sync diagnostics

- Surfaces the **actual** Google error on a failed sync (Drive API not enabled,
  key not allowed for Drive, folder not shared, key blocked by website) instead
  of a generic message; logs the full error to the console.
- Warns when an API key and an OAuth Client ID are pasted into the wrong fields.
- Friendlier empty-folder message (an empty folder means the connection works).

---

## [0.7.0] — Hours-derived filters + category editing/merging

### Added
- **Quick filters (auto, from opening hours).** A chip group computed from the
  structured hours we already fetch — no manual tagging:
  *Open now, Open today, Breakfast, Weekday lunch, Dinner, Open late, Open
  weekends.* Combine several (AND). Shown only when the map has hours data
  (i.e. Google-sourced places).
- **Category editor**: tap a category to rename it, change its icon/color, or
  **merge it into another category** (moves all its places, then removes it) —
  the practical fix for the many mismatched categories you get from a KML import.

### Notes
- "Breakfast/lunch/dinner/late" are derived from opening times (e.g. breakfast =
  open in the morning), so they need places that have hours. Things Google's
  search data doesn't expose (terrace seating, lunch *deals*) still come from
  the Tabelog scraper's `--tags`, not from Google.

---

## [0.6.0] — Tags & custom filters + mobile performance

### Added
- **Per-place tags** (free-form labels), editable in the place popup.
- **Tag filter** in the sidebar: toggle tag chips, with a **match all / match
  any** switch. This is the general mechanism for custom filters such as
  "breakfast", "テラス席", or "weekday lunch" — tag the places (by hand, via CSV
  import, or via the scraper) and filter on them.
- **Tags column** in the table (sortable); tags included in CSV (`tags` column,
  `;`-separated) and JSON export/import; tags are also matched by the text box.

### Performance
- Leaflet marker popups are now built **lazily** (only when opened) instead of
  constructing a popup DOM tree for every place on every re-render.
- Filter typing (text / radius) is **debounced**, so a full map re-render no
  longer fires on every keystroke.

### Notes
- "Serves breakfast", "outdoor seating", and "lunch deals" are not reliably
  available from the Google/OSM search data this app uses, so they're modeled as
  tags rather than queried live.

---

## [0.5.0] — Google Drive read-sync + project scaffolding

### Added
- **Google Drive folder sync (read-only).** ⋯ menu → *Sync with Google Drive*:
  paste a shared folder link + a Drive-enabled API key and Wandermark lists the
  folder and loads every `.json` as a map under "☁️ Shared from Drive". Optional
  auto-sync on open. No Google sign-in required (uses an API key against
  publicly-shared files).
- Synced maps are read-only in the app; a **Copy to my maps** action forks an
  editable local copy.
- **Version tag** in the UI and a structured changelog comment at the top of the
  HTML file.
- `CHANGELOG.md` and `README.md` (developer/architecture notes).

### Known limitations
- Sync is **load-only**. Saving edits back to Drive would require OAuth sign-in
  and the app hosted at a fixed URL (see "Roadmap" in README).

---

## [0.4.0] — Multiple maps + My Maps import

### Added
- **Multiple maps** ("a map per city"). New data model: a library of maps, each
  with its own places and categories. Header **🗂️ map switcher** and a manage
  panel to create / rename / duplicate / delete / switch.
- Maps are grouped as **My maps** vs **Curated / imported lists**.
- **Google My Maps import** via KML and KMZ. My Maps layers become categories.
- **Full-week table**: all seven days as columns (today highlighted) instead of
  a single day, plus a live "Now" Open/Closed column.
- Category **All / None** buttons and a **Reset all filters** button.

### Fixed
- Table is now horizontally scrollable on desktop (`width: max-content` inside a
  scrolling container) instead of being clipped.

### Migration
- Old single-map saves are automatically wrapped into one map named "My map".

---

## [0.3.0] — Google engine, photos, hours, language

### Added
- **Google Maps engine** (bring your own API key) alongside the keyless
  OpenStreetMap engine, behind a shared adapter interface.
- **Place photos** (popup banner + list thumbnail) from Google.
- **Structured opening hours**: aligned day/time grid in the popup, today
  highlighted, and an "Open now / Closed now" status.
- **Display-language switcher** for place names & addresses.
- **Collapsible filters** with an active-filter count badge.
- **Distance anchors**: measure from *my location* or a *typed address*.

### Fixed
- Popup Save/Delete buttons no longer clipped.

---

## [0.2.0] — Durable storage + sharing

### Added
- Storage abstraction: tries the in-app `window.storage`, falls back to browser
  `localStorage`, then memory — so places persist when the file is opened
  locally.
- **Share codes** (export/import a map as a compact text string).

### Fixed
- "Places vanished on reload" — root cause was relying only on in-app storage.

---

## [0.1.0] — First version

### Added
- Single-file app: keyless OpenStreetMap base, search-to-add, customizable
  categories (icon + color), interactive map, sidebar list, spreadsheet/table
  view, JSON & CSV import/export.
