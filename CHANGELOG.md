# Changelog

All notable changes to Wandermark. This project uses loose [semantic
versioning](https://semver.org/) while pre-1.0 (expect rough edges; the data
format may still shift).

The version that ships in the app is the `WANDERMARK_VERSION` constant near the
top of the `<script>` in `wandermark.html`, and it's shown at the bottom of the
⋯ menu.

---

## [0.9.45] — Mobile header fix, Google search fallback, "already on map" hint

### Fixed
- Mobile header: the "Wandermark" title text shared the first row with the
  map-name button, leaving no room for it and pushing the ⋯ menu and then
  the search bar each onto their own row. The title text is now hidden on
  small screens (just the 🧭 glyph remains), so the map name and ⋯ menu fit
  on one row again.
- Google "search to add" (`GoogleEngine.suggest`) now falls back to
  `PlacesService.textSearch` when `AutocompleteService` returns no
  predictions. Autocomplete is tuned for as-you-type predictions and can
  miss exact-name matches (reported: searching a place's kanji name found
  nothing, but its hiragana reading did) that the regular Maps search box
  finds.

### Added
- Search-to-add results that match a place already on the active map are
  now flagged with a "✓ On this map" badge (matched by Google `placeId`, or
  by coordinates for OSM results) to reduce accidental duplicates.

## [0.9.44] — Fix lost edits on backgrounded/closed tabs

### Fixed
- `save()` debounced writes to storage by 300ms. If the tab was hidden or
  closed within that window (e.g. switching apps right after adding a place
  on mobile), the edit was never written and appeared lost on next launch.
  The pending write is now flushed immediately on `visibilitychange`
  (hidden) and `pagehide`.
- Similarly, a dirty map's auto-push to Drive waited up to 12s before
  starting. That pending push is now also kicked off immediately when the
  tab is hidden/closed, instead of potentially never running.

## [0.9.43] — Live default categories, per-place icons

### Changed
- **Built-in categories (Eat, Coffee, Bakery, Drinks, Stay, See, Shop,
  Other) are no longer frozen into each map at creation time.** A map's
  "Eat" category now keeps tracking the app's current default name,
  icon, and color — so a future change to the defaults (like 0.9.42's
  🍴 swap) reaches every map that hasn't customized that category.
  As soon as you edit a category via ⋯ → Categories → tap it → Save,
  that category's name/icon/color are frozen to your choices for that
  map and stop tracking future default changes. Custom categories you've
  added are unaffected either way.
  - Maps saved before this version have no record of which built-in
    categories were customized, so they're treated as not-yet-customized
    and will pick up live defaults until edited.

### Added
- **Per-place icons.** Each place's popup now has an "Icon" picker
  (below the category dropdown) with an "✨ Automatic" option plus a set
  of more specific icons (🍕 🍣 🍜 🍔 🌮 🍰 🍷 🥩 🦞 etc.). "Automatic"
  uses a more specific icon based on the place's genre when known (e.g.
  🍕 for a pizza restaurant, 🍣 for sushi) — set when looking up a place
  via Google — and otherwise falls back to the category's icon. Picking
  an icon overrides this for that place on the map marker and in the
  sidebar list.

## [0.9.42] — Don't eat the first tap of a double-tap, generic "Eat" icon

### Fixed
- **Tapping the map to drop a pin (or the new "add this POI" popup)
  fired immediately on the first tap**, which on mobile interrupted the
  standard double-tap(-and-hold-drag) zoom gesture before it could
  register — every attempt to zoom that way dropped a pin/POI dialog
  instead. Map clicks now wait ~300ms; if a second tap/click (the start
  of a double-tap) arrives in that window, the pin/POI dialog is
  cancelled and the map's own double-tap zoom handles it.

### Changed
- **Default "Eat" category icon is now 🍴** (fork and knife) instead of
  🍜 (ramen), for new maps. 🍴 is also now in the icon picker for
  existing categories — open ⋯ → Categories → tap "Eat" → pick a new
  icon to update an existing map.

## [0.9.41] — POI "add" popup matches the normal place popup

### Changed
- **The "add this place" popup for Google Maps POIs (0.9.40) now reuses
  the same popup layout as an existing place** — photo, category badge,
  rating/price, address, hours grid, and website/Tabelog/Instagram links —
  with editable category, notes, and tags fields, and a single "＋ Add"
  button. Previously it was a separate bare modal with just a category
  dropdown.

## [0.9.40] — Tapping a Google Maps POI offers to add it, not a blank pin

### Changed
- **Clicking a labeled point of interest on Google Maps** (a restaurant,
  shop, landmark, etc.) now looks up that place's details — name,
  address, hours, rating, and a guessed category — and shows an "＋ Add
  to map" dialog for it, the same data you'd get by searching for it.
  Previously every map click, including taps on POIs, dropped a generic
  "Drop a pin" with no name or details.
- Clicking empty map area (no POI under the tap) still opens the plain
  "Drop a pin" dialog as before.

## [0.9.39] — Lock down category editing in view-only mode

### Fixed
- **Categories could still be added/renamed/recolored/merged/deleted while
  viewing a shared map read-only.** The "＋ New category" button is now
  hidden, and the Categories dialog opens in a view-only list (no add
  form, no "Edit ›" links) when `ui.readOnly` is set.

## [0.9.38] — Maps always need a place to live

### Changed
- **"Local only" maps are no longer a thing.** A map should always have a
  place it's saved to (your Drive folder) or, for view-only links, a place
  it's read from. If you arrive without a `?map=` link and you're not
  signed in to Google with a Drive folder connected, a full-screen "Welcome
  to Wandermark" gate now asks you to sign in and pick/create a folder
  before you can create or edit any map.
- Opening a shared map link (`?map=...`) is unaffected — it still opens
  view-only without requiring sign-in.
- Any maps that were already saved locally before this change get
  automatically pushed to your Drive folder the moment one is connected
  (`publishAllUnpublished`), so nothing is lost.

## [0.9.37] — Don't attempt silent re-auth on devices that never signed in

### Fixed
- **On boot, a window could briefly flash open and close on mobile**,
  even while signed out. This was Wandermark trying a silent Google
  re-auth (`prompt:"none"`) on every boot if Drive was configured —
  Google Identity Services implements that "silent" check with a
  popup/tab on some mobile browsers. Now skipped entirely on devices that
  have never signed in to Drive, since there's no session to refresh.
  Devices that have signed in before are unaffected.

---

## [0.9.36] — Maps always have a place to live

### Added
- **"Connect a Drive folder" dialog**: if you create a new map (or
  duplicate/import one) and no Drive folder is connected yet, Wandermark
  now asks you to pick one immediately, then pushes the new map (and any
  other unpublished maps you own) there right away — instead of silently
  leaving it as a browser-only map with just a toast you could miss.
- **"Heads up" nudge for orphaned edits**: if a map somehow has unsaved
  changes but still isn't connected to Drive, you'll get a toast (at most
  once every 10 minutes) pointing you at 🗂️ Map ▾ to connect a folder.

### Philosophy
- Wandermark maps are meant to be available anywhere and shareable — a
  map that only exists in one browser's local storage is treated as a gap
  to close, not a normal state. View-only "Shared with you" maps are
  unaffected; they already read from someone else's Drive file.

---

## [0.9.35] — Drop the redundant "Update on Drive" button

### Changed
- **Removed "⤴ Update on Drive"** for maps that are already published to
  Drive and have no unsaved changes — there was nothing for it to push.
  "⤴ Publish to Drive" (for new/unpublished maps) and "⤴ Push edits" (for
  maps with pending changes) are unchanged; edits to published maps still
  auto-push to Drive ~12s after you make them.

---

## [0.9.34] — Map type and a proper rename dialog

### Added
- **"Rename" (in the "Your maps" list) now opens a dialog** instead of a
  bare browser `prompt()`, and it also lets you set the map's **type**:
  🧳 Personal or ⭐ Curated.

### Changed
- **Personal maps now show a 🧳 suitcase icon** (next to the map name and
  in "Your maps") instead of 🗂️, which read more like a Drive/folder
  status indicator than "this is your map". Curated maps still show ⭐.

---

## [0.9.33] — The actual ghost circle, take two

### Fixed
- **The "second circle" overlapping "My location" on Google Maps** was
  Google's unified "camera control" — a circular pan/zoom/rotate widget
  that Google Maps adds separately from (and in addition to) the legacy
  zoom/rotate controls, and which defaults to the bottom-right regardless
  of `zoomControlOptions`/`rotateControlOptions`. Disabled it with
  `cameraControl:false`.

---

## [0.9.32] — Mobile header layout, sign-in box, and the real ghost-circle fix

### Changed
- **Map name button** (top of page) no longer truncates with `…` on
  mobile — it now shares a row with the ⋯ menu and wraps onto a second
  line for long names.
- **"Switch account" / "Sign out"** buttons in the Drive sign-in box now
  sit together on their own row below the "Signed in as…" text, instead
  of one wrapping awkwardly below the other on narrow screens.
- **Removed the 🗺️ Map / ▦ Table tab toggle from the header.** Map is
  now the only view shown by default; switch to the spreadsheet via
  ⋯ → "Spreadsheet view" (still has its own "✕ Back to map" button).

### Fixed
- **The actual "second circle" overlapping "My location"** turned out to
  be Leaflet's attribution control — on narrow screens it collapses to a
  small circular "i" toggle, anchored bottom-right by default, right on
  top of our button. Moved Leaflet's attribution control to the
  bottom-left (Google Maps' zoom/rotate controls were already moved
  there in 0.9.31).

---

## [0.9.31] — Map ownership on new devices, account info, control overlap

### Fixed
- **Your own maps no longer show up under "Shared with you" on a device
  where they were pulled down via Drive sync** (e.g. signing in on
  mobile after a map was created/published on desktop). New maps added
  during a sync now check Drive's `owners(me)` field to determine
  whether you own the file; already-synced maps that were
  misclassified are corrected on the next sync too.
- **The "second circle" next to the "My location" button was Google
  Maps' own zoom/rotate control**, which defaults to the bottom-right
  corner — directly under our button. It's now anchored bottom-left
  instead, so the two no longer overlap. (The `filter:drop-shadow`
  change from 0.9.30 is harmless but wasn't the actual fix.)

### Added
- **The Drive sign-in box now shows who you're signed in as** (email or
  name, via Drive's `about` endpoint), with **"Switch account"** and
  **"Sign out"** buttons — previously it just said "Signed in to
  Google" with no way to change or clear the session short of clearing
  site data.

---

## [0.9.30] — Map name layout + another ghost-circle attempt

### Changed
- **"Your maps" list:** the map name now always sits on its own line
  above its action buttons (Rename/Duplicate/Delete/etc.), instead of
  being squeezed into the remaining horizontal space to their left on
  narrow screens.

### Fixed
- Another attempt at the faint duplicate "ghost" circle next to the "My
  location" button, which 0.9.28's `transform:translateZ(0)` didn't
  resolve (still present on Android and Windows Chrome). Switched the
  button's shadow from `box-shadow` to `filter:drop-shadow(...)`, which
  follows the rendered alpha shape rather than a separate rounded-rect
  geometry and shouldn't suffer the same subpixel mismatch.

---

## [0.9.29] — Longer-lived Google Drive sign-in

### Changed
- The cached Google Drive access token now lives in `localStorage`
  instead of `sessionStorage`, so signing in once carries over across
  browser/tab restarts (not just page refreshes within the same tab).
  It's still a real OAuth access token, so it still expires after about
  an hour either way.
- On boot, if there's no valid cached token but Drive is configured,
  Wandermark now tries a silent (no-popup) re-auth via Google Identity
  Services first. If that succeeds you're signed back in with no action;
  if it fails (e.g. no active Google session, or third-party cookies
  blocked), the "🔑 Sign in to Google" badge appears as before.

---

## [0.9.28] — Attempt fix for ghost circle next to "My location" button

### Fixed
- On Chrome/Windows (commonly with display scaling other than 100%), a
  faint duplicate circle outline could appear offset next to the "My
  location" button — likely a subpixel rendering artifact from
  `box-shadow` + `border-radius:50%` on an absolutely positioned element.
  Forced the button onto its own compositor layer with
  `transform:translateZ(0)`, which typically resolves this class of
  Chrome rendering glitch.

---

## [0.9.27] — Replace "My location" icon with inline SVG

### Fixed
- The ⌖ Unicode glyph used for the "My location" button rendered with
  extra/offset strokes on some Android fonts, looking like a duplicate
  circle or broken shadow next to the button. Replaced with a small
  inline SVG crosshair icon for consistent rendering everywhere.

---

## [0.9.26] — Wrap long map names in "Your maps"

### Fixed
- On narrow screens (e.g. Android Chrome), map names in the "Your maps"
  list were truncated with `…` because there wasn't enough horizontal
  room next to the action buttons. Names now wrap onto additional lines
  instead of being cut off.

---

## [0.9.25] — Fix "My location" button cut off on mobile Chrome

### Fixed
- The ⌖ "My location" button was anchored to `bottom: 24px` of an `#app`
  shell sized with `100vh`. On mobile Chrome, `100vh` is taller than the
  visible viewport when the address bar/bottom toolbar are showing, so the
  button could render below the fold and be inaccessible. The app shell now
  uses `100dvh` (with a `100vh` fallback), and the button additionally
  insets by `env(safe-area-inset-bottom)` for devices with a home indicator.

---

## [0.9.24] — "My location" button

### Added
- New ⌖ "My location" button at the bottom-right of the map. Tapping it
  asks for your browser/device location, drops a Google-Maps-style blue
  dot at your position, and pans the map there — so you can see where
  places are relative to you on mobile. Works in both OpenStreetMap and
  Google Maps modes, and the dot persists across map refreshes and engine
  switches.

---

## [0.9.23] — Fix "Enrich from Google" crash on findPlaceFromQuery

### Fixed
- Every lookup for a place without a `placeId` threw `Uncaught
  InvalidValueError: in property locationBias: ...` and was skipped. The
  Maps JS API's `findPlaceFromQuery` requires `locationBias` as a `Circle`
  object (`{center:{lat,lng},radius}`), not the web-service
  `"circle:radius@lat,lng"` string format used by `enrichFromGoogle`.

---

## [0.9.22] — Enrich from Google: diagnostic logging

### Added
- "✨ Enrich from Google" now logs the Places API status code to the console
  (`[enrich] ...`) for any lookup that doesn't return `OK`, to help diagnose
  why places aren't being found/updated.

---

## [0.9.21] — Enrich from Google: don't hang on blocked requests

### Fixed
- "✨ Enrich from Google" could hang indefinitely (no toast, no update) if a
  single Places API request was silently dropped — e.g. by an ad blocker or
  privacy extension. Each lookup now has an 8s timeout and falls through to
  the next place if it doesn't respond. Progress toasts now appear every 10
  places so it's clear it's working.

---

## [0.9.20] — Enrich from Google

### Added
- **"✨ Enrich from Google" (⋯ menu, Google Maps mode).** A one-time pass over
  every place on the map that fills in (without overwriting existing data):
  - Photo and Google Maps link
  - A coarse genre badge (e.g. "Italian", "Cocktail bar", "Café")
  - Star rating and price level ($–$$$$)
  - Hours, website, and address for places that don't have them yet

  Places that already have a Google place ID are refreshed directly; places
  imported without one (e.g. from CSV/curated lists) are matched by name +
  address via a "Find Place" lookup first. Results are saved into the map
  data, so it's a one-time cost for the map owner, not per-viewer.
- Genre, star rating, and price level now show in the place list and in the
  map popup for any place that has them.

---

## [0.9.19] — Share link fixes + collaborator management

### Added
- **Collaborator management.** New "👥 Manage access" button in the share
  modal and a "👥 Share" button on each of your Drive-published maps in the
  maps list. Opens an "Access" modal showing:
  - The share link with a copy button
  - A toggle for "Anyone with the link can view" (creates/removes the Drive
    `anyone → reader` permission, no sign-in required to view)
  - Current collaborators (name, email, role) with a Remove button
  - "Add person" form: enter any Google email, pick Editor or Viewer, hit Add
  Changes sync immediately to the Drive file's permissions.

### Changed
- **Single share link instead of two.** The old `?view=<id>` (always read-only)
  and `?map=<id>` (editable after sign-in) links have been merged into one:
  `?map=<id>`. Access level is determined by whether the recipient is signed in
  and has Drive write access. Old `?view=` links from v0.9.18 still open
  correctly (treated as `?map=` links going forward).

### Fixed
- **Empty "My map" no longer appears** when opening a shared link in a fresh
  browser session. The default placeholder map created at boot is removed as
  soon as the linked map loads.
- **Opening the same link twice no longer creates duplicates.** If a map with
  the same Drive file ID is already in the map list, it's updated in place
  rather than added as a second entry.

---

## [0.9.18] — Link-based map sharing

### Added
- **Share links for public and collaborative access.** The "Share this map
  (code)" modal (`⋯` menu → Share) now shows two copyable URLs when the
  active map has been published to Drive:

  - **Public link** (`?view=<driveFileId>`) — view-only, no sign-in needed.
    Set the Drive file's sharing to "Anyone with the link → Viewer" and
    anyone can open the map and explore it. Editing controls (Save/Delete
    in place popups, search to add places) are hidden.
  - **Collaborative link** (`?map=<driveFileId>`) — opens in view-only mode
    for anyone not signed in, but shows a "Sign in to edit" bar at the top.
    After signing in, the full editing UI unlocks. You must share the Drive
    file with specific people as Editor for them to save changes.

  If the map hasn't been published to Drive yet, the share modal shows a
  hint to publish first.

- **URL param routing.** Opening `wandermark.html?view=<id>` or
  `?map=<id>` fetches the Drive file at boot and shows it as the active
  map. The link can be opened by anyone — they don't need to have ever
  used Wandermark before.

- **`index.html` redirect now preserves query parameters**, so short links
  like `kabigone.github.io/Wandermark/?view=<id>` (without `wandermark.html`)
  also work correctly.

---

## [0.9.17] — Make sidebar always accessible regardless of browser mode

### Fixed
- **The ☰ sidebar toggle and the sidebar itself were inaccessible on some
  phones regardless of how the CSS media queries were tuned.** The entire
  "show the toggle / make the sidebar off-canvas" mechanism was conditional
  on a CSS media query matching. On some devices (e.g., "Request Desktop
  Site" mode in Chrome Android, unusual browser configurations, WebViews
  with non-standard viewport or pointer reporting) no combination of
  `max-width` and `pointer: coarse` was reliably matching.

  The fix removes the dependency on media queries for the two critical
  behaviors:
  1. **The ☰ toggle is now always visible** — `display:inline-flex` in the
     base CSS, no media query required.
  2. **The sidebar is now always off-canvas** — `position:absolute` +
     `transform:translateX(-104%)` in the base CSS (moved out of the media
     query). It slides in/out the same way at every viewport width.

  On a non-touch desktop (mouse/keyboard), the sidebar opens automatically
  on boot so the experience is identical to before. On any touch device —
  phone or tablet, narrow or wide, normal or "Request Desktop Site" — the
  sidebar starts closed and ☰ always opens it.

---

## [0.9.16] — Fix sidebar toggle disappearing with "Request Desktop Site"

### Fixed
- **The ☰ sidebar toggle (and mobile layout) vanished when Chrome Android's
  "Request Desktop Site" was enabled.** The mobile layout was gated purely on
  viewport width (`max-width: 820px`). "Request Desktop Site" tells Chrome to
  report a ~980 px desktop viewport, which is wider than 820 px — so the
  mobile media query never fired, `.mobile-toggle` stayed `display: none`,
  and the ☰ button was completely gone (invisible and non-tappable). The
  sidebar still existed in the DOM but only as a 344 px desktop side-panel
  scaled down to ~145 px physical pixels — completely impractical.

  The media query now also matches any touch-only device
  (`(hover: none) and (pointer: coarse)`), which remains true on a phone
  regardless of the desktop-site flag. Any phone or tablet — whether or not
  "Request Desktop Site" is on — now always gets the proper off-canvas drawer
  layout with a working ☰ toggle.

---

## [0.9.15] — Fix the squished mobile search bar

### Fixed
- **The search bar could shrink down to an unusable bare icon on phones.**
  In the header, the search box sat in the same flex row as the map-name
  button and the "🔑 Sign in to Google" badge. At very common phone widths
  (roughly 360-430px — most current Android and iPhone models), the row just
  barely fit without wrapping, so the search box — the only flexible item —
  got squeezed down to almost nothing instead of wrapping to its own line.
  It now always gets its own full-width row on phones, so it's reliably
  visible and tappable regardless of how long the active map's name or the
  sign-in badge happen to be.

---

## [0.9.14] — Maps are organized by ownership now, not by where they live

### Changed
- **Merged "My maps" and "☁️ Shared from Drive" into "Your maps" / "Shared with
  you"** — the same ownership model Google My Maps uses. The old idea of a map
  living only in your browser until you remembered to "Publish" it is gone:
  every map you create now publishes to your connected Drive folder right
  away (and shows up immediately under "Your maps" with its ☁️/Drive status),
  and any older map that was still sitting locally gets swept up to Drive the
  moment you connect a folder. "Yours" is always fully editable — rename,
  duplicate, delete, like before; "shared with you" stays editable only if its
  owner gave your account Drive edit access, exactly as collaborative editing
  already worked.
- The 🗂️ map-button badge and the ⭐ "curated/imported" cue now reflect
  ownership rather than publish status, so duplicating one of your own already-
  published maps correctly says "Duplicated" (not "Copied to your maps"), and
  renaming an owned map now pushes the new name to Drive instead of going
  stale until some unrelated edit syncs it.

---

## [0.9.13] — See whose folder you've connected to

### Added
- **The "Connected to ___" confirmation now names the folder's owner** when
  it isn't you — e.g. "Connected to Wandermark — shared by Alex" instead of
  just "Connected to Wandermark." When a friend shares their Wandermark
  folder with you and you land on it (whether auto-detected or hand-picked),
  you immediately know it's *theirs* and that you're in the right place,
  rather than wondering whether you've actually found the shared folder or
  just something of your own with a similar name. (Best-effort: quietly
  omitted if the lookup fails, or you connected without signing in.)

---

## [0.9.12] — Background sync survives a long session

### Fixed
- **Quiet Drive updates could go stale mid-session.** The background pull
  (the thing that shows collaborators' new places without you refreshing)
  reads the folder using your signed-in Google account when you're connected
  — but if your ~hour-long token quietly expired while the tab stayed open,
  it silently fell back to the public API key, which can't see a **privately
  shared** folder. Updates would then stop appearing — looking like "spotty"
  sync — until you noticed the 🔑 Sign in badge and reconnected by hand. Now
  the periodic check refreshes an expired-but-known token silently first (the
  same no-popup trick auto-push already relies on), so a long session keeps
  pulling fresh data without you having to do anything.

---

## [0.9.11] — Sign-in sticks, and folder pick is automatic

### Changed
- **Sign-in now survives refreshes and tab switches.** The OAuth access token
  used to live only in a JS variable, so any reload wiped it and brought back
  the sign-in prompt — even though the token itself was still valid for ~an
  hour. It's now mirrored to `sessionStorage` and restored on launch, so you
  only have to sign in again when the token actually expires (or you close the
  tab), not on every refresh. (Note: this is `sessionStorage`, not
  `localStorage` — it's scoped to the browser tab/session on purpose, since an
  access token is a short-lived credential that shouldn't outlive it.)
- **Folder selection is now automatic when it can be.** Right after you sign
  in, Wandermark looks for a Drive folder whose name contains "wandermark"
  (owned by you or shared with you) and connects to it straight away — no
  picker, no clicking around. The picker only appears if it finds none or more
  than one candidate, so you can point it at the right one by hand.

---

## [0.9.10] — Read access for privately-shared folders

### Added
- **Drive sync now works with folders shared privately with specific people**,
  not only ones shared "Anyone with the link." When you're signed in, listing
  the folder and downloading its map files (`driveListFolder`/`driveFetchFile`)
  now authenticate as **you** (your OAuth token) instead of relying solely on
  the embedded public API key — falling back to the API key automatically when
  you're signed out, so public-folder sync keeps working exactly as before.

### Why this matters
- This unlocks a better sharing model for privacy-conscious owners: share your
  folder directly with named friends' Google accounts (Viewer, or Editor to
  let them edit too) instead of "Anyone with the link." That keeps the folder
  out of public reach **and** — as a bonus — makes it actually show up in their
  📁 folder picker, since Drive only surfaces folders that were explicitly
  shared with an account in "Shared with me" / browsing views.
- Friendlier error message when a folder genuinely isn't accessible: it now
  tells you whether to double-check the link (public-folder path) or to sign in
  with the account the folder was shared with (private-folder path).

---

## [0.9.9] — Reverted: silent sign-in on launch

### Changed
- **Backed out the 0.9.8 "try silent re-auth on launch" change.** In practice,
  for an OAuth app still in Google's **"testing"** publishing status with the
  restricted full-`drive` scope, the silent (`prompt:"none"`) flow doesn't
  succeed quietly — Google flashes its **own** brief error popup ("you don't
  have access / you're not a test user") on every page load before failing,
  which is more disruptive than just showing the **🔑 Sign in to Google** badge
  and letting you click it (the manual `consent` flow reliably works because it
  lets you pick the right account). One click to reconnect remains the way to
  go until the OAuth app is verified — at which point silent re-auth should
  behave better and this could be revisited.

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
