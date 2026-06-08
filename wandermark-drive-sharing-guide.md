# Sharing Wandermark with Google Drive

A simple, no-server way to share the app and your maps with friends. There are
two separate things you might share, and they work differently:

1. **The app** — `wandermark.html` (the program itself)
2. **The maps** — your places, exported as small `.json` (or `.csv`) files

---

## TL;DR — the recommended layout

Make one shared Drive folder and put this inside it:

```
📁 Wandermark  (shared with your friends)
├── wandermark.html          ← the app — everyone downloads this once
├── README.txt               ← optional: paste the "How to use" steps below
└── 📁 maps                   ← one file per city/trip
    ├── tokyo.json
    ├── kyoto.json
    ├── lisbon.json
    └── tabelog-ramen-tokyo.json
```

Then each friend:
1. Opens the shared folder, **downloads `wandermark.html`**, and opens it from
   their own computer (double-click the file).
2. Downloads whichever map files they want from `maps/`.
3. In the app: **⋯ menu → Import file** → picks a `.json`. Each import becomes
   its own map, switchable from the **🗂️ map menu** at the top.

That's it. No accounts, no keys shared.

---

## Automatic sync from a Drive folder (new — no more manual import)

Wandermark can now read a whole Drive folder and turn every map file in it into
a map automatically. This is the easiest way to share a *directory* of maps:
you maintain the folder, everyone else just opens the app.

**One-time setup (each person), all from 🗂️ Map ▾ ("Your maps") — that's the
front door for this:**
1. Owner: put your map JSON files in one Drive folder and share it with the
   group — either **"Anyone with the link"** (simplest, but the folder is then
   reachable by anyone who has the link), or, for a more private setup, **share
   it directly with each friend's Google account** (Viewer to read, Editor to
   also edit) — see "Keeping it private" below.
2. Each person: open **🗂️ Map ▾**, tap **🔑 Sign in to Google**, then
   **📁 Choose shared folder from Drive** — Google's own folder picker opens so
   you can browse and click the folder, no copying links out of Drive.

After that, every map in the folder shows up under **"☁️ Shared from Drive"** in
🗂️ Map ▾, and refreshes automatically. Change a file in the folder (or edit a
shared map right in the app, once you're signed in) and everyone gets the
update without downloading or importing anything — see "Can we all edit the
same map together?" below, because the answer is now **yes**.

**Good to know:**
- The hosted copy ([kabigone.github.io/Wandermark](https://kabigone.github.io/Wandermark/))
  has a working Drive connection and key built in — most people never touch a
  key at all. The picker needs you to be signed in and the app hosted at a
  fixed URL (OAuth doesn't work from a double-clicked local file).
- If you ever do need to point at a folder by hand (e.g. a different folder, or
  troubleshooting), there's a manual "paste a link + key" fallback in
  **🗂️ Map ▾ → ⚙ Advanced: Drive connection settings** — most people will never
  need to open it.
- The folder needs to be shared with the group (at least **Viewer** to read;
  **Editor** if you want them to publish/edit maps back to it too).

### Keeping it private (sharing with named people instead of "anyone with the link")

If you'd rather not have a folder anyone-with-the-link can reach — say you're
thinking about sharing the app more broadly later and don't want your personal
maps along for the ride — share the Drive folder directly with each friend's
**Google account** (their email, as Viewer or Editor) instead of "Anyone with
the link." Two things fall out of that automatically:

- **It stays private.** Only the accounts you named can read it — nothing
  about the folder is guessable or link-shareable.
- **It actually shows up in their picker.** Drive only surfaces folders that
  were explicitly shared with an account inside "Shared with me" / browsing
  views — "anyone with the link" folders are invisible there even though the
  person technically has access. Once you share directly with someone, signing
  in and tapping **📁 Choose shared folder from Drive** will show your folder
  right away, no searching.

When someone's signed in, Wandermark reads the folder **as them** (their own
Google access), so a privately-shared folder works exactly like a public one
once they're connected — they just need to be signed in for it to sync.

---

## Why you download the app instead of "opening" it in Drive

Google Drive can store `wandermark.html`, but it **won't reliably run it**.
Drive's in-browser preview doesn't execute the page's JavaScript (and Google
retired the old "host a website from Drive" feature). So treat Drive as a place
to **hand someone the file**, not to run it.

To share the app, you have two good options:

- **Easiest — share for download (recommended).** Put `wandermark.html` in the
  shared folder. Friends download it and open it locally. Done.
- **If you want a clickable link that just works** — host the single file on a
  free static host instead of Drive:
  - **GitHub Pages**, **Netlify Drop** (drag-and-drop the file), or **Cloudflare Pages**.
  - You'll get a URL like `https://yourname.github.io/wandermark.html` that
    anyone can open directly. The app still stores each person's data in *their*
    browser.

> Either way the app is the same single file — there's no install and no build step.

---

## Sharing maps (the actual places)

Your places live **inside each person's browser**, not in the HTML file. To move
a map between people, export it and share the small file.

**To send a map:**
- In Wandermark: **⋯ menu → Export this map (JSON)**. You get
  `wandermark-<mapname>.json`.
- Drop that file into the shared `maps/` folder (or just send it / paste a
  **share code** from **⋯ → Share this map**).

**To receive a map:**
- Download the `.json` and use **⋯ menu → Import file**.
- It appears as a **new map** — your existing maps are untouched.

CSV works too (**Export this map (CSV)**) if you'd rather edit it in a
spreadsheet; import the CSV the same way.

---

## "Can we all edit the same map together?"

Yes, once everyone's signed in (🗂️ Map ▾ → 🔑 Sign in to Google) and the folder
is shared as **Editor**: edits to a shared map auto-push to Drive a few seconds
after you stop typing, and the app quietly re-checks Drive in the background (and
right away when you switch back to the tab) so others' changes show up without a
manual refresh. It feels like a shared document.

Two things to know, both **by design, like Google My Maps**:
- **Last-writer-wins, no merging.** If two people edit the same map at the same
  moment, whoever's change reaches Drive last "wins" — you'll get a heads-up
  toast if that's about to happen to your unsaved edits.
- **No true real-time co-editing** (you won't see someone else's cursor as they
  type) — that would need a small backend (a serverless database, Firebase,
  etc.), a much bigger project than a single HTML file.

---

## The Google Maps API key — usually nothing to think about

- The hosted copy already has a shared, referrer-restricted key built in, so
  Google Maps mode "just works" there — nobody needs to find, paste, or manage
  a key. **🗺️ Map style** in 🗂️ Map ▾ is just an OpenStreetMap/Google toggle.
- **"Bring your own key"** only shows up as a small fallback link in that same
  panel, and only if the built-in connection fails (e.g. you're running the
  file locally rather than from the website). If you do enter your own, it's
  stored only in your browser — **never** written into `wandermark.html`, into
  exports, or into share codes. Don't put a key in the shared Drive folder.
- No key at all? The app still works fully in keyless **OpenStreetMap** mode
  for viewing and editing places.

---

## Importing your existing Google My Maps

Bonus, since you already have maps there:

1. In **Google My Maps**, open the map → **⋮ menu → Export to KML/KMZ**.
2. Choose **"Export to a `.KML` file"** (a `.kmz` also works).
3. In Wandermark: **⋯ menu → Import file** → pick the `.kml`/`.kmz`.
4. It comes in as a new map; your My Maps **layers become categories**.

You can then re-export it as Wandermark JSON and drop it in the shared `maps/`
folder like any other map.

---

## A ready-to-paste README for the shared folder

> **Wandermark — quick start**
> 1. Open the app at its hosted URL (or download `wandermark.html` and
>    double-click it — works offline-ish in OpenStreetMap mode).
> 2. Tap **🗂️ Map ▾** and **🔑 Sign in to Google**, then **📁 Choose shared
>    folder from Drive** to connect — its maps appear automatically.
> 3. Switch between maps, or copy a shared one to edit, all from **🗂️ Map ▾**.
> 4. Editing a shared map auto-saves back to Drive once you're signed in — no
>    exporting or replacing files needed.
