import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

const { fontFamily: inter } = loadInter("normal", { weights: ["600", "800"] });

const NAVY = "#0b1a3a";
const BLUE = "#2196f3";
const RED = "#e53935";

// Circular picture-in-picture of whichever presenter is the active speaker —
// sized to ~1/4 of the frame's area (diameter ~540px on a 1280x720 canvas):
// area = pi*r^2 = 0.25 * 1280*720 -> r ~= 271px -> diameter ~= 540px.
// A static-photo stand-in for where a lip-synced avatar clip will later go.
const PresenterBubble: React.FC<{ src: string; side: "left" | "right" }> = ({ src, side }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
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
          boxShadow: `0 0 0 6px ${BLUE}, 0 20px 50px rgba(0,0,0,0.55)`,
        }}
      >
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
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

const StatCard: React.FC<{ value: number; label: string; note: string }> = ({ value, label, note }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const in1 = spring({ frame, fps, config: { damping: 18 } });
  const statSpring = spring({ frame: frame - 8, fps, config: { damping: 20, stiffness: 90 } });
  const shown = Math.round(interpolate(statSpring, [0, 1], [0, value], { extrapolateRight: "clamp" }));

  return (
    <AbsoluteFill style={{ background: `linear-gradient(160deg, ${NAVY} 0%, #142a5c 100%)`, alignItems: "center", justifyContent: "center" }}>
      <div style={{ opacity: Math.min(1, in1), transform: `translateY(${(1 - Math.min(1, in1)) * 20}px)`, textAlign: "center" }}>
        <Img src={staticFile("medilearn/logo.png")} style={{ height: 80, marginBottom: 24, borderRadius: 12 }} />
        <div style={{ fontFamily: inter, fontWeight: 800, fontSize: 92, color: "#fff", lineHeight: 1 }}>{shown}</div>
        <div style={{ fontFamily: inter, fontWeight: 600, fontSize: 28, color: BLUE, marginTop: 10, maxWidth: 700 }}>{label}</div>
        <div style={{ fontFamily: inter, fontSize: 15, color: "rgba(255,255,255,0.55)", marginTop: 26 }}>{note}</div>
      </div>
    </AbsoluteFill>
  );
};

// Dramatic red alarm insert for the "200/110" reading moment.
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
        <div style={{ fontFamily: inter, fontWeight: 600, fontSize: 26, color: "#fff", marginTop: 16, letterSpacing: "0.05em" }}>
          PRESSION ARTÉRIELLE AFFICHÉE
        </div>
      </div>
    </AbsoluteFill>
  );
};

type Block =
  | { from: number; to: number; kind: "avatar"; src: string }
  | { from: number; to: number; kind: "broll"; src: string; startFrom?: number; circle?: "F" | "H" }
  | { from: number; to: number; kind: "statcard"; value: number; label: string; note: string }
  | { from: number; to: number; kind: "alarm" };

const BLOCKS: Block[] = [
  { from: 0, to: 13.76, kind: "avatar", src: "medilearn/avatar/seg_wide_femme.mp4" },
  { from: 13.76, to: 19.32, kind: "broll", src: "medilearn/broll/ecg_exam.mp4", circle: "H" },
  { from: 19.32, to: 24.1, kind: "broll", src: "medilearn/broll/pixabay_bp.mp4", circle: "F" },
  { from: 24.1, to: 28.1, kind: "statcard", value: 33, label: "des adultes concernés par l'HTA — l'hypertension artérielle*", note: "*Estimation mondiale illustrative — à vérifier avant diffusion finale" },
  { from: 28.1, to: 35.06, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "H" },
  { from: 35.06, to: 50.44, kind: "broll", src: "medilearn/broll/waiting_room.mp4", circle: "F" },
  { from: 50.44, to: 54.54, kind: "broll", src: "medilearn/broll/nurse_bp.mp4", circle: "F" },
  { from: 54.54, to: 61.28, kind: "alarm" },
  { from: 61.28, to: 73.9, kind: "broll", src: "medilearn/broll/xray_scan.mp4", circle: "F" },
  { from: 73.9, to: 99.0, kind: "broll", src: "medilearn/broll/xray_scan.mp4", startFrom: 13, circle: "H" },
  { from: 99.0, to: 113.16, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "F" },
  { from: 113.16, to: 119.78, kind: "broll", src: "medilearn/broll/doctor_talk.mp4", circle: "H" },
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
        if (b.kind === "statcard") {
          return (
            <Sequence key={i} from={from} durationInFrames={duration}>
              <StatCard value={b.value} label={b.label} note={b.note} />
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
                  src={b.circle === "F" ? "medilearn/female_face.png" : "medilearn/male_face.png"}
                  side={b.circle === "F" ? "right" : "left"}
                />
              </Sequence>
            )}
          </>
        );
      })}

      {/* Small corner bug so the brand is always present */}
      <AbsoluteFill style={{ padding: 30, alignItems: "flex-start" }}>
        <Img src={staticFile("medilearn/logo.png")} style={{ height: 60, width: "auto", borderRadius: 8, opacity: 0.92, display: "block" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
