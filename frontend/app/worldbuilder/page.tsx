"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  Plus,
  Pencil,
  Trash2,
  Play,
  MapPin,
  Users,
  Flag,
  Sparkles,
  ArrowLeft,
  X,
  Loader2,
} from "lucide-react";

/* ────────────────────── types ────────────────────── */

interface World {
  id: string;
  name: string;
  description: string;
  npcs?: any[];
  locations?: any[];
  npc_count?: number;
  location_count?: number;
  locations_count?: number;
  npcs_count?: number;
  factions_count?: number;
}

type EditorTab = "locations" | "npcs" | "overview";

/* ────────────────────── helpers ────────────────────── */

function worldLocations(w: World): number {
  return w.locations?.length ?? w.location_count ?? w.locations_count ?? 0;
}
function worldNpcs(w: World): number {
  return w.npcs?.length ?? w.npc_count ?? w.npcs_count ?? 0;
}
function worldFactions(w: World): number {
  return w.factions_count ?? 0;
}

/* ────────────────────── fade variants ────────────────────── */

const fade = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

const stagger = {
  visible: { transition: { staggerChildren: 0.07 } },
};

/* ══════════════════════ PAGE ══════════════════════ */

export default function WorldBuilderPage() {
  const t = useT();

  /* ── state ── */
  const [worlds, setWorlds] = useState<World[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<World | null>(null);
  const [tab, setTab] = useState<EditorTab>("locations");
  const [showCreate, setShowCreate] = useState(false);
  const [createName, setCreateName] = useState("");
  const [createDesc, setCreateDesc] = useState("");
  const [creating, setCreating] = useState(false);

  /* add location */
  const [locName, setLocName] = useState("");
  const [locDesc, setLocDesc] = useState("");
  const [locType, setLocType] = useState("");

  /* add npc */
  const [npcName, setNpcName] = useState("");
  const [npcDesc, setNpcDesc] = useState("");
  const [npcType, setNpcType] = useState("");

  /* ai generate */
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  /* ── data fetching ── */
  const fetchWorlds = useCallback(async () => {
    try {
      const data = await api.listWorlds();
      setWorlds(Array.isArray(data) ? data : data.worlds ?? []);
    } catch {
      /* silent */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorlds();
  }, [fetchWorlds]);

  const refreshSelected = useCallback(async (id: string) => {
    try {
      const w = await api.getWorld(id);
      setSelected(w);
    } catch {
      /* silent */
    }
  }, []);

  /* ── actions ── */
  const handleCreate = async () => {
    if (!createName.trim()) return;
    setCreating(true);
    try {
      await api.createWorld({ name: createName, description: createDesc });
      setCreateName("");
      setCreateDesc("");
      setShowCreate(false);
      await fetchWorlds();
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    await api.deleteWorld(id);
    if (selected?.id === id) setSelected(null);
    await fetchWorlds();
  };

  const handleLoad = async (id: string) => {
    await api.loadWorld(id);
  };

  const handleSelect = async (w: World) => {
    setSelected(w);
    setTab("locations");
    await refreshSelected(w.id);
  };

  const handleAddLocation = async () => {
    if (!selected || !locName.trim()) return;
    await api.addLocation(selected.id, { name: locName, description: locDesc, type: locType });
    setLocName("");
    setLocDesc("");
    setLocType("");
    await refreshSelected(selected.id);
    await fetchWorlds();
  };

  const handleAddNpc = async () => {
    if (!selected || !npcName.trim()) return;
    await api.addNpc(selected.id, { name: npcName, description: npcDesc, type: npcType });
    setNpcName("");
    setNpcDesc("");
    setNpcType("");
    await refreshSelected(selected.id);
    await fetchWorlds();
  };

  const handleAiGenerate = async (kind: "npc" | "location") => {
    if (!selected || !aiPrompt.trim()) return;
    setAiLoading(true);
    try {
      if (kind === "npc") await api.generateNpc(selected.id, aiPrompt);
      else await api.generateLocation(selected.id, aiPrompt);
      setAiPrompt("");
      await refreshSelected(selected.id);
      await fetchWorlds();
    } finally {
      setAiLoading(false);
    }
  };

  /* ── tabs config ── */
  const tabs: { key: EditorTab; label: string }[] = [
    { key: "locations", label: t("worlds.locations") },
    { key: "npcs", label: t("worlds.npcs") },
    { key: "overview", label: t("worlds.overview") },
  ];

  /* ══════════════════════ RENDER ══════════════════════ */

  return (
    <div
      className="min-h-screen overflow-auto"
      style={{
        background: "#0D1117",
      }}
    >
      {/* Ambient gold glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at 50% 120%, rgba(194,58,46,0.06) 0%, transparent 60%)",
        }}
      />

      {/* ── back link ── */}
      <div className="px-6 pt-5 relative z-10">
        <Link href="/" className="ghost-btn inline-flex items-center gap-2 text-xs">
          <ArrowLeft size={14} />
          {t("nav.backToGame")}
        </Link>
      </div>

      {/* ── header ── */}
      <header className="text-center pt-8 pb-6 relative z-10">
        <h1 className="text-4xl md:text-5xl tracking-wider mb-3" style={{ color: "rgba(194,58,46,0.8)" }}>{t("worlds.title")}</h1>
        <div className="accent-line mx-auto mb-3" />
        <p className="text-sm" style={{ color: "rgba(230,237,243,0.5)" }}>
          {t("worlds.subtitle")}
        </p>
      </header>

      <div className="max-w-7xl mx-auto px-6 pb-16 relative z-10">
        {/* ── Create button row ── */}
        <div className="flex items-center justify-center mb-8">
          <button onClick={() => setShowCreate(true)} className="btn-stone flex items-center gap-2 text-sm py-2.5 px-6">
            <Plus size={15} />
            {t("worlds.createNew")}
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-32" style={{ color: "rgba(194,58,46,0.4)" }}>
            <Loader2 size={20} className="animate-spin mr-2" />
            {t("common.loading")}
          </div>
        ) : worlds.length === 0 ? (
          /* ══════════ EMPTY STATE — centered ══════════ */
          <div className="flex flex-col items-center justify-center py-32 text-center" style={{ color: "rgba(194,58,46,0.4)" }}>
            <Globe size={48} className="mb-4 opacity-20" />
            <p className="text-xl mb-2">{t("worlds.noWorlds")}</p>
            <p className="text-sm opacity-70 mb-6">{t("worlds.noWorldsDesc")}</p>
            <button onClick={() => setShowCreate(true)} className="btn-stone flex items-center gap-2">
              <Plus size={14} />
              {t("worlds.createNew")}
            </button>
          </div>
        ) : (
          /* ══════════ WORLDS + EDITOR — sidebar + content ══════════ */
          <div className="flex gap-0">
          {/* ══════════ LEFT: WORLD SIDEBAR ══════════ */}
          <aside
            className="w-[260px] shrink-0 border-r overflow-y-auto"
            style={{ borderColor: "rgba(194,58,46,0.06)", background: "rgba(22,27,34,0.5)", maxHeight: "calc(100vh - 250px)" }}
          >
            {/* Sidebar header */}
            <div
              className="flex items-center justify-between px-4 py-3 sticky top-0 z-10"
              style={{ borderBottom: "1px solid rgba(194,58,46,0.06)", background: "rgba(22,27,34,0.95)" }}
            >
              <span className="text-xs uppercase tracking-widest" style={{ color: "rgba(194,58,46,0.4)", fontFamily: "Cinzel, serif" }}>
                {t("worlds.title")}
              </span>
              <button
                onClick={() => setShowCreate(true)}
                className="p-1.5 rounded transition-colors"
                style={{ color: "rgba(194,58,46,0.4)" }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.8)"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.4)"; }}
                title={t("worlds.createNew")}
              >
                <Plus size={16} />
              </button>
            </div>

            {/* World items */}
            <div className="py-1">
              {worlds.map((w) => (
                <div
                  key={w.id}
                  className="group cursor-pointer px-4 py-3 transition-all duration-150"
                  style={{
                    borderLeft: selected?.id === w.id ? "2px solid rgba(194,58,46,0.6)" : "2px solid transparent",
                    background: selected?.id === w.id ? "rgba(194,58,46,0.04)" : "transparent",
                  }}
                  onClick={() => handleSelect(w)}
                  onMouseEnter={(e) => {
                    if (selected?.id !== w.id) (e.currentTarget as HTMLElement).style.background = "rgba(194,58,46,0.02)";
                  }}
                  onMouseLeave={(e) => {
                    if (selected?.id !== w.id) (e.currentTarget as HTMLElement).style.background = "transparent";
                  }}
                >
                  <div className="flex items-center justify-between">
                    <h3
                      className="text-sm font-semibold break-words"
                      style={{ color: selected?.id === w.id ? "rgba(194,58,46,0.8)" : "rgba(230,237,243,0.6)" }}
                      title={w.name}
                    >
                      {w.name}
                    </h3>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-2">
                      <button
                        className="p-1 rounded transition-colors"
                        style={{ color: "rgba(194,58,46,0.3)" }}
                        onClick={(e) => { e.stopPropagation(); handleLoad(w.id); }}
                        title={t("worlds.load")}
                        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.7)"; }}
                        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.3)"; }}
                      >
                        <Play size={12} />
                      </button>
                      <button
                        className="p-1 rounded transition-colors"
                        style={{ color: "rgba(194,58,46,0.3)" }}
                        onClick={(e) => { e.stopPropagation(); handleDelete(w.id); }}
                        title={t("common.delete")}
                        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.7)"; }}
                        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(194,58,46,0.3)"; }}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                  <div className="flex gap-3 mt-1" style={{ color: "rgba(194,58,46,0.3)", fontSize: "11px" }}>
                    <span className="flex items-center gap-1"><MapPin size={9} />{worldLocations(w)}</span>
                    <span className="flex items-center gap-1"><Users size={9} />{worldNpcs(w)}</span>
                    <span className="flex items-center gap-1"><Flag size={9} />{worldFactions(w)}</span>
                  </div>
                </div>
              ))}
            </div>
          </aside>

        {/* ══════════ RIGHT: EDITOR ══════════ */}
        <section className="flex-1 min-w-0 px-8 py-6">
          {!selected ? (
            <div className="flex flex-col items-center justify-center h-full py-32" style={{ color: "rgba(194,58,46,0.2)" }}>
              <Globe size={32} className="mb-3 opacity-20" />
              <span className="text-sm" style={{ color: "rgba(194,58,46,0.2)" }}>
                {t("worlds.selectWorld" as any)}
              </span>
            </div>
          ) : (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
              {/* editor header */}
              <div className="mb-6">
                <h2 className="text-2xl tracking-wide mb-1" style={{ color: "rgba(194,58,46,0.8)" }}>{selected.name}</h2>
                {selected.description && (
                  <p className="text-sm" style={{ color: "rgba(230,237,243,0.4)" }}>
                    {selected.description}
                  </p>
                )}
              </div>

              {/* tabs — gold underline */}
              <div className="flex gap-6 mb-6" style={{ borderBottom: "1px solid rgba(194,58,46,0.06)" }}>
                {tabs.map((t_item) => (
                  <button
                    key={t_item.key}
                    onClick={() => setTab(t_item.key)}
                    className="relative pb-3 text-sm uppercase tracking-widest transition-colors"
                    style={{
                      fontFamily: "Cinzel, serif",
                      color: tab === t_item.key ? "rgba(194,58,46,0.8)" : "rgba(194,58,46,0.35)",
                    }}
                  >
                    {t_item.label}
                    {tab === t_item.key && (
                      <motion.div
                        layoutId="tab-underline"
                        className="absolute bottom-0 left-0 right-0 h-[2px]"
                        style={{ background: "rgba(194,58,46,0.6)" }}
                      />
                    )}
                  </button>
                ))}
              </div>

              {/* tab content */}
              <AnimatePresence mode="wait">
                {tab === "locations" && (
                  <motion.div key="locations" variants={fade} initial="hidden" animate="visible" exit="exit">
                    {/* existing locations */}
                    <div className="mb-6">
                      {(selected.locations ?? []).length > 0 ? (
                        <div className="flex flex-col gap-2">
                          {(selected.locations ?? []).map((loc: any, i: number) => (
                            <div key={loc.id ?? i} className="game-card p-3 flex items-center gap-3">
                              <MapPin size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                              <div className="flex-1 min-w-0">
                                <span className="text-sm font-semibold" style={{ color: "rgba(230,237,243,0.7)" }}>{loc.name}</span>
                                {loc.type && (
                                  <span className="ml-2 text-xs" style={{ color: "rgba(194,58,46,0.35)" }}>
                                    {loc.type}
                                  </span>
                                )}
                                {loc.description && (
                                  <p className="text-xs mt-0.5 line-clamp-1" style={{ color: "rgba(230,237,243,0.35)" }}>
                                    {loc.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm py-4" style={{ color: "rgba(194,58,46,0.3)" }}>
                          {t("worlds.noLocations" as any)}
                        </p>
                      )}
                    </div>

                    {/* add location form */}
                    <div className="glass-panel p-4">
                      <span className="section-title mb-3 block">{t("worlds.addLocation")}</span>
                      <div className="flex flex-col gap-3">
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.name")}
                          value={locName}
                          onChange={(e) => setLocName(e.target.value)}
                        />
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.type")}
                          value={locType}
                          onChange={(e) => setLocType(e.target.value)}
                        />
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.description")}
                          value={locDesc}
                          onChange={(e) => setLocDesc(e.target.value)}
                        />
                        <button className="btn-stone self-start" onClick={handleAddLocation}>
                          {t("common.create")}
                        </button>
                      </div>
                    </div>

                    {/* ai generate location */}
                    <div className="glass-panel p-4 mt-4">
                      <span className="section-title mb-3 flex items-center gap-2">
                        <Sparkles size={13} style={{ color: "rgba(194,58,46,0.6)" }} />
                        {t("worlds.aiGenerate")}
                      </span>
                      <textarea
                        className="input-fantasy input-scroll min-h-[80px] resize-none"
                        placeholder={t("worlds.aiPrompt")}
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                      />
                      <button
                        className="btn-stone mt-3 flex items-center gap-2"
                        disabled={aiLoading}
                        onClick={() => handleAiGenerate("location")}
                      >
                        {aiLoading && <Loader2 size={13} className="animate-spin" />}
                        {t("worlds.aiGenerate")}
                      </button>
                    </div>
                  </motion.div>
                )}

                {tab === "npcs" && (
                  <motion.div key="npcs" variants={fade} initial="hidden" animate="visible" exit="exit">
                    {/* existing npcs */}
                    <div className="mb-6">
                      {(selected.npcs ?? []).length > 0 ? (
                        <div className="flex flex-col gap-2">
                          {(selected.npcs ?? []).map((npc: any, i: number) => (
                            <div key={npc.id ?? i} className="game-card p-3 flex items-center gap-3">
                              <Users size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                              <div className="flex-1 min-w-0">
                                <span className="text-sm font-semibold" style={{ color: "rgba(230,237,243,0.7)" }}>{npc.name}</span>
                                {npc.type && (
                                  <span className="ml-2 text-xs" style={{ color: "rgba(194,58,46,0.35)" }}>
                                    {npc.type}
                                  </span>
                                )}
                                {npc.description && (
                                  <p className="text-xs mt-0.5 line-clamp-1" style={{ color: "rgba(230,237,243,0.35)" }}>
                                    {npc.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm py-4" style={{ color: "rgba(194,58,46,0.3)" }}>
                          {t("worlds.noNpcs" as any)}
                        </p>
                      )}
                    </div>

                    {/* add npc form */}
                    <div className="glass-panel p-4">
                      <span className="section-title mb-3 block">{t("worlds.addNpc")}</span>
                      <div className="flex flex-col gap-3">
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.name")}
                          value={npcName}
                          onChange={(e) => setNpcName(e.target.value)}
                        />
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.type")}
                          value={npcType}
                          onChange={(e) => setNpcType(e.target.value)}
                        />
                        <input
                          className="input-fantasy input-scroll"
                          placeholder={t("common.description")}
                          value={npcDesc}
                          onChange={(e) => setNpcDesc(e.target.value)}
                        />
                        <button className="btn-stone self-start" onClick={handleAddNpc}>
                          {t("common.create")}
                        </button>
                      </div>
                    </div>

                    {/* ai generate npc */}
                    <div className="glass-panel p-4 mt-4">
                      <span className="section-title mb-3 flex items-center gap-2">
                        <Sparkles size={13} style={{ color: "rgba(194,58,46,0.6)" }} />
                        {t("worlds.aiGenerate")}
                      </span>
                      <textarea
                        className="input-fantasy input-scroll min-h-[80px] resize-none"
                        placeholder={t("worlds.aiPrompt")}
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                      />
                      <button
                        className="btn-stone mt-3 flex items-center gap-2"
                        disabled={aiLoading}
                        onClick={() => handleAiGenerate("npc")}
                      >
                        {aiLoading && <Loader2 size={13} className="animate-spin" />}
                        {t("worlds.aiGenerate")}
                      </button>
                    </div>
                  </motion.div>
                )}

                {tab === "overview" && (
                  <motion.div key="overview" variants={fade} initial="hidden" animate="visible" exit="exit">
                    <div className="glass-panel p-5">
                      <div className="mb-4">
                        <span className="section-title block mb-1">{t("worlds.worldName")}</span>
                        <p className="text-lg" style={{ color: "rgba(194,58,46,0.8)" }}>{selected.name}</p>
                      </div>
                      {selected.description && (
                        <div className="mb-4">
                          <span className="section-title block mb-1">{t("common.description")}</span>
                          <p className="text-sm" style={{ color: "rgba(230,237,243,0.5)" }}>
                            {selected.description}
                          </p>
                        </div>
                      )}
                      <div className="divider-ornament" />
                      <div className="grid grid-cols-3 gap-4 mt-4">
                        <div className="text-center">
                          <MapPin size={18} className="mx-auto mb-1" style={{ color: "rgba(194,58,46,0.5)" }} />
                          <p className="text-2xl font-bold" style={{ color: "rgba(194,58,46,0.8)" }}>{worldLocations(selected)}</p>
                          <p className="text-xs" style={{ color: "rgba(194,58,46,0.35)" }}>
                            {t("worlds.locations")}
                          </p>
                        </div>
                        <div className="text-center">
                          <Users size={18} className="mx-auto mb-1" style={{ color: "rgba(194,58,46,0.5)" }} />
                          <p className="text-2xl font-bold" style={{ color: "rgba(194,58,46,0.8)" }}>{worldNpcs(selected)}</p>
                          <p className="text-xs" style={{ color: "rgba(194,58,46,0.35)" }}>
                            {t("worlds.npcs")}
                          </p>
                        </div>
                        <div className="text-center">
                          <Flag size={18} className="mx-auto mb-1" style={{ color: "rgba(194,58,46,0.5)" }} />
                          <p className="text-2xl font-bold" style={{ color: "rgba(194,58,46,0.8)" }}>{worldFactions(selected)}</p>
                          <p className="text-xs" style={{ color: "rgba(194,58,46,0.35)" }}>
                            {t("worlds.factions")}
                          </p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </section>
        </div>
        )}
      </div>

      {/* ══════════ CREATE MODAL ══════════ */}
      <AnimatePresence>
        {showCreate && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* backdrop */}
            <div
              className="absolute inset-0"
              style={{ background: "rgba(0,0,0,0.8)" }}
              onClick={() => setShowCreate(false)}
            />

            {/* panel */}
            <motion.div
              className="glass-panel relative z-10 w-full max-w-md p-6"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg tracking-wide" style={{ color: "rgba(194,58,46,0.8)" }}>{t("worlds.createNew")}</h3>
                <button
                  className="p-1"
                  style={{ color: "rgba(194,58,46,0.4)" }}
                  onClick={() => setShowCreate(false)}
                >
                  <X size={18} />
                </button>
              </div>

              <div className="flex flex-col gap-4">
                <div>
                  <label className="section-title block mb-1.5">{t("worlds.worldName")}</label>
                  <input
                    className="input-fantasy input-scroll"
                    placeholder={t("common.name")}
                    value={createName}
                    onChange={(e) => setCreateName(e.target.value)}
                    autoFocus
                  />
                </div>
                <div>
                  <label className="section-title block mb-1.5">{t("common.description")}</label>
                  <textarea
                    className="input-fantasy input-scroll min-h-[80px] resize-none"
                    placeholder={t("common.description")}
                    value={createDesc}
                    onChange={(e) => setCreateDesc(e.target.value)}
                  />
                </div>
                <div className="flex gap-3 justify-end mt-2">
                  <button className="ghost-btn text-xs" onClick={() => setShowCreate(false)}>
                    {t("common.cancel")}
                  </button>
                  <button className="btn-stone" disabled={creating || !createName.trim()} onClick={handleCreate}>
                    {creating && <Loader2 size={13} className="animate-spin mr-2 inline" />}
                    {t("common.create")}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
