"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { DiamondDivider } from "./ui/Ornament";
import { EventIcon } from "./ui/EventIcons";

interface Props {
  entries: any[];
}

const tensionOpacity: Record<string, number> = {
  low: 0.4,
  rising: 0.6,
  climax: 0.9,
  resolution: 0.5,
  high: 0.8,
  medium: 0.6,
};

function ScenarioBanner({ scenarios }: { scenarios: any[] }) {
  if (!scenarios || scenarios.length === 0) return null;
  return (
    <div className="mb-4 space-y-2">
      {scenarios.map((sc: any, i: number) => {
        const opacity = tensionOpacity[sc.tension_level] || 0.4;
        return (
          <div
            key={i}
            className="p-3 rounded-lg"
            style={{
              border: `1px solid rgba(194, 58, 46, ${opacity * 0.4})`,
              background: `rgba(194, 58, 46, ${opacity * 0.04})`,
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <span
                className="text-xs font-bold uppercase tracking-widest"
                style={{ color: `rgba(194, 58, 46, ${opacity * 0.7})` }}
              >
                {sc.tension_level}
              </span>
              <span
                className="font-medieval text-sm font-bold"
                style={{ color: `rgba(194, 58, 46, ${opacity})` }}
              >
                {sc.title}
              </span>
            </div>
            <p className="text-xs font-body" style={{ color: "rgba(230,237,243,0.5)" }}>
              {sc.narrative_update || sc.description}
            </p>
            <p className="text-xs font-body mt-1" style={{ color: "rgba(230,237,243,0.3)" }}>
              Phase: {sc.phase_name}
            </p>
          </div>
        );
      })}
    </div>
  );
}

function EventTag({ type }: { type: string }) {
  return (
    <span
      className="badge border inline-flex items-center"
      style={{
        background: "rgba(194,58,46,0.08)",
        color: "rgba(194,58,46,0.6)",
        border: "1px solid rgba(194,58,46,0.15)",
      }}
    >
      <EventIcon type={type} size={12} className="mr-1 inline-block" />
      {type || "event"}
    </span>
  );
}

export function WorldLog({ entries: initialEntries }: Props) {
  const t = useT();
  const [entries, setEntries] = useState(initialEntries);

  useEffect(() => {
    api
      .worldLog()
      .then((data) => setEntries(data.entries))
      .catch(console.error);
  }, []);

  if (entries.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center animate-fade-in">
        <div className="text-center">
          <div className="mb-4 opacity-20">
            <svg viewBox="0 0 40 40" width="48" height="48">
              <rect x="8" y="4" width="24" height="32" rx="2" fill="none" stroke="rgba(194,58,46,0.6)" strokeWidth="1.5"/>
              <line x1="13" y1="12" x2="27" y2="12" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
              <line x1="13" y1="18" x2="27" y2="18" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
              <line x1="13" y1="24" x2="22" y2="24" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
            </svg>
          </div>
          <h3 className="font-medieval text-lg mb-2" style={{ color: "rgba(194,58,46,0.5)" }}>
            {t("log.quiet")}
          </h3>
          <p className="text-sm font-body max-w-xs" style={{ color: "rgba(230,237,243,0.25)" }}>
            {t("log.quietDesc")}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 animate-fade-in relative">
      {/* Dungeon background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-[0.05]"
          style={{ backgroundImage: "url(/images/dungeon.jpg)" }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0D1117] via-transparent to-[#0D1117]" />
      </div>

      {/* Title */}
      <div className="mb-6 relative z-10">
        <h2 className="font-medieval text-xl tracking-wider" style={{ color: "rgba(194,58,46,0.7)" }}>
          {t("log.title")}
        </h2>
        <p className="text-xs font-body mt-1" style={{ color: "rgba(230,237,243,0.3)" }}>
          {t("log.subtitle")}
        </p>
      </div>

      {/* Timeline */}
      <div className="relative z-10">
        {/* Timeline line */}
        <div
          className="absolute left-4 top-0 bottom-0 w-px"
          style={{ background: "linear-gradient(to bottom, rgba(194,58,46,0.2), rgba(194,58,46,0.05), transparent)" }}
        />

        <div className="space-y-4">
          {entries
            .slice()
            .reverse()
            .map((entry, i, arr) => (
              <div key={i} className="relative pl-10 animate-slide-up" style={{ animationDelay: `${i * 0.05}s` }}>
                {/* Timeline dot */}
                <div
                  className="absolute left-2.5 top-4 w-3 h-3 rounded-full"
                  style={{ background: "#0D1117", border: "2px solid rgba(194,58,46,0.3)" }}
                />

                <div className="glass-panel scroll-panel p-4">
                  {/* Day header */}
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medieval text-sm font-bold tracking-wide" style={{ color: "rgba(194,58,46,0.7)" }}>
                      {t("log.day" as any)} {entry.day || "?"}
                    </h3>
                    <span className="text-xs" style={{ color: "rgba(230,237,243,0.2)" }}>
                      {entry.events?.length || 0} {t("log.eventsCount" as any)}
                    </span>
                  </div>

                  {/* Active Scenarios */}
                  <ScenarioBanner scenarios={entry.active_scenarios} />

                  {/* Events */}
                  {entry.events?.length > 0 && (
                    <div className="mb-3">
                      <h4 className="section-title mb-2">{t("log.events")}</h4>
                      <div className="space-y-2">
                        {entry.events.map((e: any, j: number) => (
                          <div key={j} className="flex items-start gap-2">
                            <EventTag type={e.type} />
                            <p className="text-sm font-body leading-relaxed" style={{ color: "rgba(230,237,243,0.55)" }}>
                              {e.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* NPC Actions */}
                  {entry.npc_actions?.length > 0 && (
                    <div className="mb-3">
                      <h4 className="section-title mb-2">{t("log.npcActions")}</h4>
                      <div className="space-y-1.5">
                        {entry.npc_actions.slice(0, 5).map((a: any, j: number) => (
                          <div key={j} className="flex items-baseline gap-2 text-xs font-body">
                            <span className="font-medieval font-semibold whitespace-nowrap" style={{ color: "rgba(194,58,46,0.5)" }}>
                              {a.npc_name}
                            </span>
                            <span style={{ color: "rgba(230,237,243,0.4)" }}>
                              {a.action}
                              {a.target && (
                                <span style={{ color: "rgba(230,237,243,0.25)" }}>
                                  {" \u2192 "}{a.target}
                                </span>
                              )}
                            </span>
                          </div>
                        ))}
                        {entry.npc_actions.length > 5 && (
                          <p className="text-xs" style={{ color: "rgba(230,237,243,0.2)" }}>
                            ...{entry.npc_actions.length - 5} {t("log.moreActions" as any)}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Interactions */}
                  {entry.interactions?.length > 0 && (
                    <div>
                      <h4 className="section-title mb-2">{t("log.interactions")}</h4>
                      <div className="space-y-1.5">
                        {entry.interactions.map((inter: any, j: number) => (
                          <p
                            key={j}
                            className="text-xs font-body pl-3"
                            style={{
                              color: "rgba(230,237,243,0.4)",
                              borderLeft: "1px solid rgba(194,58,46,0.15)",
                            }}
                          >
                            {inter.summary?.slice(0, 150)}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {i < arr.length - 1 && <DiamondDivider className="my-3" />}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
