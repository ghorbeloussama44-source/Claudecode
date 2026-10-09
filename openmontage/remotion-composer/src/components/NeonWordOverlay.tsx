import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadNotoKufiArabic } from "@remotion/google-fonts/NotoKufiArabic";

const { fontFamily: notoKufiArabic } = loadNotoKufiArabic("normal", {
  weights: ["700", "900"],
});

// Reuses the same word-timestamp shape as CaptionOverlay.
export interface NeonWord {
  word: string;
  startMs: number;
  endMs: number;
}

export type NeonWordOverlayProps = {
  words: NeonWord[];
  fontSize?: number;
  neonColor?: string;
  fontFamily?: string;
  rtl?: boolean;
};

const WordCard: React.FC<{
  word: NeonWord;
  durationInFrames: number;
  fontSize: number;
  neonColor: string;
  fontFamily: string;
  rtl: boolean;
}> = ({ durationInFrames, word, fontSize, neonColor, fontFamily, rtl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance: quick punch-in scale, slight overshoot for a "luxe" snap.
  const entrance = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 200, mass: 0.6 },
  });

  // Exit: fast fade/scale-down over the last few frames.
  const exitFrames = Math.min(6, durationInFrames - 1);
  const exit = interpolate(
    frame,
    [durationInFrames - exitFrames, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const scale = interpolate(entrance, [0, 1], [0.55, 1]) * (0.94 + exit * 0.06);
  const opacity = Math.min(entrance, 1) * exit;

  // Slow continuous glow pulse so the neon reads as "lit", not static.
  const pulse = 0.85 + 0.15 * Math.sin((frame / fps) * Math.PI * 2 * 1.4);

  const glow = [
    `0 0 ${10 * pulse}px ${neonColor}`,
    `0 0 ${22 * pulse}px ${neonColor}`,
    `0 0 ${44 * pulse}px ${neonColor}cc`,
    `0 0 ${80 * pulse}px ${neonColor}66`,
    `0 3px 10px rgba(0,0,0,0.55)`,
  ].join(", ");

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          fontFamily,
          fontWeight: 900,
          fontSize,
          color: "#fff8ec",
          textShadow: glow,
          letterSpacing: rtl ? "0" : "0.02em",
          direction: rtl ? "rtl" : "ltr",
          unicodeBidi: "plaintext",
          WebkitTextStroke: `1px ${neonColor}`,
          padding: "0 40px",
          textAlign: "center",
        }}
      >
        {word.word}
      </div>
    </AbsoluteFill>
  );
};

export const NeonWordOverlay: React.FC<NeonWordOverlayProps> = ({
  words,
  fontSize = 140,
  neonColor = "#FFC94A",
  fontFamily,
  rtl = false,
}) => {
  const { fps } = useVideoConfig();
  const resolvedFontFamily = fontFamily ?? notoKufiArabic;

  return (
    <AbsoluteFill>
      {words.map((w, i) => {
        const fromFrame = Math.round((w.startMs / 1000) * fps);
        const holdMs = 120;
        const duration = Math.max(
          1,
          Math.round(((w.endMs - w.startMs + holdMs) / 1000) * fps)
        );
        return (
          <Sequence key={`${w.startMs}-${i}`} from={fromFrame} durationInFrames={duration}>
            <WordCard
              word={w}
              durationInFrames={duration}
              fontSize={fontSize}
              neonColor={neonColor}
              fontFamily={resolvedFontFamily}
              rtl={rtl}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
