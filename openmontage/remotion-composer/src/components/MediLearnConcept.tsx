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

// Full-frame AI-generated (lip-synced) avatar clip — used for the key
// "hook" and "payoff" beats; b-roll + big PiP circle carries the
// explanatory middle where a full avatar render isn't worth the cost yet.
const AvatarClip: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill>
    <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
  </AbsoluteFill>
);

const StatCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const in1 = spring({ frame, fps, config: { damping: 18 } });
  const statSpring = spring({ frame: frame - 12, fps, config: { damping: 20, stiffness: 80 } });
  const statValue = Math.round(interpolate(statSpring, [0, 1], [0, 33], { extrapolateRight: "clamp" }));

  return (
    <AbsoluteFill style={{ background: `linear-gradient(160deg, ${NAVY} 0%, #142a5c 100%)`, alignItems: "center", justifyContent: "center" }}>
      <div style={{ opacity: Math.min(1, in1), transform: `translateY(${(1 - Math.min(1, in1)) * 20}px)`, textAlign: "center" }}>
        <Img
          src={staticFile("medilearn/logo.png")}
          style={{ height: 90, marginBottom: 28, borderRadius: 12 }}
        />
        <div style={{ fontFamily: inter, fontWeight: 800, fontSize: 100, color: "#fff", lineHeight: 1 }}>
          {statValue}%
        </div>
        <div style={{ fontFamily: inter, fontWeight: 600, fontSize: 30, color: BLUE, marginTop: 10 }}>
          des adultes concernés par l'HTA*
        </div>
        <div style={{ fontFamily: inter, fontSize: 16, color: "rgba(255,255,255,0.55)", marginTop: 30 }}>
          *Estimation mondiale illustrative — à vérifier avant diffusion finale
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const MediLearnConcept: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = (seconds: number) => Math.round(seconds * fps);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* --- Timeline: hook (AI avatar) -> b-roll+PiP explanatory middle -> stat card -> payoff (AI avatar) --- */}

      {/* 0-13.88s: femme — AI-generated avatar, full frame (the "hook") */}
      <Sequence from={0} durationInFrames={f(13.88)}>
        <AvatarClip src="medilearn/avatar/seg_wide_femme.mp4" />
      </Sequence>

      {/* 14.5-19.26s: homme — b-roll (ECG) + big circle PiP */}
      <Sequence from={f(14.5)} durationInFrames={f(19.26 - 14.5)}>
        <OffthreadVideo src={staticFile("medilearn/broll/pixabay_ecg.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>
      <Sequence from={f(14.5)} durationInFrames={f(19.26 - 14.5)}>
        <PresenterBubble src="medilearn/male_face.png" side="left" />
      </Sequence>

      {/* 19.26-24.1s: femme — b-roll (tension artérielle) + big circle PiP */}
      <Sequence from={f(19.26)} durationInFrames={f(24.1 - 19.26)}>
        <OffthreadVideo src={staticFile("medilearn/broll/pixabay_bp.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>
      <Sequence from={f(19.26)} durationInFrames={f(24.1 - 19.26)}>
        <PresenterBubble src="medilearn/female_face.png" side="right" />
      </Sequence>

      {/* 24.1-28.1s: branded stat card (definition of HTA) */}
      <Sequence from={f(24.1)} durationInFrames={f(28.1 - 24.1)}>
        <StatCard />
      </Sequence>

      {/* 28.1-30.208s: homme — AI-generated avatar, full frame (the "payoff") */}
      <Sequence from={f(28.1)} durationInFrames={f(30.208 - 28.1)}>
        <AvatarClip src="medilearn/avatar/seg_homme_close.mp4" />
      </Sequence>

      {/* Small corner bug so the brand is always present */}
      <AbsoluteFill style={{ padding: 30, alignItems: "flex-start" }}>
        <Img src={staticFile("medilearn/logo.png")} style={{ height: 60, width: "auto", borderRadius: 8, opacity: 0.92, display: "block" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
