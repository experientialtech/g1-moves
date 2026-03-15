import React from "react";
import {
  AbsoluteFill,
  Sequence,
  OffthreadVideo,
  Img,
  interpolate,
  useCurrentFrame,
  staticFile,
} from "remotion";
import { COLORS, FONTS } from "./styles";

interface ShowcaseClip {
  id: string;
  category: "DANCE" | "KARATE";
  path: string;
  durationS: number;
}

const sc = (cat: "DANCE" | "KARATE", id: string, catDir: string, dur: number): ShowcaseClip => ({
  id,
  category: cat,
  path: staticFile(`${catDir}/${id}/policy/${id}_policy.mp4`),
  durationS: dur,
});

const CLIPS: ShowcaseClip[] = [
  sc("DANCE",  "J_Dance5_Hype",       "dance",  20),
  sc("DANCE",  "J_Dance17_Shuffle",   "dance",  20),
  sc("DANCE",  "J_Dance18_TikTok",    "dance",  17.92),
  sc("KARATE", "M_ShortMove16",       "karate", 4),
  sc("KARATE", "M_Move11",            "karate", 4),
  sc("KARATE", "M_Move7",             "karate", 20),
];

const safeStart = (clip: ShowcaseClip, needed: number) => {
  const totalFrames = clip.durationS * 30;
  const mid = Math.floor(totalFrames * 0.375);
  return Math.min(mid, Math.max(0, Math.floor(totalFrames - needed)));
};

/* ---- Title card ---- */
const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const subOp = interpolate(frame, [15, 30], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [50, 60], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
      opacity: fadeOut,
    }}>
      <div style={{
        position: "absolute",
        width: 500, height: 500, borderRadius: "50%",
        background: `radial-gradient(circle, ${COLORS.accent}25, transparent 70%)`,
        opacity: interpolate(frame, [5, 20], [0, 0.6], { extrapolateRight: "clamp" }),
      }} />
      <h1 style={{
        fontFamily: FONTS.display, fontSize: 180,
        letterSpacing: "0.12em", lineHeight: 1, margin: 0,
        opacity: titleOp,
        background: `linear-gradient(180deg, ${COLORS.text} 20%, ${COLORS.muted} 100%)`,
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text",
      }}>
        TOP 6
      </h1>
      <p style={{
        fontFamily: FONTS.mono, fontSize: 28,
        color: COLORS.accent, letterSpacing: "0.15em",
        opacity: subOp, marginTop: 16,
      }}>
        3 DANCE + 3 KARATE
      </p>
    </AbsoluteFill>
  );
};

/* ---- 3x2 Grid ---- */
const GridView: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [120, 140], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, opacity: fadeIn * fadeOut }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gridTemplateRows: "repeat(2, 1fr)",
        width: "100%", height: "100%", gap: 4, padding: 4,
      }}>
        {CLIPS.map((clip, i) => {
          const delay = i * 4;
          const cellOp = interpolate(frame - delay, [0, 12], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          });

          return (
            <div key={clip.id} style={{
              overflow: "hidden", borderRadius: 6,
              opacity: cellOp, position: "relative",
            }}>
              <OffthreadVideo
                src={clip.path}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
                startFrom={safeStart(clip, 150)}
              />
              {/* Category + name label */}
              <div style={{
                position: "absolute", bottom: 10, left: 10,
                display: "flex", gap: 8, alignItems: "center",
              }}>
                <span style={{
                  fontFamily: FONTS.display, fontSize: 20,
                  color: clip.category === "DANCE" ? COLORS.accent : "#ff6b35",
                  background: `${COLORS.bg}dd`, padding: "2px 10px",
                  borderRadius: 3, letterSpacing: "0.08em",
                }}>
                  {clip.category}
                </span>
                <span style={{
                  fontFamily: FONTS.mono, fontSize: 13,
                  color: COLORS.text, background: `${COLORS.bg}cc`,
                  padding: "2px 8px", borderRadius: 3,
                }}>
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

/* ---- Flash frame ---- */
const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 1, 3], [0, 0.9, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.accent, opacity: op }} />
  );
};

/* ---- Individual clip cut ---- */
const IndividualCut: React.FC<{ clip: ShowcaseClip }> = ({ clip }) => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [67, 75], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [0, 75], [1.0, 1.08], { extrapolateRight: "clamp" });
  const labelOp = interpolate(frame, [8, 20], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const labelX = interpolate(frame, [8, 20], [-60, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  const accentColor = clip.category === "DANCE" ? COLORS.accent : "#ff6b35";

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <div style={{
        width: "100%", height: "100%", overflow: "hidden",
        opacity: fadeIn * fadeOut,
      }}>
        <OffthreadVideo
          src={clip.path}
          style={{
            width: "100%", height: "100%", objectFit: "cover",
            transform: `scale(${scale})`,
          }}
          startFrom={safeStart(clip, 90)}
        />
      </div>
      {/* Overlay labels */}
      <div style={{
        position: "absolute", bottom: 80, left: 80,
        opacity: labelOp * fadeOut,
        transform: `translateX(${labelX}px)`,
      }}>
        <div style={{
          fontFamily: FONTS.display, fontSize: 28,
          color: accentColor, letterSpacing: "0.15em",
          marginBottom: 8,
        }}>
          {clip.category}
        </div>
        <div style={{
          fontFamily: FONTS.display, fontSize: 72,
          color: COLORS.text, letterSpacing: "0.05em",
          textShadow: `0 0 40px ${COLORS.bg}`,
          lineHeight: 1,
        }}>
          {clip.id.replace(/^[A-Z]_/, "").replace(/_/g, " ").toUpperCase()}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---- Main composition ---- */
// Title: 60f (2s) | Grid: 150f (5s) | 6x(flash 3f + clip 75f) = 468f (15.6s) | End: 45f (1.5s)
// Total: 723 frames = 24.1s

export const ShowcaseReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <Sequence durationInFrames={60}>
        <TitleCard />
      </Sequence>
      <Sequence from={60} durationInFrames={150}>
        <GridView />
      </Sequence>

      {CLIPS.map((clip, i) => {
        const base = 210 + i * 78;
        return (
          <React.Fragment key={clip.id}>
            <Sequence from={base} durationInFrames={3}>
              <Flash />
            </Sequence>
            <Sequence from={base + 3} durationInFrames={75}>
              <IndividualCut clip={clip} />
            </Sequence>
          </React.Fragment>
        );
      })}

      {/* End card */}
      <Sequence from={210 + 6 * 78} durationInFrames={45}>
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 15, 30, 45], [0, 1, 1, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{
      backgroundColor: COLORS.bg,
      justifyContent: "center",
      alignItems: "center",
      opacity: op,
    }}>
      <Img
        src={staticFile("experiential_logo.png")}
        style={{ width: 300, marginBottom: 20 }}
      />
      <p style={{
        fontFamily: FONTS.mono, fontSize: 18,
        color: COLORS.muted, letterSpacing: "0.1em",
      }}>
        huggingface.co/datasets/exptech/g1-moves
      </p>
    </AbsoluteFill>
  );
};
