import { useState } from "react";
import BackgroundOrbs from "./components/BackgroundOrbs";
import VibeSearchBar from "./components/VibeSearchBar";
import RecommendationsGrid from "./components/RecommendationsGrid";
import { LoadingState, EmptyState, ErrorState } from "./components/StatusStates";
import { embedQuery } from "./lib/embed";
import { rankSongs } from "./lib/similarity";
import songVectors from "./data/songVectors.json";
import "./App.css";

const EXAMPLE_VIBES = [
  "rainy day coding",
  "hype gym workout",
  "chill study lofi",
  "late night drive",
  "sunny road trip pop",
  "heartbreak on repeat",
  "cozy coffee shop morning",
];

export default function App() {
  const [query, setQuery] = useState(null);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | loading-model | searching | error
  const [error, setError] = useState(null);

  async function runSearch(vibe) {
    setQuery(vibe);
    setResults(null);
    setError(null);
    setStatus("loading-model");

    try {
      const queryVector = await embedQuery(vibe);
      setStatus("searching");
      const ranked = rankSongs(queryVector, songVectors, 6);
      setResults(ranked);
      setStatus("idle");
    } catch (err) {
      console.error(err);
      setError("Something went wrong finding recommendations. Check your connection and try again.");
      setStatus("error");
    }
  }

  function handleSurpriseMe() {
    const vibe = EXAMPLE_VIBES[Math.floor(Math.random() * EXAMPLE_VIBES.length)];
    runSearch(vibe);
  }

  const isBusy = status === "loading-model" || status === "searching";

  return (
    <div className="sym-app">
      <BackgroundOrbs />

      <header className="sym-header">
        <div className="sym-header__brand">
          <span className="sym-header__mark" />
          Symphony
        </div>
      </header>

      <main className="sym-main">
        <div className="sym-hero">
          <div className="sym-hero__eyebrow">Symphony · music recommendations</div>
          <h1 className="sym-hero__title">
            What should you
            <br />
            hear next?
          </h1>
          <p className="sym-hero__subtitle">
            Describe a vibe — a mood, a moment, a feeling — and Symphony finds real songs
            that match it. No account, no noise.
          </p>
        </div>

        <VibeSearchBar onSearch={runSearch} onSurpriseMe={handleSurpriseMe} disabled={isBusy} />

        <div className="sym-content">
          {status === "loading-model" && <LoadingState label="Loading the recommendation model…" />}
          {status === "searching" && <LoadingState label="Finding songs that match your vibe…" />}
          {status === "error" && <ErrorState message={error} onRetry={() => query && runSearch(query)} />}
          {status === "idle" && !results && <EmptyState />}
          {status === "idle" && results && <RecommendationsGrid query={query} results={results} />}
        </div>
      </main>
    </div>
  );
}