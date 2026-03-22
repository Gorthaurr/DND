"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NPCFull } from "@/lib/types";
import { NPCPortrait } from "./ui/NPCPortrait";
import { SectionDivider } from "./ui/Ornament";

function PersonalityBars({ personality }: { personality: string }) {
  const labels: Record<string, string> = {
    O: "Openness", C: "Conscientiousness", E: "Extraversion", A: "Agreeableness", N: "Neuroticism"
  };
  const values: Record<string, number> = { low: 25, mid: 50, high: 75 };

  const traits = personality.split(",").map(t => t.trim()).map(t => {
    const [key, level] = t.split(":");
    return { key: key?.trim(), label: labels[key?.trim()] || key?.trim(), value: values[level?.trim()] || 50 };
  });

  return (
    <div className="space-y-3">
      {traits.map(t => (
        <div key={t.key}>
          <div className="flex justify-between mb-1">
            <span className="text-xs font-body" style={{ color: "rgba(230,237,243,0.5)" }}>{t.label}</span>
            <span className="text-xs font-body" style={{ color: "rgba(194,58,46,0.5)" }}>{t.value}%</span>
          </div>
          <div className="personality-bar">
            <div className="personality-bar-fill" style={{ width: `${t.value}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ObserverMode() {
  const [npcs, setNpcs] = useState<string[]>([]);
  const [selected, setSelected] = useState<NPCFull | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    api.worldMap().then((map) => {
      setNpcs(Object.keys(map.npc_locations));
    });
  }, []);

  useEffect(() => {
    if (!autoRefresh || !selected) return;
    const interval = setInterval(() => {
      api.npcObserve(selected.id).then(setSelected).catch(console.error);
    }, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh, selected]);

  const observe = async (id: string) => {
    const data = await api.npcObserve(id);
    setSelected(data);
  };

  return (
    <div className="flex-1 p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title text-lg" style={{ color: "rgba(194,58,46,0.7)" }}>Observer Mode</h2>
        <label className="flex items-center gap-2 text-xs" style={{ color: "rgba(230,237,243,0.4)" }}>
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="accent-gold"
          />
          Auto-refresh
        </label>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {npcs.map((id) => (
          <button
            key={id}
            onClick={() => observe(id)}
            className="px-3 py-1 rounded text-xs border transition-colors"
            style={
              selected?.id === id
                ? { background: "rgba(194,58,46,0.12)", borderColor: "rgba(194,58,46,0.4)", color: "rgba(194,58,46,0.8)" }
                : { borderColor: "rgba(194,58,46,0.15)", color: "rgba(230,237,243,0.5)" }
            }
          >
            {id.replace("npc-", "")}
          </button>
        ))}
      </div>

      {!selected && (
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          <div className="mb-8 opacity-40">
            <svg viewBox="0 0 120 120" width="120" height="120">
              <ellipse cx="60" cy="60" rx="40" ry="25" fill="none" stroke="rgba(194,58,46,0.4)" strokeWidth="1.5"/>
              <circle cx="60" cy="60" r="12" fill="none" stroke="rgba(194,58,46,0.5)" strokeWidth="1"/>
              <circle cx="60" cy="60" r="5" fill="rgba(194,58,46,0.3)"/>
              {[0,45,90,135,180,225,270,315].map(angle => (
                <line
                  key={angle}
                  x1={60 + Math.cos(angle * Math.PI / 180) * 45}
                  y1={60 + Math.sin(angle * Math.PI / 180) * 28}
                  x2={60 + Math.cos(angle * Math.PI / 180) * 55}
                  y2={60 + Math.sin(angle * Math.PI / 180) * 35}
                  stroke="rgba(194,58,46,0.2)"
                  strokeWidth="0.5"
                />
              ))}
            </svg>
          </div>
          <h3 className="font-medieval text-xl mb-3 tracking-wider" style={{ color: "rgba(194,58,46,0.5)" }}>The All-Seeing Eye</h3>
          <p className="text-sm font-body max-w-sm text-center mb-8" style={{ color: "rgba(230,237,243,0.3)" }}>
            Select a villager from the list above to observe their thoughts, relationships, and memories.
          </p>

          {npcs.length > 0 && (
            <div className="w-full max-w-md">
              <p className="section-title mb-3 text-center" style={{ fontSize: "10px" }}>Notable Villagers</p>
              <div className="grid grid-cols-4 gap-2">
                {npcs.slice(0, 8).map((id) => {
                  const displayName = id.replace("npc-", "").replace(/-/g, " ");
                  return (
                    <button
                      key={id}
                      onClick={() => observe(id)}
                      className="npc-card-hover hover-lift p-3 rounded-lg text-center"
                      style={{ border: "1px solid rgba(194,58,46,0.08)", background: "rgba(194,58,46,0.02)" }}
                    >
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-1.5"
                        style={{ background: "rgba(194,58,46,0.08)", border: "1px solid rgba(194,58,46,0.15)" }}
                      >
                        <span className="text-xs font-medieval uppercase" style={{ color: "rgba(194,58,46,0.5)" }}>{displayName.charAt(0)}</span>
                      </div>
                      <div className="text-2xs font-medieval truncate capitalize" style={{ color: "rgba(230,237,243,0.4)" }}>{displayName}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {selected && (
        <div
          className="rounded-lg p-5 relative overflow-hidden"
          style={{ border: "1px solid rgba(194,58,46,0.15)", background: "rgba(194,58,46,0.03)" }}
        >
          {/* Dungeon background */}
          <div className="absolute inset-0 z-0 pointer-events-none">
            <div
              className="absolute inset-0 bg-cover bg-center opacity-[0.06]"
              style={{ backgroundImage: "url(/images/dungeon.jpg)" }}
            />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#0D1117]/90" />
          </div>
          {/* Header */}
          <div className="flex items-center gap-3 mb-4 relative z-10">
            <NPCPortrait name={selected.name} occupation={selected.occupation} mood={selected.mood} size={48} />
            <div>
              <h3 className="font-bold text-lg" style={{ color: "rgba(194,58,46,0.8)" }}>
                {selected.name}
                {selected.alive === false && (
                  <span className="text-xs ml-2" style={{ color: "#DA3633" }}>{"\u2620"} DEAD</span>
                )}
              </h3>
              <p className="text-sm" style={{ color: "rgba(230,237,243,0.5)" }}>
                {selected.age}y/o {selected.occupation} |{" "}
                <span style={{ color: "rgba(230,237,243,0.4)" }}>{selected.mood}</span>
              </p>
            </div>
          </div>

          <p className="text-sm mb-4 relative z-10" style={{ color: "rgba(230,237,243,0.5)" }}>
            Location: {selected.location?.name || "unknown"}
          </p>

          <SectionDivider />

          {/* Personality */}
          {(selected as any).personality && (
            <>
              <h4 className="section-title mb-3">Personality</h4>
              <PersonalityBars personality={(selected as any).personality} />
              <SectionDivider />
            </>
          )}

          {/* Backstory */}
          <h4 className="section-title mb-3">Backstory</h4>
          <p className="drop-cap text-sm font-body mb-4" style={{ color: "rgba(230,237,243,0.5)", lineHeight: 1.8 }}>
            {selected.backstory}
          </p>

          <SectionDivider />

          {/* Goals & Relationships grid */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="section-title mb-2">Goals</h4>
              <ul className="text-xs space-y-1.5">
                {selected.goals.map((g, i) => (
                  <li key={i} className="flex items-start gap-2" style={{ color: "rgba(230,237,243,0.5)" }}>
                    <span style={{ color: "rgba(194,58,46,0.4)", marginTop: "2px" }}>&#9670;</span>
                    <span>{g}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="section-title mb-2">Relationships</h4>
              <div className="space-y-2.5">
                {selected.relationships.map((r, i) => {
                  const normalized = Math.min(100, Math.max(0, ((r.sentiment + 1) / 2) * 100));
                  return (
                    <div key={i}>
                      <div className="flex justify-between mb-1">
                        <span className="text-xs font-body" style={{ color: "rgba(230,237,243,0.5)" }}>{r.name}</span>
                        <span className="text-xs font-body" style={{ color: "rgba(194,58,46,0.5)" }}>{r.sentiment.toFixed(1)}</span>
                      </div>
                      <div className="relationship-bar">
                        <div className="relationship-bar-fill" style={{ width: `${normalized}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Memories */}
          {selected.recent_memories.length > 0 && (
            <>
              <SectionDivider />
              <h4 className="section-title mb-2">Memories</h4>
              <div className="space-y-1.5">
                {selected.recent_memories.map((m, i) => (
                  <p
                    key={i}
                    className="text-xs pl-3 mb-1 font-body"
                    style={{
                      color: "rgba(230,237,243,0.4)",
                      borderLeft: "1px solid rgba(194,58,46,0.15)",
                    }}
                  >
                    {m}
                  </p>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
