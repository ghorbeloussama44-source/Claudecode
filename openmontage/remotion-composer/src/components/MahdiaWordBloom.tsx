import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadTajawal } from "@remotion/google-fonts/Tajawal";

const { fontFamily: tajawal } = loadTajawal("normal", { weights: ["700"] });

const PARCHMENT = "#f5efdc";
const GOLD = "#cda44d";
const TEAL = "#3aa89a";

export interface BloomWord {
  word: string;
  startMs: number;
  endMs: number;
}

export type MahdiaWordBloomProps = {
  words: BloomWord[];
  fontSize?: number;
  rtl?: boolean;
};

// One word at a time, centered in frame, popping/blooming in exactly when
// the narrator says it — a bouncy scale-up with a soft radial glow behind
// the text — instead of a lower-third multi-word caption bar. Each word
// gets its own independent Sequence so timing never depends on neighboring
// words (the previous paged design could leave a beat of nothing visible
// between two back-to-back words with no silence gap).
const WordBloomItem: React.FC<{ text: string; fontSize: number; exitStartFrame: number; durationInFrames: number }> = ({
  text,
  fontSize,
  exitStartFrame,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Bouncy pop-in: low damping lets it overshoot past 1 before settling —
  // that overshoot-and-settle reads as the "blooming" flourish.
  const pop = spring({ frame, fps, config: { damping: 10, stiffness: 200, mass: 0.6 } });
  const scale = interpolate(pop, [0, 1], [0.35, 1], { extrapolateRight: "extend" });

  const exit = interpolate(frame, [exitStartFrame, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const entranceOpacity = interpolate(pop, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const opacity = Math.min(entranceOpacity, exit);

  const glowScale = interpolate(pop, [0, 1], [0.4, 1.6], { extrapolateRight: "extend" });
  const glowOpacity = opacity * 0.6;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          position: "absolute",
          width: 420,
          height: 420,
          borderRadius: "50%",
          transform: `scale(${glowScale})`,
          opacity: glowOpacity,
          background: `radial-gradient(circle, ${TEAL}55 0%, ${GOLD}33 45%, transparent 72%)`,
          filter: "blur(4px)",
        }}
      />
      <div
        style={{
          position: "relative",
          opacity,
          transform: `scale(${scale})`,
          fontFamily: tajawal,
          fontWeight: 700,
          fontSize,
          color: PARCHMENT,
          direction: "rtl",
          unicodeBidi: "plaintext",
          textAlign: "center",
          padding: "0 60px",
          textShadow: `0 0 40px ${TEAL}88, 0 0 18px rgba(0,0,0,0.7), 0 3px 10px rgba(0,0,0,0.6)`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

export const MahdiaWordBloom: React.FC<MahdiaWordBloomProps> = ({ words, fontSize = 76 }) => {
  const { fps } = useVideoConfig();
  const holdMs = 180;

  return (
    <AbsoluteFill>
      {words.map((w, i) => {
        const fromFrame = Math.round((w.startMs / 1000) * fps);
        const nextWord = words[i + 1];
        const uncappedEndFrame = Math.round(((w.endMs + holdMs) / 1000) * fps);
        const endFrame = nextWord
          ? Math.min(uncappedEndFrame, Math.round((nextWord.startMs / 1000) * fps))
          : uncappedEndFrame;
        const durationInFrames = Math.max(1, endFrame - fromFrame);
        const wordFrames = Math.max(1, Math.round(((w.endMs - w.startMs) / 1000) * fps));
        const exitStartFrame = Math.min(wordFrames, Math.max(0, durationInFrames - 3), durationInFrames - 1);

        return (
          <Sequence key={i} from={fromFrame} durationInFrames={durationInFrames}>
            <WordBloomItem
              text={w.word}
              fontSize={fontSize}
              exitStartFrame={exitStartFrame}
              durationInFrames={durationInFrames}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
