import {
  AbsoluteFill,
  Img,
  Loop,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Layout measured from the client's TV/podium reference photo
// (projects/medilearn/assets/originals/tv_podium_reference.png, 1672x941,
// resized 1:1 aspect to this 1280x720 canvas): circle detected via Hough
// transform at center (403,419) r=313 in source px; diapo panel is the
// white card to its right, bounded by the screen bezel.
const CIRCLE = { cx: 308, cy: 321, r: 240 };
const DIAPO = { left: 548, top: 65, width: 683, height: 559 };
const SLIDE_BG = "#1b252f"; // sampled from the slide deck's own background
const RING =
  "0 0 0 7px #4fc3f7, 0 0 46px 10px rgba(79,195,247,0.5), 0 20px 55px rgba(0,0,0,0.55)";

const FEMME_LOOP = "medilearn/avatar/loop_femme.mp4";
const HOMME_LOOP = "medilearn/avatar/loop_homme.mp4";
const FEMME_LOOP_FRAMES = Math.round(9.041667 * 24);
const HOMME_LOOP_FRAMES = Math.round(5.041667 * 24);

const loopFor = (speaker: "F" | "H") => ({
  src: speaker === "F" ? FEMME_LOOP : HOMME_LOOP,
  frames: speaker === "F" ? FEMME_LOOP_FRAMES : HOMME_LOOP_FRAMES,
});

// Speaker turns for topic 1 (0:00-5:00.7), from pitch (F0) classification
// of the real audio per transcript line, merged into continuous turns.
type Turn = { from: number; to: number; speaker: "F" | "H" };
const TURNS: Turn[] = [
  { from: 0.0, to: 13.8, speaker: "F" },
  { from: 14.5, to: 18.6, speaker: "H" },
  { from: 19.3, to: 28.1, speaker: "F" },
  { from: 28.1, to: 35.1, speaker: "H" },
  { from: 35.4, to: 47.7, speaker: "F" },
  { from: 48.0, to: 50.4, speaker: "H" },
  { from: 50.7, to: 59.0, speaker: "F" },
  { from: 59.2, to: 61.3, speaker: "H" },
  { from: 61.5, to: 73.9, speaker: "F" },
  { from: 74.2, to: 90.3, speaker: "H" },
  { from: 90.4, to: 93.7, speaker: "F" },
  { from: 93.7, to: 103.1, speaker: "H" },
  { from: 103.6, to: 111.0, speaker: "F" },
  { from: 111.0, to: 119.8, speaker: "H" },
  { from: 120.1, to: 123.3, speaker: "F" },
  { from: 123.3, to: 136.0, speaker: "H" },
  { from: 136.3, to: 138.8, speaker: "F" },
  { from: 139.0, to: 147.7, speaker: "H" },
  { from: 148.4, to: 149.8, speaker: "F" },
  { from: 150.3, to: 159.1, speaker: "H" },
  { from: 159.3, to: 162.0, speaker: "F" },
  { from: 162.4, to: 169.7, speaker: "H" },
  { from: 169.7, to: 175.7, speaker: "F" },
  { from: 175.7, to: 184.2, speaker: "H" },
  { from: 184.4, to: 186.4, speaker: "F" },
  { from: 187.0, to: 199.4, speaker: "H" },
  { from: 199.4, to: 204.2, speaker: "F" },
  { from: 204.3, to: 210.5, speaker: "H" },
  { from: 210.8, to: 216.0, speaker: "F" },
  { from: 216.5, to: 220.1, speaker: "H" },
  { from: 220.3, to: 234.5, speaker: "F" },
  { from: 234.7, to: 241.3, speaker: "H" },
  { from: 241.6, to: 242.2, speaker: "F" },
  { from: 242.6, to: 252.2, speaker: "H" },
  { from: 252.8, to: 253.4, speaker: "F" },
  { from: 253.6, to: 256.7, speaker: "H" },
  { from: 256.7, to: 266.0, speaker: "F" },
  { from: 266.5, to: 278.2, speaker: "H" },
  { from: 278.4, to: 283.8, speaker: "F" },
  { from: 283.8, to: 296.5, speaker: "H" },
  { from: 296.8, to: 300.7, speaker: "F" },
];

// Diapo (slide) segments matched to the script's topical beats.
type Slide = { from: number; to: number; src: string };
const SLIDES: Slide[] = [
  { from: 0.0, to: 61.3, src: "medilearn/slides/slide_01.jpg" }, // "200/110 - démystifier le chiffre"
  { from: 61.3, to: 99.5, src: "medilearn/slides/slide_02.jpg" }, // mythe de la salle d'attente / AVC
  { from: 99.5, to: 193.0, src: "medilearn/slides/slide_03.jpg" }, // mesure dynamique / effet blouse blanche
  { from: 193.0, to: 300.7, src: "medilearn/slides/slide_04.jpg" }, // seuils ESC 2024
];

// Shot grammar: which visual treatment is on screen. Cut points are snapped
// to speaker-turn boundaries so cuts always land between sentences, never
// mid-word. Kinds never repeat back-to-back.
// - tv_duo:      standard podium — TV background, diapo panel, one circle
// - tv_solo_big: podium, diapo panel behind, ONE large pulsing circle
// - tv_duo_both: podium, diapo panel, both presenters together (small pair)
// - diapo_full:  slide fills the whole frame, no presenter visible
// - diapo_pip:   slide fills the frame, small presenter circle bottom-right
// - avatar_wide: the raw AI-generated presenter clip, full-bleed — a
//                different "set" entirely, for visual variety
type ShotKind = "tv_duo" | "tv_solo_big" | "tv_duo_both" | "diapo_full" | "diapo_pip" | "avatar_wide";
type Shot = { from: number; to: number; kind: ShotKind };
const SHOTS: Shot[] = [
  { from: 0.0, to: 28.1, kind: "diapo_full" },
  { from: 28.1, to: 61.3, kind: "tv_duo" },
  { from: 61.3, to: 90.3, kind: "diapo_full" },
  { from: 90.3, to: 119.8, kind: "tv_solo_big" },
  { from: 119.8, to: 149.8, kind: "avatar_wide" },
  { from: 149.8, to: 175.7, kind: "tv_duo_both" },
  { from: 175.7, to: 204.2, kind: "diapo_pip" },
  { from: 204.2, to: 234.5, kind: "diapo_full" },
  { from: 234.5, to: 256.7, kind: "tv_duo" },
  { from: 256.7, to: 283.8, kind: "tv_solo_big" },
  { from: 283.8, to: 300.7, kind: "tv_duo_both" },
];

const activeAt = <T extends { from: number; to: number }>(list: T[], t: number): T =>
  list.find((x) => t >= x.from && t < x.to) ?? list[list.length - 1];

const TvBackground: React.FC = () => (
  <Img
    src={staticFile("medilearn/tv/podium_bg.jpg")}
    style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover" }}
  />
);

const SlideImage: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  <Img src={staticFile(src)} style={{ width: "100%", height: "auto", objectFit: "contain", ...style }} />
);

const DiapoPanel: React.FC<{ src: string }> = ({ src }) => (
  <div
    style={{
      position: "absolute",
      left: DIAPO.left,
      top: DIAPO.top,
      width: DIAPO.width,
      height: DIAPO.height,
      background: SLIDE_BG,
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
    }}
  >
    <SlideImage src={src} />
  </div>
);

const DiapoFullscreen: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill style={{ background: SLIDE_BG, alignItems: "center", justifyContent: "center" }}>
    <SlideImage src={src} />
  </AbsoluteFill>
);

const Circle: React.FC<{
  speaker: "F" | "H";
  cx: number;
  cy: number;
  r: number;
  pulse?: number; // amplitude of the breathing scale animation, 0 = static
}> = ({ speaker, cx, cy, r, pulse = 0 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { src, frames } = loopFor(speaker);
  const scale = pulse ? 1 + pulse * Math.sin(frame / 18) : 1;
  const size = r * 2;

  return (
    <div
      style={{
        position: "absolute",
        left: cx - r,
        top: cy - r,
        width: size,
        height: size,
        borderRadius: "50%",
        overflow: "hidden",
        transform: `scale(${scale})`,
        boxShadow: RING,
      }}
    >
      <Loop durationInFrames={frames} times={Math.ceil(durationInFrames / frames)}>
        <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </Loop>
    </div>
  );
};

const AvatarWideFullscreen: React.FC<{ speaker: "F" | "H" }> = ({ speaker }) => {
  const { durationInFrames } = useVideoConfig();
  const { src, frames } = loopFor(speaker);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Loop durationInFrames={frames} times={Math.ceil(durationInFrames / frames)}>
        <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </Loop>
    </AbsoluteFill>
  );
};

export const MediLearnTV: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const slide = activeAt(SLIDES, t);
  const turn = activeAt(TURNS, t);
  const shot = activeAt(SHOTS, t).kind;

  if (shot === "diapo_full") {
    return <DiapoFullscreen src={slide.src} />;
  }

  if (shot === "diapo_pip") {
    return (
      <AbsoluteFill>
        <DiapoFullscreen src={slide.src} />
        <Circle speaker={turn.speaker} cx={1130} cy={600} r={110} />
      </AbsoluteFill>
    );
  }

  if (shot === "avatar_wide") {
    return <AvatarWideFullscreen speaker={turn.speaker} />;
  }

  // tv_duo / tv_solo_big / tv_duo_both — always keep the TV background fully
  // covered (diapo panel + circle(s)) so the reference photo's own
  // placeholder art is never left visible underneath.
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <TvBackground />
      <DiapoPanel src={slide.src} />
      {shot === "tv_duo" && <Circle speaker={turn.speaker} cx={CIRCLE.cx} cy={CIRCLE.cy} r={CIRCLE.r} />}
      {shot === "tv_solo_big" && (
        <Circle speaker={turn.speaker} cx={340} cy={340} r={290} pulse={0.045} />
      )}
      {shot === "tv_duo_both" && (
        <>
          <Circle
            speaker={turn.speaker}
            cx={250}
            cy={300}
            r={195}
            pulse={0.03}
          />
          <Circle speaker={turn.speaker === "F" ? "H" : "F"} cx={455} cy={505} r={145} />
        </>
      )}
    </AbsoluteFill>
  );
};
