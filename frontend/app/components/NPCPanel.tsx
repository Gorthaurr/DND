"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import type { NPC, NPCFull } from "@/lib/types";
import { NPCPortrait } from "./ui/NPCPortrait";

interface Props {
  npcs: NPC[];
}

function SentimentBar({ value, name }: { value: number; name: string }) {
  const isPositive = value >= 0;
  const width = Math.abs(value) * 50;

  return (
    <div className="flex items-center gap-3 group">
      <span className="text-sm font-body w-24 truncate" style={{ color: "rgba(230,237,243,0.7)" }}>
        {name}
      </span>
      <div className="flex-1 h-1.5 bg-surface-overlay/50 rounded-full overflow-hidden relative">
        <div className="absolute inset-0 flex">
          {/* Center line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-parchment/10" />
        </div>
        <div
          className="absolute top-0 bottom-0 rounded-full transition-all duration-500"
          style={{
            left: isPositive ? "50%" : `${50 - width}%`,
            width: `${width}%`,
            background: isPositive
              ? "rgba(194,58,46,0.5)"
              : "rgba(194,58,46,0.2)",
          }}
        />
      </div>
      <span
        className="text-xs font-mono w-10 text-right"
        style={{ color: isPositive ? "rgba(194,58,46,0.7)" : "rgba(194,58,46,0.4)" }}
      >
        {isPositive ? "+" : ""}
        {value.toFixed(1)}
      </span>
    </div>
  );
}

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="animate-fade-in">
      <h4 className="section-title mb-2">{title}</h4>
      {children}
    </div>
  );
}

export function NPCPanel({ npcs }: Props) {
  const t = useT();
  const [selected, setSelected] = useState<NPCFull | null>(null);
  const [loading, setLoading] = useState(false);

  const loadNpc = async (id: string) => {
    setLoading(true);
    try {
      const data = await api.npcObserve(id);
      setSelected(data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* NPC list sidebar */}
      <div className="w-56 border-r border-light-wood/8 overflow-y-auto bg-surface-raised/30">
        <div className="p-4">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-6 h-6 rounded flex items-center justify-center text-xs" style={{ background: "rgba(194,58,46,0.1)", color: "rgba(194,58,46,0.5)" }}>
              &#128065;
            </span>
            <h3 className="font-medieval text-gold text-sm font-bold tracking-wide">
              {t("observer.title")}
            </h3>
          </div>
          <p className="text-parchment/25 text-xs font-body mb-4">
            {t("observer.desc")}
          </p>

          {npcs.length === 0 && (
            <p className="text-parchment/30 text-xs font-body text-center py-8">
              {t("observer.noNpcs" as any)}
            </p>
          )}

          <div className="space-y-1">
            {npcs.map((npc) => (
              <button
                key={npc.id}
                onClick={() => loadNpc(npc.id)}
                className={`npc-card npc-card-hover block w-full text-left px-3 py-2.5 rounded-lg transition-all ${
                  selected?.id === npc.id ? "selected" : ""
                }`}
                style={{
                  background: selected?.id === npc.id ? "rgba(194,58,46,0.04)" : undefined,
                }}
                onMouseEnter={(e) => {
                  if (selected?.id !== npc.id)
                    (e.currentTarget as HTMLElement).style.background = "rgba(194,58,46,0.04)";
                }}
                onMouseLeave={(e) => {
                  if (selected?.id !== npc.id)
                    (e.currentTarget as HTMLElement).style.background = "";
                }}
              >
                <div className="flex items-center gap-2">
                  <NPCPortrait name={npc.name} occupation={npc.occupation} mood={npc.mood} size={32} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medieval text-sm truncate" style={{ color: "rgba(194,58,46,0.8)" }}>
                        {npc.name}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-0.5">
                      <span className="text-xs" style={{ color: "rgba(230,237,243,0.3)", fontSize: "12px" }}>
                        {npc.occupation}
                      </span>
                      <span className="text-xs" style={{ color: "rgba(230,237,243,0.4)" }}>
                        {npc.mood}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* NPC Details */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="animate-pulse text-center">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3" style={{ background: "rgba(194,58,46,0.1)" }}>
                <span className="text-xl" style={{ color: "rgba(194,58,46,0.4)" }}>&#128065;</span>
              </div>
              <p className="text-parchment/30 text-sm font-body">
                {t("observer.reading")}
              </p>
            </div>
          </div>
        )}

        {!loading && !selected && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center animate-fade-in">
              <div className="w-16 h-16 rounded-2xl bg-surface-overlay/50 flex items-center justify-center mx-auto mb-4 border border-light-wood/5">
                <span className="text-3xl opacity-20">&#128065;</span>
              </div>
              <p className="text-parchment/25 text-sm font-body max-w-xs">
                {t("observer.selectDesc" as any)}
              </p>
            </div>
          </div>
        )}

        {!loading && selected && (
          <div className="p-6 space-y-5 animate-slide-up">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <NPCPortrait name={selected.name} occupation={selected.occupation} mood={selected.mood} size={48} />
                <div>
                  <h2 className="font-medieval text-gold text-xl font-bold tracking-wide text-shadow-sm">
                    {selected.name}
                  </h2>
                  <p className="text-parchment/40 text-sm font-body mt-0.5">
                    {selected.age}-year-old {selected.occupation}
                  </p>
                </div>
              </div>
              <span className="text-xs" style={{ color: "rgba(230,237,243,0.4)" }}>{selected.mood}</span>
            </div>

            <div className="divider-ornament" />

            <DetailSection title={t("observer.personality")}>
              <p className="text-parchment/70 text-sm font-body leading-relaxed">
                {typeof selected.personality === "object"
                  ? Object.entries(selected.personality).map(([k, v]) => `${k}: ${v}`).join(", ")
                  : selected.personality}
              </p>
            </DetailSection>

            <DetailSection title={t("observer.backstory")}>
              <p className="text-parchment/60 text-sm font-body leading-relaxed">
                {selected.backstory}
              </p>
            </DetailSection>

            <DetailSection title={t("observer.goals")}>
              <ul className="space-y-1.5">
                {selected.goals.map((g, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm font-body text-parchment/70">
                    <span className="text-gold/40 mt-0.5">&#9670;</span>
                    <span>{g}</span>
                  </li>
                ))}
              </ul>
            </DetailSection>

            {selected.relationships.length > 0 && (
              <DetailSection title={t("observer.relationships")}>
                <div className="space-y-2.5">
                  {selected.relationships.map((r, i) => (
                    <SentimentBar key={i} value={r.sentiment} name={r.name} />
                  ))}
                </div>
              </DetailSection>
            )}

            {selected.recent_memories.length > 0 && (
              <DetailSection title={t("observer.memories")}>
                <div className="space-y-2 pl-3 border-l border-light-wood/10">
                  {selected.recent_memories.map((m, i) => (
                    <p
                      key={i}
                      className="text-parchment/45 text-xs font-body leading-relaxed"
                    >
                      {m}
                    </p>
                  ))}
                </div>
              </DetailSection>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
