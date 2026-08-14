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

// Playback order: original linear sequence (1 -> 2 -> 3 -> 4 -> 5 -> 6).
const STAGE_ORDER = [1, 2, 3, 4, 5, 6];
const STAGE_BOUNDS: Keyframe[] = [[0, S1], [S1, S2], [S2, S3], [S3, S4], [S4, S5], [S5, S6]];

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
 * TEMPORAL THREAD FIELD — a hierarchical "temporal loom" architecture,
 * not a bag of independent random lines.
 *
 * 18 primary branches per side (fixed Y rows) x 8 child strands each
 * = 288 structured strands, plus 32 hero/spark strands that read as
 * the network's most important pathways. All ~320 strands trace back
 * to a deterministic seed, so the composition is reproducible and
 * reads as engineered rather than noisy — small per-child jitter adds
 * organic motion on top of that fixed skeleton.
 *
 * Color budget stays ~55% background / ~30% midground / ~15% hero,
 * and only a sliver of the hero tier ever goes mint/white — the scene
 * must stay dark emerald/teal at a glance.
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
  depth: number;
  /** Fixed offset from the hand center this strand targets, so endpoints land
   *  in a volumetric cluster instead of a single pixel. Fades out on collapse. */
  clusterOffsetX: number;
  clusterOffsetY: number;
  /** Deterministic lateral bias used during Stage 3 to cross the centerline —
   *  a designed weave, not per-frame chaos. Relaxes away once ASTA takes control. */
  crossBias: number;
}

// Deterministic PRNG so the loom's structure is reproducible across reloads —
// only fine motion (turbulence, drift) stays time-based/animated.
function mulberry32(seed: number) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let x = Math.imul(t ^ (t >>> 15), t | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

const STRUCTURE_SEED = 0x415354; // "AST" — fixed so the loom is stable across sessions

interface TemporalBranch {
  side: "left" | "right";
  index: number;
  originY: number;
  strandCount: number;
  spread: number;
  curvature: number;
  depth: number;
  phase: number;
  targetCluster: number;
  revealDelay: number;
}

const BRANCH_ORIGIN_Y = [52, 82, 112, 142, 174, 205, 235, 265, 295, 325, 355, 385, 415, 446, 476, 508, 538, 568];
const STRANDS_PER_BRANCH = 8;
const HERO_STRAND_COUNT = 32;

// Small deterministic constellation of points around each hand so incoming
// strands terminate in a volumetric cluster rather than one exact pixel.
const CLUSTER_OFFSETS: Array<{ x: number; y: number }> = [
  { x: 0, y: 0 },
  { x: 9, y: -6 }, { x: -9, y: -6 }, { x: 9, y: 6 }, { x: -9, y: 6 },
  { x: 0, y: -12 }, { x: 0, y: 12 }, { x: 15, y: 0 }, { x: -15, y: 0 },
];

function buildBranches(rand: () => number): TemporalBranch[] {
  const branches: TemporalBranch[] = [];

  // Left side defines the base architecture.
  const leftBase = BRANCH_ORIGIN_Y.map((originY) => {
    const distFromCenter = Math.abs(originY - 300) / 300; // 0 near mid-row, 1 at the edges
    return {
      originY,
      spread: 60 + rand() * 90 + distFromCenter * 40,
      curvature: 0.5 + rand() * 0.8,
      depth: 0.15 + rand() * 0.8,
      phase: rand() * Math.PI * 2,
      targetCluster: Math.floor(rand() * CLUSTER_OFFSETS.length),
      revealDelay: distFromCenter * 0.5 + rand() * 0.3, // outer rows emerge first
    };
  });

  leftBase.forEach((b, i) => branches.push({ side: "left", index: i, strandCount: STRANDS_PER_BRANCH, ...b }));

  // Right side mirrors the left row-for-row (same Y, engineered symmetry) but
  // with small deterministic jitter on every other property — organic, not a clone.
  leftBase.forEach((b, i) => {
    const jitter = () => 0.85 + rand() * 0.3;
    branches.push({
      side: "right",
      index: i,
      originY: b.originY,
      strandCount: STRANDS_PER_BRANCH,
      spread: b.spread * jitter(),
      curvature: b.curvature * jitter(),
      depth: clamp01(b.depth * jitter()),
      phase: b.phase + (rand() - 0.5) * 0.6,
      targetCluster: Math.floor(rand() * CLUSTER_OFFSETS.length),
      revealDelay: clamp01(b.revealDelay * jitter()),
    });
  });

  return branches;
}

function tierStyle(layer: ThreadLayer, tier: ThreadTier, rand: () => number) {
  if (layer === "background") {
    return {
      speed: 0.0005 + rand() * 0.001,
      strokeWidth: 0.2 + rand() * 0.2,
      opacityMult: 0.02 + rand() * 0.03,
      strokeColor: rand() > 0.5 ? "10,32,24" : "13,40,32",
      particleColor: "16,48,38",
      pSize: 0.4 + rand() * 0.4,
      pOpacity: 0.12,
      depth: 0.06 + rand() * 0.24,
    };
  }
  if (layer === "midground") {
    return {
      speed: 0.0016 + rand() * 0.0018,
      strokeWidth: 0.4 + rand() * 0.4,
      opacityMult: 0.09 + rand() * 0.09,
      strokeColor: rand() > 0.5 ? "21,82,64" : "18,94,80",
      particleColor: "40,120,98",
      pSize: 0.8 + rand() * 0.4,
      pOpacity: 0.28,
      depth: 0.32 + rand() * 0.3,
    };
  }
  if (tier === "bright") {
    return {
      speed: 0.0032 + rand() * 0.0026,
      strokeWidth: 0.8 + rand() * 0.6,
      opacityMult: 0.38 + rand() * 0.2,
      strokeColor: rand() > 0.5 ? "13,148,120" : "8,140,132",
      particleColor: "94,214,178",
      pSize: 1.3 + rand() * 0.6,
      pOpacity: 0.6,
      depth: 0.6 + rand() * 0.26,
    };
  }
  return {
    speed: 0.0038 + rand() * 0.003,
    strokeWidth: 1.0 + rand() * 0.4,
    opacityMult: 0.55 + rand() * 0.25,
    strokeColor: "134,239,199",
    particleColor: "196,250,228",
    pSize: 1.6 + rand() * 0.7,
    pOpacity: 0.85,
    depth: 0.82 + rand() * 0.18,
  };
}

// A child strand inherits its parent branch's row, curvature and reveal
// timing, then adds small per-child variation — this is what makes strands
// read as belonging to the same bundle instead of independent lines.
function buildChildStrand(branch: TemporalBranch, childIndex: number, rand: () => number): ThreadConfig {
  const isLeft = branch.side === "left";
  const withinBranchT = branch.strandCount > 1 ? childIndex / (branch.strandCount - 1) : 0.5;

  const tierRoll = rand();
  let layer: ThreadLayer;
  let tier: ThreadTier;
  if (tierRoll < 0.62) { layer = "background"; tier = "dark"; }
  else if (tierRoll < 0.945) { layer = "midground"; tier = "dark"; }
  else { layer = "hero"; tier = "bright"; }

  const style = tierStyle(layer, tier, rand);
  const cluster = CLUSTER_OFFSETS[branch.targetCluster];

  return {
    isLeft,
    layer,
    tier,
    yStart: branch.originY + (withinBranchT - 0.5) * branch.spread,
    yOffset1: (rand() - 0.5) * 90 * branch.curvature,
    yOffset2: (rand() - 0.5) * 55 * branch.curvature,
    xOffset1: (rand() - 0.5) * 60 * branch.curvature,
    xOffset2: (rand() - 0.5) * 40 * branch.curvature,
    xStartOffset: (rand() - 0.5) * 40,
    speed: style.speed,
    u: rand(),
    opacityMult: style.opacityMult,
    strokeWidth: style.strokeWidth,
    strokeColor: style.strokeColor,
    particleColor: style.particleColor,
    pSize: style.pSize,
    pOpacity: style.pOpacity,
    phase: branch.phase + childIndex * 0.41,
    revealDelay: clamp01(branch.revealDelay + (rand() - 0.5) * 0.1),
    isSpark: false,
    depth: style.depth,
    clusterOffsetX: cluster.x + (rand() - 0.5) * 6,
    clusterOffsetY: cluster.y + (rand() - 0.5) * 6,
    crossBias: (childIndex % 2 === 0 ? 1 : -1) * (0.4 + rand() * 0.6) * (branch.index % 3 === 0 ? 1 : 0.5),
  };
}

// The network's most important pathways — brighter, thicker, and revealed
// last (per stage 2's "hero branches appear slightly later"). A minority of
// these carry the rare mint/white highlight treatment.
function buildHeroStrand(index: number, rand: () => number): ThreadConfig {
  const isLeft = index % 2 === 0;
  const isHighlight = rand() < 0.35;
  const layer: ThreadLayer = "hero";
  const tier: ThreadTier = isHighlight ? "highlight" : "bright";
  const style = tierStyle(layer, tier, rand);
  const curvature = 0.9 + rand() * 0.6;
  const cluster = CLUSTER_OFFSETS[Math.floor(rand() * CLUSTER_OFFSETS.length)];

  return {
    isLeft,
    layer,
    tier,
    yStart: 40 + rand() * 520,
    yOffset1: (rand() - 0.5) * 130 * curvature,
    yOffset2: (rand() - 0.5) * 80 * curvature,
    xOffset1: (rand() - 0.5) * 90,
    xOffset2: (rand() - 0.5) * 60,
    xStartOffset: (rand() - 0.5) * 60,
    speed: style.speed,
    u: rand(),
    opacityMult: style.opacityMult,
    strokeWidth: style.strokeWidth,
    strokeColor: style.strokeColor,
    particleColor: style.particleColor,
    pSize: style.pSize,
    pOpacity: style.pOpacity,
    phase: rand() * Math.PI * 2,
    revealDelay: clamp01(0.68 + rand() * 0.32),
    isSpark: isHighlight && rand() < 0.35,
    depth: style.depth,
    clusterOffsetX: cluster.x + (rand() - 0.5) * 5,
    clusterOffsetY: cluster.y + (rand() - 0.5) * 5,
    crossBias: (rand() - 0.5) * 1.6,
  };
}

function composeThreadField(): ThreadConfig[] {
  const rand = mulberry32(STRUCTURE_SEED);
  const branches = buildBranches(rand);

  const strands: ThreadConfig[] = [];
  for (const branch of branches) {
    for (let c = 0; c < branch.strandCount; c++) strands.push(buildChildStrand(branch, c, rand));
  }
  for (let i = 0; i < HERO_STRAND_COUNT; i++) strands.push(buildHeroStrand(i, rand));

  return strands;
}

const THREADS_CONFIG = composeThreadField();

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
  const scanlinePatternRef = useRef<CanvasPattern | null>(null);

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

    // Precompute the scanline texture once as a tileable pattern so the render loop
    // pays for a single fillRect instead of a per-row loop every frame.
    const scanTile = document.createElement("canvas");
    scanTile.width = 1;
    scanTile.height = 4;
    const scanCtx = scanTile.getContext("2d");
    if (scanCtx) {
      scanCtx.fillStyle = "rgba(20,60,48,0.05)";
      scanCtx.fillRect(0, 0, 1, 1.4);
    }
    scanlinePatternRef.current = ctx.createPattern(scanTile, "repeat");

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

      // Map real elapsed time onto the swapped playback order: this slot's
      // own duration is kept, but the content drawn is whichever original
      // stage STAGE_ORDER assigns to it, replayed across its natural range.
      const [realStart, realEnd] = STAGE_BOUNDS[stage - 1];
      const originalStage = STAGE_ORDER[stage - 1];
      const [natStart, natEnd] = STAGE_BOUNDS[originalStage - 1];
      const localProgress = realEnd === realStart ? 0 : clamp01((t - realStart) / (realEnd - realStart));
      const T = natStart + localProgress * (natEnd - natStart);

      const { w, h } = sizeRef.current;
      const dpr = dprRef.current;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const scaleX = w / 1000;
      const scaleY = h / 600;

      ctx.fillStyle = "#030706";
      ctx.fillRect(0, 0, w, h);

      const systemOpacity = sampleKF(KF_SYSTEM_OPACITY, T);
      const coreOrbitOpacity = sampleKF(KF_CORE_ORBIT, T);
      const weave = sampleKF(KF_WEAVE, T);
      const attract = sampleKF(KF_ATTRACT, T);
      const collapseRaw = sampleKF(KF_COLLAPSE, T);
      const collapseU = Math.pow(collapseRaw, 1.6);
      const silOpacity = sampleKF(KF_SIL_OPACITY, T);
      const handEnergy = sampleKF(KF_HAND_ENERGY, T);
      const hudOpacity = sampleKF(KF_HUD_OPACITY, T);

      const leftX = sampleKF(KF_LEFT_X, T);
      const leftY = sampleKF(KF_LEFT_Y, T);
      const rightX = sampleKF(KF_RIGHT_X, T);
      const rightY = sampleKF(KF_RIGHT_Y, T);

      const cx = 500 * scaleX;
      const cy = 300 * scaleY;

      // Atmospheric green haze — layered radial falloff for a foggy, volumetric feel.
      // Corners stay near-black since the gradient never reaches the edges.
      if (systemOpacity > 0.01 || silOpacity > 0.01) {
        const pulse = 0.14 + Math.sin(T / 420) * 0.03;
        const hazeStrength = Math.max(systemOpacity, silOpacity * 0.7) * (1 + collapseU * 1.4);
        const haze = ctx.createRadialGradient(cx, cy, 0, cx, cy, 560 * scaleX);
        haze.addColorStop(0, `rgba(24,210,158,${pulse * 1.1 * hazeStrength})`);
        haze.addColorStop(0.24, `rgba(16,150,115,${pulse * 0.62 * hazeStrength})`);
        haze.addColorStop(0.55, `rgba(8,90,68,${pulse * 0.3 * hazeStrength})`);
        haze.addColorStop(1, "transparent");
        ctx.fillStyle = haze;
        ctx.beginPath();
        ctx.arc(cx, cy, 560 * scaleX, 0, Math.PI * 2);
        ctx.fill();
      }

      // Technological scanline texture — one tiled-pattern fill instead of a
      // per-row loop, which is far cheaper per frame.
      if (scanlinePatternRef.current) {
        ctx.fillStyle = scanlinePatternRef.current;
        ctx.fillRect(0, 0, w, h);
      }

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
          const reveal = T < S1
            ? 0
            : sampleKF([[S1 + thread.revealDelay * 650, 0], [S1 + thread.revealDelay * 650 + 420, 1]], T);
          if (reveal <= 0.001) continue;

          const baseStartX = thread.isLeft ? 0 + thread.xStartOffset : 1000 + thread.xStartOffset;
          const xStart = lerp(baseStartX, 500, collapseU) * scaleX;
          const yStart = lerp(thread.yStart, 300, collapseU) * scaleY;
          // Endpoints land in a small cluster around the hand rather than one exact
          // pixel — this is what makes the energy node read as volumetric. The
          // cluster collapses to the literal center point as the core consumes it.
          const clusterFade = 1 - collapseU;
          const xEnd = ((thread.isLeft ? leftX : rightX) + thread.clusterOffsetX * clusterFade) * scaleX;
          const yEnd = ((thread.isLeft ? leftY : rightY) + thread.clusterOffsetY * clusterFade) * scaleY;

          // Depth drives how dynamic a strand's curvature and drift feel: distant
          // strands stay gentle and hazy, close/hero strands sway more and hold still
          // relative to the fog behind them — the core parallax + volume cue.
          const dx = Math.abs(xEnd - xStart) / 2;
          const curveScale = 0.5 + thread.depth * 0.9;
          const parallax = Math.sin(T * 0.00022 + thread.phase * 0.6) * (1 - thread.depth) * 22;
          const turbulence = Math.sin(T * 0.0018 + thread.phase) * 34 * weave * curveScale;
          // Deterministic cross-centerline bend during Stage 3's weave, which relaxes
          // out once ASTA's hands take control in Stage 5 — a designed weave, not noise.
          const crossX = thread.crossBias * weave * 26 * (1 - attract * 0.6) * scaleX;

          const cp1x = (thread.isLeft ? xStart + dx : xStart - dx) + lerp(thread.xOffset1 * curveScale, 0, collapseU) * scaleX;
          const cp2x = (thread.isLeft ? xEnd - dx : xEnd + dx) + lerp(thread.xOffset2 * curveScale, 0, collapseU) * scaleX + crossX;

          const cp1yBase = thread.yStart + thread.yOffset1 * curveScale * (1 - attract * 0.35) + turbulence + parallax;
          const cp2yBase = (thread.isLeft ? leftY : rightY) + thread.yOffset2 * curveScale * (1 - attract * 0.85) + turbulence * 0.6 + parallax * 0.5;
          const cp1y = lerp(cp1yBase, 300, collapseU) * scaleY;
          const cp2y = lerp(cp2yBase, 300, collapseU) * scaleY;

          ctx.beginPath();
          ctx.moveTo(xStart, yStart);
          ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, xEnd, yEnd);

          const proximity = Math.pow(thread.u, 2.2) * attract;
          const brightnessMult = 1 + proximity * 0.7;
          const baseAlpha = systemOpacity * thread.opacityMult * reveal * (1 - collapseU);
          const finalAlpha = Math.min(1, baseAlpha * (1 + proximity * 0.3));

          // Brightness falls off along the strand (dim at the tips, hot through the
          // middle) instead of a flat, uniform color — this alone is what separates a
          // "volumetric loom strand" from a flat neon line. Gradients also cost far
          // less to render than shadowBlur, so this doubles as the GPU-load reduction.
          if (thread.layer === "hero") {
            const grad = ctx.createLinearGradient(xStart, yStart, xEnd, yEnd);
            grad.addColorStop(0, `rgba(${thread.strokeColor},${finalAlpha * 0.08})`);
            grad.addColorStop(0.22, `rgba(${thread.strokeColor},${finalAlpha * 0.55})`);
            grad.addColorStop(0.6, `rgba(${thread.strokeColor},${finalAlpha})`);
            grad.addColorStop(1, `rgba(${thread.strokeColor},${finalAlpha * 0.5})`);
            ctx.strokeStyle = grad;
            ctx.lineWidth = thread.strokeWidth * (0.85 + thread.depth * 0.5);
            ctx.stroke();
          } else if (thread.layer === "midground") {
            const grad = ctx.createLinearGradient(xStart, yStart, xEnd, yEnd);
            grad.addColorStop(0, `rgba(${thread.strokeColor},${finalAlpha * 0.15})`);
            grad.addColorStop(0.5, `rgba(${thread.strokeColor},${finalAlpha})`);
            grad.addColorStop(1, `rgba(${thread.strokeColor},${finalAlpha * 0.35})`);
            ctx.strokeStyle = grad;
            ctx.lineWidth = thread.strokeWidth;
            ctx.stroke();
          } else {
            ctx.strokeStyle = `rgba(${thread.strokeColor},${finalAlpha})`;
            ctx.lineWidth = thread.strokeWidth;
            ctx.stroke();
          }

          // Moving particle along the strand, accelerating during collapse.
          const acc = T >= S5 ? 1 + Math.pow(collapseU, 3.2) * 20 : 1;
          const uFactor = attract > 0 ? 1 + Math.pow(thread.u, 2) * attract * 2 : 1;
          thread.u = (thread.u + thread.speed * acc * uFactor * 16) % 1;
          const u = thread.u;
          const mu = 1 - u;
          let px = mu * mu * mu * xStart + 3 * mu * mu * u * cp1x + 3 * mu * u * u * cp2x + u * u * u * xEnd;
          let py = mu * mu * mu * yStart + 3 * mu * mu * u * cp1y + 3 * mu * u * u * cp2y + u * u * u * yEnd;

          // Subtle inward spiral as the collapse accelerates, rather than a straight
          // pull to center — reads as gravitational rather than a simple slide.
          if (collapseU > 0.02) {
            const ang = collapseU * collapseU * 0.9 * (thread.isLeft ? 1 : -1);
            const cosA = Math.cos(ang);
            const sinA = Math.sin(ang);
            const dxp = px - cx;
            const dyp = py - cy;
            px = cx + dxp * cosA - dyp * sinA;
            py = cy + dxp * sinA + dyp * cosA;
          }

          const particleAlpha = Math.min(1, systemOpacity * thread.pOpacity * reveal * brightnessMult * (1 - collapseU * 0.6));
          const useSparkColor = thread.isSpark && thread.tier === "highlight" && (thread.u > 0.55 && thread.u < 0.8);
          const pRadius = thread.pSize * (0.7 + thread.depth * 0.7) * (1 - collapseU * 0.3) * scaleX;

          if (thread.layer === "hero") {
            // Soft radial falloff reads as a glowing, volumetric particle core without
            // the per-primitive blur pass shadowBlur would cost.
            const glowR = pRadius * 2.6;
            const color = useSparkColor ? "255,255,255" : thread.particleColor;
            const glow = ctx.createRadialGradient(px, py, 0, px, py, glowR);
            glow.addColorStop(0, `rgba(${color},${particleAlpha})`);
            glow.addColorStop(0.4, `rgba(${color},${particleAlpha * 0.55})`);
            glow.addColorStop(1, "transparent");
            ctx.fillStyle = glow;
            ctx.beginPath();
            ctx.arc(px, py, glowR, 0, Math.PI * 2);
            ctx.fill();
          } else {
            ctx.fillStyle = `rgba(${thread.particleColor},${particleAlpha})`;
            ctx.beginPath();
            ctx.arc(px, py, pRadius, 0, Math.PI * 2);
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
      if (T >= S6 - 320) {
        const flashU = clamp01((T - (S6 - 320)) / 320);
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

      // Depth vignette — pulls focus toward the central convergence point and
      // reinforces foreground/background separation. One cheap gradient fill.
      const vignette = ctx.createRadialGradient(cx, cy, Math.min(w, h) * 0.2, cx, cy, Math.max(w, h) * 0.72);
      vignette.addColorStop(0, "rgba(0,0,0,0)");
      vignette.addColorStop(1, "rgba(0,0,0,0.5)");
      ctx.fillStyle = vignette;
      ctx.fillRect(0, 0, w, h);

      // HTML overlay state via CSS variables — no per-frame React renders.
      const root = containerRef.current;
      if (root) {
        const coreY = sampleKF(KF_CORE_Y, T);
        let coreScale = 1;
        let coreOpacity = t < 200 ? t / 200 : 1;
        if (T >= S6 - 320) {
          const flashU = clamp01((T - (S6 - 320)) / 320);
          coreScale = 1 + Math.sin(flashU * Math.PI) * 0.22;
        }
        const titleOpacity = sampleKF(KF_TITLE_OPACITY, T);
        const titleScale = sampleKF(KF_TITLE_SCALE, T);
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

  const displayStage = STAGE_ORDER[activeStage - 1] ?? activeStage;
  const activeLabel = STAGE_LABELS[displayStage - 1] ?? STAGE_LABELS[0];

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
