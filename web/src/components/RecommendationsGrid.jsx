import TrackCard from "./TrackCard";
import "./RecommendationsGrid.css";

export default function RecommendationsGrid({ query, results }) {
  return (
    <div className="sym-results">
      <div className="sym-results__header">
        <div>
          <h2 className="sym-results__title">Recommended for you</h2>
          <div className="sym-results__subtitle">
            Seeded from <span className="sym-results__query">"{query}"</span> · {results.length} tracks
          </div>
        </div>
      </div>

      <div className="sym-results__grid">
        {results.map(({ song, score }, index) => (
          <TrackCard key={song.id} song={song} score={score} index={index} />
        ))}
      </div>
    </div>
  );
}