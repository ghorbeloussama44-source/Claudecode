import {
  AbsoluteFill,
  Img,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

const { fontFamily: inter } = loadInter("normal", { weights: ["500", "700", "800"] });

const INK = "#1a1a1a";
const YELLOW = "#ffd54a";
const PINK = "#f4c9e0";
const RED = "#e53935";
const CREAM = "#fdfcf8";

// Light "whiteboard explainer" background — dot grid on cream, matching the
// client's Notebook-LM-style reference video instead of a dark corporate card.
const SketchBg: React.FC = () => (
  <AbsoluteFill
    style={{
      background: CREAM,
      backgroundImage: "radial-gradient(circle, #e4e0d4 1.5px, transparent 1.5px)",
      backgroundSize: "28px 28px",
    }}
  />
);

const Highlight: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = YELLOW }) => (
  <span style={{ background: color, padding: "2px 10px", borderRadius: 6, boxDecorationBreak: "clone" as any }}>
    {children}
  </span>
);

const DefinitionCard: React.FC<{ title: string; body: string }> = ({ title, body }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const in1 = spring({ frame, fps, config: { damping: 18 } });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <SketchBg />
      <div style={{ opacity: Math.min(1, in1), transform: `translateY(${(1 - Math.min(1, in1)) * 16}px)`, textAlign: "center", maxWidth: 980, padding: "0 60px" }}>
        <div style={{ fontFamily: inter, fontWeight: 800, fontSize: 52, color: INK, lineHeight: 1.25 }}>
          <Highlight>{title}</Highlight>
        </div>
        <div style={{ fontFamily: inter, fontWeight: 500, fontSize: 30, color: "#3a3a3a", marginTop: 30, lineHeight: 1.4 }}>
          {body}
        </div>
      </div>
      <Img src={staticFile("medilearn/logo.png")} style={{ position: "absolute", top: 30, left: 30, height: 50, borderRadius: 8 }} />
    </AbsoluteFill>
  );
};

type TableRow = { method: string; pas: string; pad: string };
const MeasurementTable: React.FC<{ rows: TableRow[] }> = ({ rows }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const in1 = spring({ frame, fps, config: { damping: 18 } });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <SketchBg />
      <div style={{ opacity: Math.min(1, in1), transform: `translateY(${(1 - Math.min(1, in1)) * 16}px)`, width: 900 }}>
        <div style={{ fontFamily: inter, fontWeight: 800, fontSize: 40, color: INK, marginBottom: 20, textAlign: "center" }}>
          Les seuils de l'HTA selon la méthode
        </div>
        <div style={{ background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 10px 30px rgba(0,0,0,0.08)", border: `2px solid ${INK}` }}>
          <div style={{ display: "flex", background: PINK, padding: "16px 28px", fontFamily: inter, fontWeight: 700, fontSize: 22, color: INK }}>
            <div style={{ flex: 1.4 }}>Méthode</div>
            <div style={{ flex: 1 }}>PAS</div>
            <div style={{ flex: 1 }}>PAD</div>
          </div>
          {rows.map((r, i) => {
            const rowSpring = spring({ frame: frame - 10 - i * 8, fps, config: { damping: 20 } });
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  padding: "20px 28px",
                  borderTop: `1px solid #eee`,
                  fontFamily: inter,
                  fontSize: 26,
                  color: INK,
                  opacity: Math.min(1, Math.max(0, rowSpring)),
                  transform: `translateX(${(1 - Math.min(1, Math.max(0, rowSpring))) * -20}px)`,
                }}
              >
                <div style={{ flex: 1.4, fontWeight: 700 }}>{r.method}</div>
                <div style={{ flex: 1, color: "#2196f3", fontWeight: 700 }}>{r.pas}</div>
                <div style={{ flex: 1, color: "#2196f3", fontWeight: 700 }}>{r.pad}</div>
              </div>
            );
          })}
        </div>
      </div>
      <Img src={staticFile("medilearn/logo.png")} style={{ position: "absolute", top: 30, left: 30, height: 50, borderRadius: 8 }} />
    </AbsoluteFill>
  );
};

const AlarmCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pulse = 1 + Math.sin(frame / 4) * 0.03;
  const in1 = spring({ frame, fps, config: { damping: 14, stiffness: 160 } });

  return (
    <AbsoluteFill style={{ background: "#1a0505", alignItems: "center", justifyContent: "center" }}>
      <div style={{ opacity: Math.min(1, in1), transform: `scale(${pulse})`, textAlign: "center" }}>
        <div style={{ fontFamily: inter, fontWeight: 800, fontSize: 150, color: RED, lineHeight: 1, textShadow: `0 0 60px ${RED}88` }}>
          200/110
        </div>
        <div style={{ fontFamily: inter, fontWeight: 700, fontSize: 26, color: "#fff", marginTop: 16, letterSpacing: "0.05em" }}>
          PRESSION ARTÉRIELLE AFFICHÉE
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Circular picture-in-picture of the active speaker — now filled with a
// looping clip of them talking (not a still), per client note that exact
// lip-sync isn't needed at concept stage. Sized to ~1/4 of frame area
// (diameter ~540px on 1280x720): pi*r^2 = 0.25*1280*720 -> r~=271px.
const PresenterBubble: React.FC<{ videoSrc: string; loopDurationInFrames: number; side: "left" | "right" }> = ({
  videoSrc,
  loopDurationInFrames,
  side,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 16, stiffness: 120 } });
  const scale = interpolate(pop, [0, 1], [0.7, 1]);
  const size = 540;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", padding: "0 20px 0px", alignItems: side === "left" ? "flex-start" : "flex-end" }}>
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          overflow: "hidden",
          transform: `scale(${scale})`,
          opacity: pop,
          marginBottom: -size * 0.18,
          boxShadow: `0 0 0 6px #2196f3, 0 20px 50px rgba(0,0,0,0.55)`,
        }}
      >
        <Loop durationInFrames={loopDurationInFrames} times={Math.ceil(durationInFrames / loopDurationInFrames)}>
          <OffthreadVideo src={staticFile(videoSrc)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </Loop>
      </div>
    </AbsoluteFill>
  );
};

const AvatarClip: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill>
    <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
  </AbsoluteFill>
);

const BrollClip: React.FC<{ src: string; startFrom?: number }> = ({ src, startFrom }) => (
  <AbsoluteFill>
    <OffthreadVideo src={staticFile(src)} startFrom={startFrom} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
  </AbsoluteFill>
);

type Block =
  | { from: number; to: number; kind: "avatar"; src: string }
  | { from: number; to: number; kind: "broll"; src: string; startFrom?: number; circle?: "F" | "H" }
  | { from: number; to: number; kind: "definition"; title: string; body: string }
  | { from: number; to: number; kind: "table" }
  | { from: number; to: number; kind: "alarm" };

// Female avatar loop clip (front-facing, ~9s) and male avatar loop clip
// (front-facing, ~5s) — used inside the PiP circles as generic "talking"
// motion. Not synced to this exact audio; a concept-stage stand-in.
const FEMME_LOOP = "medilearn/avatar/loop_femme.mp4";
const HOMME_LOOP = "medilearn/avatar/loop_homme.mp4";
const FEMME_LOOP_FRAMES = Math.round(9.041667 * 24);
const HOMME_LOOP_FRAMES = Math.round(5.041667 * 24);

const BLOCKS: Block[] = [
  { from: 0, to: 13.76, kind: "avatar", src: "medilearn/avatar/seg_wide_femme.mp4" },
  { from: 13.76, to: 19.32, kind: "broll", src: "medilearn/broll/ecg_exam.mp4", circle: "H" },
  { from: 19.32, to: 24.1, kind: "broll", src: "medilearn/broll/pixabay_bp.mp4", circle: "F" },
  { from: 24.1, to: 28.1, kind: "definition", title: "Qu'est-ce que l'HTA ?", body: "L'hypertension artérielle : le sujet du jour, expliqué simplement." },
  { from: 28.1, to: 35.06, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "H" },
  { from: 35.06, to: 50.44, kind: "broll", src: "medilearn/broll/waiting_room.mp4", circle: "F" },
  { from: 50.44, to: 54.54, kind: "broll", src: "medilearn/broll/nurse_bp.mp4", circle: "F" },
  { from: 54.54, to: 61.28, kind: "alarm" },
  { from: 61.28, to: 73.9, kind: "broll", src: "medilearn/broll/xray_scan.mp4", circle: "F" },
  { from: 73.9, to: 99.0, kind: "broll", src: "medilearn/broll/xray_scan.mp4", startFrom: 13, circle: "H" },
  { from: 99.0, to: 113.16, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "F" },
  { from: 113.16, to: 140.5, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "H" },
  { from: 140.5, to: 169.7, kind: "definition", title: "Une élévation persistante", body: "La définition clinique stricte de l'HTA : une élévation persistante — pas ponctuelle — de la pression dans les artères. D'où la règle d'or : toujours confirmer par plusieurs mesures." },
  { from: 169.7, to: 193.0, kind: "broll", src: "medilearn/broll/waiting_room.mp4", startFrom: 5, circle: "F" },
  { from: 193.0, to: 242.6, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "H" },
  { from: 242.6, to: 271.1, kind: "table" },
  { from: 271.1, to: 300.7, kind: "definition", title: "Pression artérielle élevée", body: "L'ESC 2024 introduit une nouvelle catégorie dès 120/139 : un signal d'alarme précoce, pas une raison de médicaliser tout le monde." },
];

export const MediLearnConcept: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = (seconds: number) => Math.round(seconds * fps);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {BLOCKS.map((b, i) => {
        const from = f(b.from);
        const duration = f(b.to - b.from);
        if (b.kind === "avatar") {
          return (
            <Sequence key={i} from={from} durationInFrames={duration}>
              <AvatarClip src={b.src} />
            </Sequence>
          );
        }
        if (b.kind === "definition") {
          return (
            <Sequence key={i} from={from} durationInFrames={duration}>
              <DefinitionCard title={b.title} body={b.body} />
            </Sequence>
          );
        }
        if (b.kind === "table") {
          return (
            <Sequence key={i} from={from} durationInFrames={duration}>
              <MeasurementTable
                rows={[
                  { method: "Cabinet", pas: "≥ 140", pad: "≥ 90" },
                  { method: "Domicile", pas: "≥ 135", pad: "≥ 85" },
                  { method: "MAPA jour", pas: "≥ 135", pad: "≥ 85" },
                  { method: "MAPA 24h", pas: "≥ 130", pad: "≥ 80" },
                ]}
              />
            </Sequence>
          );
        }
        if (b.kind === "alarm") {
          return (
            <Sequence key={i} from={from} durationInFrames={duration}>
              <AlarmCard />
            </Sequence>
          );
        }
        return (
          <>
            <Sequence key={`${i}-v`} from={from} durationInFrames={duration}>
              <BrollClip src={b.src} startFrom={b.startFrom ? f(b.startFrom) : undefined} />
            </Sequence>
            {b.circle && (
              <Sequence key={`${i}-p`} from={from} durationInFrames={duration}>
                <PresenterBubble
                  videoSrc={b.circle === "F" ? FEMME_LOOP : HOMME_LOOP}
                  loopDurationInFrames={b.circle === "F" ? FEMME_LOOP_FRAMES : HOMME_LOOP_FRAMES}
                  side={b.circle === "F" ? "right" : "left"}
                />
              </Sequence>
            )}
          </>
        );
      })}

      {/* Small corner bug so the brand is always present, even during avatar/alarm beats */}
      <AbsoluteFill style={{ padding: 30, alignItems: "flex-start" }}>
        <Img src={staticFile("medilearn/logo.png")} style={{ height: 60, width: "auto", borderRadius: 8, opacity: 0.92, display: "block" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
