import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONTS } from "../styles";

export const TitleReveal: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(frame, [0, 30], [40, 0], { extrapolateRight: "clamp" });
  const subtitleOpacity = interpolate(frame, [50, 80], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const scanLineY = interpolate(frame, [0, 60], [-10, 110], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [170, 210], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
      opacity: fadeOut,
    }}>
      {/* Scan line */}
      <div style={{
        position: "absolute", left: 0, right: 0, height: 4,
        top: `${scanLineY}%`,
        background: `linear-gradient(90deg, transparent, ${COLORS.accent}, transparent)`,
        opacity: frame < 60 ? 0.8 : 0,
        boxShadow: `0 0 30px ${COLORS.accent}`,
      }} />

      <div style={{ textAlign: "center" }}>
        <h1 style={{
          fontFamily: FONTS.display,
          fontSize: 180,
          color: COLORS.text,
          letterSpacing: "0.08em",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textShadow: `0 0 60px ${COLORS.accent}80`,
          lineHeight: 1,
          margin: 0,
        }}>
          G1 MOVES
        </h1>
        <p style={{
          fontFamily: FONTS.mono,
          fontSize: 28,
          color: COLORS.muted,
          opacity: subtitleOpacity,
          marginTop: 24,
          letterSpacing: "0.1em",
        }}>
          THE LARGEST OPEN-SOURCE MOTION LIBRARY FOR HUMANOID ROBOTS
        </p>
      </div>
    </AbsoluteFill>
  );
};
