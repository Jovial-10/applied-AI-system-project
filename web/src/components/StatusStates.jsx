import "./StatusStates.css";

export function LoadingState({ label }) {
  return (
    <div className="sym-status">
      <span className="sym-status__spinner" />
      {label}
    </div>
  );
}

export function EmptyState() {
  return (
    <div className="sym-status sym-status--muted">
      Search an artist, track, or genre — or just describe a vibe — to get started.
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="sym-status sym-status--error">
      <span>{message}</span>
      {onRetry && (
        <button className="sym-status__retry" onClick={onRetry} type="button">
          Try again
        </button>
      )}
    </div>
  );
}