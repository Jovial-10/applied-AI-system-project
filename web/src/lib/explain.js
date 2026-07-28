// The match score is a cosine similarity from an embedding model with no
// literal "reasons" to extract, and the catalog only carries a genre (no
// mood/audio-features for these tracks — see src/catalog_builder.py). So the
// per-song explanation is a hand-written genre -> vibe descriptor, not
// something derived from the model itself.
//
// Also imported by scripts/build_embeddings.mjs to enrich the text each song
// is embedded from — a bare genre noun gives the model too little to weigh
// against a title that happens to share a literal word with the query (see
// src/vibe_recommender.py's song_to_text for the same fix on the Python
// side; keep both dictionaries in sync).
export const GENRE_VIBE = {
  pop: { feature: "polished hooks and an upbeat, radio-ready energy", vibe: "feel-good" },
  lofi: { feature: "warm tape hiss and a slow, laid-back beat", vibe: "chill" },
  rock: { feature: "driving guitars and raw, live-band energy", vibe: "high-energy" },
  ambient: { feature: "airy pads and almost no percussion", vibe: "atmospheric" },
  jazz: { feature: "improvisational phrasing and a loose, swinging groove", vibe: "smooth" },
  synthwave: { feature: "retro synth arpeggios and a steady electronic pulse", vibe: "neon-lit, nostalgic" },
  "indie pop": { feature: "breezy melodies and lo-fi production charm", vibe: "dreamy" },
  edm: { feature: "a pounding four-on-the-floor beat and big drops", vibe: "euphoric" },
  country: { feature: "twangy guitars and storytelling vocals", vibe: "nostalgic" },
  "r&b": { feature: "smooth vocal runs and a laid-back groove", vibe: "sultry" },
  metal: { feature: "distorted riffs and aggressive percussion", vibe: "intense" },
  folk: { feature: "acoustic instrumentation and plainspoken lyrics", vibe: "earthy" },
  soul: { feature: "expressive vocals over a warm, groove-driven backbone", vibe: "soulful" },
  "hip-hop": { feature: "a heavy beat and rhythmic vocal delivery", vibe: "confident" },
  latin: { feature: "percussive rhythms and danceable grooves", vibe: "vibrant" },
  classical: { feature: "orchestral arrangement and no vocals", vibe: "reflective" },
  punk: { feature: "fast tempos and raw, stripped-down energy", vibe: "rebellious" },
  reggae: { feature: "off-beat guitar skanks and a relaxed groove", vibe: "laid-back" },
  blues: { feature: "expressive guitar bends and a slow, soulful groove", vibe: "moody" },
  gospel: { feature: "layered vocal harmonies and an uplifting build", vibe: "uplifting" },
  "k-pop": { feature: "polished production and high-energy hooks", vibe: "energetic" },
  afrobeats: { feature: "syncopated percussion and a danceable groove", vibe: "vibrant" },
  disco: { feature: "a steady four-on-the-floor groove and lush strings", vibe: "danceable" },
  funk: { feature: "a syncopated bassline and a tight rhythmic groove", vibe: "groovy" },
  trance: { feature: "sweeping synth builds and a hypnotic tempo", vibe: "euphoric" },
  "drum and bass": { feature: "fast breakbeats and deep basslines", vibe: "high-energy" },
  dubstep: { feature: "heavy sub-bass drops and syncopated rhythm", vibe: "intense" },
  "post-punk": { feature: "angular guitars and a cool, detached tone", vibe: "moody" },
  shoegaze: { feature: "wall-of-sound guitar textures and hazy vocals", vibe: "dreamy" },
  grunge: { feature: "distorted guitars and a raw, unpolished edge", vibe: "brooding" },
  bluegrass: { feature: "fast picking and acoustic string arrangements", vibe: "lively" },
  flamenco: { feature: "intricate guitar work and passionate rhythm", vibe: "fiery" },
  opera: { feature: "a powerful vocal performance over orchestral backing", vibe: "dramatic" },
  world: { feature: "traditional instrumentation from outside the mainstream", vibe: "eclectic" },
  "trip-hop": { feature: "a slow, downtempo beat and a hazy atmosphere", vibe: "moody" },
  emo: { feature: "raw, confessional vocals and emotional guitar hooks", vibe: "emotional" },
  "bossa nova": { feature: "gentle nylon-string guitar and a soft samba sway", vibe: "relaxed" },
};

export function explainMatch(song) {
  const descriptor = GENRE_VIBE[song.genre];
  if (!descriptor) {
    return `This song's ${song.genre} sound lines up with the vibe you described.`;
  }
  return `This song has ${descriptor.feature} that creates a ${descriptor.vibe} vibe.`;
}