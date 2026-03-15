import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame } from "remotion";
import { HERO_CLIP, midStart } from "../videos";
import { COLORS, FONTS } from "../styles";

const specs = [
  { label: "UNITREE G1", delay: 30 },
  { label: "29 DOF", delay: 60 },
  { label: "EDITION EDU", delay: 90 },
];

export const HeroShot: React.FC = () => {
  const frame = useCurrentFrame();

  const videoOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [260, 300], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <OffthreadVideo
        src={HERO_CLIP.path}
        style={{
          width: "100%", height: "100%", objectFit: "cover",
          opacity: videoOpacity * fadeOut,
        }}
        startFrom={Math.min(midStart(HERO_CLIP), Math.max(0, Math.floor(HERO_CLIP.durationS * 30) - 300))}
      />

      {/* Spec labels */}
      <div style={{
        position: "absolute", right: 80, top: "50%", transform: "translateY(-50%)",
        display: "flex", flexDirection: "column", gap: 20,
      }}>
        {specs.map(({ label, delay }) => {
          const opacity = interpolate(frame, [delay, delay + 20], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });
          const x = interpolate(frame, [delay, delay + 20], [40, 0], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });
          return (
            <div key={label} style={{
              fontFamily: FONTS.mono, fontSize: 24, color: COLORS.accent,
              opacity: opacity * fadeOut,
              transform: `translateX(${x}px)`,
              padding: "8px 20px",
              border: `1px solid ${COLORS.accent}40`,
              background: `${COLORS.bg}cc`,
            }}>
              {label}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
