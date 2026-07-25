import { gradientFor } from "../lib/gradientArt";
import "./TrackCard.css";

export default function TrackCard({ song, score, index }) {
  return (
    <div className="sym-card" style={{ animationDelay: `${index * 60}ms` }}>
      <div className="sym-card__art" style={{ background: gradientFor(song) }} />
      <div className="sym-card__info">
        <div className="sym-card__title">{song.title}</div>
        <div className="sym-card__artist">{song.artist}</div>
      </div>
      <div className="sym-card__footer">
        <span className="sym-card__dot" />
        {song.genre} · {Math.round(score * 100)}% match
      </div>
    </div>
  );
}