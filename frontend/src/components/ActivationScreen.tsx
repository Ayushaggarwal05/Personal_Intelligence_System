import React, { useState, useEffect, useRef } from "react";
import { Terminal, Cpu, Play } from "lucide-react";

interface ActivationScreenProps {
  onComplete: () => void;
}

const BOOT_STAGES = [
  { progress: 15, delay: 0, text: "Initializing ASTA Orchestrator Core..." },
  { progress: 35, delay: 800, text: "Connecting local rel-index (SQLite)... [OK]" },
  { progress: 60, delay: 1700, text: "Indexing Vector Embeddings Engine (LanceDB)... [OK]" },
  { progress: 85, delay: 2800, text: "Calibrating Model Router & local APIs... [OK]" },
  { progress: 100, delay: 3800, text: "ASTA Engineering Intelligence activated." }
];

export const ActivationScreen: React.FC<ActivationScreenProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [fadeOut, setFadeOut] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1. Progress smooth interpolation over ~4.2 seconds
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 1;
      });
    }, 40);

    // 2. Stream log lines matching boot sequence stages
    const timers = BOOT_STAGES.map((stage) => {
      return setTimeout(() => {
        setLogs((prev) => [...prev, `[system@asta ~]$ ${stage.text}`]);
      }, stage.delay);
    });

    // 3. Final completion transition around 4.6 seconds
    const endTimer = setTimeout(() => {
      setFadeOut(true);
      setTimeout(onComplete, 600); // Wait for CSS fade-out animation
    }, 4600);

    return () => {
      clearInterval(interval);
      timers.forEach(clearTimeout);
      clearTimeout(endTimer);
    };
  }, [onComplete]);

  // Scroll terminal logs to bottom automatically
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleSkip = () => {
    setFadeOut(true);
    setTimeout(onComplete, 400);
  };

  return (
    <div
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-between p-8 transition-all duration-500 select-none ${
        fadeOut ? "opacity-0 scale-95 blur-md pointer-events-none" : "opacity-100 scale-100"
      }`}
      style={{
        background: "var(--bg-app)",
        color: "var(--txt-primary)",
      }}
    >
      {/* Background Tech Grids / Accent Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(circle at center, rgba(77, 124, 115, 0.12) 0%, transparent 65%)",
        }}
      />
      
      {/* Top Console Bar (Width 80%) */}
      <div className="w-[80%] max-w-4xl flex items-center justify-between text-[10px] md:text-xs font-mono border-b border-white/5 pb-4 z-10" style={{ color: "var(--txt-muted)" }}>
        <div className="flex items-center gap-2">
          <Terminal size={14} style={{ color: "var(--accent)" }} />
          <span>ASTA_BOOT_SEQUENCE_v1.0.SYS</span>
        </div>
        <div className="flex items-center gap-4">
          <span>HOST: LOCALHOST</span>
          <span>SECURE_MODE: ACTIVE</span>
        </div>
      </div>

      {/* Center AI Core Pulse */}
      <div className="flex flex-col items-center gap-6 my-auto z-10">
        <div className="relative flex items-center justify-center w-32 h-32 md:w-36 md:h-36">
          {/* Outer rotating dashed ring */}
          <div
            className="absolute w-28 h-28 md:w-32 md:h-32 rounded-full border border-dashed animate-spin opacity-35"
            style={{
              borderColor: "var(--accent)",
              animationDuration: "12s",
            }}
          />
          {/* Animated radar rings using standard styling & css classes */}
          <div
            className="absolute inset-0 rounded-full border animate-ping opacity-20"
            style={{
              borderColor: "var(--accent)",
              animationDuration: "3s",
            }}
          />
          <div
            className="absolute w-24 h-24 md:w-28 md:h-28 rounded-full border animate-pulse opacity-45"
            style={{
              borderColor: "var(--accent)",
              animationDuration: "2s",
            }}
          />
          <div
            className="absolute w-16 h-16 md:w-20 md:h-20 rounded-full border flex items-center justify-center shadow-lg bg-[#1a211e]"
            style={{
              borderColor: "var(--accent)",
              boxShadow: "0 0 30px rgba(77, 124, 115, 0.3)",
            }}
          >
            {/* Tweak: signature ASTA character >_< instead of Cpu */}
            <span
              className="font-mono font-black select-none tracking-tighter"
              style={{
                fontSize: "18px",
                color: "var(--accent)",
                textShadow: "0 0 10px rgba(77, 124, 115, 0.6)"
              }}
            >
              &gt;_&lt;
            </span>
          </div>
        </div>
        
        <div className="text-center">
          {/* Improved Design: Text Gradient for ASTA Title */}
          <h1
            className="font-heading font-black tracking-[0.3em] text-2xl md:text-3xl flex items-center justify-center gap-1"
          >
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent)] to-[var(--sage)]">
              ASTA
            </span>
          </h1>
          <div
            className="font-mono text-[9px] md:text-[10px] tracking-widest uppercase mt-2 animate-pulse"
            style={{ color: "var(--accent)" }}
          >
            Calibrating Neural Interfaces
          </div>
        </div>
      </div>

      {/* Bottom Logger & Progress */}
      <div className="w-full max-w-xl flex flex-col gap-5 z-10">
        {/* Terminal Logs Mock Window Container */}
        <div className="bg-black/35 rounded-xl border border-white/5 overflow-hidden flex flex-col shadow-2xl">
          {/* Window Header */}
          <div className="flex items-center justify-between px-4 py-2 bg-black/20 border-b border-white/5">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-500/60" />
              <span className="w-2 h-2 rounded-full bg-yellow-500/60" />
              <span className="w-2 h-2 rounded-full bg-green-500/60" />
            </div>
            <span className="font-mono text-[9px] text-[var(--txt-muted)] select-none">
              calibrating_kernel.sh
            </span>
            <div className="w-8" />
          </div>

          {/* Terminal Logs Sandbox */}
          <div
            className="h-28 p-4 overflow-y-auto font-mono text-[10px] md:text-[11px] flex flex-col gap-2 shadow-inner"
            style={{ color: "var(--txt-second)" }}
          >
            {logs.map((log, index) => (
              <div key={index} className="animate-fade-in flex items-start gap-2 leading-relaxed">
                <span style={{ color: "var(--accent)" }} className="select-none">&gt;</span>
                <span>{log}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* Linear Progress bar */}
        <div className="flex items-center gap-4">
          <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${progress}%`,
                background: "linear-gradient(90deg, var(--accent) 0%, var(--sage) 100%)",
                boxShadow: "0 0 8px var(--accent)",
              }}
            />
          </div>
          <span className="font-mono text-[10px] md:text-xs min-w-[36px] text-right" style={{ color: "var(--txt-muted)" }}>
            {progress}%
          </span>
        </div>

        {/* Controls Footer */}
        <div className="flex items-center justify-center mt-1">
          <button
            onClick={handleSkip}
            className="flex items-center gap-1.5 px-4 py-2 font-mono text-[9px] md:text-[10px] rounded-lg border transition-all cursor-pointer bg-white/5 border-white/5 text-[var(--txt-muted)] hover:text-[var(--txt-primary)] hover:bg-white/10"
            style={{
              color: "var(--txt-muted)",
              borderColor: "var(--border)",
            }}
          >
            <Play size={8} fill="currentColor" />
            SKIP CALIBRATION
          </button>
        </div>
      </div>
    </div>
  );
};
