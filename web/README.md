# Symphony

Describe a vibe — a mood, a moment, a feeling — and Symphony recommends real songs that match it.

This is the web UI for the `applied-AI-system-final` project. It reuses the same recommendation idea as the Python CLI (`src/vibe_recommender.py`): embed a free-text query and rank a catalog of real Spotify tracks by cosine similarity. The catalog here is `data/songs_vibe.csv` (136 tracks, built via `src/catalog_builder.py`), precomputed into embeddings once and shipped as a static asset — so the deployed site makes **no live Spotify API calls and needs no Spotify credentials at runtime.**

## How it works

- `scripts/build_embeddings.mjs` reads `../data/songs_vibe.csv`, embeds each song's `"{title} by {artist}: a {genre} song"` blurb with the [`all-MiniLM-L6-v2`](https://huggingface.co/Xenova/all-MiniLM-L6-v2) model (via `@xenova/transformers`), and writes `src/data/songVectors.json`.
- In the browser, the same model embeds the user's query, and `src/lib/similarity.js` ranks the catalog by cosine similarity (both sides are L2-normalized at embed time, so it's a plain dot product).
- The model itself (~90MB) is fetched from the Hugging Face CDN on first use and cached by the browser — it isn't bundled into the site.

## Run locally

```bash
npm install
npm run dev
```

Open the printed local URL. First search will take a few seconds while the model downloads; after that it's instant.

## Regenerating the song catalog

Only needed if you want to refresh which real tracks are in the catalog. Requires the Spotify credentials already set up at the repo root (`../.env`):

```bash
cd ..
python -m src.catalog_builder      # rebuilds data/songs_vibe.csv from live Spotify search
cd web
npm run build:embeddings           # re-embeds it into src/data/songVectors.json
```

## Deploying to Netlify

This site is fully static — no Netlify Functions or environment variables needed.

1. Install the Netlify CLI if you don't have it: `npm install -g netlify-cli`
2. From the repo root (not `web/`):
   ```bash
   netlify login
   netlify init      # or `netlify link` if the site already exists
   netlify deploy --prod
   ```
   `netlify.toml` at the repo root already points Netlify at `base = "web"`, `command = "npm run build"`, `publish = "dist"`, so it builds and deploys correctly from a subdirectory.
3. Netlify will give you the live URL after `--prod` finishes.

To redeploy after changes, just repeat `netlify deploy --prod` (or push to your linked git branch if you connect the repo through the Netlify dashboard instead of the CLI).