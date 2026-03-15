import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, staticFile } from "remotion";
import { COLORS } from "../styles";

export const LogoIntro: React.FC = () => {
  const frame = useCurrentFrame();

  const logoOpacity = interpolate(frame, [0, 40, 110, 150], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const logoScale = interpolate(frame, [0, 40], [0.9, 1], { extrapolateRight: "clamp" });
  const glowOpacity = interpolate(frame, [20, 60, 110, 150], [0, 0.6, 0.6, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
    }}>
      <div style={{
        position: "absolute",
        width: 500, height: 500, borderRadius: "50%",
        background: `radial-gradient(circle, ${COLORS.accent}40, transparent 70%)`,
        opacity: glowOpacity,
      }} />
      <Img
        src={staticFile("experiential_logo.png")}
        style={{
          width: 500,
          opacity: logoOpacity,
          transform: `scale(${logoScale})`,
        }}
      />
    </AbsoluteFill>
  );
};
