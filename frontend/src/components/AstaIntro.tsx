import { useEffect, useRef, useState } from "react";
import { Terminal, Play } from "lucide-react";

interface AstaIntroProps {
  onComplete: () => void;
}

/* ==================================================================
 * STAGE TIMING
 * Six cinematic stages, ~9s total, boundaries mark the END of each
 * stage. Every animated value is driven by keyframe curves sampled
 * against elapsed time so stages bleed into one another instead of
 * hard-cutting.
 * ================================================================== */
const S1 = 1300; // SYSTEM AWAKENING ends
const S2 = 2800; // TEMPORAL THREADS EMERGE ends
const S3 = 4100; // WEAVING THE LOOM ends
const S4 = 5500; // ASTA MATERIALIZES ends
const S5 = 7000; // ASTA TAKES CONTROL ends
const S6 = 9000; // COLLAPSING INTO CORE ends
const TOTAL_MS = S6;

const STAGE_LABELS = [
  { header: "SYSTEM AWAKENING", subText: "DARKNESS. A SPARK.", footer: "ASTA CORE INITIALIZING" },
  { header: "TEMPORAL THREADS EMERGE", subText: "CONNECTING TEMPORAL LAYERS", footer: "THREADS SEEKING TIMELINES" },
  { header: "WEAVING THE LOOM", subText: "SYNCHRONIZING TIMELINES", footer: "MAPPING THE TEMPORAL NETWORK" },
  { header: "ASTA MATERIALIZES", subText: "WEAVING TEMPORAL MEMORY LOOM", footer: "CORE ONLINE" },
  { header: "ASTA TAKES CONTROL", subText: "GRASPING THE THREADS OF TIME", footer: "DIRECTING THE TEMPORAL NETWORK" },
  { header: "COLLAPSING INTO CORE", subText: "CONSOLIDATING EVERYTHING", footer: "PREPARING LOCAL DEPLOYMENT" },
];

const LEFT_HUD = ["MEMORY", "CONTEXT", "CODE", "REASONING"];
const RIGHT_HUD = ["PROJECTS", "EXPERIENCE", "KNOWLEDGE", "PATTERNS"];

/* ==================================================================
 * MATH HELPERS
 * ================================================================== */
type Keyframe = [number, number];

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);
const lerp = (a: number, b: number, u: number) => a + (b - a) * u;

const sampleKF = (keys: Keyframe[], t: number): number => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [t0, v0] = keys[i];
    const [t1, v1] = keys[i + 1];
    if (t <= t1) {
      const u = t1 === t0 ? 1 : clamp01((t - t0) / (t1 - t0));
      const s = u * u * (3 - 2 * u); // smoothstep - avoids linear-feeling motion
      return v0 + (v1 - v0) * s;
    }
  }
  return keys[keys.length - 1][1];
};

/* Animation curves for every scalar the scene needs. Keeping these as
 * data (rather than branching if/else per frame) is what lets each
 * stage bleed smoothly into the next. */
const KF_SYSTEM_OPACITY: Keyframe[] = [[0, 0], [S1, 0], [S1 + 350, 0.4], [S3, 0.78], [S5, 1], [S6 - 260, 0.32], [S6, 0]];
const KF_CORE_ORBIT: Keyframe[] = [[0, 0], [500, 0.2], [S1, 0.85], [S2, 0.45], [S3, 0.1], [S3 + 400, 0]];
const KF_WEAVE: Keyframe[] = [[0, 0], [S2, 0], [S3, 1], [S4, 0.55], [S6, 0.3]];
const KF_ATTRACT: Keyframe[] = [[0, 0], [S3 + 900, 0], [S4, 0.15], [S5, 1], [S6, 1]];
const KF_COLLAPSE: Keyframe[] = [[0, 0], [S5, 0], [S6, 1]];

const KF_SIL_OPACITY: Keyframe[] = [[0, 0], [S3 - 150, 0], [S4, 1], [S6 - 220, 1], [S6, 0]];
const KF_HAND_ENERGY: Keyframe[] = [[0, 0], [S3 + 900, 0], [S4, 0.4], [S5, 1], [S6 - 260, 1.15], [S6 - 90, 0.35], [S6, 0]];
const KF_HUD_OPACITY: Keyframe[] = [[0, 0], [S4, 0], [S4 + 420, 1], [S5, 1], [S6 - 420, 1], [S6 - 120, 0]];
const KF_TITLE_OPACITY: Keyframe[] = [[0, 0], [S3 + 700, 0], [S4, 1], [S5, 1], [S6 - 320, 1], [S6, 0]];
const KF_TITLE_SCALE: Keyframe[] = [[0, 0.88], [S3 + 700, 0.88], [S4, 1], [S5, 1.08], [S6 - 320, 1.08], [S6, 0.2]];
const KF_CORE_Y: Keyframe[] = [[0, 50], [S3, 50], [S4, 33], [S5, 33], [S6, 50]];

const HAND_L = { x: 360, y: 330 };
const HAND_R = { x: 640, y: 330 };

const KF_LEFT_X: Keyframe[] = [[0, -30], [S1, -30], [S2, 378], [S3, 468], [S4, HAND_L.x], [S5, HAND_L.x], [S6, 500]];
const KF_LEFT_Y: Keyframe[] = [[0, 300], [S3, 300], [S4, HAND_L.y], [S5, HAND_L.y], [S6, 300]];
const KF_RIGHT_X: Keyframe[] = [[0, 1030], [S1, 1030], [S2, 622], [S3, 532], [S4, HAND_R.x], [S5, HAND_R.x], [S6, 500]];
const KF_RIGHT_Y: Keyframe[] = [[0, 300], [S3, 300], [S4, HAND_R.y], [S5, HAND_R.y], [S6, 300]];

/* ==================================================================
 * TEMPORAL THREAD FIELD (precomputed once at module load)
 * 80% dark emerald/teal, ~15% brighter emerald/cyan, ~5% mint/white
 * high-energy highlights - never a predominantly white field.
 * ================================================================== */
type ThreadLayer = "background" | "midground" | "hero";
type ThreadTier = "dark" | "bright" | "highlight";

interface ThreadConfig {
  isLeft: boolean;
  layer: ThreadLayer;
  tier: ThreadTier;
  yStart: number;
  yOffset1: number;
  yOffset2: number;
  xOffset1: number;
  xOffset2: number;
  xStartOffset: number;
  speed: number;
  u: number;
  opacityMult: number;
  strokeWidth: number;
  strokeColor: string;
  particleColor: string;
  pSize: number;
  pOpacity: number;
  phase: number;
  revealDelay: number;
  isSpark: boolean;
}

function buildThreads(count: number): ThreadConfig[] {
  const threads: ThreadConfig[] = [];
  for (let i = 0; i < count; i++) {
    const isLeft = i % 2 === 0;
    const rand = Math.random();
    let layer: ThreadLayer;
    let tier: ThreadTier;
    if (rand < 0.66) { layer = "background"; tier = "dark"; }
    else if (rand < 0.86) { layer = "midground"; tier = "dark"; }
    else if (rand < 0.96) { layer = "hero"; tier = "bright"; }
    else { layer = "hero"; tier = "highlight"; }

    const yStart = 20 + Math.random() * 560;
    const yOffset1 = (Math.random() - 0.5) * 400;
    const yOffset2 = (Math.random() - 0.5) * 240;
    const xOffset1 = (Math.random() - 0.5) * 190;
    const xOffset2 = (Math.random() - 0.5) * 130;
    const xStartOffset = (Math.random() - 0.5) * 160;
    const phase = Math.random() * Math.PI * 2;
    const revealDelay = Math.random();

    let speed: number, strokeWidth: number, opacityMult: number;
    let strokeColor: string, particleColor: string, pSize: number, pOpacity: number;

    if (layer === "background") {
      speed = 0.0005 + Math.random() * 0.001;
      strokeWidth = 0.2 + Math.random() * 0.3;
      opacityMult = 0.02 + Math.random() * 0.03;
      strokeColor = Math.random() > 0.5 ? "10,32,24" : "13,40,32";
      particleColor = "16,48,38";
      pSize = 0.4 + Math.random() * 0.4;
      pOpacity = 0.12;
    } else if (layer === "midground") {
      speed = 0.0016 + Math.random() * 0.0018;
      strokeWidth = 0.5 + Math.random() * 0.35;
      opacityMult = 0.09 + Math.random() * 0.09;
      strokeColor = Math.random() > 0.5 ? "21,82,64" : "18,94,80";
      particleColor = "40,120,98";
      pSize = 0.8 + Math.random() * 0.4;
      pOpacity = 0.28;
    } else if (tier === "bright") {
      speed = 0.0032 + Math.random() * 0.0026;
      strokeWidth = 0.9 + Math.random() * 0.45;
      opacityMult = 0.38 + Math.random() * 0.2;
      strokeColor = Math.random() > 0.5 ? "13,148,120" : "8,140,132";
      particleColor = "94,214,178";
      pSize = 1.3 + Math.random() * 0.6;
      pOpacity = 0.6;
    } else {
      speed = 0.0038 + Math.random() * 0.003;
      strokeWidth = 1.1 + Math.random() * 0.5;
      opacityMult = 0.55 + Math.random() * 0.25;
      strokeColor = "134,239,199";
      particleColor = "196,250,228";
      pSize = 1.6 + Math.random() * 0.7;
      pOpacity = 0.85;
    }

    threads.push({
      isLeft, layer, tier, yStart, yOffset1, yOffset2, xOffset1, xOffset2, xStartOffset,
      speed, u: Math.random(), opacityMult, strokeWidth, strokeColor, particleColor, pSize, pOpacity,
      phase, revealDelay, isSpark: tier === "highlight" && Math.random() < 0.35,
    });
  }
  return threads;
}

const THREADS_CONFIG = buildThreads(320);

/* Tiny dormant particles orbiting the core in Stage 1, which fade as
 * the thread field takes over — "particles around the core become
 * timeline strands". */
interface OrbitParticle {
  angle: number;
  radius: number;
  speed: number;
  size: number;
  opacity: number;
  isSpark: boolean;
}

function buildOrbitParticles(count: number): OrbitParticle[] {
  const list: OrbitParticle[] = [];
  for (let i = 0; i < count; i++) {
    list.push({
      angle: Math.random() * Math.PI * 2,
      radius: 14 + Math.random() * 34,
      speed: 0.0004 + Math.random() * 0.0009,
      size: 0.6 + Math.random() * 1.0,
      opacity: 0.25 + Math.random() * 0.45,
      isSpark: i % 10 === 0,
    });
  }
  return list;
}

const CORE_ORBIT = buildOrbitParticles(42);

/* ==================================================================
 * ASTA SILHOUETTE — a holographic particle entity, never a solid
 * shape. Head / neck / shoulders / arms terminate at HAND_L / HAND_R
 * so the hand energy nodes line up with the temporal thread endpoints.
 * ================================================================== */
interface SilParticle {
  tx: number;
  ty: number;
  r: number;
  angle: number;
  speed: number;
  opacity: number;
  bright: boolean;
}

function buildSilhouette(): SilParticle[] {
  const particles: SilParticle[] = [];
  const push = (tx: number, ty: number) => {
    particles.push({
      tx, ty,
      r: 0.6 + Math.random() * 0.7,
      angle: Math.random() * Math.PI * 2,
      speed: 0.012 + Math.random() * 0.02,
      opacity: 0.3 + Math.random() * 0.5,
      bright: Math.random() < 0.16,
    });
  };
  const line = (x1: number, y1: number, x2: number, y2: number, count: number) => {
    for (let i = 0; i < count; i++) {
      const r = i / count;
      push(x1 + (x2 - x1) * r, y1 + (y2 - y1) * r);
    }
  };
  const curve = (x1: number, y1: number, cx: number, cy: number, x2: number, y2: number, count: number) => {
    for (let i = 0; i < count; i++) {
      const t = i / count;
      const mt = 1 - t;
      push(mt * mt * x1 + 2 * mt * t * cx + t * t * x2, mt * mt * y1 + 2 * mt * t * cy + t * t * y2);
    }
  };

  const headCx = 500, headCy = 175, rx = 23, ry = 29;
  for (let i = 0; i < 70; i++) {
    const th = (i / 70) * Math.PI * 2;
    push(headCx + Math.cos(th) * rx, headCy + Math.sin(th) * ry);
  }
  line(500, 204, 500, 226, 8); // neck
  line(500, 226, 438, 248, 18); // left shoulder
  line(500, 226, 562, 248, 18); // right shoulder
  curve(438, 248, 398, 288, HAND_L.x, HAND_L.y, 30); // left arm -> left hand
  curve(562, 248, 602, 288, HAND_R.x, HAND_R.y, 30); // right arm -> right hand
  line(438, 248, 466, 362, 26); // torso left
  line(562, 248, 534, 362, 26); // torso right
  line(466, 362, 534, 362, 16); // hips

  return particles;
}

const SIL_PARTICLES = buildSilhouette();

/* ==================================================================
 * COMPONENT
 * ================================================================== */
export function AstaIntro({ onComplete }: AstaIntroProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStage, setActiveStage] = useState(1);
  const [showSkip, setShowSkip] = useState(false);

  const rafRef = useRef<number | null>(null);
  const startRef = useRef<number | null>(null);
  const dprRef = useRef(1);
  const sizeRef = useRef({ w: window.innerWidth, h: window.innerHeight });
  const stageRef = useRef(1);
  const skipShownRef = useRef(false);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      onComplete();
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d") ?? null;
    if (!canvas || !ctx) {
      onComplete();
      return;
    }

    const handleResize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = window.innerWidth;
      const h = window.innerHeight;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      dprRef.current = dpr;
      sizeRef.current = { w, h };
    };
    handleResize();
    window.addEventListener("resize", handleResize);

    const drawHandNode = (hx: number, hy: number, energy: number, scaleX: number) => {
      if (energy <= 0.01) return;
      const r = Math.max(energy, 0);

      const bloom = ctx.createRadialGradient(hx, hy, 0, hx, hy, 46 * r * scaleX);
      bloom.addColorStop(0, `rgba(16,185,129,${0.46 * r})`);
      bloom.addColorStop(0.35, `rgba(13,120,100,${0.18 * r})`);
      bloom.addColorStop(1, "transparent");
      ctx.fillStyle = bloom;
      ctx.beginPath();
      ctx.arc(hx, hy, 46 * r * scaleX, 0, Math.PI * 2);
      ctx.fill();

      const inner = ctx.createRadialGradient(hx, hy, 0, hx, hy, 15 * r * scaleX);
      inner.addColorStop(0, `rgba(150,250,217,${0.95 * r})`);
      inner.addColorStop(0.55, `rgba(16,185,129,${0.7 * r})`);
      inner.addColorStop(1, "transparent");
      ctx.fillStyle = inner;
      ctx.beginPath();
      ctx.arc(hx, hy, 15 * r * scaleX, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = `rgba(255,255,255,${0.9 * r})`;
      ctx.beginPath();
      ctx.arc(hx, hy, 3.4 * r * scaleX, 0, Math.PI * 2);
      ctx.fill();

      const orbitCount = 6;
      for (let i = 0; i < orbitCount; i++) {
        const angle = performance.now() * 0.0032 + (i * Math.PI * 2) / orbitCount;
        const dist = (11 + Math.sin(performance.now() * 0.005 + i) * 3) * r * scaleX;
        ctx.fillStyle = `rgba(150,250,217,${0.85 * r})`;
        ctx.beginPath();
        ctx.arc(hx + Math.cos(angle) * dist, hy + Math.sin(angle) * dist, 1.2 * scaleX, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const animate = (ts: number) => {
      if (startRef.current === null) startRef.current = ts;
      const t = Math.min(TOTAL_MS, ts - startRef.current);

      let stage = 1;
      if (t >= S5) stage = 6;
      else if (t >= S4) stage = 5;
      else if (t >= S3) stage = 4;
      else if (t >= S2) stage = 3;
      else if (t >= S1) stage = 2;
      if (stage !== stageRef.current) {
        stageRef.current = stage;
        setActiveStage(stage);
      }
      if (!skipShownRef.current && t >= 1800) {
        skipShownRef.current = true;
        setShowSkip(true);
      }

      const { w, h } = sizeRef.current;
      const dpr = dprRef.current;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const scaleX = w / 1000;
      const scaleY = h / 600;

      ctx.fillStyle = "#030706";
      ctx.fillRect(0, 0, w, h);

      const systemOpacity = sampleKF(KF_SYSTEM_OPACITY, t);
      const coreOrbitOpacity = sampleKF(KF_CORE_ORBIT, t);
      const weave = sampleKF(KF_WEAVE, t);
      const attract = sampleKF(KF_ATTRACT, t);
      const collapseRaw = sampleKF(KF_COLLAPSE, t);
      const collapseU = Math.pow(collapseRaw, 1.6);
      const silOpacity = sampleKF(KF_SIL_OPACITY, t);
      const handEnergy = sampleKF(KF_HAND_ENERGY, t);
      const hudOpacity = sampleKF(KF_HUD_OPACITY, t);

      const leftX = sampleKF(KF_LEFT_X, t);
      const leftY = sampleKF(KF_LEFT_Y, t);
      const rightX = sampleKF(KF_RIGHT_X, t);
      const rightY = sampleKF(KF_RIGHT_Y, t);

      const cx = 500 * scaleX;
      const cy = 300 * scaleY;

      // Atmospheric green haze — concentrated, corners stay near-black.
      if (systemOpacity > 0.01 || silOpacity > 0.01) {
        const pulse = 0.14 + Math.sin(t / 420) * 0.03;
        const haze = ctx.createRadialGradient(cx, cy, 0, cx, cy, 460 * scaleX);
        haze.addColorStop(0, `rgba(16,185,129,${pulse * Math.max(systemOpacity, silOpacity * 0.7)})`);
        haze.addColorStop(0.5, `rgba(6,90,68,${pulse * 0.5 * Math.max(systemOpacity, silOpacity * 0.7)})`);
        haze.addColorStop(1, "transparent");
        ctx.fillStyle = haze;
        ctx.beginPath();
        ctx.arc(cx, cy, 460 * scaleX, 0, Math.PI * 2);
        ctx.fill();
      }

      // Very subtle technological scanline texture.
      ctx.fillStyle = "rgba(20,60,48,0.012)";
      for (let y = 0; y < h; y += 4) ctx.fillRect(0, y, w, 1.4);

      // Stage 1: dormant particles orbiting the core.
      if (coreOrbitOpacity > 0.01) {
        for (const p of CORE_ORBIT) {
          p.angle += p.speed * 16;
          const px = 500 + Math.cos(p.angle) * p.radius;
          const py = 300 + Math.sin(p.angle) * p.radius * 0.6;
          const alpha = p.opacity * coreOrbitOpacity;
          if (p.isSpark) {
            ctx.fillStyle = `rgba(196,250,228,${alpha})`;
          } else {
            ctx.fillStyle = `rgba(60,150,120,${alpha})`;
          }
          ctx.beginPath();
          ctx.arc(px * scaleX, py * scaleY, p.size * scaleX, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Temporal thread field.
      if (systemOpacity > 0.01) {
        for (const thread of THREADS_CONFIG) {
          const reveal = t < S1
            ? 0
            : sampleKF([[S1 + thread.revealDelay * 650, 0], [S1 + thread.revealDelay * 650 + 420, 1]], t);
          if (reveal <= 0.001) continue;

          const baseStartX = thread.isLeft ? 0 + thread.xStartOffset : 1000 + thread.xStartOffset;
          const xStart = lerp(baseStartX, 500, collapseU) * scaleX;
          const yStart = lerp(thread.yStart, 300, collapseU) * scaleY;
          const xEnd = (thread.isLeft ? leftX : rightX) * scaleX;
          const yEnd = (thread.isLeft ? leftY : rightY) * scaleY;

          const dx = Math.abs(xEnd - xStart) / 2;
          const turbulence = Math.sin(t * 0.0018 + thread.phase) * 34 * weave * (thread.layer === "hero" ? 1 : 0.55);

          const cp1x = (thread.isLeft ? xStart + dx : xStart - dx) + lerp(thread.xOffset1, 0, collapseU) * scaleX;
          const cp2x = (thread.isLeft ? xEnd - dx : xEnd + dx) + lerp(thread.xOffset2, 0, collapseU) * scaleX;

          const cp1yBase = thread.yStart + thread.yOffset1 * (1 - attract * 0.35) + turbulence;
          const cp2yBase = (thread.isLeft ? leftY : rightY) + thread.yOffset2 * (1 - attract * 0.85) + turbulence * 0.6;
          const cp1y = lerp(cp1yBase, 300, collapseU) * scaleY;
          const cp2y = lerp(cp2yBase, 300, collapseU) * scaleY;

          ctx.beginPath();
          ctx.moveTo(xStart, yStart);
          ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, xEnd, yEnd);

          const proximity = Math.pow(thread.u, 2.2) * attract;
          const brightnessMult = 1 + proximity * 0.7;
          const baseAlpha = systemOpacity * thread.opacityMult * reveal * (1 - collapseU);
          const finalAlpha = Math.min(1, baseAlpha * (1 + proximity * 0.3));

          if (thread.layer === "hero") {
            ctx.save();
            ctx.shadowBlur = 16 * brightnessMult * (1 - collapseU);
            ctx.shadowColor = `rgba(${thread.strokeColor},0.6)`;
            ctx.strokeStyle = `rgba(${thread.strokeColor},${finalAlpha * 0.4})`;
            ctx.lineWidth = thread.strokeWidth * 2.6;
            ctx.stroke();
            ctx.shadowBlur = 4 * brightnessMult * (1 - collapseU);
            ctx.strokeStyle = `rgba(${thread.strokeColor},${finalAlpha})`;
            ctx.lineWidth = thread.strokeWidth;
            ctx.stroke();
            ctx.restore();
          } else {
            ctx.shadowBlur = 0;
            ctx.strokeStyle = `rgba(${thread.strokeColor},${finalAlpha})`;
            ctx.lineWidth = thread.strokeWidth;
            ctx.stroke();
          }

          // Moving particle along the strand, accelerating during collapse.
          const acc = t >= S5 ? 1 + Math.pow(collapseU, 3.2) * 20 : 1;
          const uFactor = attract > 0 ? 1 + Math.pow(thread.u, 2) * attract * 2 : 1;
          thread.u = (thread.u + thread.speed * acc * uFactor * 16) % 1;
          const u = thread.u;
          const mu = 1 - u;
          const px = mu * mu * mu * xStart + 3 * mu * mu * u * cp1x + 3 * mu * u * u * cp2x + u * u * u * xEnd;
          const py = mu * mu * mu * yStart + 3 * mu * mu * u * cp1y + 3 * mu * u * u * cp2y + u * u * u * yEnd;

          const particleAlpha = Math.min(1, systemOpacity * thread.pOpacity * reveal * brightnessMult * (1 - collapseU * 0.6));
          const useSparkColor = thread.isSpark && thread.tier === "highlight" && (thread.u > 0.55 && thread.u < 0.8);
          if (thread.layer === "hero") {
            ctx.save();
            ctx.shadowBlur = 6 * brightnessMult * (1 - collapseU);
            ctx.shadowColor = `rgba(${thread.particleColor},0.7)`;
            ctx.fillStyle = useSparkColor ? `rgba(255,255,255,${particleAlpha})` : `rgba(${thread.particleColor},${particleAlpha})`;
            ctx.beginPath();
            ctx.arc(px, py, thread.pSize * (1 - collapseU * 0.3) * scaleX, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
          } else {
            ctx.fillStyle = `rgba(${thread.particleColor},${particleAlpha})`;
            ctx.beginPath();
            ctx.arc(px, py, thread.pSize * (1 - collapseU * 0.3) * scaleX, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }

      // ASTA holographic silhouette.
      if (silOpacity > 0.01) {
        ctx.save();
        const backdropEase = Math.pow(collapseU, 3);
        const bx = lerp(500, 500, backdropEase);
        const by = lerp(175, 300, backdropEase);

        ctx.beginPath();
        ctx.ellipse(bx * scaleX, by * scaleY, 23 * (1 - backdropEase) * scaleX, 29 * (1 - backdropEase) * scaleY, 0, 0, Math.PI * 2);
        ctx.moveTo(lerp(438, 500, backdropEase) * scaleX, lerp(248, 300, backdropEase) * scaleY);
        ctx.lineTo(lerp(466, 500, backdropEase) * scaleX, lerp(362, 300, backdropEase) * scaleY);
        ctx.lineTo(lerp(534, 500, backdropEase) * scaleX, lerp(362, 300, backdropEase) * scaleY);
        ctx.lineTo(lerp(562, 500, backdropEase) * scaleX, lerp(248, 300, backdropEase) * scaleY);
        ctx.closePath();
        ctx.fillStyle = `rgba(4,10,8,${0.72 * silOpacity * (1 - backdropEase)})`;
        ctx.fill();

        for (const p of SIL_PARTICLES) {
          p.angle += p.speed;
          const ease = Math.pow(collapseU, 3.5);
          const tx = lerp(p.tx, 500, ease);
          const ty = lerp(p.ty, 300, ease);
          const drift = 1.4 * (1 - ease);
          const px = (tx + Math.sin(p.angle) * drift) * scaleX;
          const py = (ty + Math.cos(p.angle) * drift) * scaleY;

          if (p.bright) {
            ctx.shadowBlur = 4 * (1 - ease);
            ctx.shadowColor = "rgba(94,214,178,0.5)";
            ctx.fillStyle = `rgba(120,220,180,${p.opacity * silOpacity})`;
          } else {
            ctx.shadowBlur = 0;
            ctx.fillStyle = `rgba(40,120,98,${p.opacity * silOpacity * 0.7})`;
          }
          ctx.beginPath();
          ctx.arc(px, py, p.r * scaleX, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.shadowBlur = 0;
        ctx.restore();
      }

      // Hand energy nodes.
      if (handEnergy > 0.01) {
        drawHandNode(leftX * scaleX, leftY * scaleY, handEnergy, scaleX);
        drawHandNode(rightX * scaleX, rightY * scaleY, handEnergy, scaleX);
      }

      // Final consolidation flash.
      if (t >= S6 - 320) {
        const flashU = clamp01((t - (S6 - 320)) / 320);
        const radius = flashU * Math.max(w, h) * 0.9;
        const flashOpacity = 1 - flashU;
        const flash = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
        flash.addColorStop(0, `rgba(255,255,255,${flashOpacity})`);
        flash.addColorStop(0.14, `rgba(210,250,235,${flashOpacity * 0.9})`);
        flash.addColorStop(0.4, `rgba(94,214,178,${flashOpacity * 0.6})`);
        flash.addColorStop(0.7, `rgba(20,90,72,${flashOpacity * 0.28})`);
        flash.addColorStop(1, "transparent");
        ctx.fillStyle = flash;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      // HTML overlay state via CSS variables — no per-frame React renders.
      const root = containerRef.current;
      if (root) {
        const coreY = sampleKF(KF_CORE_Y, t);
        let coreScale = 1;
        let coreOpacity = t < 200 ? t / 200 : 1;
        if (t >= S6 - 320) {
          const flashU = clamp01((t - (S6 - 320)) / 320);
          coreScale = 1 + Math.sin(flashU * Math.PI) * 0.22;
        }
        const titleOpacity = sampleKF(KF_TITLE_OPACITY, t);
        const titleScale = sampleKF(KF_TITLE_SCALE, t);
        const titleBlur = (1 - titleOpacity) * 14;

        root.style.setProperty("--core-y", `${coreY}%`);
        root.style.setProperty("--core-scale", coreScale.toFixed(3));
        root.style.setProperty("--core-opacity", coreOpacity.toFixed(3));
        root.style.setProperty("--title-opacity", titleOpacity.toFixed(3));
        root.style.setProperty("--title-scale", titleScale.toFixed(3));
        root.style.setProperty("--title-blur", `${titleBlur.toFixed(1)}px`);
        root.style.setProperty("--hud-opacity", hudOpacity.toFixed(3));
      }

      if (t < TOTAL_MS) {
        rafRef.current = requestAnimationFrame(animate);
      } else {
        onComplete();
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [onComplete]);

  const activeLabel = STAGE_LABELS[activeStage - 1] ?? STAGE_LABELS[0];

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-between p-8 select-none overflow-hidden"
      style={{ background: "#030706", color: "var(--txt-primary)" }}
    >
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full z-0" />

      {/* Top status bar */}
      <div
        className="w-[80vw] flex items-center justify-between text-[10px] md:text-xs font-mono border-b border-white/5 pb-4 z-10"
        style={{ color: "var(--txt-muted)" }}
      >
        <div className="flex items-center gap-2">
          <Terminal size={14} style={{ color: "var(--accent)" }} />
          <span>ASTA_INCEPTION_STREAM_LOG</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="font-bold tracking-widest text-[var(--accent)] uppercase animate-pulse-soft">
            {activeLabel.header}
          </span>
          <span>STAGE_0{activeStage}/06</span>
        </div>
      </div>

      {/* HUD side labels — subtle, only during ASTA TAKES CONTROL */}
      <div
        className="absolute left-4 md:left-8 top-1/2 -translate-y-1/2 z-10 pointer-events-none flex flex-col gap-3 font-mono text-[8px] md:text-[9px] tracking-[0.2em] uppercase"
        style={{ opacity: "var(--hud-opacity, 0)", color: "var(--sage)" }}
      >
        {LEFT_HUD.map((label) => (
          <span key={label}>{label}</span>
        ))}
      </div>
      <div
        className="absolute right-4 md:right-8 top-1/2 -translate-y-1/2 z-10 pointer-events-none flex flex-col gap-3 font-mono text-[8px] md:text-[9px] tracking-[0.2em] uppercase text-right"
        style={{ opacity: "var(--hud-opacity, 0)", color: "var(--sage)" }}
      >
        {RIGHT_HUD.map((label) => (
          <span key={label}>{label}</span>
        ))}
      </div>

      {/* Core + title overlay */}
      <div className="absolute inset-0 z-10 pointer-events-none">
        <div
          className="absolute left-1/2 flex items-center justify-center w-36 h-36 md:w-44 md:h-44"
          style={{
            top: "var(--core-y, 50%)",
            transform: "translate(-50%, -50%) scale(var(--core-scale, 1))",
            opacity: "var(--core-opacity, 1)",
          }}
        >
          <div className="absolute inset-0 rounded-full border opacity-20 animate-pulse" style={{ borderColor: "var(--accent)" }} />
          <div
            className="absolute w-[80%] h-[80%] rounded-full border border-dashed animate-[spin_30s_linear_infinite]"
            style={{ borderColor: "var(--accent)", opacity: 0.3 }}
          />
          <div
            className="absolute w-[60%] h-[60%] rounded-full border flex items-center justify-center bg-[#0a0f0c]"
            style={{ borderColor: "var(--accent)", boxShadow: "0 0 25px rgba(77,124,115,0.35)" }}
          >
            <span
              className="font-mono font-black select-none tracking-tighter"
              style={{ fontSize: 24, color: "var(--accent)", textShadow: "0 0 12px rgba(77,124,115,0.7)" }}
            >
              &gt;_&lt;
            </span>
          </div>
        </div>

        <div
          className="absolute top-1/2 left-1/2 text-center"
          style={{
            transform: "translate(-50%, -10%) scale(var(--title-scale, 0.85))",
            opacity: "var(--title-opacity, 0)",
            filter: "drop-shadow(0 0 20px rgba(94,214,178,0.5)) blur(var(--title-blur, 12px))",
          }}
        >
          <h1 className="font-heading font-black tracking-[0.38em] text-4xl md:text-6xl flex items-center justify-center gap-1 select-none">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent)] to-[var(--sage)]">ASTA</span>
          </h1>
          <p className="font-mono text-[9px] md:text-[10px] tracking-[0.16em] uppercase mt-4 animate-pulse" style={{ color: "var(--accent)" }}>
            {activeLabel.subText}
          </p>
        </div>
      </div>

      {/* Bottom status bar + skip */}
      <div className="w-[80vw] flex items-center justify-between border-t border-white/5 pt-4 font-mono z-10 text-[10px] md:text-xs">
        <div className="flex flex-col gap-1" style={{ color: "var(--txt-muted)" }}>
          <span className="text-[var(--accent)] uppercase font-semibold">STATUS: {activeLabel.footer}</span>
          <span className="text-[8px] opacity-50">TEMPORAL TIMELINE MATRIX SYNCHRONIZED</span>
        </div>

        {showSkip && (
          <button
            onClick={onComplete}
            className="flex items-center gap-1.5 px-4 py-2 font-mono text-[9px] md:text-[10px] rounded-lg border transition-all cursor-pointer bg-white/5 border-white/5 text-[var(--txt-muted)] hover:text-[var(--txt-primary)] hover:bg-white/10"
          >
            <Play size={8} fill="currentColor" />
            SKIP INTRO
          </button>
        )}
      </div>
    </div>
  );
}
