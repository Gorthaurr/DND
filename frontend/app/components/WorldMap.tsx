"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import type { WorldMap } from "@/lib/types";

const LAYOUT: Record<string, { x: number; y: number }> = {
  "loc-square": { x: 300, y: 250 },
  "loc-tavern": { x: 150, y: 140 },
  "loc-market": { x: 460, y: 140 },
  "loc-smithy": { x: 510, y: 310 },
  "loc-chapel": { x: 140, y: 360 },
  "loc-forest": { x: 450, y: 430 },
  "loc-farm": { x: 100, y: 460 },
};

const TYPE_ICONS: Record<string, { opacity: number; icon: string }> = {
  tavern: { opacity: 0.7, icon: "🍺" },
  market: { opacity: 0.6, icon: "🏪" },
  smithy: { opacity: 0.8, icon: "⚒" },
  square: { opacity: 0.9, icon: "🏛" },
  forest: { opacity: 0.5, icon: "🌲" },
  chapel: { opacity: 0.65, icon: "⛪" },
  farm: { opacity: 0.55, icon: "🌾" },
};

interface Props {
  data: WorldMap | null;
}

export function WorldMapView({ data: initialData }: Props) {
  const t = useT();
  const [data, setData] = useState<WorldMap | null>(initialData);
  const [hoveredLoc, setHoveredLoc] = useState<string | null>(null);
  const [selectedLoc, setSelectedLoc] = useState<any>(null);

  useEffect(() => {
    if (!data) {
      api.worldMap().then(setData).catch(console.error);
    }
  }, [data]);

  if (!data) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="w-12 h-12 rounded-xl bg-gold/10 flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl text-gold/40">🗺</span>
          </div>
          <p className="text-parchment/30 font-body text-sm">
            {t("map.loading")}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex-1 flex flex-col p-6 animate-fade-in parchment-panel relative"
      style={{
        background: "#0D1117",
      }}
    >
      {/* Map parchment background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-[0.08]"
          style={{ backgroundImage: "url(/images/map-bg.jpg)" }}
        />
      </div>
      {/* Title */}
      <div className="text-center mb-4 relative z-10">
        <h2 className="font-medieval text-gold text-xl tracking-wider text-shadow-sm">
          {t("map.title")}
        </h2>
        <p className="text-parchment/30 text-xs font-body mt-1">
          {t("map.subtitle" as any)}
        </p>
      </div>

      {/* Map SVG */}
      <div className="flex-1 flex items-center justify-center relative z-10">
        <svg viewBox="0 0 620 540" className="w-full max-w-3xl">
          {/* Background grid + parchment texture */}
          <defs>
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(28, 33, 40, 0.8)" strokeWidth="0.5" />
            </pattern>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="hoverGlow">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <radialGradient id="playerGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#C23A2E" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#C23A2E" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Parchment background texture */}
          <rect width="620" height="540" fill="url(#grid)" />
          <rect
            width="620"
            height="540"
            fill="transparent"
            style={{
              filter: "url(#grid)",
            }}
          />
          {/* Radial parchment glow */}
          <ellipse cx="310" cy="270" rx="280" ry="240" fill="rgba(194,58,46,0.02)" />

          {/* Compass Rose — gold only */}
          <g transform="translate(560, 40)" opacity="0.15">
            <circle cx="0" cy="0" r="20" fill="none" stroke="rgba(194,58,46,1)" strokeWidth="0.5"/>
            <line x1="0" y1="-18" x2="0" y2="18" stroke="rgba(194,58,46,1)" strokeWidth="0.5"/>
            <line x1="-18" y1="0" x2="18" y2="0" stroke="rgba(194,58,46,1)" strokeWidth="0.5"/>
            <line x1="-13" y1="-13" x2="13" y2="13" stroke="rgba(194,58,46,1)" strokeWidth="0.3"/>
            <line x1="13" y1="-13" x2="-13" y2="13" stroke="rgba(194,58,46,1)" strokeWidth="0.3"/>
            <text x="0" y="-22" textAnchor="middle" fill="rgba(194,58,46,1)" fontSize="8" fontFamily="Cinzel">N</text>
            <text x="0" y="28" textAnchor="middle" fill="rgba(194,58,46,1)" fontSize="8" fontFamily="Cinzel">S</text>
            <text x="24" y="3" textAnchor="middle" fill="rgba(194,58,46,1)" fontSize="8" fontFamily="Cinzel">E</text>
            <text x="-24" y="3" textAnchor="middle" fill="rgba(194,58,46,1)" fontSize="8" fontFamily="Cinzel">W</text>
          </g>

          {/* Connections */}
          {data.connections.map((conn, i) => {
            const from = LAYOUT[conn.from_id];
            const to = LAYOUT[conn.to_id];
            if (!from || !to) return null;
            return (
              <g key={i}>
                <line
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="rgba(194,58,46,0.06)"
                  strokeWidth="6"
                  strokeLinecap="round"
                />
                <line
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="rgba(194,58,46,0.2)"
                  strokeWidth="1.5"
                  strokeDasharray="4,3"
                  strokeLinecap="round"
                  opacity="0.4"
                />
              </g>
            );
          })}

          {/* Locations */}
          {data.locations.map((loc) => {
            const pos = LAYOUT[loc.id];
            if (!pos) return null;
            const isPlayerHere = loc.id === data.player_location_id;
            const isHovered = hoveredLoc === loc.id;
            const typeInfo = TYPE_ICONS[loc.type] || { opacity: 0.5, icon: "📍" };
            const npcCount = Object.values(data.npc_locations).filter(
              (lid) => lid === loc.id
            ).length;
            const goldColor = `rgba(194,58,46,${typeInfo.opacity})`;

            return (
              <g
                key={loc.id}
                onMouseEnter={() => setHoveredLoc(loc.id)}
                onMouseLeave={() => setHoveredLoc(null)}
                onClick={() => setSelectedLoc({ ...loc, npcCount })}
                style={{
                  cursor: "pointer",
                  filter: isHovered ? "drop-shadow(0 0 8px rgba(194,58,46,0.3))" : undefined,
                }}
              >
                {/* Player glow */}
                {isPlayerHere && (
                  <>
                    <circle cx={pos.x} cy={pos.y} r="50" fill="url(#playerGlow)">
                      <animate
                        attributeName="r"
                        values="45;55;45"
                        dur="3s"
                        repeatCount="indefinite"
                      />
                    </circle>
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r="30"
                      fill="none"
                      stroke="rgba(194,58,46,0.5)"
                      strokeWidth="1.5"
                      opacity="0.4"
                    >
                      <animate
                        attributeName="r"
                        values="28;34;28"
                        dur="2s"
                        repeatCount="indefinite"
                      />
                      <animate
                        attributeName="opacity"
                        values="0.4;0.1;0.4"
                        dur="2s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  </>
                )}

                {/* Hover glow */}
                {isHovered && !isPlayerHere && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="30"
                    fill="none"
                    stroke="rgba(194,58,46,0.3)"
                    strokeWidth="1.5"
                    opacity="0.4"
                  />
                )}

                {/* Location base */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="24"
                  fill={isPlayerHere ? "rgba(194,58,46,0.15)" : "#0D1117"}
                  fillOpacity={isPlayerHere ? 1 : 0.8}
                  stroke={isPlayerHere ? "rgba(194,58,46,0.6)" : "rgba(194,58,46,0.3)"}
                  strokeWidth={isPlayerHere ? 2.5 : isHovered ? 2 : 1}
                  opacity={isPlayerHere ? 1 : isHovered ? 1 : 0.7}
                />
                {/* Inner accent ring */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="22"
                  fill="none"
                  stroke={goldColor}
                  strokeWidth="0.5"
                  opacity={isHovered ? 0.5 : 0.15}
                />

                {/* Location icon (emoji) */}
                <text
                  x={pos.x}
                  y={pos.y + 5}
                  fontSize="16"
                  textAnchor="middle"
                  style={{ pointerEvents: "none" }}
                >
                  {typeInfo.icon}
                </text>

                {/* NPC count badge */}
                {npcCount > 0 && (
                  <g>
                    <circle
                      cx={pos.x + 20}
                      cy={pos.y - 18}
                      r="8"
                      fill="#161B22"
                      stroke="rgba(194,58,46,0.4)"
                      strokeWidth="1"
                    />
                    <text
                      x={pos.x + 20}
                      y={pos.y - 14}
                      fill="rgba(194,58,46,0.7)"
                      fontSize="9"
                      textAnchor="middle"
                      fontFamily="Cinzel, serif"
                      fontWeight="bold"
                    >
                      {npcCount}
                    </text>
                  </g>
                )}

                {/* Player marker */}
                {isPlayerHere && (
                  <g filter="url(#glow)">
                    <circle
                      cx={pos.x - 20}
                      cy={pos.y - 18}
                      r="8"
                      fill="#C23A2E"
                    />
                    <text
                      x={pos.x - 20}
                      y={pos.y - 14}
                      fill="#0D1117"
                      fontSize="9"
                      textAnchor="middle"
                      fontWeight="bold"
                    >
                      P
                    </text>
                  </g>
                )}

                {/* Location name */}
                <text
                  x={pos.x}
                  y={pos.y + 42}
                  fill={isPlayerHere ? "#E6EDF3" : "rgba(230,237,243,0.5)"}
                  fontSize="11"
                  textAnchor="middle"
                  fontFamily="Cinzel, serif"
                  fontWeight={isPlayerHere ? "bold" : "normal"}
                >
                  {loc.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {Object.entries(TYPE_ICONS).map(([type, info]) => (
          <div key={type} className="flex items-center gap-1.5 text-2xs text-parchment/40">
            <span className="text-sm">{info.icon}</span>
            <span className="capitalize">{type}</span>
          </div>
        ))}
      </div>

      {/* Selected location info panel */}
      {selectedLoc && (
        <div
          className="parchment-panel p-4 mt-4 mx-4"
          style={{ border: "1px solid rgba(194,58,46,0.2)" }}
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medieval text-gold text-sm font-bold">{selectedLoc.name}</h3>
            <span className="text-2xs" style={{ color: "rgba(194,58,46,0.4)" }}>{selectedLoc.type}</span>
          </div>
          <p className="text-parchment/50 text-xs font-body mb-3">{selectedLoc.description}</p>
          <div className="flex items-center justify-between">
            <span className="text-parchment/30 text-2xs">{selectedLoc.npcCount} NPCs here</span>
            <button
              className="btn-stone text-xs px-4 py-1.5"
              onClick={() => {
                api.action(`go ${selectedLoc.name}`).catch(console.error);
                setSelectedLoc(null);
              }}
            >
              Travel Here
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
