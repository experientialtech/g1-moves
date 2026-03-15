import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, staticFile } from "remotion";
import { COLORS, FONTS } from "../styles";

export const LogoTitle: React.FC = () => {
  const frame = useCurrentFrame();

  const logoOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  const logoScale = interpolate(frame, [0, 30], [0.9, 1], { extrapolateRight: "clamp" });
  const glowOpacity = interpolate(frame, [15, 50, 110, 150], [0, 0.5, 0.5, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const titleOpacity = interpolate(frame, [25, 55], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [25, 55], [30, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const subtitleOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [130, 150], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
      opacity: fadeOut,
    }}>
      {/* Cyan glow */}
      <div style={{
        position: "absolute",
        width: 600, height: 600, borderRadius: "50%",
        background: `radial-gradient(circle, ${COLORS.accent}30, transparent 70%)`,
        opacity: glowOpacity,
      }} />

      <div style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", gap: 30,
      }}>
        <Img
          src={staticFile("experiential_logo.png")}
          style={{
            width: 400,
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
          }}
        />
        <h1 style={{
          fontFamily: FONTS.display,
          fontSize: 160,
          letterSpacing: "0.1em",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          lineHeight: 1,
          margin: 0,
          background: `linear-gradient(180deg, ${COLORS.text} 20%, ${COLORS.muted} 100%)`,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
        }}>
          G1 MOVES
        </h1>
        <p style={{
          fontFamily: FONTS.mono,
          fontSize: 24,
          color: COLORS.muted,
          opacity: subtitleOpacity,
          letterSpacing: "0.1em",
          marginTop: 8,
        }}>
          ALL MOTION CAPTURED FROM REAL PERFORMERS IN AUSTIN, TX
        </p>
      </div>
    </AbsoluteFill>
  );
};
