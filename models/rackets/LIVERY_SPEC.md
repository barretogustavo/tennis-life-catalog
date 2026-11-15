# Racket livery spec

Each racket in `data/rackets.json` has a livery file at `models/rackets/liveries/<id>.json`.
`scripts/generate_racket_models.py` reads it and builds `models/rackets/<id>.glb` on top of the
shared low-poly racket geometry. A livery describes **where each color sits** on the real racket
(front view, racket upright, head on top), simplified to the parts the model has.

## Model parts

```
             90° (12 o'clock, top of head)
                  ____
   180° (9h)    /      \    0° (3h)
               |  head  |
                \______/
          ~235°  \    /  ~305°     <- head meets throat around 235..305
                  \  /   throat: two arms (left/right) forming a "V" + bridge at the top
                   ||    shaft (short section above the handle)
                   ||    handle + grip wraps
                   []    butt cap (+ thin band above it)
```

- Angles go **counter-clockwise from 3 o'clock**: 0 = right side, 90 = top, 180 = left side,
  270 = bottom (where the throat attaches). Use range `-90..270`.
- `head`: ordered list of segments that together cover the whole loop from `-90` to `270`
  with no gaps or overlaps. Each segment names a palette role.
- Left/right are as seen by someone looking at the racket's front face (string bed facing you).

## Schema

```json
{
  "id": "babolat-pure-drive",
  "year": "2021 (11th gen)",
  "source": "https://... (page or image URL you actually looked at)",
  "notes": "One or two sentences describing the real paint job.",
  "palette": {
    "main":   "#1278E4",
    "second": "#181A1E",
    "third":  "#F5F7FA",
    "fourth": "#1278E4"
  },
  "finish": "gloss",
  "head": [
    { "from": -90, "to": 22,  "role": "main" },
    { "from": 22,  "to": 58,  "role": "third" },
    { "from": 58,  "to": 112, "role": "main" },
    { "from": 112, "to": 200, "role": "second" },
    { "from": 200, "to": 270, "role": "main" }
  ],
  "bumper": "second",
  "throat": { "left": "main", "right": "main", "bridge": "main" },
  "throatGraphics": [
    { "side": "right", "from": 0.10, "to": 0.70, "role": "third", "style": "blocks" },
    { "side": "left",  "from": 0.55, "to": 0.66, "role": "third", "style": "solid" },
    { "side": "left",  "from": 0.05, "to": 0.30, "role": "second", "style": "solid" }
  ],
  "shaft": "main",
  "strings": "#34363A",
  "stencil": { "color": "#F5F7FA", "shape": "babolat" },
  "grip": "#181A1E",
  "wraps": "#282A2E",
  "collar": "second",
  "cap": "second",
  "capBand": "main"
}
```

### Fields

| Field | Meaning |
| --- | --- |
| `palette` | Up to 4 colors (hex, sRGB). `main` = dominant frame color. Unused roles may repeat another color. |
| `finish` | `gloss`, `satin`, `matte` or `metallic` — how the main paint looks. |
| `head` | Color segments around the head loop (see angles above). Be faithful: e.g. Pure Aero = yellow top/sides with black lower sides; Blade v9 = green with darker sides; Pro Staff = black with small accents. |
| `bumper` | Bumper guard color on top of the head (roughly 62°..118°). Role name. |
| `throat` | Base color of the left arm, right arm and the bridge at the top of the throat. Role names. |
| `throatGraphics` | 0–4 painted areas on the throat arms. `from`/`to` are fractions along the arm (0 = where it meets the head, 1 = down at the shaft). `style`: `solid` (one band) or `blocks` (5 short blocks, like lettering). |
| `shaft` | Role name. |
| `strings` | String color (hex). Use the factory/stock string color you see in photos; default `#E6E6DE` (natural) or `#34363A` (dark poly) if unclear. |
| `stencil` | Logo painted on the string bed. `shape`: `babolat`, `wilson`, `head`, `yonex`, `tecnifibre`, `dunlop`, `prince`, `volkl`, or `none`. `color` hex. |
| `grip` / `wraps` | Grip color and the slightly different wrap ridges (hex). |
| `collar` / `cap` / `capBand` | Role names for the grip collar, butt cap and the thin band above the cap. |

Keep it simplified but recognizable: someone who owns the racket should see it at a glance.
