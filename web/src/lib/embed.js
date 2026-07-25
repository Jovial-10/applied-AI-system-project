import { pipeline, env } from "@xenova/transformers";

// Runs entirely in the browser (WASM) — model weights are fetched from the
// HF hub CDN on first use and cached by the browser after that. No server
// call, no API key, matches the catalog embeddings in scripts/build_embeddings.mjs.
env.allowLocalModels = false;

const MODEL_NAME = "Xenova/all-MiniLM-L6-v2";
let embedderPromise = null;

export function getEmbedder(onProgress) {
  if (!embedderPromise) {
    embedderPromise = pipeline("feature-extraction", MODEL_NAME, {
      progress_callback: onProgress,
    });
  }
  return embedderPromise;
}

export async function embedQuery(text, onProgress) {
  const embedder = await getEmbedder(onProgress);
  const output = await embedder(text, { pooling: "mean", normalize: true });
  return Array.from(output.data);
}