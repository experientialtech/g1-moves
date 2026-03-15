import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame } from "remotion";
import { ClipDef, midStart } from "../videos";
import { COLORS, FONTS } from "../styles";

interface Props {
  title: string;
  clips: ClipDef[];
  count: number;
  gridCols?: number;
  gridRows?: number;
}

export const CategoryMontage: React.FC<Props> = ({
  title, clips, count, gridCols = 3, gridRows = 2,
}) => {
  const frame = useCurrentFrame();
  const gridSize = gridCols * gridRows;

  // Title card: first 45 frames (1.5s)
  const titlePhase = frame < 45;
  const titleOpacity = titlePhase
    ? interpolate(frame, [0, 15, 30, 45], [0, 1, 1, 0], { extrapolateRight: "clamp" })
    : 0;

  // Grid phase: remaining frames
  const gridFrame = Math.max(0, frame - 45);
  const cycleFrames = 75; // 2.5s per cycle
  const cycleIndex = Math.floor(gridFrame / cycleFrames);

  // Count badge
  const countOpacity = interpolate(frame, [45, 75], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  if (titlePhase) {
    return (
      <AbsoluteFill style={{
        backgroundColor: COLORS.bg,
        justifyContent: "center",
        alignItems: "center",
      }}>
        <h2 style={{
          fontFamily: FONTS.display, fontSize: 140, color: COLORS.accent,
          opacity: titleOpacity, letterSpacing: "0.15em",
          textShadow: `0 0 40px ${COLORS.accent}60`,
          margin: 0,
        }}>
          {title}
        </h2>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
        gridTemplateRows: `repeat(${gridRows}, 1fr)`,
        width: "100%", height: "100%", gap: 4, padding: 4,
      }}>
        {Array.from({ length: gridSize }).map((_, i) => {
          const clipIdx = ((cycleIndex * gridSize) + i) % clips.length;
          const clip = clips[clipIdx];
          const cellDelay = i * 3;
          const cellOpacity = interpolate(gridFrame - cellDelay, [0, 15], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });

          return (
            <div key={i} style={{
              overflow: "hidden", borderRadius: 4,
              opacity: cellOpacity, position: "relative",
            }}>
              <OffthreadVideo
                src={clip.path}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
                startFrom={midStart(clip)}
              />
              <div style={{
                position: "absolute", bottom: 8, left: 8,
                fontFamily: FONTS.mono, fontSize: 14, color: COLORS.accent,
                background: `${COLORS.bg}cc`, padding: "2px 8px", borderRadius: 2,
              }}>
                {clip.id.replace(/_/g, " ")}
              </div>
            </div>
          );
        })}
      </div>

      {/* Count badge */}
      <div style={{
        position: "absolute", bottom: 40, right: 40,
        fontFamily: FONTS.display, fontSize: 48, color: COLORS.accent,
        opacity: countOpacity,
        background: `${COLORS.bg}dd`, padding: "8px 24px", borderRadius: 8,
        border: `1px solid ${COLORS.accent}40`,
      }}>
        {count} {title} MOTIONS
      </div>
    </AbsoluteFill>
  );
};
