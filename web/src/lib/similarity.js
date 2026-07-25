// Both the query vector (embed.js) and catalog vectors (songVectors.json)
// are L2-normalized at embed time, so a plain dot product already equals
// cosine similarity — no need to divide by magnitudes here.
function dot(a, b) {
  let sum = 0;
  for (let i = 0; i < a.length; i++) sum += a[i] * b[i];
  return sum;
}

export function rankSongs(queryVector, songs, k = 6) {
  return songs
    .map((song) => ({ song, score: dot(queryVector, song.vector) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}