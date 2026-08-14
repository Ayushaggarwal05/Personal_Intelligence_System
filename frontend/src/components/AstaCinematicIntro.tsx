import React, { useState, useEffect, useRef } from "react";
import { Terminal, Play } from "lucide-react";

interface AstaCinematicIntroProps {
  onComplete: () => void;
}

const STAGE_LABELS = [
  {
    header: "SYSTEM AWAKENING",
    subText: "DARKNESS. A SPARK.",
    footer: "ASTA CORE INITIALIZING"
  },
  {
    header: "TEMPORAL THREADS EMERGE",
    subText: "CONNECTING TO TEMPORAL LAYERS",
    footer: "SYSTEM SEEKING TIMELINES"
  },
  {
    header: "ASTA TAKES CONTROL",
    subText: "GRASPING THE THREADS OF TIME",
    footer: "DIRECTING ACTIVE CODE PLOTS"
  },
  {
    header: "ASTA MATERIALIZES",
    subText: "WEAVING TEMPORAL MEMORY LOOM",
    footer: "CORE ONLINE"
  },
  {
    header: "WEAVING THE LOOM",
    subText: "SYNCHRONIZING TIMELINES",
    footer: "MAPPING SYSTEM CALL TREE"
  },
  {
    header: "COLLAPSING INTO CORE",
    subText: "CONSOLIDATING EVERYTHING",
    footer: "PREPARING LOCAL DEPLOYMENT"
  }
];

const NUM_THREADS = 220;
const THREADS_CONFIG = Array.from({ length: NUM_THREADS }).map((_, idx) => {
  const isLeft = idx < NUM_THREADS / 2;
  
  // Distribute layers: 60% background (extremely subtle), 30% midground, 10% hero
  let layer: 'background' | 'midground' | 'hero' = 'background';
  const rand = Math.random();
  if (rand > 0.90) {
    layer = 'hero';
  } else if (rand > 0.60) {
    layer = 'midground';
  }

  // Vertical distribution (spread start Y from 25 to 575)
  const yStart = 25 + Math.random() * 550;

  // Curvature offsets (organic waviness) - more variation
  const yOffset1 = (Math.random() - 0.5) * 380; 
  const yOffset2 = (Math.random() - 0.5) * 220;

  // Horizontal control point offsets (adds S-curves and depth)
  const xOffset1 = (Math.random() - 0.5) * 180;
  const xOffset2 = (Math.random() - 0.5) * 120;

  // Staggered horizontal start offsets to avoid flat edge look
  const xStartOffset = (Math.random() - 0.5) * 150;

  // Timing speed variations
  let baseSpeed = 0.003;
  let strokeWidth = 0.6;
  let opacityMult = 0.07;
  let color = "rgba(22, 38, 30, 0.7)"; // Deep Green
  let pSize = 1.0;
  let pOpacity = 0.3;

  if (layer === 'background') {
    baseSpeed = 0.0006 + Math.random() * 0.0012;
    strokeWidth = 0.2 + Math.random() * 0.35;
    opacityMult = 0.015 + Math.random() * 0.025; // keep extremely subtle
    color = Math.random() > 0.5 ? "rgba(16, 44, 34, 0.4)" : "rgba(22, 58, 48, 0.3)";
    pSize = 0.4 + Math.random() * 0.4;
    pOpacity = 0.08;
  } else if (layer === 'midground') {
    baseSpeed = 0.002 + Math.random() * 0.002;
    strokeWidth = 0.5 + Math.random() * 0.4;
    opacityMult = 0.06 + Math.random() * 0.08; // subtle
    color = "rgba(77, 124, 115, 0.5)"; // Accent Teal
    pSize = 0.8 + Math.random() * 0.5;
    pOpacity = 0.25;
  } else {
    // Hero
    baseSpeed = 0.004 + Math.random() * 0.003;
    strokeWidth = 1.0 + Math.random() * 0.5;
    opacityMult = 0.45 + Math.random() * 0.2;
    color = Math.random() > 0.5 ? "rgba(0, 180, 140, 0.95)" : "rgba(16, 185, 129, 0.95)"; // Saturated Teal / Emerald
    pSize = 1.6 + Math.random() * 0.8;
    pOpacity = 0.8;
  }

  return {
    isLeft,
    layer,
    yStart,
    yOffset1,
    yOffset2,
    xOffset1,
    xOffset2,
    xStartOffset,
    speed: baseSpeed,
    u: Math.random(),
    opacityMult,
    strokeWidth,
    color,
    pSize,
    pOpacity
  };
});

export const AstaCinematicIntro: React.FC<AstaCinematicIntroProps> = ({ onComplete }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStage, setActiveStage] = useState(1);
  const [showSkip, setShowSkip] = useState(false);
  const requestRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  // Digital silhouette floating particles forming ASTA outline
  const silParticles = useRef<Array<{ targetX: number; targetY: number; x: number; y: number; r: number; angle: number; speed: number; opacity: number }>>([]);

  useEffect(() => {
    // Check accessibility reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      onComplete();
      return;
    }

    // Initialize silhouette particles outlining the entity shape
    if (silParticles.current.length === 0) {
      const particles: Array<{ targetX: number; targetY: number; x: number; y: number; r: number; angle: number; speed: number; opacity: number }> = [];

      // 1. Head ellipse
      const headCx = 500;
      const headCy = 180;
      const rx = 24;
      const ry = 30;
      for (let i = 0; i < 80; i++) {
        const theta = (i / 80) * Math.PI * 2;
        const tx = headCx + Math.cos(theta) * rx;
        const ty = headCy + Math.sin(theta) * ry;
        particles.push({
          targetX: tx,
          targetY: ty,
          x: tx,
          y: ty,
          r: 0.6 + Math.random() * 0.8,
          angle: Math.random() * Math.PI * 2,
          speed: 0.015 + Math.random() * 0.02,
          opacity: 0.35 + Math.random() * 0.5
        });
      }

      // Helper to add lines
      const addLineParticles = (x1: number, y1: number, x2: number, y2: number, count: number) => {
        for (let i = 0; i < count; i++) {
          const ratio = i / count;
          const tx = x1 + (x2 - x1) * ratio;
          const ty = y1 + (y2 - y1) * ratio;
          particles.push({
            targetX: tx,
            targetY: ty,
            x: tx,
            y: ty,
            r: 0.6 + Math.random() * 0.8,
            angle: Math.random() * Math.PI * 2,
            speed: 0.015 + Math.random() * 0.02,
            opacity: 0.35 + Math.random() * 0.5
          });
        }
      };

      // Helper to add curves
      const addCurveParticles = (x1: number, y1: number, cx: number, cy: number, x2: number, y2: number, count: number) => {
        for (let i = 0; i < count; i++) {
          const t = i / count;
          const tx = (1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * cx + t * t * x2;
          const ty = (1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * cy + t * t * y2;
          particles.push({
            targetX: tx,
            targetY: ty,
            x: tx,
            y: ty,
            r: 0.6 + Math.random() * 0.8,
            angle: Math.random() * Math.PI * 2,
            speed: 0.015 + Math.random() * 0.02,
            opacity: 0.35 + Math.random() * 0.5
          });
        }
      };

      // 2. Neck
      addLineParticles(500, 210, 500, 230, 8);

      // 3. Shoulders
      addLineParticles(500, 230, 440, 250, 16);
      addLineParticles(500, 230, 560, 250, 16);

      // 4. Arms (curved quadratic)
      addCurveParticles(440, 250, 400, 290, 360, 330, 28);
      addCurveParticles(560, 250, 600, 290, 640, 330, 28);

      // 5. Torso sides & hips
      addLineParticles(440, 250, 468, 360, 24);
      addLineParticles(560, 250, 532, 360, 24);
      addLineParticles(468, 360, 532, 360, 18);

      silParticles.current = particles;
    }

    // Canvas resize handler
    const handleResize = () => {
      if (canvasRef.current) {
        canvasRef.current.width = window.innerWidth;
        canvasRef.current.height = window.innerHeight;
      }
    };
    window.addEventListener("resize", handleResize);
    handleResize();

    const lerp = (start: number, end: number, amt: number) => start + (end - start) * amt;

    const animate = (timestamp: number) => {
      if (startTimeRef.current === null) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const t = Math.min(10000, elapsed);

      // Determine active stage based on scaled 10-second boundaries
      let currentStage = 1;
      if (t < 1500) currentStage = 1;
      else if (t < 3200) currentStage = 2;
      else if (t < 4800) currentStage = 3;
      else if (t < 6500) currentStage = 4;
      else if (t < 8200) currentStage = 5;
      else currentStage = 6;

      setActiveStage(currentStage);

      // Show Skip button after 2 seconds
      if (t >= 2000 && !showSkip) {
        setShowSkip(true);
      }

      // Perform drawing
      if (canvasRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const w = canvas.width;
          const h = canvas.height;
          const scaleX = w / 1000;
          const scaleY = h / 600;

          // Clear canvas to deep dark pitch black
          ctx.fillStyle = "#050806";
          ctx.fillRect(0, 0, w, h);

          // Render subtle background scanlines
          ctx.fillStyle = "rgba(77, 124, 115, 0.015)";
          for (let y = 0; y < h; y += 4) {
            ctx.fillRect(0, y, w, 1.5);
          }

          // Compute core endpoints and thread states
          let leftX = 500;
          let leftY = 300;
          let rightX = 500;
          let rightY = 300;
          let threadOpacity = 0;
          let collapseU = 0;

          if (t >= 1500 && t < 3200) {
            const u = (t - 1500) / 1700;
            leftX = lerp(0, 350, u);
            rightX = lerp(1000, 650, u);
            threadOpacity = Math.min(1, (t - 1500) / 300) * 0.7;
          } else if (t >= 3200 && t < 4800) {
            // Stage 3: ASTA Takes Control (Silhouette materializes & hand nodes expand)
            const u = (t - 3200) / 1600;
            leftX = lerp(350, 360, u);
            leftY = lerp(300, 330, u);
            rightX = lerp(650, 640, u);
            rightY = lerp(300, 330, u);
            threadOpacity = 0.75;
          } else if (t >= 4800 && t < 6500) {
            // Stage 4: ASTA Materializes (Typography logo appears)
            leftX = 360;
            leftY = 330;
            rightX = 640;
            rightY = 330;
            threadOpacity = 0.75;
          } else if (t >= 6500 && t < 8200) {
            // Stage 5: Weaving The Loom (Threads pull into center woven network)
            const u = (t - 6500) / 1700;
            leftX = lerp(360, 500, u);
            leftY = lerp(330, 300, u);
            rightX = lerp(640, 500, u);
            rightY = lerp(300, 300, u);
            threadOpacity = 0.75;
          } else if (t >= 8200 && t <= 10000) {
            // Stage 6: Collapsing Into Core
            collapseU = Math.min(1, (t - 8200) / 1500);
            const easeU = Math.pow(collapseU, 3);
            leftX = lerp(500, 500, easeU);
            leftY = lerp(300, 300, easeU);
            rightX = lerp(500, 500, easeU);
            rightY = lerp(300, 300, easeU);
            threadOpacity = Math.max(0, 0.75 - easeU * 1.5);
          }

          // 1. Render Holographic Particle-based Silhouette (Stage 3 to 6)
          let silOpacity = 0;
          if (t >= 3200 && t < 8200) {
            silOpacity = Math.min(1, (t - 3200) / 1600);
          } else if (t >= 8200 && t < 9500) {
            // Silhouette fades out a bit later and more gradually during collapse
            silOpacity = Math.max(0, 1 - (t - 8200) / 1300);
          }

          if (silOpacity > 0) {
            ctx.save();

            // Draw a very faint background silhouette backdrop to block out timelines behind ASTA
            // During Stage 6 collapse, the backdrop also moves and shrinks to (500, 300)
            const backdropEase = Math.pow(collapseU, 3);
            ctx.beginPath();
            ctx.ellipse(
              lerp(500, 500, backdropEase) * scaleX,
              lerp(180, 300, backdropEase) * scaleY,
              24 * (1 - backdropEase) * scaleX,
              30 * (1 - backdropEase) * scaleY,
              0,
              0,
              Math.PI * 2
            );
            ctx.moveTo(lerp(440, 500, backdropEase) * scaleX, lerp(250, 300, backdropEase) * scaleY);
            ctx.lineTo(lerp(468, 500, backdropEase) * scaleX, lerp(360, 300, backdropEase) * scaleY);
            ctx.lineTo(lerp(532, 500, backdropEase) * scaleX, lerp(360, 300, backdropEase) * scaleY);
            ctx.lineTo(lerp(560, 500, backdropEase) * scaleX, lerp(250, 300, backdropEase) * scaleY);
            ctx.closePath();
            ctx.fillStyle = `rgba(12, 16, 14, ${0.85 * silOpacity * (1 - backdropEase)})`;
            ctx.fill();

            // Draw extremely faint digital scanline texture inside the torso/head
            ctx.save();
            ctx.beginPath();
            ctx.ellipse(
              lerp(500, 500, backdropEase) * scaleX,
              lerp(180, 300, backdropEase) * scaleY,
              24 * (1 - backdropEase) * scaleX,
              30 * (1 - backdropEase) * scaleY,
              0,
              0,
              Math.PI * 2
            );
            ctx.rect(
              lerp(440, 500, backdropEase) * scaleX,
              lerp(210, 300, backdropEase) * scaleY,
              120 * (1 - backdropEase) * scaleX,
              150 * (1 - backdropEase) * scaleY
            );
            ctx.clip();
            ctx.beginPath();
            for (let y = 150 * scaleY; y < 360 * scaleY; y += 8) {
              ctx.moveTo(400 * scaleX, y);
              ctx.lineTo(600 * scaleX, y);
            }
            ctx.strokeStyle = `rgba(77, 124, 115, ${0.05 * silOpacity * (1 - backdropEase)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();

            // Draw the 250 outline particles with animated organic drift (teal + mint edge lighting)
            // During Stage 6 collapse, particles compress into the center core (500, 300)
            silParticles.current.forEach((p, pIdx) => {
              p.angle += p.speed;

              const easeU = Math.pow(collapseU, 3.5);
              const pTargetX = lerp(p.targetX, 500, easeU);
              const pTargetY = lerp(p.targetY, 300, easeU);
              const drift = 1.5 * (1 - easeU);

              const px = (pTargetX + Math.sin(p.angle) * drift) * scaleX;
              const py = (pTargetY + Math.cos(p.angle) * drift) * scaleY;

              const isHighlight = pIdx % 4 === 0;
              ctx.fillStyle = isHighlight
                ? `rgba(152, 182, 167, ${p.opacity * silOpacity})`
                : `rgba(77, 124, 115, ${p.opacity * silOpacity * 0.6})`;

              if (isHighlight) {
                ctx.shadowBlur = 4 * (1 - easeU);
                ctx.shadowColor = "rgba(152, 182, 167, 0.5)";
              } else {
                ctx.shadowBlur = 0;
              }

              ctx.beginPath();
              ctx.arc(px, py, p.r * scaleX, 0, Math.PI * 2);
              ctx.fill();
            });

            ctx.shadowBlur = 0;

            // Draw hand nodes (glowing time nodes with orbiting dots)
            // During Stage 6 collapse, these move inward along with leftX/rightX & leftY/rightY
            const drawHandNode = (hx: number, hy: number) => {
              const nodeEase = Math.pow(collapseU, 3);
              const radiusMult = 1 - nodeEase;

              // 1. Large Outer Bloom (emerald/teal)
              const bloomGrad = ctx.createRadialGradient(hx, hy, 0, hx, hy, 48 * radiusMult * scaleX);
              bloomGrad.addColorStop(0, `rgba(16, 185, 129, ${0.48 * silOpacity * radiusMult})`);
              bloomGrad.addColorStop(0.3, `rgba(77, 124, 115, ${0.16 * silOpacity * radiusMult})`);
              bloomGrad.addColorStop(1, "transparent");
              ctx.fillStyle = bloomGrad;
              ctx.beginPath();
              ctx.arc(hx, hy, 48 * radiusMult * scaleX, 0, Math.PI * 2);
              ctx.fill();

              // 2. Soft Inner Glow (mint/teal instead of white)
              const innerGrad = ctx.createRadialGradient(hx, hy, 0, hx, hy, 16 * radiusMult * scaleX);
              innerGrad.addColorStop(0, `rgba(147, 250, 217, ${0.95 * silOpacity * radiusMult})`);
              innerGrad.addColorStop(0.5, `rgba(16, 185, 129, ${0.75 * silOpacity * radiusMult})`);
              innerGrad.addColorStop(1, "transparent");
              ctx.fillStyle = innerGrad;
              ctx.beginPath();
              ctx.arc(hx, hy, 16 * radiusMult * scaleX, 0, Math.PI * 2);
              ctx.fill();

              // 3. Bright White Center (keep white only for the tiny center point)
              ctx.fillStyle = `rgba(255, 255, 255, ${silOpacity * radiusMult})`;
              ctx.beginPath();
              ctx.arc(hx, hy, 4.0 * radiusMult * scaleX, 0, Math.PI * 2);
              ctx.fill();

              // 4. Orbiting Particles (6 dots circling) - mint/teal instead of white
              const orbitCount = 6;
              const orbitSpeed = t * 0.0035;
              for (let i = 0; i < orbitCount; i++) {
                const angle = orbitSpeed + (i * Math.PI * 2) / orbitCount;
                const dist = (12 + Math.sin(t * 0.006 + i) * 3) * radiusMult * scaleX;
                const ox = hx + Math.cos(angle) * dist;
                const oy = hy + Math.sin(angle) * dist;

                ctx.fillStyle = `rgba(147, 250, 217, ${0.9 * silOpacity * radiusMult})`;
                ctx.beginPath();
                ctx.arc(ox, oy, 1.3 * scaleX, 0, Math.PI * 2);
                ctx.fill();
              }
            };

            // Draw hand nodes pulled inward dynamically using leftX, leftY, rightX, rightY
            drawHandNode(leftX * scaleX, leftY * scaleY);
            drawHandNode(rightX * scaleX, rightY * scaleY);

            ctx.restore();
          }

          // 2. Render Temporal Threads & Atmospheric Glow Haze
          if (threadOpacity > 0) {
            ctx.save();

            // Draw stronger emerald atmospheric haze / bloom in the background
            const glowOpacity = 0.16 + Math.sin(t / 400) * 0.04;
            const backGlow = ctx.createRadialGradient(
              500 * scaleX,
              300 * scaleY,
              0,
              500 * scaleX,
              300 * scaleY,
              450 * scaleX
            );
            backGlow.addColorStop(0, `rgba(16, 185, 129, ${glowOpacity * threadOpacity * (t < 8200 ? 1 : 1 - collapseU)})`);
            backGlow.addColorStop(0.5, `rgba(4, 120, 87, ${glowOpacity * 0.5 * threadOpacity * (t < 8200 ? 1 : 1 - collapseU)})`);
            backGlow.addColorStop(1, "transparent");
            ctx.fillStyle = backGlow;
            ctx.beginPath();
            ctx.arc(500 * scaleX, 300 * scaleY, 450 * scaleX, 0, Math.PI * 2);
            ctx.fill();

            // Draw the timeline strands
            THREADS_CONFIG.forEach((thread) => {
              const baseStartX = thread.isLeft ? (0 + thread.xStartOffset) : (1000 + thread.xStartOffset);
              const xStart = lerp(baseStartX, 500, collapseU) * scaleX;
              const yStart = lerp(thread.yStart, 300, collapseU) * scaleY;
              const xEnd = (thread.isLeft ? leftX : rightX) * scaleX;
              const yEnd = (thread.isLeft ? leftY : rightY) * scaleY;

              const dx = Math.abs(xEnd - xStart) / 2;
              const cp1x = (thread.isLeft ? xStart + dx : xStart - dx) + lerp(thread.xOffset1, 0, collapseU) * scaleX;
              const cp2x = (thread.isLeft ? xEnd - dx : xEnd + dx) + lerp(thread.xOffset2, 0, collapseU) * scaleX;

              // --- ATTRACTION & REPULSION FORMULAS ---

              // A. Repulsion from central ASTA text (Stage 4, 4.8s - 8.2s)
              const dy = thread.yStart - 300;
              let textPush = 0;
              if (Math.abs(dy) < 150 && t >= 4800 && t < 8200) {
                const pushAmt = (1 - Math.abs(dy) / 150) * 45;
                const uPush = Math.min(1, (t - 4800) / 1000);
                textPush = (dy < 0 ? -pushAmt : pushAmt) * uPush;
              }

              // B. Attraction to hand nodes (Stage 3 onwards, 3.2s - 8.2s)
              const uAttract = (t >= 3200 && t < 8200) ? Math.min(1, (t - 3200) / 1000) : 0;
              const currentOffset1 = lerp(thread.yOffset1, 0, uAttract * 0.4);
              const currentOffset2 = lerp(thread.yOffset2, 0, uAttract * 0.85); // pulls the control points towards the hand node

              // Apply organic waviness + attraction + repulsion to control points
              // In Stage 6 collapse, control points pull completely to center 300
              const cp1y = lerp(thread.yStart + currentOffset1 + textPush, 300, collapseU) * scaleY;
              const cp2y = lerp(yEnd + currentOffset2, 300, collapseU) * scaleY;

              // Draw base thread curve
              ctx.beginPath();
              ctx.moveTo(xStart, yStart);
              ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, xEnd, yEnd);

              // Calculate brightness multiplier near hand nodes (u -> 1)
              const brightnessMult = 1 + Math.pow(thread.u, 2.5) * 0.8 * uAttract;

              // Make threads slightly brighter as they approach the nodes
              const threadBaseOpacity = threadOpacity * thread.opacityMult;
              const finalThreadOpacity = Math.min(1, threadBaseOpacity * (1 + uAttract * 0.3)) * (1 - collapseU);

              // Apply glow settings and stroke for hero/mid/back layers
              if (thread.layer === "hero") {
                // Layer 1: Soft green/emerald aura underneath
                ctx.save();
                ctx.shadowBlur = 18 * brightnessMult * (1 - collapseU);
                ctx.shadowColor = "rgba(16, 185, 129, 0.65)";
                const auraOpacity = finalThreadOpacity * 0.35;
                ctx.strokeStyle = `rgba(16, 185, 129, ${auraOpacity})`;
                ctx.lineWidth = thread.strokeWidth * 3;
                ctx.stroke();
                ctx.restore();

                // Layer 2: Sharp teal line on top
                ctx.save();
                ctx.shadowBlur = 5 * brightnessMult * (1 - collapseU);
                ctx.shadowColor = "rgba(20, 184, 166, 0.8)";
                ctx.strokeStyle = thread.color.replace(/[\d\.]+\)$/, `${finalThreadOpacity})`);
                ctx.lineWidth = thread.strokeWidth;
                ctx.stroke();
                ctx.restore();
              } else {
                ctx.save();
                ctx.shadowBlur = 0;
                ctx.strokeStyle = thread.color.replace(/[\d\.]+\)$/, `${finalThreadOpacity})`);
                ctx.lineWidth = thread.strokeWidth;
                ctx.stroke();
                ctx.restore();
              }

              // Draw moving timeline particles
              // Strong non-linear acceleration during Stage 6 collapse (pulling into center)
              const acc = t >= 8200 ? 1 + Math.pow(collapseU, 3.5) * 22 : 1;
              // In Stage 5, particles accelerate as they get closer to the hand nodes (u -> 1)
              const uFactor = (t >= 6500 && t < 8200) ? 1 + Math.pow(thread.u, 2) * 2.0 : 1;
              thread.u = (thread.u + thread.speed * acc * uFactor) % 1;

              // Calculate current cubic Bezier coordinate
              const u = thread.u;
              const px =
                Math.pow(1 - u, 3) * xStart +
                3 * Math.pow(1 - u, 2) * u * cp1x +
                3 * (1 - u) * Math.pow(u, 2) * cp2x +
                Math.pow(u, 3) * xEnd;
              const py =
                Math.pow(1 - u, 3) * yStart +
                3 * Math.pow(1 - u, 2) * u * cp1y +
                3 * (1 - u) * Math.pow(u, 2) * cp2y +
                Math.pow(u, 3) * yEnd;

              // Draw particle dot with glow that increases near hand nodes, fading out as it converges
              if (thread.layer === "hero") {
                ctx.save();
                ctx.shadowBlur = 6 * brightnessMult * (1 - collapseU);
                ctx.shadowColor = "rgba(16, 185, 129, 0.7)";
                ctx.fillStyle = `rgba(147, 250, 217, ${Math.min(1, threadOpacity * thread.pOpacity * brightnessMult * (1 - collapseU * 0.55))})`;
                ctx.beginPath();
                ctx.arc(px, py, thread.pSize * (1 - collapseU * 0.3) * scaleX, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
              } else if (thread.layer === "midground") {
                ctx.save();
                ctx.shadowBlur = 0;
                ctx.fillStyle = `rgba(152, 182, 167, ${Math.min(1, threadOpacity * thread.pOpacity * brightnessMult * (1 - collapseU * 0.55))})`;
                ctx.beginPath();
                ctx.arc(px, py, thread.pSize * (1 - collapseU * 0.3) * scaleX, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
              } else {
                ctx.save();
                ctx.shadowBlur = 0;
                ctx.fillStyle = `rgba(77, 124, 115, ${Math.min(1, threadOpacity * thread.pOpacity * brightnessMult * (1 - collapseU * 0.55))})`;
                ctx.beginPath();
                ctx.arc(px, py, thread.pSize * (1 - collapseU * 0.3) * scaleX, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
              }
            });

            ctx.shadowBlur = 0; // Reset shadowBlur
            ctx.restore();
          }

          // 3. Render Final Core Collapse Soft Teal Bloom Flash (9.7s - 10.0s)
          if (t >= 9700) {
            const flashU = (t - 9700) / 300;
            const maxRadius = Math.max(w, h) * 1.0;
            const radius = flashU * maxRadius;
            const flashOpacity = 1 - flashU;

            const radialGlow = ctx.createRadialGradient(
              500 * scaleX,
              300 * scaleY,
              0,
              500 * scaleX,
              300 * scaleY,
              radius
            );
            radialGlow.addColorStop(0, `rgba(255, 255, 255, ${flashOpacity})`); // Pure white-hot center shine
            radialGlow.addColorStop(0.12, `rgba(230, 250, 240, ${flashOpacity * 0.95})`); // Light green/white shine
            radialGlow.addColorStop(0.35, `rgba(152, 182, 167, ${flashOpacity * 0.8})`); // Glowing mint green
            radialGlow.addColorStop(0.65, `rgba(77, 124, 115, ${flashOpacity * 0.35})`); // Dark teal bloom
            radialGlow.addColorStop(1, "transparent");

            ctx.fillStyle = radialGlow;
            ctx.beginPath();
            ctx.arc(500 * scaleX, 300 * scaleY, radius, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }

      // Handle CSS custom properties updates to avoid React rendering cycles
      if (containerRef.current) {
        const root = containerRef.current;
        let coreY = "50%";
        let coreScale = "1";
        let coreOpacity = "1";
        let titleOpacity = "0";
        let titleScale = "0.85";
        let titleBlur = "12px";

        if (t < 200) {
          coreOpacity = (t / 200).toFixed(3);
        }

        if (t >= 4800 && t < 5400) {
          const u = (t - 4800) / 600;
          coreY = `${50 - u * 17}%`;
          titleOpacity = u.toFixed(3);
          titleScale = (0.95 + u * 0.3).toFixed(3); // goes from 0.95 to 1.25 (25% bigger)
          titleBlur = `${12 - u * 12}px`;
        } else if (t >= 5400 && t < 8200) {
          coreY = "33%";
          titleOpacity = "1";
          titleScale = "1.25"; // 1.25 scale (bigger ASTA logo)
          titleBlur = "0px";
        } else if (t >= 8200 && t <= 9700) {
          const u = (t - 8200) / 1500;
          const easeU = Math.pow(u, 2.5); // stronger cubic ease down to center
          coreY = `${33 + easeU * 17}%`;
          coreScale = "1.000"; // Core remains fully visible and at scale = 1 as gravitational center
          coreOpacity = "1.000";
          titleOpacity = (1 - u).toFixed(3);
          titleScale = (1.25 - u * 1.1).toFixed(3); // shrink typography from 1.25 down to 0.15 size
          titleBlur = `${u * 20}px`; // dissolve with heavy blur
        } else if (t > 9700) {
          const flashU = (t - 9700) / 300;
          coreY = "50%";
          // Central >_< core does a heartbeat pulse at the final consolidation bloom
          coreScale = (1 + Math.sin(flashU * Math.PI) * 0.22).toFixed(3);
          coreOpacity = "1.000"; // Keep core fully visible during the pulse
        }

        root.style.setProperty("--core-y", coreY);
        root.style.setProperty("--core-scale", coreScale);
        root.style.setProperty("--core-opacity", coreOpacity);
        root.style.setProperty("--title-opacity", titleOpacity);
        root.style.setProperty("--title-scale", titleScale);
        root.style.setProperty("--title-blur", titleBlur);
      }

      if (t < 10000) {
        requestRef.current = requestAnimationFrame(animate);
      } else {
        onComplete();
      }
    };

    requestRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [onComplete]);

  const activeLabel = STAGE_LABELS[activeStage - 1] || STAGE_LABELS[0];

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-between p-8 select-none transition-all duration-500 overflow-hidden"
      style={{
        background: "#050806",
        color: "var(--txt-primary)",
      }}
    >
      {/* Background canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full z-0" />

      {/* Top Header Bar */}
      <div className="w-[80vw] flex items-center justify-between text-[10px] md:text-xs font-mono border-b border-white/5 pb-4 z-10" style={{ color: "var(--txt-muted)" }}>
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

      {/* HTML Layout overlays driven by local CSS variables */}
      <div className="absolute inset-0 z-10 pointer-events-none">
        {/* Core circle containing >_< */}
        <div
          className="absolute left-1/2 flex items-center justify-center w-36 h-36 md:w-44 md:h-44 transition-all duration-100 ease-out"
          style={{
            top: "var(--core-y, 50%)",
            transform: "translate(-50%, -50%) scale(var(--core-scale, 1))",
            opacity: "var(--core-opacity, 1)",
          }}
        >
          {/* Pulsating outer core halos */}
          <div
            className="absolute inset-0 rounded-full border opacity-20 animate-pulse"
            style={{ borderColor: "var(--accent)" }}
          />
          <div
            className="absolute w-[80%] h-[80%] rounded-full border border-dashed animate-[spin_30s_linear_infinite]"
            style={{ borderColor: "var(--accent)", opacity: 0.3 }}
          />
          <div
            className="absolute w-[60%] h-[60%] rounded-full border flex items-center justify-center bg-[#111714]"
            style={{
              borderColor: "var(--accent)",
              boxShadow: "0 0 25px rgba(77, 124, 115, 0.35)",
            }}
          >
            <span
              className="font-mono font-black select-none tracking-tighter"
              style={{
                fontSize: "24px",
                color: "var(--accent)",
                textShadow: "0 0 12px rgba(77, 124, 115, 0.7)",
              }}
            >
              &gt;_&lt;
            </span>
          </div>
        </div>

        {/* Large ASTA title logo */}
        <div
          className="absolute top-1/2 left-1/2 text-center transition-all duration-100 ease-out"
          style={{
            transform: "translate(-50%, -10%) scale(var(--title-scale, 0.85))",
            opacity: "var(--title-opacity, 0)",
            filter: "drop-shadow(0 0 20px rgba(152, 182, 167, 0.58)) blur(var(--title-blur, 12px))",
          }}
        >
          <h1 className="font-heading font-black tracking-[0.38em] text-4xl md:text-6xl flex items-center justify-center gap-1 select-none">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent)] to-[var(--sage)]">
              ASTA
            </span>
          </h1>
          <p
            className="font-mono text-[9px] md:text-[10px] tracking-[0.16em] uppercase mt-4 animate-pulse"
            style={{ color: "var(--accent)" }}
          >
            {activeLabel.subText}
          </p>
        </div>
      </div>

      {/* Bottom Status Labels & Skip Controls */}
      <div className="w-[80vw] flex items-center justify-between border-t border-white/5 pt-4 font-mono z-10 text-[10px] md:text-xs">
        <div className="flex flex-col gap-1" style={{ color: "var(--txt-muted)" }}>
          <span className="text-[var(--accent)] uppercase font-semibold">
            STATUS: {activeLabel.footer}
          </span>
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
};
