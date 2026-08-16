import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadNotoSansArabic } from "@remotion/google-fonts/NotoSansArabic";

const { fontFamily: notoSansArabicFamily } = loadNotoSansArabic("normal", {
  weights: ["700"],
});

// Word-level caption for TikTok-style highlight display
export interface WordCaption {
  word: string;
  startMs: number;
  endMs: number;
}

type CaptionOverlayProps = {
  words: WordCaption[];
  // How many words to show at once in a "page"
  wordsPerPage?: number;
  fontSize?: number;
  color?: string;
  highlightColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  // Right-to-left script (Arabic, Hebrew, ...): keeps word order correct
  // within a page instead of the browser's default LTR paragraph flow.
  rtl?: boolean;
};

interface CaptionPage {
  words: WordCaption[];
  startMs: number;
  endMs: number;
}

// Gap between two words beyond which we treat it as silence (instrumental
// break, breath, line change) rather than normal speech pacing. A page
// never spans a gap this large — it ends before the gap and a new page
// starts after it, so the caption box isn't left sitting on screen with
// nothing being said.
const SILENCE_GAP_MS = 700;

function buildPages(words: WordCaption[], wordsPerPage: number): CaptionPage[] {
  const pages: CaptionPage[] = [];
  let current: WordCaption[] = [];

  const flush = () => {
    if (current.length === 0) return;
    pages.push({
      words: current,
      startMs: current[0].startMs,
      endMs: current[current.length - 1].endMs,
    });
    current = [];
  };

  for (const w of words) {
    const prev = current[current.length - 1];
    const isSilenceBreak = prev !== undefined && w.startMs - prev.endMs > SILENCE_GAP_MS;
    if (isSilenceBreak || current.length >= wordsPerPage) {
      flush();
    }
    current.push(w);
  }
  flush();

  return pages;
}

const PageRenderer: React.FC<{
  page: CaptionPage;
  durationInFrames: number;
  fontSize: number;
  color: string;
  highlightColor: string;
  backgroundColor: string;
  fontFamily: string;
  rtl: boolean;
}> = ({ page, durationInFrames, fontSize, color, highlightColor, backgroundColor, fontFamily, rtl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentMs = page.startMs + (frame / fps) * 1000;

  // Spring entrance
  const entrance = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 120 },
  });
  // Fade out over the last few frames instead of a hard cut when the page ends.
  const exitFrames = Math.min(8, durationInFrames - 1);
  const exit = interpolate(
    frame,
    [durationInFrames - exitFrames, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = entrance * exit;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 80,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${interpolate(entrance, [0, 1], [20, 0])}px)`,
          backgroundColor,
          borderRadius: 12,
          padding: "14px 28px",
          maxWidth: "80%",
          textAlign: "center",
        }}
      >
        <span
          style={{
            fontSize,
            fontWeight: 700,
            fontFamily,
            lineHeight: 1.4,
            whiteSpace: "pre-wrap",
            direction: rtl ? "rtl" : "ltr",
            unicodeBidi: "plaintext",
          }}
        >
          {page.words.map((w, i) => {
            const isActive = w.startMs <= currentMs && w.endMs > currentMs;
            const isPast = w.endMs <= currentMs;
            return (
              <span
                key={`${w.startMs}-${i}`}
                style={{
                  color: isActive ? highlightColor : isPast ? color : `${color}99`,
                  transition: "none", // CSS transitions forbidden in Remotion
                  textShadow: isActive
                    ? `0 0 20px ${highlightColor}66, 0 2px 4px rgba(0,0,0,0.5)`
                    : "0 2px 4px rgba(0,0,0,0.5)",
                }}
              >
                {w.word}{i < page.words.length - 1 ? " " : ""}
              </span>
            );
          })}
        </span>
      </div>
    </AbsoluteFill>
  );
};

export const CaptionOverlay: React.FC<CaptionOverlayProps> = ({
  words,
  wordsPerPage = 6,
  fontSize = 42,
  color = "#F8FAFC",
  highlightColor = "#22D3EE",
  backgroundColor = "rgba(15, 23, 42, 0.75)",
  fontFamily,
  rtl = false,
}) => {
  const { fps } = useVideoConfig();
  const pages = buildPages(words, wordsPerPage);
  const resolvedFontFamily =
    fontFamily ?? (rtl ? notoSansArabicFamily : "Space Grotesk, Inter, system-ui, sans-serif");

  return (
    <AbsoluteFill>
      {pages.map((page, i) => {
        const fromFrame = Math.round((page.startMs / 1000) * fps);
        // Hold each page for its own words plus a short trailing beat for
        // readability — never until the next page starts. That's what let
        // the box sit frozen through a silence before this fix.
        const holdMs = 450;
        const duration = Math.max(
          1,
          Math.round(((page.endMs - page.startMs + holdMs) / 1000) * fps)
        );

        return (
          <Sequence key={i} from={fromFrame} durationInFrames={duration}>
            <PageRenderer
              page={page}
              durationInFrames={duration}
              fontSize={fontSize}
              color={color}
              highlightColor={highlightColor}
              backgroundColor={backgroundColor}
              fontFamily={resolvedFontFamily}
              rtl={rtl}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
