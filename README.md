# 🎵 Symphony

## Original Project (Modules 1-3)

The original project was **Music Recommender Simulation**, a small content-based recommender. It stored a fixed catalog of about 20 hand-written songs, each with a genre, mood, and a few audio features, and matched them against a single user's taste profile. It scored every song with a strict, hand-tuned rule (genre +2.0, mood +1.0, energy closeness, acoustic fit) and returned the top matches through a command line app.

## Summary

Symphony is a music recommender system that helps users find songs that match a certain "vibe" that they may want to listen to. It can also help you find new songs that are similar to songs that you already like. Instead of typing in a genre and hoping the catalog has it, you describe the feeling you want in plain words and Symphony returns real Spotify tracks that fit it.

This matters because taste is not just a genre label. People reach for music by mood and moment, like "rainy day coding" or "hype gym workout," and Symphony is built to answer that kind of request.

## What Changed From The Original

The original used made-up songs and a strict scoring formula that only compared fixed fields like genre and mood. Symphony replaces both halves of that:

- **Real data instead of fake songs.** Songs are pulled from Spotify's live API, so the catalog is around 1,380 real tracks across 37 genres.
- **Embeddings instead of a fixed formula.** Every song's "vibe" description is embedded into a vector. Your query is embedded the same way, and songs are scored dynamically by how close their vector is to yours. This is a small RAG-style retrieval system rather than a rule that only checks exact fields.

## Architecture Overview

There are two offline steps and one live app. First, `catalog_builder.py` pulls tracks from Spotify and writes them to `data/songs_vibe.csv`, with each song given a short hand-written vibe line. Second, `build_embeddings.mjs` turns every vibe line into a vector using the `all-MiniLM-L6-v2` model and saves them to `songVectors.json`. Third, the Symphony web app runs entirely in the browser: it embeds your typed query with the same model, ranks the catalog by cosine similarity, and shows the top songs with a short explanation of why each one matched. The full diagram is in [diagrams/architecture.mmd](diagrams/architecture.mmd).

## Setup Instructions

**Python side (catalog and tests):**

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the tests:

   ```bash
   pytest
   ```

**Web app (Symphony):**

1. Move into the web folder and install:

   ```bash
   cd web
   npm install
   ```

2. Start the app:

   ```bash
   npm run dev
   ```

3. Open the local URL it prints and type a vibe into the search bar.

To rebuild the song vectors after changing the catalog, run `npm run build:embeddings` from the `web` folder.

## Sample Interactions

These are real outputs from the vibe recommender on the current catalog (top 3 shown):

**Query: "rainy day coding session"**

```
1. TRUSTFALL - Guitar Instrumental (lofi)   sim 0.45
   vibe: rainy-window, instrumental and mood-setting
2. Fullautostop - IAMPAUL (lofi)            sim 0.42
   vibe: rainy-window, tape-warm calm
3. Entity INM TNE - Marc Behrens (lofi)     sim 0.42
   vibe: rainy-window, tape-warm calm
```

**Query: "hype gym workout pump"**

```
1. Bling-Bang-Bang-Born - Creepy Nuts (world)   sim 0.44
   vibe: hyperactive, anime-adrenaline hype
2. Thunderstruck - AC/DC (rock)                 sim 0.43
   vibe: electric, swaggering stadium adrenaline
3. Overdrive - Air Diver (trance)               sim 0.42
   vibe: pulsing, uplifting, hands-up rush
```

**Query: "late night heartbreak drive"**

```
1. stupid song - Olivia Rodrigo (pop)               sim 0.56
   vibe: breezy heartbreak playing it cool
2. Apocalypse - Cigarettes After Sex (indie pop)    sim 0.51
   vibe: hazy, aching, slow-motion heartbreak
3. I Had Some Help - Post Malone (pop)              sim 0.50
   vibe: rowdy, hard-drinking heartbreak singalong
```

## Design Decisions

While there were a lot of design changes, I ultimately chose to design the program this way to ensure that the songs I recommend to users represent a wide variety of musical genres and that the actual "vibe" that users want songs for are carefully selected and recommended.

A few specific choices supported that:

- **Match on the vibe line alone.** Songs are embedded from their vibe description, not their title. Early on, a literal word in a title (like "Rain") would win a match even when the song's real feeling was unrelated. Dropping the title from the embedding fixed most of that.
- **Two catalogs.** Spotify's audio-features endpoint stopped responding after about 17 tracks, so the vibe catalog only uses Search, which is not blocked. That trade let the catalog grow to over a thousand songs instead of staying tiny.
- **No vector database.** At this scale a cosine similarity over an in-memory list is enough, so I kept it simple and ran everything in the browser with no server.
- **Confidence weighting.** Vibe lines marked "inferred" are nudged down slightly so a verified song wins a close call.

## Testing Summary

Testing is a pytest suite with deterministic fake embeddings, so most tests run without downloading a model or hitting the network. What worked well was the ranking logic and the Spotify cache, which reads from disk with no live call. What did not fully work was the literal-overlap problem. Embedding the vibe line alone fixed most cases, but one regression test against the real model shows that a strong emotional word shared between a query and a title can still occasionally win. What I learned is that a clean data choice, like dropping titles from the text being embedded, can fix a bug more reliably than adding more scoring rules on top.

## Reflection

This project taught me that the data matters as much as the algorithm. Moving from a strict formula to embeddings did not just add features, it changed the whole problem from "does this song match these exact fields" to "does this song feel like what the user asked for." It also showed me that small, careful choices, like what text you embed, often solve problems that more complex logic cannot.
