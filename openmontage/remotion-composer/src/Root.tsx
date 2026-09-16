import { Composition, CalculateMetadataFunction } from "remotion";
import { Explainer, ExplainerProps } from "./Explainer";
import {
  CinematicRenderer,
  calculateCinematicMetadata,
} from "./CinematicRenderer";
import { signalFromTomorrowWithMusicFixture } from "./cinematic/fixtures";
import { TalkingHead, TalkingHeadProps } from "./TalkingHead";
import {
  TitledVideo,
  calculateTitledVideoMetadata,
} from "./TitledVideo";
import { EndTag, EndTagProps } from "./components/EndTag";
import { HeroTitle } from "./components/HeroTitle";
import { ProductReveal, ProductRevealProps } from "./components/ProductReveal";
import { CaptionOverlay, WordCaption } from "./components/CaptionOverlay";
import { MahdiaWordBloom } from "./components/MahdiaWordBloom";
import { MediLearnConcept } from "./components/MediLearnConcept";
import { NeonWordOverlay, NeonWordOverlayProps, NeonWord } from "./components/NeonWordOverlay";
import { CollageBurst, CollageBurstProps } from "./CollageBurst";
import { LyricOverlay, LyricOverlayProps } from "./LyricOverlay";
import { MahdiaTitleCard, MahdiaTitleCardProps } from "./components/MahdiaTitleCard";

// Word-level timestamps for the main VO script ("في مدينة المهدية..." through
// "...من كل أنحاء العالم"), transcribed via faster-whisper from
// projects/mahdia-festival/assets/audio/clip2_vo_final.wav (offset +20000ms,
// the point in the final montage where clip2's local time 0 lands — a plain
// hard concat at exactly 20s, no crossfade/fade-to-black, so the wave
// transition inside opening_ai.mp4's own 19s-20s plays fully intact) and
// clip3_vo_final.wav (offset +30000ms, where clip3 starts after the concat,
// using the original unshifted 20.0s-37.1s video window — the paint-explosion
// beat still lands close to "إبداع بلا قيود" because the +1s later clip2/clip3
// start offsets from removing the crossfade compensate for it).
// Typos from ASR ("يلتق", "بالمهدي", "ابداع") are corrected for on-screen
// display; timings are left as transcribed.
const mahdiaScriptWords: WordCaption[] = [
  { word: "في", startMs: 20000, endMs: 20160 },
  { word: "مدينة", startMs: 20160, endMs: 20640 },
  { word: "المهدية", startMs: 20640, endMs: 21300 },
  { word: "حيث", startMs: 21300, endMs: 21920 },
  { word: "يلتقي", startMs: 21920, endMs: 22300 },
  { word: "البحر", startMs: 22300, endMs: 22700 },
  { word: "بالتاريخ", startMs: 22700, endMs: 23480 },
  { word: "تنطلق", startMs: 23480, endMs: 24180 },
  { word: "الدورة", startMs: 24180, endMs: 24680 },
  { word: "الأولى", startMs: 24680, endMs: 25140 },
  { word: "من", startMs: 25140, endMs: 25260 },
  { word: "المهرجان", startMs: 25260, endMs: 25860 },
  { word: "الدولي", startMs: 25860, endMs: 26400 },
  { word: "الجامعي", startMs: 26400, endMs: 27400 },
  { word: "للفنون", startMs: 27400, endMs: 27880 },
  { word: "التشكيلية", startMs: 27880, endMs: 28640 },
  { word: "بالمهدية", startMs: 28640, endMs: 29500 },
  { word: "فن", startMs: 30000, endMs: 30920 },
  { word: "بلا", startMs: 30920, endMs: 31300 },
  { word: "حدود", startMs: 31300, endMs: 31800 },
  { word: "إبداع", startMs: 31800, endMs: 32640 },
  { word: "بلا", startMs: 32640, endMs: 32940 },
  { word: "قيود", startMs: 32940, endMs: 33460 },
  { word: "من", startMs: 33460, endMs: 34100 },
  { word: "26", startMs: 34100, endMs: 34920 },
  { word: "إلى", startMs: 34920, endMs: 35560 },
  { word: "31", startMs: 35560, endMs: 36340 },
  { word: "أكتوبر", startMs: 36340, endMs: 37240 },
  { word: "المهدية", startMs: 37240, endMs: 38320 },
  { word: "تفتح", startMs: 38320, endMs: 38900 },
  { word: "أبوابها", startMs: 38900, endMs: 39560 },
  { word: "للفن", startMs: 39560, endMs: 40000 },
  { word: "والإبداع", startMs: 40000, endMs: 40620 },
  { word: "القادم", startMs: 40620, endMs: 41440 },
  { word: "من", startMs: 41440, endMs: 41600 },
  { word: "كل", startMs: 41600, endMs: 41900 },
  { word: "أنحاء", startMs: 41900, endMs: 42380 },
  { word: "العالم", startMs: 42380, endMs: 42880 },
];

// ---------------------------------------------------------------------------
// Theme System — prevents every video from looking like dark fintech
// ---------------------------------------------------------------------------

export interface ThemeConfig {
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  surfaceColor: string;
  textColor: string;
  mutedTextColor: string;
  headingFont: string;
  bodyFont: string;
  monoFont: string;
  chartColors: string[];
  springConfig: { damping: number; stiffness: number; mass: number };
  transitionDuration: number;
  captionHighlightColor: string;
  captionBackgroundColor: string;
}

export const THEMES: Record<string, ThemeConfig> = {
  "clean-professional": {
    primaryColor: "#2563EB",
    accentColor: "#F59E0B",
    backgroundColor: "#FFFFFF",
    surfaceColor: "#F9FAFB",
    textColor: "#1F2937",
    mutedTextColor: "#6B7280",
    headingFont: "Inter",
    bodyFont: "Inter",
    monoFont: "JetBrains Mono",
    chartColors: ["#2563EB", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899", "#06B6D4"],
    springConfig: { damping: 20, stiffness: 120, mass: 1 },
    transitionDuration: 0.4,
    captionHighlightColor: "#2563EB",
    captionBackgroundColor: "rgba(255, 255, 255, 0.85)",
  },
  "flat-motion-graphics": {
    primaryColor: "#7C3AED",
    accentColor: "#EC4899",
    backgroundColor: "#0F172A",
    surfaceColor: "#1E293B",
    textColor: "#F8FAFC",
    mutedTextColor: "#94A3B8",
    headingFont: "Space Grotesk",
    bodyFont: "Space Grotesk",
    monoFont: "Fira Code",
    chartColors: ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#10B981", "#EF4444"],
    springConfig: { damping: 12, stiffness: 80, mass: 1 },
    transitionDuration: 0.3,
    captionHighlightColor: "#22D3EE",
    captionBackgroundColor: "rgba(15, 23, 42, 0.75)",
  },
  "minimalist-diagram": {
    primaryColor: "#1A1A2E",
    accentColor: "#E94560",
    backgroundColor: "#FAFAFA",
    surfaceColor: "#FFFFFF",
    textColor: "#1A1A2E",
    mutedTextColor: "#6B7280",
    headingFont: "IBM Plex Sans",
    bodyFont: "IBM Plex Sans",
    monoFont: "IBM Plex Mono",
    chartColors: ["#E94560", "#1A1A2E", "#0F3460", "#9CA3AF"],
    springConfig: { damping: 25, stiffness: 150, mass: 1 },
    transitionDuration: 0.5,
    captionHighlightColor: "#E94560",
    captionBackgroundColor: "rgba(250, 250, 250, 0.9)",
  },
  "anime-ghibli": {
    primaryColor: "#2D5016",
    accentColor: "#FFB347",
    backgroundColor: "#0A0A1A",
    surfaceColor: "#1A2332",
    textColor: "#F0E6D3",
    mutedTextColor: "#A8957E",
    headingFont: "Noto Serif JP",
    bodyFont: "Noto Sans",
    monoFont: "Fira Code",
    chartColors: ["#FFB347", "#2D5016", "#FF6B9D", "#A8E6CF", "#6B4C8A", "#E8927C"],
    springConfig: { damping: 18, stiffness: 60, mass: 1 },
    transitionDuration: 1.0,
    captionHighlightColor: "#FFB347",
    captionBackgroundColor: "rgba(10, 10, 26, 0.8)",
  },
};

// Default theme when none is specified — uses the existing dark style for backwards compatibility
export const DEFAULT_THEME = THEMES["flat-motion-graphics"];

export function resolveTheme(props: Record<string, unknown>): ThemeConfig {
  const themeName = (props.theme as string) || (props.playbook as string);
  if (themeName && THEMES[themeName]) {
    return THEMES[themeName];
  }
  // Allow custom theme passed as full object
  if (props.themeConfig && typeof props.themeConfig === "object") {
    return { ...DEFAULT_THEME, ...(props.themeConfig as Partial<ThemeConfig>) };
  }
  return DEFAULT_THEME;
}

const calculateMetadata: CalculateMetadataFunction<ExplainerProps> = async ({
  props,
}) => {
  const cuts = props.cuts || [];
  if (cuts.length === 0) {
    return { durationInFrames: 30 * 60 };
  }
  const lastEnd = Math.max(...cuts.map((c) => c.out_seconds || 0));
  // Add 1 second padding for final fade
  return { durationInFrames: Math.ceil((lastEnd + 1) * 30) };
};

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="Explainer"
        component={Explainer}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          cuts: [],
          overlays: [],
          captions: [],
          audio: {},
        }}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="CinematicRenderer"
        component={CinematicRenderer}
        durationInFrames={30 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          scenes: [],
          titleFontSize: 78,
          titleWidth: 1320,
          signalLineCount: 18,
        }}
        calculateMetadata={calculateCinematicMetadata}
      />
      <Composition
        id="SignalFromTomorrowWithMusic"
        component={CinematicRenderer}
        durationInFrames={30 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={signalFromTomorrowWithMusicFixture}
        calculateMetadata={calculateCinematicMetadata}
      />
      <Composition
        id="TalkingHead"
        component={TalkingHead}
        durationInFrames={30 * 300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          videoSrc: "",
          captions: [],
          overlays: [],
          wordsPerPage: 4,
          fontSize: 52,
          highlightColor: "#22D3EE",
        }}
      />
      <Composition
        id="TitledVideo"
        component={TitledVideo}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          videoSrc: "",
          tagline: "home is a verb.",
          taglineInSeconds: 53.5,
          taglineOutSeconds: undefined,
          topPx: 150,
          fontSize: 148,
          accentColor: "#F5C470",
        }}
        calculateMetadata={calculateTitledVideoMetadata}
      />
      <Composition
        id="HeroTitle"
        component={HeroTitle}
        durationInFrames={30 * 17}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "THE CALIBRATORS",
          subtitle: "The People Who Define Reality",
        }}
      />
      <Composition
        id="ProductReveal"
        component={ProductReveal}
        durationInFrames={30 * 8}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{
          productImage: "airnothing/product.png",
          productName: "AirNothing Pro Max Ultra",
          price: "Starting at $999",
          tagline: "Nothing included.",
          closer: "Less is nothing.",
          accentColor: "#00D4FF",
        } as ProductRevealProps}
      />
      <Composition
        id="ProductRevealVertical"
        component={ProductReveal}
        durationInFrames={30 * 8}
        fps={30}
        width={720}
        height={1280}
        defaultProps={{
          productImage: "airnothing/product.png",
          productName: "AirNothing Pro Max Ultra",
          price: "Starting at $999",
          tagline: "Nothing included.",
          closer: "Less is nothing.",
          accentColor: "#00D4FF",
        } as ProductRevealProps}
      />
      <Composition
        id="CaptionOverlayOnly"
        component={CaptionOverlay}
        durationInFrames={30 * 300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          words: [] as WordCaption[],
          wordsPerPage: 3,
          fontSize: 58,
          highlightColor: "#FACC15",
          backgroundColor: "rgba(15, 23, 42, 0.75)",
          rtl: false,
        }}
      />
      <Composition
        id="CollageBurst"
        component={CollageBurst}
        durationInFrames={30 * 30}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          backgroundSrc: "",
          backgroundInSeconds: 0,
          curtainStartSeconds: 1.5,
          curtainEndSeconds: 3.0,
          clips: [],
        } as CollageBurstProps}
      />
      <Composition
        id="LyricOverlay"
        component={LyricOverlay}
        durationInFrames={30 * 28}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          videoSrc: "",
          lyrics: [],
          bottomY: 0.88,
        } as LyricOverlayProps}
      />
      <Composition
        id="LyricOverlayOnly"
        component={LyricOverlay}
        durationInFrames={30 * 300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          lyrics: [],
          bottomY: 0.88,
          rtl: false,
        } as LyricOverlayProps}
      />
      <Composition
        id="NeonWordOverlayOnly"
        component={NeonWordOverlay}
        durationInFrames={30 * 300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          words: [] as NeonWord[],
          fontSize: 140,
          neonColor: "#FFC94A",
          rtl: false,
        } as NeonWordOverlayProps}
      />
      <Composition
        id="MahdiaCreditsCard"
        component={MahdiaTitleCard}
        durationInFrames={500}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ variant: "credits" } as MahdiaTitleCardProps}
      />
      <Composition
        id="MahdiaCreditsOverlay"
        component={MahdiaTitleCard}
        durationInFrames={480}
        fps={24}
        width={1280}
        height={720}
        defaultProps={{ variant: "creditsOverlay" } as MahdiaTitleCardProps}
      />
      <Composition
        id="MahdiaScriptCaptions"
        component={MahdiaWordBloom}
        durationInFrames={1131}
        fps={24}
        width={1280}
        height={720}
        defaultProps={{
          words: mahdiaScriptWords,
          fontSize: 76,
          rtl: true,
        }}
      />
      <Composition
        id="MediLearnConcept"
        component={MediLearnConcept}
        durationInFrames={7217}
        fps={24}
        width={1280}
        height={720}
      />
      <Composition
        id="MahdiaTitleCard"
        component={MahdiaTitleCard}
        durationInFrames={30 * 8}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ variant: "title" } as MahdiaTitleCardProps}
      />
      <Composition
        id="MahdiaClosingCard"
        component={MahdiaTitleCard}
        durationInFrames={30 * 8}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ variant: "closing" } as MahdiaTitleCardProps}
      />
      <Composition
        id="EndTag"
        component={EndTag}
        // 5.5s at 30fps = 165 frames. Render CLI can override via --props.
        durationInFrames={165}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          text: "THE CITY KEEPS ITS OWN VIGIL.",
          palette: "cool_offwhite_on_black",
          fadeInSeconds: 0.6,
          holdSeconds: 4.3,
          fadeOutSeconds: 0.6,
        } as EndTagProps}
      />
      <Composition
        id="EndTagOverlay"
        component={EndTag}
        // 8.19s at 30fps = 246 frames. Render CLI can override via --props.
        // Intended to be composited on top of body footage, not concat'd.
        durationInFrames={246}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          text: "EARN THE LIGHT.",
          palette: "cool_offwhite_on_black",
          fadeInSeconds: 1.0,
          holdSeconds: 5.69,
          fadeOutSeconds: 1.5,
          overlay: true,
        } as EndTagProps}
      />
    </>
  );
};
