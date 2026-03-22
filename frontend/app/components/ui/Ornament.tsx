"use client";

export function DiamondDivider({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-0 my-3 ${className}`}>
      <div className="flex-1 h-px" style={{ background: "rgba(194, 58, 46, 0.15)" }} />
      <svg viewBox="0 0 8 8" width="8" height="8" className="mx-2 flex-shrink-0">
        <rect x="1" y="1" width="6" height="6" transform="rotate(45 4 4)" fill="rgba(194, 58, 46, 0.3)" />
      </svg>
      <div className="flex-1 h-px" style={{ background: "rgba(194, 58, 46, 0.15)" }} />
    </div>
  );
}

export function SectionDivider({ className = "" }: { className?: string }) {
  return (
    <div className={`h-px my-4 ${className}`} style={{ background: "rgba(230, 237, 243, 0.08)" }} />
  );
}

export function WaveDivider({ className = "" }: { className?: string }) {
  return (
    <div className={`my-4 flex justify-center ${className}`}>
      <svg viewBox="0 0 120 8" width="120" height="8" className="opacity-30">
        <path d="M0,4 C10,0 20,8 30,4 C40,0 50,8 60,4 C70,0 80,8 90,4 C100,0 110,8 120,4" fill="none" stroke="rgba(194, 58, 46, 1)" strokeWidth="0.8"/>
      </svg>
    </div>
  );
}
