// Both the query vector (embed.js) and catalog vectors (songVectors.json)
// are L2-normalized at embed time, so a plain dot product already equals
// cosine similarity — no need to divide by magnitudes here.
function dot(a, b) {
  let sum = 0;
  for (let i = 0; i < a.length; i++) sum += a[i] * b[i];
  return sum;
}

// Songs whose vibe line was inferred (rather than verified — see the
// `confidence` column in data/songs_vibe.csv) get their similarity nudged
// down so that, on close matches, a verified song ranks ahead of an inferred
// one. Small enough not to bury a clearly-better inferred match.
const INFERRED_WEIGHT = 0.9;

export function rankSongs(queryVector, songs, k = 6) {
  return songs
    .map((song) => {
      const weight = song.confidence === "inferred" ? INFERRED_WEIGHT : 1;
      return { song, score: dot(queryVector, song.vector) * weight };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}