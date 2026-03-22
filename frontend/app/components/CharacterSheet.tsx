"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import Link from "next/link";

interface CharacterData {
  name: string;
  race: string;
  class: string;
  level: number;
  hp: number;
  max_hp: number;
  ac: number;
  initiative: number;
  proficiency_bonus: number;
  abilities: Record<string, number>;
  equipment: { name: string; type: string }[];
  gold: number;
  silver: number;
  copper: number;
}

const ABILITY_SHORT = ["STR", "DEX", "CON", "INT", "WIS", "CHA"] as const;

function mod(score: number): string {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : `${m}`;
}

function HpBar({ current, max }: { current: number; max: number }) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (current / max) * 100)) : 0;
  const color =
    pct > 60 ? "from-forest to-forest-light" : pct > 30 ? "from-ember to-gold" : "from-blood to-ember";
  return (
    <div className="w-full h-2.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}>
      <div
        className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-500`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function CharacterSheet() {
  const t = useT();
  const [char, setChar] = useState<CharacterData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api
      .getCharacter()
      .then((data) => {
        if (data && data.name) setChar(data);
        else setError(true);
      })
      .catch(() => setError(true));
  }, []);

  if (error || !char) {
    return (
      <div className="p-4">
        <h3 className="section-title mb-3">{t("sheet.title")}</h3>
        <div className="text-center py-6">
          <span className="text-2xl opacity-15 block mb-2">&#9876;</span>
          <p style={{ color: "rgba(255,255,255,0.25)", fontSize: "13px" }} className="font-body mb-3">
            {t("sheet.createChar")}
          </p>
          <Link
            href="/character"
            className="btn-fantasy inline-block text-center w-full"
            style={{ fontSize: "11px", letterSpacing: "0.1em", padding: "10px 12px" }}
          >
            {t("char.openCreator")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded flex items-center justify-center"
          style={{ background: "rgba(194,58,46,0.1)", border: "1px solid rgba(194,58,46,0.15)" }}
        >
          <span className="text-gold text-sm font-medieval font-bold">{char.level}</span>
        </div>
        <div className="min-w-0">
          <h3 className="font-medieval text-sm font-bold tracking-wide truncate" style={{ color: "#E6EDF3" }}>
            {char.name}
          </h3>
          <p style={{ color: "rgba(255,255,255,0.35)", fontSize: "13px" }} className="font-body">
            {char.race} {char.class}
          </p>
        </div>
      </div>

      {/* HP */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="section-title">{t("sheet.hp")}</span>
          <span style={{ color: "rgba(255,255,255,0.4)", fontSize: "13px" }} className="font-body">
            {char.hp}/{char.max_hp}
          </span>
        </div>
        <HpBar current={char.hp} max={char.max_hp} />
      </div>

      {/* Combat stats */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: t("sheet.ac"), value: char.ac },
          { label: t("sheet.init"), value: `${char.initiative >= 0 ? "+" : ""}${char.initiative}` },
          { label: t("sheet.prof"), value: `+${char.proficiency_bonus}` },
        ].map((s) => (
          <div key={s.label} className="text-center p-2 rounded" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)" }}>
            <div style={{ color: "rgba(255,255,255,0.3)", fontSize: "12px" }} className="font-body">{s.label}</div>
            <div className="font-medieval font-bold" style={{ color: "#E6EDF3" }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="divider-ornament" />

      {/* Abilities */}
      <div className="grid grid-cols-3 gap-1.5">
        {ABILITY_SHORT.map((ab) => {
          const score = char.abilities?.[ab] ?? 10;
          return (
            <div key={ab} className="text-center p-1.5 rounded" style={{ background: "rgba(255,255,255,0.015)", border: "1px solid rgba(255,255,255,0.04)" }}>
              <div style={{ color: "rgba(255,255,255,0.25)", fontSize: "11px" }} className="font-medieval">{ab}</div>
              <div className="text-sm font-medieval font-bold leading-tight" style={{ color: "#E6EDF3" }}>{score}</div>
              <div style={{ color: "rgba(194,58,46,0.7)", fontSize: "12px" }}>{mod(score)}</div>
            </div>
          );
        })}
      </div>

      <div className="divider-ornament" />

      {/* Equipment */}
      {char.equipment && char.equipment.length > 0 && (
        <div>
          <h4 className="section-title mb-2">{t("sheet.equipment")}</h4>
          <div className="space-y-0.5">
            {char.equipment.map((item, i) => (
              <div key={i} className="flex items-center gap-2 px-2 py-1 rounded" style={{ fontSize: "13px" }}>
                <span style={{ color: "rgba(255,255,255,0.2)" }}>
                  {item.type === "weapon" ? "\u2694" : item.type === "armor" ? "\u26E8" : "\u25CB"}
                </span>
                <span style={{ color: "rgba(255,255,255,0.5)" }} className="font-body truncate">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Wealth */}
      <div>
        <h4 className="section-title mb-2">{t("sheet.wealth")}</h4>
        <div className="flex gap-3" style={{ fontSize: "13px" }}>
          <span className="flex items-center gap-1">
            <span className="text-gold">&#9733;</span>
            <span className="text-gold font-medieval">{char.gold ?? 0}</span>
            <span style={{ color: "rgba(194,58,46,0.3)" }}>gp</span>
          </span>
          <span className="flex items-center gap-1">
            <span style={{ color: "rgba(255,255,255,0.3)" }}>&#9733;</span>
            <span style={{ color: "rgba(255,255,255,0.4)" }} className="font-medieval">{char.silver ?? 0}</span>
            <span style={{ color: "rgba(255,255,255,0.2)" }}>sp</span>
          </span>
          <span className="flex items-center gap-1">
            <span style={{ color: "rgba(255,96,70,0.3)" }}>&#9733;</span>
            <span style={{ color: "rgba(255,96,70,0.4)" }} className="font-medieval">{char.copper ?? 0}</span>
            <span style={{ color: "rgba(255,96,70,0.2)" }}>cp</span>
          </span>
        </div>
      </div>
    </div>
  );
}
