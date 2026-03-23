"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

const races = [
  { id: "human", name: "Human", bonus: "+1 all stats", desc: "Versatile and ambitious" },
  { id: "elf", name: "Elf", bonus: "+2 DEX, +1 INT", desc: "Graceful and long-lived" },
  { id: "dwarf", name: "Dwarf", bonus: "+2 CON, +1 STR", desc: "Sturdy and resilient" },
  { id: "halfling", name: "Halfling", bonus: "+2 DEX, +1 CHA", desc: "Lucky and brave" },
  { id: "half-orc", name: "Half-Orc", bonus: "+2 STR, +1 CON", desc: "Fierce and enduring" },
];

const classes = [
  { id: "fighter", name: "Fighter", hp: 10, desc: "Master of martial combat", icon: "⚔️" },
  { id: "rogue", name: "Rogue", hp: 8, desc: "Stealthy and cunning", icon: "🗡️" },
  { id: "wizard", name: "Wizard", hp: 6, desc: "Wielder of arcane magic", icon: "🔮" },
  { id: "cleric", name: "Cleric", hp: 8, desc: "Divine healer and protector", icon: "✝️" },
  { id: "ranger", name: "Ranger", hp: 10, desc: "Hunter of the wilds", icon: "🏹" },
];

const raceSVGs: Record<string, JSX.Element> = {
  human: (
    <svg viewBox="0 0 40 60" width="50" height="75">
      <circle cx="20" cy="10" r="6" fill="currentColor"/>
      <rect x="15" y="17" width="10" height="20" rx="2" fill="currentColor"/>
      <rect x="8" y="20" width="7" height="3" rx="1" fill="currentColor"/>
      <rect x="25" y="20" width="7" height="3" rx="1" fill="currentColor"/>
      <rect x="15" y="38" width="4" height="15" rx="1" fill="currentColor"/>
      <rect x="21" y="38" width="4" height="15" rx="1" fill="currentColor"/>
      <rect x="30" y="18" width="2" height="18" rx="1" fill="currentColor" transform="rotate(15,31,27)"/>
    </svg>
  ),
  elf: (
    <svg viewBox="0 0 40 60" width="50" height="75">
      <circle cx="20" cy="10" r="5" fill="currentColor"/>
      <path d="M14,8 L8,4" stroke="currentColor" strokeWidth="1.5" fill="none"/>
      <path d="M26,8 L32,4" stroke="currentColor" strokeWidth="1.5" fill="none"/>
      <rect x="16" y="16" width="8" height="22" rx="2" fill="currentColor"/>
      <rect x="14" y="38" width="4" height="16" rx="1" fill="currentColor"/>
      <rect x="22" y="38" width="4" height="16" rx="1" fill="currentColor"/>
      <path d="M28,15 L36,8" stroke="currentColor" strokeWidth="1.5" fill="none"/>
      <line x1="36" y1="8" x2="36" y2="35" stroke="currentColor" strokeWidth="1"/>
    </svg>
  ),
  dwarf: (
    <svg viewBox="0 0 40 60" width="50" height="75">
      <circle cx="20" cy="12" r="7" fill="currentColor"/>
      <path d="M13,16 Q20,24 27,16" fill="currentColor" opacity="0.7"/>
      <rect x="12" y="20" width="16" height="18" rx="3" fill="currentColor"/>
      <rect x="13" y="39" width="6" height="12" rx="2" fill="currentColor"/>
      <rect x="21" y="39" width="6" height="12" rx="2" fill="currentColor"/>
      <rect x="6" y="22" width="5" height="14" rx="2" fill="currentColor"/>
    </svg>
  ),
  halfling: (
    <svg viewBox="0 0 40 60" width="50" height="75">
      <circle cx="20" cy="18" r="6" fill="currentColor"/>
      <rect x="15" y="25" width="10" height="14" rx="2" fill="currentColor"/>
      <rect x="15" y="40" width="4" height="10" rx="1" fill="currentColor"/>
      <rect x="21" y="40" width="4" height="10" rx="1" fill="currentColor"/>
      <line x1="20" y1="27" x2="20" y2="15" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="20" cy="14" r="1.5" fill="currentColor"/>
    </svg>
  ),
  "half-orc": (
    <svg viewBox="0 0 40 60" width="50" height="75">
      <circle cx="20" cy="10" r="7" fill="currentColor"/>
      <rect x="11" y="18" width="18" height="22" rx="3" fill="currentColor"/>
      <rect x="6" y="20" width="7" height="5" rx="2" fill="currentColor"/>
      <rect x="27" y="20" width="7" height="5" rx="2" fill="currentColor"/>
      <rect x="12" y="41" width="6" height="14" rx="2" fill="currentColor"/>
      <rect x="22" y="41" width="6" height="14" rx="2" fill="currentColor"/>
      <rect x="30" y="14" width="3" height="20" rx="1" fill="currentColor" transform="rotate(10,31,24)"/>
    </svg>
  ),
};

export default function CharacterCreation() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [race, setRace] = useState("");
  const [classId, setClassId] = useState("");
  const [creating, setCreating] = useState(false);

  const canCreate = name.trim().length >= 2 && race && classId;

  const handleCreate = async () => {
    if (!canCreate) return;
    setCreating(true);
    try {
      await api.createCharacter({ name: name.trim(), race, class_id: classId });
      router.push("/");
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  return (
    <main
      className="min-h-screen  flex items-center justify-center p-8"
      style={{
        background: "#0D1117",
      }}
    >
      {/* Hero background image */}
      <div className="fixed inset-0 z-0">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-[0.15]"
          style={{ backgroundImage: "url(/images/hero-bg.jpg)" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0D1117] via-[#0D1117]/70 to-[#0D1117]/90" />
      </div>
      {/* Ambient gold glow */}
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: "radial-gradient(ellipse at 50% 120%, rgba(194,58,46,0.08) 0%, transparent 60%)",
        }}
      />

      <div className="w-full max-w-3xl relative z-10">
        <Link href="/" className="btn-stone inline-flex items-center gap-2 px-4 py-2 text-sm mb-8">
          <span>&#8592;</span>
          <span className="font-medieval tracking-wider">Back to Game</span>
        </Link>

        {/* Decorative Forge Illustration */}
        <div className="flex justify-center mb-6 opacity-30">
          <svg viewBox="0 0 140 80" width="140" height="80">
            {/* Anvil */}
            <path d="M50,55 L55,40 L85,40 L90,55 Z" fill="none" stroke="rgba(194,58,46,0.6)" strokeWidth="1.5"/>
            <rect x="45" y="55" width="50" height="6" rx="2" fill="none" stroke="rgba(194,58,46,0.5)" strokeWidth="1"/>
            {/* Anvil horn */}
            <path d="M85,43 L105,38 L105,42 L85,47" fill="none" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
            {/* Hammer */}
            <line x1="70" y1="35" x2="55" y2="15" stroke="rgba(194,58,46,0.5)" strokeWidth="1.5"/>
            <rect x="45" y="8" width="20" height="10" rx="2" fill="none" stroke="rgba(194,58,46,0.6)" strokeWidth="1.5" transform="rotate(-15, 55, 13)"/>
            {/* Sparks — gold only */}
            <circle cx="65" cy="38" r="1" fill="rgba(194,58,46,0.6)">
              <animate attributeName="opacity" values="0.6;0;0.6" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <circle cx="72" cy="35" r="0.8" fill="rgba(194,58,46,0.5)">
              <animate attributeName="opacity" values="0;0.5;0" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="60" cy="33" r="0.6" fill="rgba(194,58,46,0.4)">
              <animate attributeName="opacity" values="0.4;0;0.4" dur="1.8s" repeatCount="indefinite"/>
            </circle>
            {/* Fire beneath — gold only */}
            <path d="M55,65 Q60,58 65,65 Q70,55 75,65 Q80,58 85,65" fill="none" stroke="rgba(194,58,46,0.3)" strokeWidth="1">
              <animate attributeName="d" values="M55,65 Q60,58 65,65 Q70,55 75,65 Q80,58 85,65;M55,65 Q60,56 65,65 Q70,57 75,65 Q80,56 85,65;M55,65 Q60,58 65,65 Q70,55 75,65 Q80,58 85,65" dur="2s" repeatCount="indefinite"/>
            </path>
          </svg>
        </div>

        {/* Title */}
        <div className="text-center mb-10">
          <h1 className="font-medieval text-4xl text-gold tracking-wider mb-2">Create Your Hero</h1>
          <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-gold/40 to-transparent" />
          <p className="text-parchment/40 text-sm font-body mt-3">Choose your name, race, and class to begin your adventure</p>
        </div>

        {/* Name */}
        <div className="mb-8 max-w-md mx-auto">
          <label className="font-medieval text-gold/70 text-sm tracking-wider block mb-2">Character Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter a name..."
            className="input-fantasy w-full text-lg"
            maxLength={30}
          />
        </div>

        {/* Race */}
        <div className="mb-8">
          <label className="font-medieval text-gold/70 text-sm tracking-wider block mb-3">Race</label>
          <div className="grid grid-cols-5 gap-3">
            {races.map((r) => (
              <button
                key={r.id}
                onClick={() => setRace(r.id)}
                className="game-card hover-lift p-4 text-center transition-all duration-200"
                style={{
                  minWidth: "150px",
                  border: race === r.id ? "1px solid rgba(194,58,46,0.5)" : "1px solid #30363D",
                  background: race === r.id ? "rgba(194,58,46,0.06)" : "#161B22",
                }}
              >
                {/* Race SVG silhouette */}
                <div className="flex justify-center mb-2" style={{ color: race === r.id ? "rgba(194,58,46,0.7)" : "rgba(194,58,46,0.3)" }}>
                  {raceSVGs[r.id]}
                </div>
                <div className="font-medieval text-sm text-gold/80 mb-1">{r.name}</div>
                <div className="text-xs text-[rgba(230,237,243,0.6)] font-body font-semibold">{r.bonus}</div>
                <div className="text-xs text-[rgba(230,237,243,0.4)] font-body mt-1.5 leading-relaxed">{r.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Class */}
        <div className="mb-10">
          <label className="font-medieval text-gold/70 text-sm tracking-wider block mb-3">Class</label>
          <div className="grid grid-cols-5 gap-3">
            {classes.map((c) => (
              <button
                key={c.id}
                onClick={() => setClassId(c.id)}
                className="game-card hover-lift p-4 text-center transition-all duration-200"
                style={{
                  minWidth: "140px",
                  border: classId === c.id ? "1px solid rgba(194,58,46,0.5)" : "1px solid #30363D",
                  background: classId === c.id ? "rgba(194,58,46,0.06)" : "#161B22",
                }}
              >
                <div className="text-2xl mb-1.5" style={{ filter: "brightness(0.8) saturate(0.5)" }}>{c.icon}</div>
                <div className="font-medieval text-sm text-gold/80">{c.name}</div>
                <div className="text-xs text-[rgba(230,237,243,0.6)] font-body font-semibold">Hit Die: d{c.hp}</div>
                <div className="text-xs text-[rgba(230,237,243,0.4)] font-body mt-1.5 leading-relaxed">{c.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Create button */}
        <div className="text-center">
          <button
            onClick={handleCreate}
            disabled={!canCreate || creating}
            className={`btn-stone px-12 py-3 text-lg font-medieval tracking-wider transition-all duration-200 ${
              canCreate && !creating ? "hover:scale-105 cursor-pointer" : "cursor-not-allowed opacity-40"
            }`}
          >
            {creating ? "Creating..." : "Begin Adventure"}
          </button>
        </div>
      </div>
    </main>
  );
}
