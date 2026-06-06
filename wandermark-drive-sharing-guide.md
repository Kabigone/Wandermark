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

**One-time setup (each person):**
1. Owner: put your map JSON files in one Drive folder and share it
   **"Anyone with the link → Viewer."**
2. Owner: copy the folder's link (the `…/folders/XXXX` URL).
3. Each person: in Wandermark, **⋯ menu → ☁️ Sync with Google Drive**, paste the
   folder link and a **Google API key with the Drive API enabled**, tick
   *Auto-sync on open* if you like, and hit **Save & sync now**.

After that, every map in the folder shows up under **"☁️ Shared from Drive"** in
the 🗂️ map menu, and refreshes whenever you sync. Change a file in the folder and
everyone gets the update on their next open. No downloading, no importing.

**Good to know:**
- This path is **read-only** in the browser — synced maps can't be edited in
  place (use *Copy to my maps* to make an editable local copy). Saving edits
  *back* to Drive automatically would require Google sign-in **and** hosting the
  app at a fixed URL; that's a bigger build (happy to do it if you host it).
- The **API key** here is a *Drive* key. It can be the same Google Cloud project
  as your Maps key, but the **Drive API must be enabled** on it. If you open the
  app as a local file, use a key that isn't restricted by website (referrer), or
  host the app and restrict the key to that host.
- The folder must be shared **Anyone with the link**, or the key (which isn't
  signed in as anyone) can't read it.

> So the realistic split today: **loading is automatic** (folder → maps), and
> **saving** is still you (owner) dropping/replacing a JSON in the folder — until
> we add hosted sign-in for write-back.

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

Honestly: not live, and not without more machinery. With Drive, the realistic
workflow is **manual sync**:

1. One person is the "owner" of, say, `tokyo.json`.
2. They edit in the app, **Export JSON**, and **replace** the file in Drive.
3. Everyone else re-downloads and re-imports to get the update.

This works fine for a small group, but be aware:
- **No merging.** If two people edit at the same time, whoever uploads last
  wins, and the other's changes are lost.
- It's a snapshot exchange, not real-time collaboration.

If you later want true shared editing (everyone adds to one map at once), that
needs a small backend — a tiny serverless database or something like Firebase —
which is a bigger project than a single HTML file. Happy to build toward that if
the manual flow gets annoying.

---

## The Google Maps API key — keep it personal

- The key is **per person**. Each friend enters their own key in
  **🗺️ engine button → Connect Google Maps**.
- It's stored only in that person's browser. It is **never** written into
  `wandermark.html`, into exports, or into share codes.
- **Do not put your key in the shared Drive folder.** If someone needs Google
  search/photos, they get their own free key (Google's free tier is generous for
  personal use), or you skip it entirely — the app works fully in keyless
  **OpenStreetMap** mode for viewing and editing places.

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
> 1. Download `wandermark.html` from this folder and open it (double-click).
> 2. (Optional) Connect your own Google Maps key via the green map button for
>    better search & photos. It stays on your computer.
> 3. To load a city map: ⋯ menu → Import file → pick a `.json` from the `maps/`
>    folder. Switch between maps with the 🗂️ button at the top.
> 4. To share your version back: ⋯ menu → Export this map (JSON), and replace the
>    file in `maps/`.
