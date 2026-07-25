import { useEffect, useRef } from "react";
import "./BackgroundOrbs.css";

// Slow drifting blurred gradient circles. Paused when the tab isn't focused
// to avoid burning CPU on an animation nobody's looking at.
export default function BackgroundOrbs() {
  const containerRef = useRef(null);

  useEffect(() => {
    const el = containerRef.current;
    const handleVisibility = () => {
      el.classList.toggle("sym-orbs--paused", document.hidden);
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  return (
    <div ref={containerRef} className="sym-orbs" aria-hidden="true">
      <div className="sym-orb sym-orb--pink" />
      <div className="sym-orb sym-orb--purple" />
      <div className="sym-orb sym-orb--teal" />
    </div>
  );
}