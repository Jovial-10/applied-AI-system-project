# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

This version is a content-based recommender: there's only one listener and a fixed song catalog, with no play history from other users to learn from. So instead of asking "what did similar users like," it asks "how closely does this song's own attributes match this listener's stated taste," scores every song in the catalog that way, and returns the top matches.

---

## How The System Works

Explain your design in plain language.

Real-world recommenders like Spotify or YouTube usually blend two ideas: collaborative filtering, which looks at what other, similar users listened to, and content-based filtering, which looks at the attributes of the content itself (genre, audio features, etc). This simulation only has a single user profile and a static catalog with no cross-user listening data, so it can only do the content-based half. It prioritizes closeness over exact matching — a song doesn't need to hit every attribute perfectly to score well, it just needs to be similar enough across enough of them, the same way a real system would rather surface something close to your taste than nothing at all.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
  - `genre` — categorical, compared for an exact match
  - `mood` — categorical, compared for an exact match
  - `energy` — continuous (0-1), compared by closeness to the user's target
  - `acousticness` — continuous (0-1), compared against the user's acoustic preference
  - `valence` — continuous (0-1), optional closeness bonus if the user sets a target
  - `tempo_bpm`, `danceability` exist in the data but aren't used in scoring yet — possible future additions
  - `id`, `title`, `artist` are identifiers, not taste signals, so they don't factor into the score
- What information does your `UserProfile` store
  - `favorite_genre` — matched against `Song.genre`
  - `favorite_mood` — matched against `Song.mood`
  - `target_energy` — compared against `Song.energy`
  - `likes_acoustic` — a boolean, compared against `Song.acousticness`
- How does your `Recommender` compute a score for each song
  - Via a **Scoring Rule**: a function of one song and the user profile that produces a single match number for that song, independent of any other song in the catalog.
- How do you choose which songs to recommend
  - Via a **Ranking Rule**: once every song has a score, sort the whole list by score, break ties, and take the top `k`. Scoring and ranking are kept separate on purpose — scoring answers "how good is this one song for this user," ranking answers "given all those numbers, what order and cutoff do we present." Scoring without ranking is just a pile of numbers with no list to show; ranking without scoring has nothing to sort by. Keeping them separate also means each can improve independently — e.g. the ranking rule could later add diversity (avoiding 5 near-identical songs) without touching how individual songs are scored.

### Algorithm Recipe

The scoring rule adds up independent points per feature:

- Genre match: +2.0 (exact match on `favorite_genre`)
- Mood match: +1.0 (exact match on `favorite_mood`)
- Energy closeness: up to +1.5, scaled by how close `energy` is to `target_energy`
- Acoustic fit: up to +1.0, rewarding high `acousticness` if `likes_acoustic` is true, low `acousticness` otherwise
- Valence closeness (optional): up to +0.75, same closeness scaling as energy, only applied if a `target_valence` is set

Ties go to whichever song's energy is closest to `target_energy`.

**Potential bias:** genre carries the most weight, so the system can over-prioritize genre and bury a great mood/energy match that happens to sit in a genre the user didn't name as a favorite.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default `pop`/`happy` profile:

```
Top recommendations for genre=pop, mood=happy, energy=0.8:

1. Sunrise City - Score: 5.29
   Reasons: genre match (+2.00), mood match (+1.00), energy similarity (+1.47), non-acoustic fit (+0.82)

2. Gym Hero - Score: 4.25
   Reasons: genre match (+2.00), energy similarity (+1.30), non-acoustic fit (+0.95)

3. Rooftop Lights - Score: 3.09
   Reasons: mood match (+1.00), energy similarity (+1.44), non-acoustic fit (+0.65)

4. Concrete Bloom - Score: 2.38
   Reasons: energy similarity (+1.50), non-acoustic fit (+0.88)

5. Neon Bazaar - Score: 2.30
   Reasons: energy similarity (+1.38), non-acoustic fit (+0.92)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments

To stress-test the Algorithm Recipe, I ran three "edge case" profiles, each one pairing a favorite genre with attributes that genre's real songs in the catalog don't actually have — so the genre-match bonus and the closeness terms pull the score in opposite directions.

**Slow acoustic rock** (`genre=rock, mood=relaxed, energy=0.25, likes_acoustic=True`): the catalog's only rock song ("Storm Runner") is intense and non-acoustic, the opposite of this profile. Result: a relaxed, acoustic jazz song ("Coffee Shop Stories") outranks the only rock song entirely — genre alone wasn't enough to win.

```
=== Slow acoustic rock (genre=rock, mood=relaxed, energy=0.25, likes_acoustic=True) ===

1. Coffee Shop Stories - Score: 3.21
   Reasons: mood match (+1.00), energy similarity (+1.32), acoustic fit (+0.89)

2. Storm Runner - Score: 2.61
   Reasons: genre match (+2.00), energy similarity (+0.51), acoustic fit (+0.10)

3. Glass Cathedral Sketch - Score: 2.47
   Reasons: energy similarity (+1.50), acoustic fit (+0.97)

4. Spacewalk Thoughts - Score: 2.38
   Reasons: energy similarity (+1.46), acoustic fit (+0.92)

5. Paper Boats - Score: 2.32
   Reasons: energy similarity (+1.42), acoustic fit (+0.90)
```

**Low-energy pop** (`genre=pop, mood=chill, energy=0.15, likes_acoustic=True`): both pop songs in the catalog are high-energy and non-acoustic. Result: three chill/ambient/lofi songs outrank both real pop songs, which still cling to 4th and 5th place purely on the genre bonus.

```
=== Low-energy pop (genre=pop, mood=chill, energy=0.15, likes_acoustic=True) ===

1. Spacewalk Thoughts - Score: 3.22
   Reasons: mood match (+1.00), energy similarity (+1.30), acoustic fit (+0.92)

2. Library Rain - Score: 3.06
   Reasons: mood match (+1.00), energy similarity (+1.20), acoustic fit (+0.86)

3. Midnight Coding - Score: 2.80
   Reasons: mood match (+1.00), energy similarity (+1.09), acoustic fit (+0.71)

4. Sunrise City - Score: 2.68
   Reasons: genre match (+2.00), energy similarity (+0.50), acoustic fit (+0.18)

5. Gym Hero - Score: 2.38
   Reasons: genre match (+2.00), energy similarity (+0.33)
```

**Deep intense country** (`genre=country, mood=intense, energy=0.85, likes_acoustic=True`): this profile is internally contradictory — in this dataset, high energy and high acousticness are inversely correlated (the loudest songs are all electric), so no song can satisfy both halves at once. Result: the sole country song ("Dust Road Ballad") still wins on genre alone despite a mood mismatch, and the runners-up are unrelated high-energy songs that at least partly match the mood.

```
=== Deep intense country (genre=country, mood=intense, energy=0.85, likes_acoustic=True) ===

1. Dust Road Ballad - Score: 3.55
   Reasons: genre match (+2.00), energy similarity (+0.90), acoustic fit (+0.65)

2. Storm Runner - Score: 2.51
   Reasons: mood match (+1.00), energy similarity (+1.41), acoustic fit (+0.10)

3. Gym Hero - Score: 2.43
   Reasons: mood match (+1.00), energy similarity (+1.38)

4. Tidewalker - Score: 1.75
   Reasons: energy similarity (+1.50), acoustic fit (+0.25)

5. Rooftop Lights - Score: 1.71
   Reasons: energy similarity (+1.36), acoustic fit (+0.35)
```

**Takeaway:** the genre bonus (+2.0) is large enough to guarantee the catalog's only song in a favorite genre always lands in the top 5, even when every other attribute is a poor match — but it's not always large enough to make that song rank #1 if a different genre fits the closeness terms much better.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

Sometimes the "vibe" described by the user will have exact words matched in the songs and the recommender would recommend you songs because it matched the title of the song, not because of the actual similarity in vibe.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

What I learned:

- **How recommenders turn data into predictions:** Recommenders turn data into predictions by comparing what a user says they like (genre, mood, energy, etc.) against each song's own attributes and adding up points for how closely they match. Even a simple, rule-based system like this one can feel like a real recommendation, because the scoring logic is what decides what matters most. Giving genre and mood more weight made the picks feel a lot closer to what a real listener would actually want.
- **Where bias or unfairness could show up:** Bias shows up here because the dataset is small and uneven — some genres have a few songs while most only have one, so fans of those genres always get the same limited pick no matter how well it actually fits. This showed me that real systems will always deal with a huge range of unique user profiles, so the dataset itself needs to represent that same diversity, not just the scoring logic.

