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

      {results.length > 0 && (
        <div className="sym-results__top3">
          <span className="sym-results__top3-label">Your top 3 songs</span>
          <ol className="sym-results__top3-list">
            {results.slice(0, 3).map(({ song }, index) => (
              <li key={song.id} className="sym-results__top3-item">
                <span className="sym-results__top3-rank">{index + 1}.</span> {song.title}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="sym-results__grid">
        {results.map(({ song, score }, index) => (
          <TrackCard key={song.id} song={song} score={score} index={index} />
        ))}
      </div>
    </div>
  );
}