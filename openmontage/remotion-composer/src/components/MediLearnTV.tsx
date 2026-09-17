import {
  AbsoluteFill,
  Img,
  Loop,
  OffthreadVideo,
  Sequence,
  staticFile,
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

const FEMME_LOOP = "medilearn/avatar/loop_femme.mp4";
const HOMME_LOOP = "medilearn/avatar/loop_homme.mp4";
const FEMME_LOOP_FRAMES = Math.round(9.041667 * 24);
const HOMME_LOOP_FRAMES = Math.round(5.041667 * 24);

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

const PresenterCircle: React.FC<{ speaker: "F" | "H" }> = ({ speaker }) => {
  const src = speaker === "F" ? FEMME_LOOP : HOMME_LOOP;
  const loopFrames = speaker === "F" ? FEMME_LOOP_FRAMES : HOMME_LOOP_FRAMES;
  const { durationInFrames } = useVideoConfig();
  const size = CIRCLE.r * 2;

  return (
    <div
      style={{
        position: "absolute",
        left: CIRCLE.cx - CIRCLE.r,
        top: CIRCLE.cy - CIRCLE.r,
        width: size,
        height: size,
        borderRadius: "50%",
        overflow: "hidden",
        boxShadow: "0 0 0 6px rgba(255,255,255,0.85), 0 20px 50px rgba(0,0,0,0.5)",
      }}
    >
      <Loop durationInFrames={loopFrames} times={Math.ceil(durationInFrames / loopFrames)}>
        <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </Loop>
    </div>
  );
};

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
    <Img src={staticFile(src)} style={{ width: "100%", height: "auto", objectFit: "contain" }} />
  </div>
);

export const MediLearnTV: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = (seconds: number) => Math.round(seconds * fps);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Img src={staticFile("medilearn/tv/podium_bg.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />

      {SLIDES.map((s, i) => (
        <Sequence key={`slide-${i}`} from={f(s.from)} durationInFrames={f(s.to - s.from)}>
          <DiapoPanel src={s.src} />
        </Sequence>
      ))}

      {TURNS.map((t, i) => (
        <Sequence key={`turn-${i}`} from={f(t.from)} durationInFrames={f(t.to - t.from)}>
          <PresenterCircle speaker={t.speaker} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
