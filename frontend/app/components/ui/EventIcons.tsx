"use client";

interface Props {
  type: string;
  size?: number;
  className?: string;
}

const GOLD_COLOR = "rgba(194,58,46,0.6)";

export function EventIcon({ type, size = 16, className = "" }: Props) {
  const icons: Record<string, string> = {
    conflict: "M14.5 17.5L3 6V3h3l11.5 11.5M13 19l6-6m3 3l-2 2",
    social: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
    natural: "M17 8c0-3-2-6-5-8-3 2-5 5-5 8a5 5 0 0 0 10 0zM12 19v3m-3-3h6",
    trade: "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
    scenario: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
    weather: "M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z",
    quest: "M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 4v13M20 4v13M8 4h8a1 1 0 0 1 1 1v4H7V5a1 1 0 0 1 1-1z",
  };

  const path = icons[type] || icons.natural;

  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={`flex-shrink-0 ${className}`}
      fill="none"
      stroke={GOLD_COLOR}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={path} />
    </svg>
  );
}
