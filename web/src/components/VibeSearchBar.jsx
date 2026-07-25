import { useState } from "react";
import "./VibeSearchBar.css";

const EXAMPLE_VIBES = [
  "rainy day coding",
  "hype gym workout",
  "chill study lofi",
  "late night drive",
  "sunny road trip pop",
];

export default function VibeSearchBar({ onSearch, onSurpriseMe, disabled }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const query = value.trim();
    if (query) onSearch(query);
  }

  function handleChipClick(vibe) {
    setValue(vibe);
    onSearch(vibe);
  }

  return (
    <div className="sym-search">
      <form className="sym-search__bar" onSubmit={handleSubmit}>
        <span className="sym-search__icon">⌕</span>
        <input
          className="sym-search__input"
          type="text"
          placeholder='Describe a vibe — "rainy day coding", "hype gym workout"…'
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
        />
        <button className="sym-search__submit" type="submit" disabled={disabled || !value.trim()}>
          Discover
        </button>
      </form>

      <div className="sym-search__chips">
        <span className="sym-search__chips-label">Try a vibe:</span>
        {EXAMPLE_VIBES.map((vibe) => (
          <button
            key={vibe}
            type="button"
            className="sym-chip"
            onClick={() => handleChipClick(vibe)}
            disabled={disabled}
          >
            {vibe}
          </button>
        ))}
      </div>

      <button className="sym-surprise" type="button" onClick={onSurpriseMe} disabled={disabled}>
        <span className="sym-surprise__spark">✦</span> Surprise me
      </button>
    </div>
  );
}