"use client";

const occupationShapes: Record<string, { icon: string; color: string }> = {
  "village elder": { icon: "crown", color: "rgba(194,58,46,0.8)" },
  "blacksmith": { icon: "anvil", color: "rgba(194,58,46,0.7)" },
  "merchant": { icon: "coins", color: "rgba(194,58,46,0.75)" },
  "farmhand": { icon: "wheat", color: "rgba(194,58,46,0.5)" },
  "baker": { icon: "bread", color: "rgba(194,58,46,0.6)" },
  "herbalist": { icon: "leaf", color: "rgba(194,58,46,0.55)" },
  "priest": { icon: "cross", color: "rgba(194,58,46,0.65)" },
  "bard": { icon: "lyre", color: "rgba(194,58,46,0.7)" },
  "hunter": { icon: "bow", color: "rgba(194,58,46,0.5)" },
  "guard": { icon: "shield", color: "rgba(194,58,46,0.6)" },
  "weaver": { icon: "thread", color: "rgba(194,58,46,0.55)" },
  "carpenter": { icon: "hammer", color: "rgba(194,58,46,0.6)" },
  "midwife": { icon: "heart", color: "rgba(194,58,46,0.5)" },
  "beggar": { icon: "hand", color: "rgba(194,58,46,0.35)" },
  "poacher": { icon: "trap", color: "rgba(194,58,46,0.4)" },
  "orphan": { icon: "star", color: "rgba(194,58,46,0.45)" },
  "drunk": { icon: "mug", color: "rgba(194,58,46,0.5)" },
  "troublemaker": { icon: "flame", color: "rgba(194,58,46,0.6)" },
  "cook": { icon: "pot", color: "rgba(194,58,46,0.55)" },
  "farmer": { icon: "wheat", color: "rgba(194,58,46,0.5)" },
  "apothecary": { icon: "potion", color: "rgba(194,58,46,0.6)" },
};

const moodColors: Record<string, string> = {
  content: "rgba(194,58,46,0.4)",
  excited: "rgba(194,58,46,0.6)",
  angry: "rgba(194,58,46,0.8)",
  fearful: "rgba(194,58,46,0.3)",
  melancholic: "rgba(194,58,46,0.35)",
  neutral: "rgba(194,58,46,0.25)",
};

function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

interface Props {
  name: string;
  occupation: string;
  mood?: string;
  size?: number;
  className?: string;
}

export function NPCPortrait({ name, occupation, mood = "neutral", size = 40, className = "" }: Props) {
  const hash = hashCode(name);
  const occ = occupationShapes[occupation.toLowerCase()] || { icon: "person", color: "rgba(194,58,46,0.5)" };
  const moodColor = moodColors[mood] || moodColors.neutral;

  // Generate unique face features from name hash
  const eyeY = 16 + (hash % 3);
  const mouthY = 26 + (hash % 2);
  const faceWidth = 14 + (hash % 4);
  const hasBeard = hash % 3 === 0;
  const hasHat = hash % 4 === 0;

  // Sepia/brown face tone based on hash — no hue variation
  const faceLightness = 25 + (hash % 10);

  return (
    <div className={`relative flex-shrink-0 ${className}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 40 40" width={size} height={size} className="rounded-full">
        {/* Background circle — dark neutral */}
        <circle cx="20" cy="20" r="20" fill={`hsl(215, 15%, 10%)`} />
        <circle cx="20" cy="20" r="19" fill="none" stroke={occ.color} strokeWidth="0.8" opacity="0.4" />

        {/* Face shape — neutral dark tones only */}
        <ellipse cx="20" cy="19" rx={faceWidth / 2} ry="10" fill={`hsl(215, 10%, ${faceLightness}%)`} opacity="0.8" />

        {/* Eyes */}
        <circle cx="16" cy={eyeY} r="1.5" fill="#E6EDF3" opacity="0.7" />
        <circle cx="24" cy={eyeY} r="1.5" fill="#E6EDF3" opacity="0.7" />
        <circle cx="16" cy={eyeY} r="0.7" fill="#1a1a1a" />
        <circle cx="24" cy={eyeY} r="0.7" fill="#1a1a1a" />

        {/* Mouth — gold tones only */}
        {mood === "angry" && (
          <line x1="16" y1={mouthY + 1} x2="24" y2={mouthY - 1} stroke="rgba(194,58,46,0.5)" strokeWidth="1" opacity="0.6" />
        )}
        {mood === "content" && (
          <path d={`M16,${mouthY} Q20,${mouthY + 3} 24,${mouthY}`} fill="none" stroke="#E6EDF3" strokeWidth="0.8" opacity="0.5" />
        )}
        {mood === "fearful" && (
          <ellipse cx="20" cy={mouthY} rx="2" ry="1.5" fill="#1a1a1a" opacity="0.3" />
        )}
        {(mood === "excited" || mood === "neutral" || mood === "melancholic") && (
          <line x1="17" y1={mouthY} x2="23" y2={mouthY} stroke="#E6EDF3" strokeWidth="0.6" opacity="0.4" />
        )}

        {/* Beard for some — neutral tones */}
        {hasBeard && (
          <path d={`M14,${mouthY + 1} Q20,${mouthY + 7} 26,${mouthY + 1}`} fill={`hsl(215, 10%, ${20 + (hash % 10)}%)`} opacity="0.5" />
        )}

        {/* Hat for some */}
        {hasHat && (
          <path d="M12,12 L20,5 L28,12" fill={occ.color} opacity="0.3" />
        )}

        {/* Occupation icon badge */}
        <circle cx="33" cy="33" r="6" fill={occ.color} opacity="0.8" />
        <text x="33" y="36" textAnchor="middle" fontSize="7" fill="#0d0d1a" fontWeight="bold">
          {occ.icon.charAt(0).toUpperCase()}
        </text>

        {/* Mood ring — gold with opacity variation */}
        <circle cx="20" cy="20" r="19.5" fill="none" stroke={moodColor} strokeWidth="1" opacity="0.5" strokeDasharray="4 8" />
      </svg>
    </div>
  );
}
