# Roku Reef

A photoreal, never-repeating coral reef screensaver. Real photo cut-outs of fish, corals and creatures are animated procedurally: the fish swim with lateral tail motion, school, graze and flee, and the reef is generated fresh each time. The goal is to run it as a screensaver on a Roku TV.

**Status:** the browser prototype in `poc/` is the working reference. The Roku port (BrightScript/SceneGraph) is **not built yet**. See [Getting it onto a Roku TV](#getting-it-onto-a-roku-tv) for the plan and the exact steps.

---

## Run the prototype (Mac / any desktop browser)

**Quickest:** open `poc/index.html` in Chrome.

```bash
open -a "Google Chrome" poc/index.html
```

**Recommended (needed for the `?bench` / `?fpsprof` debug modes):** serve it locally.

```bash
cd poc && python3 -m http.server 8765
# then visit http://127.0.0.1:8765/
```

The scene renders at 1920×1080 and scales to fit the window. Go full screen (⌃⌘F) for screensaver mode.

> **Frame rate:** Chrome caps animations at 30 fps when Energy Saver is on (automatically below 20% battery). Plug in, or turn it off in Chrome → Settings → Performance.

### Keyboard controls

| Key | Action |
|---|---|
| **S** | send a shark past |
| **T** | sea turtle |
| **M** | manta / eagle ray |
| **J** | jellyfish |
| **O** | bring the octopus out at the centre of the screen |
| **C** | start a chase between two fish |
| **R** | drift (fade) to a newly generated reef |
| **N** | instantly load a new reef (new random seed) |
| **P** | pause |
| **D** | stats overlay (fps, seed, counts) |

### URL options

| Param | Meaning |
|---|---|
| `?seed=123` | reproducible reef layout |
| `?regen=1200` | seconds between automatic reef regenerations (default 20 min) |
| `?day=2400` | seconds per day-light cycle (default 40 min) |

Debug and test modes (for development): `?t=30` renders one frame after 30 simulated seconds (add `&spawn=1` to force a turtle, ray, jellies and octopus, or `&shark=25` to set when the shark arrives). The others are `?film=<species>[&turn=1][&peck=1]` (filmstrip of one fish), `?swimtest`, `?turntest=yellowtang,lion`, `?pitchtest`, `?raytest`, `?rigtest`, `?crawltest`, `?octotest`, `?eeltest&ext=.6`, `?sharklog`, `?bench` (per-stage cost; serve over http) and `?fpsprof` (real-fps sweep that toggles each feature).

---

## What's in the scene

- **Three parallax depth layers** (far / mid / near), with depth-of-field blur, water fog and a slow side-to-side camera pan.
- **Fish:** about 20 photo species, drawn as 2.5D sliced bodies (real lateral yaw while swimming; turns swing the head toward the camera with a head-on photo cross-fade where one exists) (tangs, angelfish, moorish idols, clownfish in anemones, lionfish, groupers, parrotfish, wrasse, triggerfish, puffers, anthias and chromis schools, damselfish clouds). They move with heading-based steering, turns, kick-and-glide gaits and body arcs when pitching. Grazers bite the coral (parrotfish leave grit puffs). Everything flees the shark.
- **Other creatures:** blacktip reef sharks, sea turtles (rigged flippers), manta and eagle rays, moon and golden jellies, moray eels in burrows, an octopus (crawls, camouflages, hides, inks), and crabs, hermit crabs, lobster and shrimp.
- **Reef:** procedurally generated, with about 40 photo coral and sponge types, rock and sand textures, tall pinnacles, see-through arches and caves.
- **Light:** god rays, caustics on everything, surface shimmer, fish shadows, passing clouds, a slow midday-to-afternoon cycle and water surge.

## Repository layout

```
poc/                     the prototype (open index.html)
  index.html             all simulation + rendering code
  v1.html                first vector-art prototype (historical)
  assets/fish/           normalized fish cut-outs + fish.js metadata
  assets/coral/          coral/sponge/anemone cut-outs + coral.js metadata
  assets/fx/             rays, turtles, jellies, crustaceans, octopus + fx.js
tools/                   asset pipeline
  commons_search.py      search Wikimedia Commons -> contact sheets
  inat_search.py         search iNaturalist (CC0/BY/BY-SA, research grade) -> contact sheets
  fetch.py, fetch_inat.py  download chosen photos (records attribution)
  cutout.js              Apple Vision subject lift (run with: osascript -l JavaScript tools/cutout.js in.jpg out.png [largest|all|N])
  lumakey.py             alpha from brightness, for subjects shot on black
  normalize.py           fish cut-outs -> poc/assets/fish (flip/rotate/crop/trim)
  normalize_coral.py     coral cut-outs -> poc/assets/coral (edge feathering)
  make_fronts.py         head-on photos -> poc/assets/front (colour-matched to the side photo they pair with)
  bake_textures.py       ambientCG (CC0) PBR sets -> pre-lit rock/sand/pebble textures in poc/assets/tex
  hires_corals.py        re-fetch coral photos at full resolution + re-cut (feeds normalize_coral.py)
  make_credits.py        regenerate CREDITS.md
  sheet.py               contact sheet of PNG cut-outs
assets_src/
  fish_config.json, coral_config.json   which source photo becomes which asset
  candidates/*.json, inat/*.json        saved search results (license + attribution)
CREDITS.md               attribution for every photo used
```

### Adding or replacing an animal or coral

1. Search: `python3 tools/inat_search.py assets_src/inat "key=Genus species"`, then look at `assets_src/inat/key_sheet.jpg`.
2. Download: `python3 tools/fetch_inat.py assets_src/inat assets_src/raw key:INDEX`.
3. Cut out: `osascript -l JavaScript tools/cutout.js "$PWD/assets_src/raw/i_key_INDEX.jpg" "$PWD/assets_src/cut/i_key_INDEX.png" largest`.
4. Add an entry to `assets_src/fish_config.json` or `assets_src/coral_config.json`, then run `tools/normalize.py` or `tools/normalize_coral.py`. Fish must end up **facing right**; use `"flip": true` or `"rot": deg` to fix them.
5. Run `python3 tools/make_credits.py`.

Notes: use `osascript` (JavaScript for Automation) for the cutout. `swiftc` currently fails on this Mac because of a Command Line Tools/SDK mismatch. Wikimedia rate-limits aggressively (HTTP 429), and iNaturalist is more reliable.

---

## Getting it onto a Roku TV

### What Roku runs

Roku apps (including screensavers) are written in **BrightScript** with the **SceneGraph** XML UI framework, not JavaScript. A screensaver is a normal Roku app whose `manifest` declares it as a screensaver and whose code provides a `RunScreenSaver()` entry point. The prototype can't be copied over directly. It has to be **ported**:

- **Sprites, not canvas drawing.** Roku draws images (`Poster` nodes) and moves them; it has no per-pixel canvas API. Every effect the prototype computes per frame (the swimming body warp, turtle flippers, octopus arms) is **pre-rendered into short sprite-sheet animations** by a bake script that reuses this prototype's renderer. The Roku then just plays the frames and moves the sprites.
- **Same behaviour.** The steering, schooling, grazing, shark/turtle/ray events and reef generation logic port directly to BrightScript.
- **Budget.** Roku devices are far weaker than a Mac. Expect fewer fish on screen and baked lighting (rays, caustics and shadows as animated overlay images), at 1920×1080 UI resolution.

### Step 1: enable Developer Mode on the TV (one time, free, no account needed)

1. On the Roku remote press: **Home ×3, Up ×2, Right, Left, Right, Left, Right**.
2. The Developer Settings screen appears. **Write down the IP address** shown (for example `http://192.168.1.50`).
3. Choose **Enable installer and restart**, accept the SDK license, and **set a password** (the username is always `rokudev`).
4. The TV restarts. Your Mac and the TV must be on the same Wi-Fi/LAN.

### Step 2: build the app package (once the port exists)

The Roku app will live in `roku/` with this layout:

```
roku/
  manifest              # title, version, icons, splash, and the screensaver entries below
  source/main.brs       # RunScreenSaver() -> creates the SceneGraph scene
  components/*.xml/.brs # Reef scene, fish/sprite components, behaviour
  images/               # baked sprite sheets, reef layers, overlays
```

Key manifest lines for a standalone screensaver:

```
screensaver_title=Roku Reef
major_version=1
minor_version=0
build_version=1
ui_resolutions=fhd
```

Zip the **contents** of `roku/` (not the folder itself):

```bash
cd roku && zip -r ../roku-reef.zip . -x "*.DS_Store" && cd ..
```

### Step 3: sideload it

**Browser:** go to `http://<TV-IP>`, log in as `rokudev` with your password, choose **Upload**, select `roku-reef.zip`, then click **Install**.

**Command line:**

```bash
curl --user rokudev:YOURPASSWORD --digest -s -S \
  -F "mysubmit=Install" -F "archive=@roku-reef.zip" \
  http://<TV-IP>/plugin_install
```

Then on the TV go to **Settings → Theme → Screensavers**, select **Roku Reef**, and set the wait time. Only one sideloaded app can be installed at a time, and installing a new zip replaces it. It stays installed until you remove it or disable Developer Mode.

### Optional: publish to the Roku Channel Store

Sideloading is enough for your own TV. To make it installable on any Roku, or to share it:

1. Create a free account at **developer.roku.com**, then enroll in the developer program and accept the agreements.
2. Package the app: on the TV's developer page, use **Packager**, which needs a signing key generated on the device (`genkey` over telnet port 8080). That produces a signed `.pkg`.
3. In the developer dashboard, create a new app, upload the `.pkg`, and fill in the store listing (icons, description, screenshots, privacy policy).
4. Submit it for **certification**. Roku's certification rules for screensavers are strict, and developers have reported false positives for standalone screensavers, so expect some back-and-forth. Keep only `screensaver_title` (no plain `title`) if static analysis flags it as an "in-channel screensaver".
5. Alternatively, publish as a **beta channel**: invite-only, without full certification, and limited to a set number of testers' devices.

**Licensing:** before distributing, make sure every photo's license allows it and that credits are shown (for example on a screensaver settings or about screen). See `CREDITS.md`. CC BY-SA images require derivatives to be shared under the same license.
