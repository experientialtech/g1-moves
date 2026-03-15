export const COLORS = {
  bg: "#07070b",
  card: "#12121b",
  accent: "#00d4ff",
  text: "#e2e2ec",
  muted: "#8585a0",
} as const;

export const FONTS = {
  display: "'Bebas Neue', sans-serif",
  body: "'Manrope', sans-serif",
  mono: "'IBM Plex Mono', monospace",
} as const;

// Frame timing at 30fps
export const SCENES = {
  logoTitle:   { start: 0,    duration: 150 },  // 0-5s     logo + G1 MOVES together
  demoVideo:   { start: 150,  duration: 510 },  // 5-22s    desktop robot video
  heroShot:    { start: 660,  duration: 300 },  // 22-32s
  dance:       { start: 960,  duration: 600 },  // 32-52s
  karate:      { start: 1560, duration: 600 },  // 52-72s
  bonus:       { start: 2160, duration: 300 },  // 72-82s
  highlights:  { start: 2460, duration: 390 },  // 82-95s
  stats:       { start: 2850, duration: 210 },  // 95-102s
  closing:     { start: 3060, duration: 150 },  // 102-107s
} as const;
