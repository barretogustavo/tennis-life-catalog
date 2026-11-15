# Contributing

- Keep `id` stable once published (slug of brand + model).
- Specs are manufacturer references (unstrung for rackets). Users can override them in the app.
- No copyrighted product photos — text/specs only.
- After editing JSON, run:

```bash
node scripts/build_index.mjs
node scripts/validate.mjs
```
