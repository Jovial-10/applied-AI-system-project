// Precomputes an embedding vector for every song in the vibe catalog, so the
// deployed app only has to embed the user's short query at request time —
// the (larger, fixed) catalog side of the cosine-similarity comparison is
// done once here, not on every page load.
//
// Run with: node scripts/build_embeddings.mjs

import { readFileSync, writeFileSync } from "node:fs";
import { parse } from "node:path";
import { pipeline } from "@xenova/transformers";
import { GENRE_VIBE } from "../src/lib/explain.js";

const CSV_PATH = new URL("../../data/songs_vibe.csv", import.meta.url);
const OUTPUT_PATH = new URL("../src/data/songVectors.json", import.meta.url);
const MODEL_NAME = "Xenova/all-MiniLM-L6-v2";

// Handles both CRLF line endings and titles/artists with embedded commas
// (quoted per RFC 4180, same as Python's csv module writes them).
function parseCsvLine(line) {
  const values = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (inQuotes) {
      if (char === '"' && line[i + 1] === '"') {
        current += '"';
        i++;
      } else if (char === '"') {
        inQuotes = false;
      } else {
        current += char;
      }
    } else if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.length > 0);
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
  });
}

function songToText(song) {
  // The catalog now carries a hand-written, per-song vibe line (see the `vibe`
  // column in data/songs_vibe.csv) — a far richer semantic signal than the
  // per-genre descriptor, which embedded every song of a genre to nearly the
  // same text. Prefer it; fall back to the genre descriptor only when a row
  // has no vibe.
  const vibe = (song.vibe || "").trim();
  if (vibe) {
    return `${song.title} by ${song.artist}: ${vibe}.`;
  }
  const descriptor = GENRE_VIBE[song.genre];
  const genrePart = descriptor
    ? `${song.genre} song with ${descriptor.feature}, a ${descriptor.vibe} vibe`
    : `${song.genre} song`;
  return `${song.title} by ${song.artist}: a ${genrePart}.`;
}

async function main() {
  const csvText = readFileSync(CSV_PATH, "utf-8");
  const songs = parseCsv(csvText);
  console.log(`Loaded ${songs.length} songs from ${parse(CSV_PATH.pathname).base}`);

  console.log(`Loading ${MODEL_NAME}...`);
  const embed = await pipeline("feature-extraction", MODEL_NAME);

  const results = [];
  for (const song of songs) {
    const output = await embed(songToText(song), { pooling: "mean", normalize: true });
    results.push({
      id: Number(song.id),
      title: song.title,
      artist: song.artist,
      genre: song.genre,
      image: song.image_url || null,
      vibe: (song.vibe || "").trim() || null,
      // "known" (verified) vs "inferred"; the ranker down-weights inferred rows.
      confidence: (song.confidence || "").trim() || null,
      vector: Array.from(output.data),
    });
    process.stdout.write(`\rEmbedded ${results.length}/${songs.length}`);
  }
  console.log();

  writeFileSync(OUTPUT_PATH, JSON.stringify(results));
  console.log(`Wrote ${results.length} vectors to ${parse(OUTPUT_PATH.pathname).base}`);
}

main();