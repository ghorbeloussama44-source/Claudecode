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
const PURPLE = "#7b3fe4";
const BLUE = "#2196f3";

// Circular picture-in-picture of whichever presenter is the active speaker —
// a static-photo stand-in for where a lip-synced avatar clip will later go.
const PresenterBubble: React.FC<{ src: string; side: "left" | "right" }> = ({ src, side }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 16, stiffness: 120 } });
  const scale = interpolate(pop, [0, 1], [0.7, 1]);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", padding: "0 60px 40px", alignItems: side === "left" ? "flex-start" : "flex-end" }}>
      <div
        style={{
          width: 180,
          height: 180,
          borderRadius: "50%",
          overflow: "hidden",
          transform: `scale(${scale})`,
          opacity: pop,
          boxShadow: `0 0 0 4px ${BLUE}, 0 10px 30px rgba(0,0,0,0.5)`,
        }}
      >
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>
    </AbsoluteFill>
  );
};

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
      {/* B-roll timeline */}
      <Sequence from={0} durationInFrames={f(13.88)}>
        <OffthreadVideo src={staticFile("medilearn/broll/doctor_consult.mp4")} startFrom={f(2)} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>
      <Sequence from={f(13.88)} durationInFrames={f(18.62 - 13.88)}>
        <OffthreadVideo src={staticFile("medilearn/broll/ecg_exam.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>
      <Sequence from={f(18.62)} durationInFrames={f(24.1 - 18.62)}>
        <OffthreadVideo src={staticFile("medilearn/broll/doctor_consult.mp4")} startFrom={f(16)} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>
      <Sequence from={f(24.1)} durationInFrames={f(28.1 - 24.1)}>
        <StatCard />
      </Sequence>
      <Sequence from={f(28.1)} durationInFrames={f(30.208 - 28.1)}>
        <OffthreadVideo src={staticFile("medilearn/broll/bp_monitor.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </Sequence>

      {/* Dark gradient scrim at the bottom so the presenter bubble reads clearly over any b-roll */}
      <AbsoluteFill
        style={{
          background: "linear-gradient(0deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 30%)",
        }}
      />

      {/* Presenter PiP bubbles, matching who's speaking (still photos — lipsync comes later) */}
      <Sequence from={0} durationInFrames={f(13.88)}>
        <PresenterBubble src="medilearn/female_face.png" side="right" />
      </Sequence>
      <Sequence from={f(13.88)} durationInFrames={f(18.62 - 13.88)}>
        <PresenterBubble src="medilearn/male_face.png" side="left" />
      </Sequence>
      <Sequence from={f(18.62)} durationInFrames={f(24.1 - 18.62)}>
        <PresenterBubble src="medilearn/female_face.png" side="right" />
      </Sequence>
      <Sequence from={f(28.1)} durationInFrames={f(30.208 - 28.1)}>
        <PresenterBubble src="medilearn/male_face.png" side="left" />
      </Sequence>

      {/* Small corner bug so the brand is always present, even over b-roll */}
      <AbsoluteFill style={{ padding: 30, alignItems: "flex-start" }}>
        <Img src={staticFile("medilearn/logo.png")} style={{ height: 60, width: "auto", borderRadius: 8, opacity: 0.92, display: "block" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
