# Changelog

All notable changes to Wandermark. This project uses loose [semantic
versioning](https://semver.org/) while pre-1.0 (expect rough edges; the data
format may still shift).

The version that ships in the app is the `WANDERMARK_VERSION` constant near the
top of the `<script>` in `wandermark.html`, and it's shown at the bottom of the
⋯ menu.

---

## [0.9.8] — Sign-in sticks across reloads

### Changed
- **No more re-clicking "Sign in to Google" on every reload.** A Drive OAuth
  token only ever lived in memory, so a page refresh always showed the sign-in
  badge/button again — even though Google itself remembered you. On launch,
  Wandermark now tries a **silent** re-authentication (no popup; the same
  no-prompt flow auto-push already used for stale tokens) if you've connected
  before, so returning with an active Google session just works, and the badge
  only appears when you genuinely need to act.

---

## [0.9.7] — Picker "developer key is invalid" fix

### Fixed
- The new folder picker (introduced in 0.9.6) could fail with **"There was an
  error! The API developer key is invalid"**. It now also passes a **Drive App
  ID** — derived from the OAuth Client ID's project number — alongside the
  developer key, matching Google's own sample wiring for `PickerBuilder`. If
  the picker still errors (e.g. the Cloud project doesn't have the **Google
  Picker API** enabled, or the API key's restrictions don't allow it), you now
  get a clear toast naming the fix instead of a silent dead end — and "Advanced:
  Drive connection settings" still has the manual paste-a-link fallback.

---

## [0.9.6] — "Your maps" is the front door for shared maps

### Changed
- **Sign-in and folder setup moved to 🗂️ Map ▾ ("Your maps")**, since that's
  where the point of all this — using shared maps — actually lives. It now
  opens with a **🔑 Sign in to Google** button if you aren't connected, or a
  ✓ status line plus your connected folder if you are. **"Sync with Google
  Drive" is gone from the ⋯ menu** — it's not something most people should ever
  need to think about.
- **A header badge** ("🔑 Sign in to Google") now shows up front whenever
  Drive sign-in is available but you haven't connected — so a first-time
  friend knows immediately that there's a shared world of maps to unlock,
  rather than only ever seeing their own empty map.
- **Choosing a folder no longer means copying a link out of Drive.** A new
  "📁 Choose shared folder from Drive" button opens Google's real folder
  picker (Picker API) — browse and click, like picking a folder in any other
  Drive-integrated app. Manually pasting a folder link still works as a
  fallback in the new **Advanced: Drive connection settings** panel (the old
  "Sync with Google Drive" modal, demoted to troubleshooting-only and linked
  quietly from the bottom of Your maps).

### Added
- New external script: Google's Picker API (`apis.google.com/js/api.js`,
  loaded lazily only when you tap "choose folder"), alongside the existing
  Google Identity Services script — see CLAUDE.md for the updated allowlist.

---

## [0.9.5] — Google Maps "just works"; no keys to look at

### Changed
- **Map style is now a plain toggle, not a "connect" flow.** The hosted site
  already embeds a shared, referrer-restricted API key that powers both Google
  Maps and Drive — so most people never need to see, paste, or manage a key at
  all. The old "Connect Google Maps" button + key-entry modal (reachable from
  the header and the ⋯ menu) is gone. In its place: a simple **Google Maps /
  OpenStreetMap** switch inside **Your maps** (🗂️ Map ▾ → Map style), right
  where you're already managing maps.
- **"Bring your own key" still exists, but only as a quiet fallback** — a small
  "having trouble connecting?" link appears in that same panel only if the
  built-in connection fails (e.g. you're running the file locally rather than
  from the website, where the referrer-restricted key won't work).
- Removed the redundant second copy of the embedded API key — `mapsKey` and
  `driveKey` in `CONFIG` were always the literal same key (one key with Maps
  JS, Places, and Drive APIs all enabled on it); merged into one `apiKey`.

---

## [0.9.4] — One clear place to sign in, and fresher pulls on tab return

### Changed
- **Sign-in, finally in one obvious place.** "Connect to Google" entry points
  used to be scattered (only reachable indirectly via per-map Publish/Push
  buttons), so it was easy to miss and hard to find when you needed it. Now
  the **Sync with Google Drive** panel (⋯ menu) opens with a single, prominent
  **🔑 Sign in to Google** button right at the top — and once you're signed in,
  a status line confirms it and explains what it unlocks. This is now *the*
  place to connect; the per-map Publish/Push buttons still work too.

### Fixed
- Collaborators' new places sometimes didn't show up until you hard-refreshed
  the page — the background pull only ran on a ~2-minute timer (and not at all
  while the tab was hidden). Wandermark now also re-checks Drive as soon as you
  switch back to the tab or window (rate-limited so it won't spam Drive if
  you're flipping tabs constantly).

---

## [0.9.3] — Auto-push doesn't fail silently on stale sign-ins

### Fixed
- Sign-in tokens expire (every ~50 min, and sessions lapse between visits —
  especially noticeable on phones). Previously, if auto-push found no valid
  token it just... did nothing, with no feedback — edits sat unsynced and
  looked exactly like data loss. Now it first tries a **silent** Google
  re-sign-in (no popup; succeeds automatically if you have an active Google
  session and previously consented), and if that's genuinely not possible,
  shows a clear "your edits aren't reaching Drive — tap Update on Drive to
  sign in" toast (rate-limited so it isn't naggy).

---

## [0.9.2] — Seamless collaboration (feels like a shared document)

### Added
- **Auto-push**: once you've signed in, edits to a map already on Drive save
  themselves to Drive automatically ~12 seconds after you stop editing — no
  more clicking "Push edits". (Publishing a brand-new map to Drive for the
  first time is still an explicit action.)
- **Background pull**: while the app is open (and the tab is visible),
  Wandermark quietly re-checks the shared Drive folder every couple of minutes
  so collaborators' changes show up without a manual refresh.
- **Conflict heads-up**: if someone else edits a shared map while you also have
  unpushed local edits, you get a toast warning before last-writer-wins would
  overwrite their changes (or yours).

### Notes
- Still last-writer-wins, like Google My Maps — these changes make the existing
  model feel more like editing a live shared document, without changing how
  conflicts are ultimately resolved.
- Auto-push only runs once you've signed in during the current session, so
  there's never a surprise sign-in popup; the manual Publish/Push buttons still
  work (and sign you in) any time.

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
