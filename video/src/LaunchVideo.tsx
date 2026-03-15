import React from "react";
import {
  AbsoluteFill,
  Series,
  OffthreadVideo,
  interpolate,
  useCurrentFrame,
  staticFile,
} from "remotion";
import { COLORS, FONTS } from "./styles";
import { LogoTitle } from "./scenes/LogoTitle";
import { HeroShot } from "./scenes/HeroShot";
import { Closing } from "./scenes/Closing";

interface ShowcaseClip {
  id: string;
  category: "DANCE" | "KARATE";
  path: string;
  durationS: number;
}

const sc = (
  cat: "DANCE" | "KARATE",
  id: string,
  catDir: string,
  dur: number,
): ShowcaseClip => ({
  id,
  category: cat,
  path: staticFile(`${catDir}/${id}/policy/${id}_policy.mp4`),
  durationS: dur,
});

const SHOWCASE_CLIPS: ShowcaseClip[] = [
  sc("DANCE", "J_Dance5_Hype", "dance", 12),
  sc("DANCE", "J_Dance17_Shuffle", "dance", 12),
  sc("DANCE", "J_Dance18_TikTok", "dance", 12),
  sc("KARATE", "M_Move7", "karate", 12),
  sc("KARATE", "B_CrazyChopsKarate", "karate", 12),
  sc("KARATE", "M_Move4", "karate", 12),
];

/** Frame at 37.5% through clip, capped so `needed` frames fit */
const safeStart = (clip: ShowcaseClip, needed: number) => {
  const total = Math.floor(clip.durationS * 30);
  const mid = Math.floor(total * 0.375);
  return Math.min(mid, Math.max(0, total - needed));
};

/* ---- 3x2 Grid of all 6 clips (10s) ---- */
const Grid6: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [270, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, opacity: fadeIn * fadeOut }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gridTemplateRows: "repeat(2, 1fr)",
          width: "100%",
          height: "100%",
          gap: 4,
          padding: 4,
        }}
      >
        {SHOWCASE_CLIPS.map((clip, i) => {
          const delay = i * 5;
          const cellOp = interpolate(frame - delay, [0, 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={clip.id}
              style={{
                overflow: "hidden",
                borderRadius: 8,
                opacity: cellOp,
                position: "relative",
              }}
            >
              <OffthreadVideo
                src={clip.path}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
                startFrom={safeStart(clip, 300)}
              />
              <div
                style={{
                  position: "absolute",
                  bottom: 12,
                  left: 12,
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                }}
              >
                <span
                  style={{
                    fontFamily: FONTS.display,
                    fontSize: 22,
                    color:
                      clip.category === "DANCE" ? COLORS.accent : "#ff6b35",
                    background: `${COLORS.bg}dd`,
                    padding: "2px 10px",
                    borderRadius: 4,
                    letterSpacing: "0.08em",
                  }}
                >
                  {clip.category}
                </span>
                <span
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 14,
                    color: COLORS.text,
                    background: `${COLORS.bg}cc`,
                    padding: "2px 8px",
                    borderRadius: 4,
                  }}
                >
                  {clip.id.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ---- Flash transition ---- */
const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 1, 3], [0, 0.9, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.accent, opacity: op }} />
  );
};

/* ---- Individual full-screen clip (10s) ---- */
const IndividualCut: React.FC<{ clip: ShowcaseClip }> = ({ clip }) => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [270, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [0, 300], [1.0, 1.06], {
    extrapolateRight: "clamp",
  });
  const labelOp = interpolate(frame, [10, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const labelX = interpolate(frame, [10, 25], [-60, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const accentColor = clip.category === "DANCE" ? COLORS.accent : "#ff6b35";

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
          opacity: fadeIn * fadeOut,
        }}
      >
        <OffthreadVideo
          src={clip.path}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
          }}
          startFrom={safeStart(clip, 300)}
        />
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 80,
          opacity: labelOp * fadeOut,
          transform: `translateX(${labelX}px)`,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 28,
            color: accentColor,
            letterSpacing: "0.15em",
            marginBottom: 8,
          }}
        >
          {clip.category}
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 72,
            color: COLORS.text,
            letterSpacing: "0.05em",
            textShadow: `0 0 40px ${COLORS.bg}`,
            lineHeight: 1,
          }}
        >
          {clip.id
            .replace(/^[A-Z]_/, "")
            .replace(/_/g, " ")
            .toUpperCase()}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Timeline:
// LogoTitle:  150f (5s)
// HeroShot:   300f (10s)
// Grid6:      300f (10s)
// 6 × (Flash 3f + Cut 300f) = 1818f (60.6s)
// Closing:    150f (5s)
// Total:     2718f = 90.6s

export const LaunchVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <Series>
        <Series.Sequence durationInFrames={150}>
          <LogoTitle />
        </Series.Sequence>
        <Series.Sequence durationInFrames={300}>
          <HeroShot />
        </Series.Sequence>
        <Series.Sequence durationInFrames={300}>
          <Grid6 />
        </Series.Sequence>
        {SHOWCASE_CLIPS.map((clip, i) => [
          <Series.Sequence key={`flash-${i}`} durationInFrames={3}>
            <Flash />
          </Series.Sequence>,
          <Series.Sequence key={`cut-${i}`} durationInFrames={300}>
            <IndividualCut clip={clip} />
          </Series.Sequence>,
        ])}
        <Series.Sequence durationInFrames={150}>
          <Closing />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
