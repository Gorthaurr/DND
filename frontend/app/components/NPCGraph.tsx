"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { NPCGraphNode, NPCGraphEdge } from "@/lib/types";
import { useT } from "@/lib/i18n";

/* ━━━━━━━━ Layout — circular with jitter ━━━━━━━━ */
function computePositions(nodes: NPCGraphNode[], edges: NPCGraphEdge[], w: number, h: number) {
  const cx = w / 2;
  const cy = h / 2;
  const r = Math.min(w, h) * 0.36;

  // Simple force-directed starting from circle
  const pos: { id: string; x: number; y: number; vx: number; vy: number }[] = nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return { id: n.id, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), vx: 0, vy: 0 };
  });

  const idxMap = new Map<string, number>();
  pos.forEach((p, i) => idxMap.set(p.id, i));

  // Run 80 iterations of force simulation
  for (let iter = 0; iter < 80; iter++) {
    const t = 1 - iter / 80;

    // Repulsion
    for (let i = 0; i < pos.length; i++) {
      for (let j = i + 1; j < pos.length; j++) {
        const dx = pos[j].x - pos[i].x;
        const dy = pos[j].y - pos[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (2500 * t) / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        pos[i].vx -= fx; pos[i].vy -= fy;
        pos[j].vx += fx; pos[j].vy += fy;
      }
    }

    // Spring along edges
    for (const e of edges) {
      const ai = idxMap.get(e.from);
      const bi = idxMap.get(e.to);
      if (ai == null || bi == null) continue;
      const dx = pos[bi].x - pos[ai].x;
      const dy = pos[bi].y - pos[ai].y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = 0.015 * (dist - 120) * t;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      pos[ai].vx += fx; pos[ai].vy += fy;
      pos[bi].vx -= fx; pos[bi].vy -= fy;
    }

    // Gravity
    for (const p of pos) {
      p.vx += (cx - p.x) * 0.008 * t;
      p.vy += (cy - p.y) * 0.008 * t;
      p.vx *= 0.8; p.vy *= 0.8;
      p.x += p.vx; p.y += p.vy;
      p.x = Math.max(50, Math.min(w - 50, p.x));
      p.y = Math.max(50, Math.min(h - 50, p.y));
    }
  }

  const result = new Map<string, { x: number; y: number }>();
  for (const p of pos) result.set(p.id, { x: p.x, y: p.y });
  return result;
}

/* ━━━━━━━━ Component ━━━━━━━━ */
export function NPCGraph() {
  const t = useT();
  const [nodes, setNodes] = useState<NPCGraphNode[]>([]);
  const [edges, setEdges] = useState<NPCGraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<NPCGraphNode | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  const W = 1200;
  const H = 900;

  useEffect(() => {
    api.npcGraph().then((data) => {
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const positions = useMemo(
    () => (nodes.length > 0 ? computePositions(nodes, edges, W, H) : new Map()),
    [nodes, edges]
  );

  const knownCount = useMemo(() => nodes.filter((n) => n.known).length, [nodes]);

  const selectedEdges = useMemo(() => {
    if (!selected) return [];
    return edges.filter((e) => e.from === selected.id || e.to === selected.id);
  }, [selected, edges]);

  const nodeById = useMemo(() => {
    const m = new Map<string, NPCGraphNode>();
    for (const n of nodes) m.set(n.id, n);
    return m;
  }, [nodes]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 rounded-full animate-spin mx-auto mb-4" style={{ borderColor: "rgba(194,58,46,0.15)", borderTopColor: "rgba(194,58,46,0.6)" }} />
          <p className="font-medieval text-sm" style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.loading" as any)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex overflow-hidden min-w-0">
      {/* Graph area */}
      <div className="flex-1 flex flex-col min-h-0 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 flex-shrink-0" style={{ borderBottom: "1px solid rgba(194,58,46,0.08)" }}>
          <div className="min-w-0">
            <h2 className="text-lg tracking-wider truncate" style={{ color: "rgba(194,58,46,0.8)" }}>{t("graph.title" as any)}</h2>
            <p className="text-xs" style={{ color: "rgba(194,58,46,0.3)" }}>{t("graph.subtitle" as any)}</p>
          </div>
          <div className="flex items-center gap-4 text-xs" style={{ color: "rgba(194,58,46,0.4)" }}>
            <span>{t("graph.knownCount" as any)}: <b style={{ color: "rgba(194,58,46,0.8)" }}>{knownCount}</b>/{nodes.length}</span>
            <span>{t("graph.relations" as any)}: <b style={{ color: "rgba(194,58,46,0.8)" }}>{edges.length}</b></span>
          </div>
        </div>

        {/* SVG */}
        <div className="flex-1 relative min-h-0 overflow-auto">
          <svg viewBox={`0 0 ${W} ${H}`} style={{ background: "transparent", width: W, height: H, minWidth: W, minHeight: H }}>
            <defs>
              <filter id="npc-glow">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <radialGradient id="node-glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="rgba(194,58,46,1)" stopOpacity="0.3" />
                <stop offset="100%" stopColor="rgba(194,58,46,1)" stopOpacity="0" />
              </radialGradient>
            </defs>

            {/* Edges — gold only, positive = brighter, negative = dimmer */}
            {edges.map((e, i) => {
              const from = positions.get(e.from);
              const to = positions.get(e.to);
              if (!from || !to) return null;
              const isHighlighted = selected && (e.from === selected.id || e.to === selected.id);
              const color = !e.visible
                ? "rgba(194,58,46,0.05)"
                : e.sentiment > 0.3
                  ? "rgba(194,58,46,0.4)"
                  : e.sentiment < -0.3
                    ? "rgba(194,58,46,0.15)"
                    : "rgba(194,58,46,0.25)";
              const opacity = isHighlighted ? 0.8 : e.visible ? 0.2 + Math.abs(e.sentiment) * 0.3 : 0.08;
              const width = isHighlighted ? 2 + Math.abs(e.sentiment) * 2 : e.visible ? 1 + Math.abs(e.sentiment) : 0.5;
              return (
                <line
                  key={i}
                  x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                  stroke={color} strokeWidth={width} opacity={opacity}
                  strokeDasharray={e.visible ? undefined : "4,4"}
                />
              );
            })}

            {/* Nodes — gold tones, known vs unknown = opacity difference */}
            {nodes.map((node) => {
              const pos = positions.get(node.id);
              if (!pos) return null;
              const isKnown = node.known;
              const isHov = hovered === node.id;
              const isSel = selected?.id === node.id;
              const radius = isKnown ? 22 : 15;
              const strokeColor = isKnown ? "rgba(194,58,46,0.6)" : "rgba(194,58,46,0.15)";

              return (
                <g
                  key={node.id}
                  style={{ cursor: "pointer" }}
                  onMouseEnter={() => setHovered(node.id)}
                  onMouseLeave={() => setHovered(null)}
                  onClick={() => setSelected(isKnown ? node : null)}
                >
                  {/* Selection glow */}
                  {isSel && <circle cx={pos.x} cy={pos.y} r={radius + 12} fill="url(#node-glow)" />}

                  {/* Hover glow */}
                  {isHov && !isSel && (
                    <circle cx={pos.x} cy={pos.y} r={radius + 6} fill="none" stroke="rgba(194,58,46,0.3)" strokeWidth="1" opacity="0.3" />
                  )}

                  {/* Node circle */}
                  <circle
                    cx={pos.x} cy={pos.y} r={radius}
                    fill={isKnown ? "#13171C" : "#0D1117"}
                    stroke={strokeColor}
                    strokeWidth={isSel ? 3 : isKnown ? 2 : 1}
                    strokeDasharray={isKnown ? undefined : "3,3"}
                    filter={isSel ? "url(#npc-glow)" : undefined}
                  />

                  {/* Inner content */}
                  {isKnown ? (
                    <text
                      x={pos.x} y={pos.y + 1}
                      textAnchor="middle" dominantBaseline="middle"
                      fill="rgba(230,237,243,0.8)" fontSize="10"
                      fontFamily="Cinzel, serif" fontWeight="bold"
                    >
                      {node.name.split(" ")[0].slice(0, 5)}
                    </text>
                  ) : (
                    <text
                      x={pos.x} y={pos.y + 1}
                      textAnchor="middle" dominantBaseline="middle"
                      fill="rgba(194,58,46,0.2)" fontSize="14" fontWeight="bold"
                    >
                      ?
                    </text>
                  )}

                  {/* Name label below */}
                  <text
                    x={pos.x} y={pos.y + radius + 14}
                    textAnchor="middle"
                    fill={isKnown ? "rgba(194,58,46,0.6)" : "rgba(194,58,46,0.15)"}
                    fontSize="10"
                    fontFamily="Cinzel, serif"
                  >
                    {isKnown ? node.name : "???"}
                  </text>

                  {/* Level badge for known NPCs */}
                  {isKnown && node.level != null && (
                    <g>
                      <circle cx={pos.x + radius - 2} cy={pos.y - radius + 2} r="7" fill="#13171C" stroke="rgba(194,58,46,0.4)" strokeWidth="1" />
                      <text x={pos.x + radius - 2} y={pos.y - radius + 5} textAnchor="middle" fill="rgba(194,58,46,0.7)" fontSize="8" fontWeight="bold">
                        {node.level}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Legend — gold only */}
          <div className="absolute bottom-3 left-3 flex items-center gap-4 px-3 py-2 rounded" style={{ background: "rgba(0,0,0,0.7)", border: "1px solid rgba(194,58,46,0.08)" }}>
            <span className="text-xs uppercase" style={{ color: "rgba(194,58,46,0.25)", letterSpacing: "0.1em", fontFamily: "Cinzel" }}>{t("graph.legend" as any)}</span>
            <span className="flex items-center gap-1 text-xs"><span className="w-4 h-0.5 inline-block rounded" style={{ background: "rgba(194,58,46,0.4)" }} /><span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.positive" as any)}</span></span>
            <span className="flex items-center gap-1 text-xs"><span className="w-4 h-0.5 inline-block rounded" style={{ background: "rgba(194,58,46,0.15)" }} /><span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.negative" as any)}</span></span>
            <span className="flex items-center gap-1 text-xs"><span className="w-3 h-3 rounded-full inline-block" style={{ border: "2px solid rgba(194,58,46,0.6)", background: "#13171C" }} /><span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.knownCount" as any)}</span></span>
            <span className="flex items-center gap-1 text-xs"><span className="w-3 h-3 rounded-full inline-block" style={{ border: "1px dashed rgba(194,58,46,0.15)", background: "#0D1117" }} /><span style={{ color: "rgba(194,58,46,0.4)" }}>???</span></span>
          </div>
        </div>
      </div>

      {/* Detail panel */}
      {selected && (
        <div className="w-72 shrink-0 overflow-y-auto" style={{ borderLeft: "1px solid rgba(194,58,46,0.08)", background: "rgba(22,27,34,0.9)" }}>
          <div className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medieval text-base tracking-wide" style={{ color: "rgba(194,58,46,0.8)" }}>{selected.name}</h3>
              <button onClick={() => setSelected(null)} className="p-1" style={{ color: "rgba(194,58,46,0.3)" }}>&#10005;</button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.occupation" as any)}</span>
                <span style={{ color: "rgba(230,237,243,0.7)" }}>{selected.occupation}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.mood" as any)}</span>
                <span style={{ color: "rgba(194,58,46,0.6)" }}>{selected.mood}</span>
              </div>
              {selected.level != null && (
                <div className="flex justify-between">
                  <span style={{ color: "rgba(194,58,46,0.4)" }}>{t("graph.level" as any)}</span>
                  <span style={{ color: "rgba(230,237,243,0.7)" }}>{selected.level}</span>
                </div>
              )}
              {selected.archetype && (
                <div className="flex justify-between">
                  <span style={{ color: "rgba(194,58,46,0.4)" }}>Archetype</span>
                  <span style={{ color: "rgba(230,237,243,0.7)" }}>{selected.archetype}</span>
                </div>
              )}
            </div>

            {/* Relationships */}
            {selectedEdges.length > 0 && (
              <div className="mt-5">
                <div className="divider-ornament mb-3" />
                <h4 className="text-xs font-bold uppercase mb-3" style={{ color: "rgba(194,58,46,0.3)", letterSpacing: "0.15em" }}>
                  {t("graph.relations" as any)}
                </h4>
                <div className="space-y-1.5">
                  {selectedEdges.map((e, i) => {
                    const otherId = e.from === selected.id ? e.to : e.from;
                    const other = nodeById.get(otherId);
                    if (!other) return null;
                    return (
                      <div key={i} className="flex items-center justify-between text-xs px-2 py-1.5 rounded" style={{ background: "rgba(194,58,46,0.02)" }}>
                        <span style={{ color: other.known ? "rgba(230,237,243,0.7)" : "rgba(194,58,46,0.2)" }}>{other.known ? other.name : "???"}</span>
                        {e.visible && (
                          <span className="font-mono" style={{ color: e.sentiment > 0 ? "rgba(194,58,46,0.7)" : "rgba(194,58,46,0.35)" }}>
                            {e.sentiment > 0 ? "+" : ""}{e.sentiment.toFixed(1)}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
