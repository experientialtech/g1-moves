import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, staticFile } from "remotion";
import { COLORS, FONTS } from "../styles";

export const Closing: React.FC = () => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 30, 120, 150], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
      opacity,
    }}>
      <div style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", gap: 40,
      }}>
        <Img src={staticFile("logo.png")} style={{ width: 400 }} />
        <div style={{
          width: 100, height: 1, background: `${COLORS.accent}60`,
        }} />
        <Img src={staticFile("experiential_logo.png")} style={{ width: 300 }} />
        <p style={{
          fontFamily: FONTS.mono, fontSize: 18, color: COLORS.muted,
          marginTop: 20, letterSpacing: "0.1em",
        }}>
          huggingface.co/datasets/exptech/g1-moves
        </p>
      </div>
    </AbsoluteFill>
  );
};
