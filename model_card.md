# 🎧 Model Card: Symphony

## 1. Model Name  

**Symphony**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

Symphony recommends songs that match a free-text "vibe" the user types, like "rainy day coding" or "hype gym workout." It can also help a user find new songs that feel similar to ones they already like. It assumes the user can describe the feeling they want in a few words. This is for classroom exploration, not real users, since the catalog is a curated slice of Spotify and the vibe descriptions are hand-written rather than learned from real listening data.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Every song has a short vibe line I wrote that describes how it feels. That sentence gets turned into a list of numbers, called a vector, that captures its meaning. When a user types a query, that gets turned into numbers the same way. The system then compares the query's numbers to every song's numbers and returns the songs whose numbers are closest, which are the ones that feel the most like what the user asked for.

This is a big change from the starter logic. The original added up points for exact matches on fixed fields like genre, mood, and energy. Now it matches by meaning instead, so a query does not have to name a genre to get good results. One other important change is that each song is matched on its vibe line alone, not its title, so a song can't win a query just because a word in its name happens to match.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog now has around 1,380 songs pulled from Spotify's live search, spread across 37 genres. Each song has a hand-written vibe line describing its feeling, and each one is marked either "known" (verified) or "inferred" (a vibe line I guessed at). Most of the lines are inferred, with a few hundred verified as known. This replaced the original tiny catalog of about 20 hand-made songs. Even at this size, parts of musical taste are still missing: the model does not read lyrics, it leans English, and it only covers the genres I seeded from Spotify.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works well for clear mood or feeling queries, like "rainy day coding" or "late night heartbreak drive," where the vibe words are strong and specific. It captures feeling across genres, so it can return the same mood from a few different genres instead of locking onto one. It matched my intuition when it pulled calm lofi tracks for a study query and high-energy tracks for a workout query, without me having to name a genre at all.

---

## 6. Limitations and Bias 

**Limitations.** The catalog is limited. It only covers the genres I seeded from Spotify search, so anything outside those buckets is missing. It also leans English and the model matches on a short written vibe line, not the actual lyrics or audio, so it never really "hears" the song. It only knows a song by the sentence I wrote to describe it. On top of that, some songs are marked "inferred," which means I guessed at their vibe line instead of verifying it, so those matches are less trustworthy by design.

**Biases.** Genre coverage is uneven. Some genres have close to 40 songs and others have far fewer, so a query that fits a thin genre has fewer good options to pull from. The catalog also comes from Spotify search, which surfaces more popular tracks, so the recommender leans toward well-known music and can miss smaller artists. Finally, the embedding model was trained on general text, so it can latch onto surface words instead of the real feeling, which is where the name-versus-vibe problem came from.

### Could this be misused, and how would I prevent that?

The misuse risk is low since the system only recommends songs from a fixed catalog and does not collect any user data. The main thing to watch is that the vibe lines are hand-written, so someone could bias what gets recommended by writing slanted descriptions, like always describing one artist in glowing terms so those songs win more queries. To prevent that I keep the vibe lines factual and mark unverified ones as "inferred" so they get down-weighted. If this were ever used for real, I would also keep the recommendations transparent by showing why each song matched, so a user can tell it is matching on vibe and not quietly pushing something.

---

## 7. Evaluation  

**What surprised me while testing reliability:** the recommender kept making the same mistake over and over, matching songs by their title instead of their actual vibe, like a "party" song winning a "party" query just because the word was in its name. What surprised me more was that the AI would say it had fixed the problem when it actually had not. That taught me to test the output myself instead of trusting that a change worked just because it was described as a fix.

> The evaluation below describes the earlier structured scoring version of the project, kept here as a record of that work.

**Profiles tested:** the starter pop/happy profile, plus three "edge case" profiles built to conflict with the catalog: Slow acoustic rock (rock genre, but low-energy and acoustic), Low-energy pop (pop genre, but calm and acoustic), and Deep intense country (country genre, but loud and acoustic at the same time — a combination that barely exists in the data). I also re-ran all four with the mood-match term temporarily disabled, to see how much of each ranking depended on mood alone.

**What surprised me:** how often the genre-matched song lost outright to a completely different genre. I expected the +2.0 genre bonus to be the strongest signal, and for well-fitting profiles like pop/happy it was. But for Slow acoustic rock and Low-energy pop, songs with no genre match at all (a jazz track, several lofi/ambient tracks) beat the only rock song and both real pop songs, because they matched mood, energy, and acoustic-fit far better. Genre only "saved" a bad-fit song when every alternative was even worse — as with Deep intense country, where the lone country song stayed #1 mostly because nothing else was close either.

**Comparing pairs of profiles:**

- *pop/happy vs. Low-energy pop* — same genre, opposite energy target. pop/happy's target (0.8) matches what pop actually sounds like here, so the two real pop songs win outright. Low-energy pop's target (0.15) matches nothing pop-related, so calm lofi/ambient songs take over and the real pop songs slide to 4th and 5th. This makes sense: the genre label only helps when the rest of the profile agrees with what that genre actually sounds like in the data.
- *Slow acoustic rock vs. Deep intense country* — both pair a genre with attributes that genre's one real song doesn't have, but the outcomes differ. The lone rock song is far from its profile (very different energy, no acoustic sound at all), so it loses to a better-fitting jazz song. The lone country song is only moderately off (energy is 0.40 away, and it's already fairly acoustic at 0.65), so it stays on top. Genre only rescues a song when the rest of its profile is a near-miss, not a wide miss.
- *Low-energy pop vs. Slow acoustic rock* — different stated genres, but nearly the same winning songs (calm, acoustic lofi/ambient tracks). This makes sense because both profiles really describe the same "vibe" — calm and acoustic — and the scoring rule responds to that vibe more strongly than to the genre label typed into the profile.

Picture someone who says they want "Happy Pop." The song "Gym Hero" keeps showing up even though its mood is labeled "intense," not "happy." That's because the scoring gives points for four separate things: genre, mood, energy, and whether the song sounds acoustic or produced. "Gym Hero" is pop (genre matches), it's loud in almost exactly the way happy pop usually is (energy matches closely), and it isn't acoustic, which fits typical pop production (acoustic-fit matches). It misses the "happy" mood completely, but it still racks up enough points from the other three categories to beat songs that only nail one or two things well. Matching most categories pretty well can beat matching only one category perfectly.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Add even more data and more genres so the recommender can handle a wider range of tastes. Verify the "inferred" vibe lines so more of the catalog is trustworthy. Add diversity to the top results so they are not all the same genre or artist. Improve the explanations so it is even clearer why each song matched. Finally, handle more complex queries, like ones that describe two feelings at once or a very specific moment.


---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Reflecting on this experience, I learned a lot more about the logic behind recommendation systems. My biggest learning moment during this project was the importance of having a diverse dataset. Systems like these will always have a lot of users which means a lot of unique musical preferences. Edge case user profiles will show up a lot so it is important to have a dataset that represents a wide variety of people. Simple algorithms can still feel like recommendations because the logic behind it is what matters, but I also saw that the data matters just as much as the algorithm.

**Collaborating with AI.** I used AI throughout the project. I had it brainstorm with me and ask me questions so I could think through my own choices, write code efficiently, and help me write tests and design the website. It sped up the work but I still had to check what it produced.

**One helpful suggestion:** switching from the simple scoring logic to using an embedder that turns each song into a vector and matches by meaning instead of exact fields. That was the change that made the whole "vibe" idea actually work, and it is the core of the current system.

**One flawed suggestion:** at one point the AI had the recommender match songs by words in their title instead of their real vibe, so a song could win a query just because a word matched its name. I had to correct that by embedding the vibe line alone instead of the title. It was a good reminder that AI suggestions still need testing, since it also claimed to have fixed this before it actually had.

If the project was extended, I would try getting a much larger dataset, so that I could make a more comprehensive and representative recommender.