// Deterministic gradient "album art" per song, in the same palette family as
// the design reference — which itself uses generated gradients rather than
// real album art, so this isn't a downgrade from the source design.
const PALETTE = [
  ["#ff6fae", "#7b5cff"],
  ["#35d0c0", "#122036"],
  ["#e8a33d", "#b8531f"],
  ["#ff4f9e", "#8e2de2"],
  ["#4b4f9e", "#161a33"],
  ["#d98a5a", "#5a2f2a"],
  ["#2f6d8c", "#122036"],
  ["#ff8fbf", "#7b5cff"],
];

function hashString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

export function gradientFor(song) {
  const [from, to] = PALETTE[hashString(`${song.id}-${song.title}`) % PALETTE.length];
  return `linear-gradient(150deg, ${from}, ${to})`;
}