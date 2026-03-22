"use client";

export function DragonBorder({ className = "" }: { className?: string }) {
  return (
    <div className={`fantasy-border ${className}`}>
      <svg viewBox="0 0 200 20" className="w-full h-5 opacity-20" preserveAspectRatio="none">
        <path d="M0,10 C20,0 30,20 50,10 C70,0 80,20 100,10 C120,0 130,20 150,10 C170,0 180,20 200,10" fill="none" stroke="currentColor" strokeWidth="1.5"/>
        <circle cx="25" cy="10" r="2" fill="currentColor" opacity="0.5"/>
        <circle cx="75" cy="10" r="2" fill="currentColor" opacity="0.5"/>
        <circle cx="125" cy="10" r="2" fill="currentColor" opacity="0.5"/>
        <circle cx="175" cy="10" r="2" fill="currentColor" opacity="0.5"/>
      </svg>
    </div>
  );
}

export function SwordDivider() {
  return (
    <div className="flex items-center justify-center gap-3 my-4 opacity-30">
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gold/50 to-transparent" />
      <svg viewBox="0 0 24 24" className="w-5 h-5 text-gold" fill="currentColor">
        <path d="M14.5 17.5L3 6V3h3l11.5 11.5M13 19l6-6m3 3l-2 2m-3-3l2-2"/>
      </svg>
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gold/50 to-transparent" />
    </div>
  );
}

export function ShieldIcon({ mood }: { mood: string }) {
  const colors: Record<string, string> = {
    angry: "#B43232",
    fearful: "#7B68EE",
    excited: "#DAA520",
    content: "#2E8B57",
    melancholic: "#4682B4",
    neutral: "#808080",
  };
  const color = colors[mood] || colors.neutral;
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill={color} opacity={0.6}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  );
}

export function ScrollFrame({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`relative ${className}`}>
      {/* Top scroll edge */}
      <div className="absolute -top-2 left-4 right-4 h-4 bg-gradient-to-b from-gray-900/20 to-transparent rounded-t-xl" />
      {/* Content */}
      <div className="relative bg-gradient-to-b from-gray-950/10 via-transparent to-gray-950/10 rounded-lg border border-gray-700/10 p-4">
        {children}
      </div>
      {/* Bottom scroll edge */}
      <div className="absolute -bottom-2 left-4 right-4 h-4 bg-gradient-to-t from-gray-900/20 to-transparent rounded-b-xl" />
    </div>
  );
}
