import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadAmiri } from "@remotion/google-fonts/Amiri";
import { loadFont as loadMarcellus } from "@remotion/google-fonts/Marcellus";
import { loadFont as loadTajawal } from "@remotion/google-fonts/Tajawal";
import { loadFont as loadJost } from "@remotion/google-fonts/Jost";

const { fontFamily: amiri } = loadAmiri("normal", { weights: ["700"] });
const { fontFamily: marcellus } = loadMarcellus("normal", { weights: ["400"] });
const { fontFamily: tajawal } = loadTajawal("normal", { weights: ["400", "500"] });
const { fontFamily: jost } = loadJost("normal", { weights: ["400", "500"] });

const GOLD = "#cda44d";
const TERRACOTTA = "#c05a34";
const TEAL = "#3aa89a";
const PARCHMENT = "#f5efdc";

const BG = (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(120% 90% at 50% 12%, #16394a 0%, #0d2733 46%, #081a22 78%, #051217 100%)",
    }}
  />
);

const Waves: React.FC<{ frame: number }> = ({ frame }) => {
  const drift = frame * 0.15;
  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.22 }}
    >
      <path
        d={`M -100 780 Q 360 ${700 + Math.sin(drift / 30) * 18} 820 760 T 2020 740`}
        stroke={TEAL}
        strokeWidth={3}
        fill="none"
      />
      <path
        d={`M -100 860 Q 480 ${800 + Math.cos(drift / 26) * 16} 960 840 T 2020 820`}
        stroke={TERRACOTTA}
        strokeWidth={2.5}
        fill="none"
        opacity={0.7}
      />
      <path
        d={`M -100 940 Q 300 ${900 + Math.sin(drift / 34) * 20} 900 930 T 2020 910`}
        stroke={GOLD}
        strokeWidth={2}
        fill="none"
        opacity={0.6}
      />
    </svg>
  );
};

export type MahdiaTitleCardProps = {
  variant: "title" | "closing" | "credits";
};

export const MahdiaTitleCard: React.FC<MahdiaTitleCardProps> = ({ variant }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const wipe = spring({ frame, fps, config: { damping: 200, stiffness: 40, mass: 1 } });
  const clipPct = interpolate(wipe, [0, 1], [0, 100], { extrapolateRight: "clamp" });

  const subtitleIn = spring({ frame: frame - 18, fps, config: { damping: 20 } });
  const taglineIn = spring({ frame: frame - 34, fps, config: { damping: 20 } });
  const ruleIn = interpolate(frame, [8, 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  if (variant === "credits") {
    // One line on screen at a time, timed to the credits voice-over
    // (see projects/mahdia-festival/assets/audio/vo_credits_transcript.json).
    const beats: { label?: string; text: string; from: number; to: number; emphasize?: boolean }[] = [
      { label: "تحت إشراف", text: "وزارة التعليم العالي والبحث العلمي", from: 0, to: 95 },
      { text: "ديوان الخدمات الجامعية للوسط", from: 95, to: 182 },
      { text: "الإدارة الجهوية للخدمات الجامعية بالمنستير", from: 182, to: 309 },
      { label: "ينظم", text: "المركز الجامعي للتنشيط الثقافي والرياضي", from: 326, to: 444, emphasize: true },
    ];

    const exitStart = 444;
    const exitOpacity = interpolate(frame, [exitStart, exitStart + 12], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    return (
      <AbsoluteFill style={{ opacity: exitOpacity }}>
        {BG}
        <Waves frame={frame} />
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: "0 160px" }}>
          {beats.map((beat, i) => {
            const holdFrames = 10;
            const localIn = spring({ frame: frame - beat.from, fps, config: { damping: 18, stiffness: 140 } });
            const localOut = interpolate(frame, [beat.to - holdFrames, beat.to], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const opacity = frame < beat.from ? 0 : Math.min(1, localIn) * localOut;
            if (opacity <= 0.001) return null;
            return (
              <AbsoluteFill
                key={i}
                style={{
                  alignItems: "center",
                  justifyContent: "center",
                  flexDirection: "column",
                  opacity,
                  transform: `translateY(${(1 - Math.min(1, localIn)) * 12}px)`,
                }}
              >
                {beat.label && (
                  <div
                    style={{
                      fontFamily: marcellus,
                      fontSize: 22,
                      letterSpacing: "0.22em",
                      textTransform: "uppercase",
                      color: beat.emphasize ? TEAL : GOLD,
                      marginBottom: 18,
                    }}
                  >
                    {beat.label}
                  </div>
                )}
                <div
                  style={{
                    fontFamily: tajawal,
                    fontWeight: 500,
                    fontSize: beat.emphasize ? 44 : 34,
                    color: PARCHMENT,
                    direction: "rtl",
                    textAlign: "center",
                    maxWidth: 1400,
                    textShadow: beat.emphasize ? `0 0 30px rgba(58,168,154,0.35)` : undefined,
                  }}
                >
                  {beat.text}
                </div>
              </AbsoluteFill>
            );
          })}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  if (variant === "title") {
    return (
      <AbsoluteFill>
        {BG}
        <Waves frame={frame} />
        <AbsoluteFill
          style={{
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 140px",
          }}
        >
          <div
            style={{
              overflow: "hidden",
              clipPath: `inset(0 ${100 - clipPct}% 0 0)`,
            }}
          >
            <div
              style={{
                fontFamily: amiri,
                fontWeight: 700,
                fontSize: 92,
                lineHeight: 1.28,
                color: PARCHMENT,
                textAlign: "center",
                direction: "rtl",
                unicodeBidi: "plaintext",
                whiteSpace: "nowrap",
                textShadow: `0 0 40px rgba(205,164,77,0.25)`,
              }}
            >
              المهرجان الدولي الجامعي
              <br />
              للفنون التشكيلية بالمهدية
            </div>
          </div>

          <div
            style={{
              marginTop: 30,
              width: 220 * ruleIn,
              height: 2,
              background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
            }}
          />

          <div
            style={{
              marginTop: 26,
              opacity: Math.min(1, subtitleIn),
              transform: `translateY(${(1 - Math.min(1, subtitleIn)) * 14}px)`,
              fontFamily: marcellus,
              fontSize: 30,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: TEAL,
            }}
          >
            Mahdia International University Festival of Plastic Arts
          </div>

          <div
            style={{
              marginTop: 34,
              opacity: Math.min(1, taglineIn),
              transform: `translateY(${(1 - Math.min(1, taglineIn)) * 10}px)`,
              fontFamily: tajawal,
              fontSize: 26,
              color: GOLD,
              direction: "rtl",
            }}
          >
            فنٌ بلا حدود · إبداعٌ بلا قيود
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  // ---- closing card ----
  const logoScale = spring({ frame, fps, config: { damping: 14, stiffness: 110, mass: 0.8 } });
  const datesIn = spring({ frame: frame - 14, fps, config: { damping: 18 } });
  const ctaIn = interpolate(frame, [30, 45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      {BG}
      <Waves frame={frame} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            width: 200,
            height: 200,
            borderRadius: "50%",
            overflow: "hidden",
            transform: `scale(${interpolate(logoScale, [0, 1], [0.6, 1])})`,
            opacity: Math.min(1, logoScale * 1.4),
            boxShadow: `0 0 0 3px ${GOLD}, 0 18px 50px rgba(0,0,0,0.5)`,
          }}
        >
          <Img src={staticFile("mahdia/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>

        <div
          style={{
            marginTop: 32,
            opacity: Math.min(1, datesIn),
            transform: `translateY(${(1 - Math.min(1, datesIn)) * 12}px)`,
            fontFamily: jost,
            fontWeight: 500,
            fontSize: 46,
            letterSpacing: "0.04em",
            color: PARCHMENT,
          }}
        >
          26 <span style={{ color: GOLD }}>—</span> 31 OCTOBRE 2026
        </div>

        <div
          style={{
            marginTop: 14,
            opacity: Math.min(1, datesIn),
            fontFamily: tajawal,
            fontSize: 24,
            color: TEAL,
            direction: "rtl",
          }}
        >
          المهدية، تونس · الدورة الأولى
        </div>

        <div
          style={{
            marginTop: 36,
            opacity: ctaIn,
            fontFamily: marcellus,
            fontSize: 20,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: TERRACOTTA,
          }}
        >
          Mahdia · Tunisie
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
