# Tennis Life Catalog

Public equipment catalog for the [Tennis Life](https://github.com/barretogustavo/tennis-life) app.

Specs only (weight, head size, string tension suggestions, court type, bag capacity). No product photos.

## Raw URLs

Primary:

```
https://raw.githubusercontent.com/barretogustavo/tennis-life-catalog/main/data/index.json
```

Fallback CDN (jsDelivr):

```
https://cdn.jsdelivr.net/gh/barretogustavo/tennis-life-catalog@main/data/index.json
```

`raw.githubusercontent.com` is **not** covered by the GitHub REST API rate limit (60 req/h unauthenticated). GitHub may still return HTTP 429 under heavy IP traffic. The app caches files locally and falls back to jsDelivr.

## Files

| File | Contents |
| --- | --- |
| `data/index.json` | Version, `updatedAt`, per-file `sha256` + counts |
| `data/rackets.json` | Rackets with unstrung specs |
| `data/strings.json` | Strings with gauge / type / suggested tension |
| `data/shoes.json` | Shoes (`court`) |
| `data/balls.json` | Balls (`pressurized`, `tubeCount`) |
| `data/bags.json` | Bags (`racketCapacity`) |
| `data/accessories.json` | Grips, dampeners, etc. |
| `data/apparel.json` | `brands` + `pieces` |

Envelope for item lists:

```json
{ "schemaVersion": 1, "items": [ { "id": "...", "brand": "...", "model": "..." } ] }
```

## Contribute

1. Edit or add items under `data/*.json` (stable `id`, unique brand+model).
2. Run `node scripts/build_index.mjs` then `node scripts/validate.mjs`.
3. Open a PR. CI re-validates hashes and uniqueness.

To regenerate from the generator script:

```bash
python3 scripts/generate_catalog.py
node scripts/build_index.mjs
node scripts/validate.mjs
```

## License

Data: [CC BY 4.0](LICENSE).
