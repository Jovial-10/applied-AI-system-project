import { gradientFor } from "../lib/gradientArt";
import { explainMatch } from "../lib/explain";
import "./TrackCard.css";

export default function TrackCard({ song, score, index }) {
  return (
    <div className="sym-card" style={{ animationDelay: `${index * 60}ms` }}>
      <div className="sym-card__art" style={!song.image ? { background: gradientFor(song) } : undefined}>
        {song.image && <img className="sym-card__art-img" src={song.image} alt="" />}
      </div>
      <div className="sym-card__info">
        <div className="sym-card__title">{song.title}</div>
        <div className="sym-card__artist">{song.artist}</div>
      </div>
      <div className="sym-card__footer">
        <span className="sym-card__dot" />
        {song.genre} · {Math.round(score * 100)}% match
      </div>
      {index < 3 && <div className="sym-card__reason">{explainMatch(song)}</div>}
    </div>
  );
}