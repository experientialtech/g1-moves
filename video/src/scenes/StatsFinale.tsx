import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONTS } from "../styles";

const stats = [
  { value: "60", label: "MOTIONS", delay: 0 },
  { value: "3", label: "CATEGORIES", delay: 20 },
  { value: "8,192", label: "PARALLEL ENVS", delay: 40 },
  { value: "29", label: "DOF", delay: 60 },
];

export const StatsFinale: React.FC = () => {
  const frame = useCurrentFrame();
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
      <div style={{ display: "flex", gap: 60 }}>
        {stats.map(({ value, label, delay }) => {
          const opacity = interpolate(frame, [delay, delay + 25], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });
          const y = interpolate(frame, [delay, delay + 25], [30, 0], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });
          return (
            <div key={label} style={{
              textAlign: "center", opacity, transform: `translateY(${y}px)`,
            }}>
              <div style={{
                fontFamily: FONTS.display, fontSize: 96, color: COLORS.accent,
                lineHeight: 1,
              }}>
                {value}
              </div>
              <div style={{
                fontFamily: FONTS.mono, fontSize: 18, color: COLORS.muted,
                marginTop: 8, letterSpacing: "0.1em",
              }}>
                {label}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        position: "absolute", bottom: 60,
        fontFamily: FONTS.mono, fontSize: 22, color: COLORS.muted,
        opacity: interpolate(frame, [80, 110], [0, 1], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp",
        }),
        letterSpacing: "0.15em",
      }}>
        OPEN SOURCE ON HUGGINGFACE
      </div>
    </AbsoluteFill>
  );
};
