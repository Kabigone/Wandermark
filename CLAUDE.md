# CLAUDE.md — Wandermark

Context for Claude Code. Read this before making changes.

## What this is

Wandermark is a **personal, shareable travel-map web app in a single HTML file**
(`wandermark.html`) — no build step, no framework, no bundler. It runs by opening
the file in a browser. It's hosted on GitHub Pages and shared with friends.

- Live: https://kabigone.github.io/Wandermark/ (redirects to `wandermark.html`)
- Map engines: keyless **OpenStreetMap** (Leaflet) or **Google Maps** (user's API key).
- Optional **Google Drive sync**: reads a shared folder of map JSONs (API key) and,
  when signed in (OAuth), writes maps back so friends can collaborate.

## Files

| File | Purpose |
|------|---------|
| `wandermark.html` | The entire app (HTML + CSS + one big `<script>` IIFE). |
| `index.html` | Redirect to `wandermark.html` for a clean Pages root URL. |
| `tabelog_hyakumeiten_to_wandermark.py` | External scraper → Wandermark JSON. |
| `README.md` | **Architecture / code-map. Read this for how the code is laid out.** |
| `CHANGELOG.md` | Version history. |
| `wandermark-drive-sharing-guide.md` | End-user Drive setup guide. |

## Run & deploy

- **Run locally:** open `wandermark.html` in a browser (OSM mode works offline-ish).
- **Deploy:** commit to `main` and push. GitHub Pages serves the repo root and
  redeploys automatically (~1 min + CDN cache). There is no build.
- After pushing, the live version lags briefly; a hard refresh shows the new build.

## Non-negotiable conventions

1. **Keep it a single self-contained file.** No build tooling, no new runtime deps.
   The only external `<script>`s are: Leaflet + JSZip from `cdnjs.cloudflare.com`,
   Google Maps JS from Google, and Google Identity Services from
   `accounts.google.com`. Don't add npm/bundlers.

2. **Validate the inline JS after every edit.** The script is plain ES5-style JS in
   one `<script>` block. Extract it and run `node --check`:
   ```bash
   python3 - <<'PY'
   import re; html=open("wandermark.html").read()
   open("/tmp/app.js","w").write(re.findall(r"<script>(.*?)</script>", html, re.S)[-1])
   PY
   node --check /tmp/app.js && echo OK
   ```

3. **Watch the recurring quote bug.** Strings are built by concatenation. The
   repeated mistake is opening a segment with `'` and closing it with `"`, e.g.
   `'<td>...</td>";` — this is an unterminated string. It must end `';`.
   Quick scan (ignore the benign `</option>";` hit):
   ```bash
   grep -nE "'[^'\"]*\">[^'\"]*\";" wandermark.html
   ```

4. **Version + changelog on every change.** Bump `WANDERMARK_VERSION` (near the top
   of the `<script>`), add a `CHANGELOG.md` entry, and update the summary comment at
   the very top of `wandermark.html`. The version shows at the bottom of the ⋯ menu.

5. **Never commit unrestricted keys or secrets.** Per-user keys are entered in-app
   and stored in the browser only. The `CONFIG` block at the top of the script may
   embed *shared* credentials, but ONLY browser keys that are **referrer-restricted
   to the site** (the restriction is the protection) plus the OAuth Client ID
   (public by design). Never put an unrestricted key, OAuth client secret, or any
   server credential in the repo.

## Architecture in one paragraph

One IIFE, divided by `/* ===== section ===== */` banners (see README for the full
map). State model: `LIB` holds many maps; `state` always points at the active map,
so most code uses `state.places` / `state.categories`. Any mutation calls
`renderAll()`, which re-renders chips, list, markers (via the active engine adapter
`Engine`), table, and then `save()`s to `window.storage`→`localStorage`. The two
map engines (`LeafletEngine`, `GoogleEngine`) implement the same interface
(`ready/init/setView/getCenter/refresh/open/fit/resize/geocode/suggest`).

## Drive model (so changes here stay coherent)

- **Read** = API key listing a public folder + fetching each `.json` (no sign-in).
- **Write** = OAuth (full `drive` scope) → create/update files via the upload
  endpoint. A map's `driveId` ties it to its Drive file; `dirty` marks unpushed
  local edits (sync won't overwrite a dirty map). Last-writer-wins by design.

## Current state & likely next work

- Version **0.9.0**. Collaborative editing works; OAuth app is in "testing" (full
  Drive scope → users see the unverified-app screen; add them as test users).
- Candidate next tasks: marker clustering for big maps on mobile; Eater/Michelin
  scrapers in the same style as the Tabelog one; making the hours-derived filter
  thresholds adjustable; optional "publish to Drive" auto-push on edit.
