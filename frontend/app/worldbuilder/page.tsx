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
  ChevronRight,
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

/* ────────────────────── motion variants ────────────────────── */

const fade = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.35, ease: "easeOut" } },
};

const staggerContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
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
      style={{ background: "#0D1117" }}
    >
      {/* Ambient glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at 50% 120%, rgba(194,58,46,0.06) 0%, transparent 60%)",
        }}
      />

      {/* ── back link ── */}
      <div className="px-6 pt-5 relative z-10">
        <Link
          href="/"
          className="ghost-btn inline-flex items-center gap-2"
          style={{ fontSize: "13px", padding: "8px 16px" }}
        >
          <ArrowLeft size={14} />
          {t("nav.backToGame")}
        </Link>
      </div>

      {/* ── header ── */}
      <header className="text-center pt-8 pb-6 relative z-10">
        <h1
          className="text-4xl md:text-5xl tracking-wider mb-3"
          style={{ color: "rgba(194,58,46,0.8)" }}
        >
          {t("worlds.title")}
        </h1>
        <div className="accent-line mx-auto mb-3" />
        <p style={{ color: "rgba(230,237,243,0.5)", fontSize: "14px" }}>
          {t("worlds.subtitle")}
        </p>
      </header>

      <div className="max-w-7xl mx-auto px-6 pb-16 relative z-10">
        {/* ── Breadcrumb when a world is selected ── */}
        {selected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 mb-6"
            style={{ color: "rgba(230,237,243,0.35)", fontSize: "13px" }}
          >
            <button
              onClick={() => setSelected(null)}
              className="hover-lift"
              style={{
                color: "rgba(194,58,46,0.6)",
                fontFamily: "Cinzel, serif",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "13px",
              }}
            >
              {t("worlds.title")}
            </button>
            <ChevronRight size={14} style={{ color: "rgba(230,237,243,0.2)" }} />
            <span
              style={{
                color: "#E6EDF3",
                fontFamily: "Cinzel, serif",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                fontSize: "13px",
              }}
            >
              {selected.name}
            </span>
          </motion.div>
        )}

        {/* ── Create button row ── */}
        {!selected && (
          <div className="flex items-center justify-center mb-8">
            <button
              onClick={() => setShowCreate(true)}
              className="btn-stone flex items-center gap-2 py-2.5 px-6"
              style={{ fontSize: "14px" }}
            >
              <Plus size={16} />
              {t("worlds.createNew")}
            </button>
          </div>
        )}

        {loading ? (
          <div
            className="flex items-center justify-center py-32"
            style={{ color: "rgba(194,58,46,0.4)" }}
          >
            <Loader2 size={20} className="animate-spin mr-2" />
            <span style={{ fontSize: "14px" }}>{t("common.loading")}</span>
          </div>
        ) : worlds.length === 0 && !selected ? (
          /* ══════════ EMPTY STATE ══════════ */
          <div
            className="flex flex-col items-center justify-center py-32 text-center"
            style={{ color: "rgba(194,58,46,0.4)" }}
          >
            <Globe size={48} className="mb-4" style={{ opacity: 0.35 }} />
            <p className="mb-2" style={{ fontSize: "20px" }}>
              {t("worlds.noWorlds")}
            </p>
            <p className="mb-6" style={{ fontSize: "14px", opacity: 0.7 }}>
              {t("worlds.noWorldsDesc")}
            </p>
            <button
              onClick={() => setShowCreate(true)}
              className="btn-stone flex items-center gap-2"
            >
              <Plus size={14} />
              {t("worlds.createNew")}
            </button>
          </div>
        ) : !selected ? (
          /* ══════════ WORLD CARD GRID ══════════ */
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            {worlds.map((w) => (
              <motion.div
                key={w.id}
                variants={cardVariants}
                className="game-card p-5 cursor-pointer flex flex-col"
                onClick={() => handleSelect(w)}
              >
                {/* Card header */}
                <div className="flex items-start gap-3 mb-3">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                    style={{ background: "rgba(194,58,46,0.08)" }}
                  >
                    <Globe size={20} style={{ color: "rgba(194,58,46,0.6)" }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3
                      className="font-bold truncate"
                      style={{
                        color: "#E6EDF3",
                        fontFamily: "Cinzel, serif",
                        fontSize: "16px",
                        lineHeight: "1.3",
                      }}
                    >
                      {w.name}
                    </h3>
                    {w.description ? (
                      <p
                        className="mt-1 line-clamp-2"
                        style={{
                          color: "rgba(230,237,243,0.6)",
                          fontSize: "13px",
                          lineHeight: "1.5",
                        }}
                      >
                        {w.description}
                      </p>
                    ) : (
                      <p
                        className="mt-1 italic"
                        style={{
                          color: "rgba(230,237,243,0.35)",
                          fontSize: "13px",
                        }}
                      >
                        No description
                      </p>
                    )}
                  </div>
                </div>

                {/* Stats row */}
                <div className="divider-ornament" style={{ margin: "8px 0" }} />
                <div
                  className="flex items-center gap-5 mb-4"
                  style={{ color: "rgba(230,237,243,0.35)" }}
                >
                  <span
                    className="flex items-center gap-1.5"
                    style={{ fontSize: "12px" }}
                  >
                    <MapPin size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                    {worldLocations(w)}
                  </span>
                  <span
                    className="flex items-center gap-1.5"
                    style={{ fontSize: "12px" }}
                  >
                    <Users size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                    {worldNpcs(w)}
                  </span>
                  <span
                    className="flex items-center gap-1.5"
                    style={{ fontSize: "12px" }}
                  >
                    <Flag size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                    {worldFactions(w)}
                  </span>
                </div>

                {/* Action buttons */}
                <div className="flex items-center gap-2 mt-auto">
                  <button
                    className="btn-stone flex items-center gap-1.5 flex-1 justify-center"
                    style={{ fontSize: "12px", padding: "6px 12px" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoad(w.id);
                    }}
                  >
                    <Play size={14} />
                    {t("worlds.load")}
                  </button>
                  <button
                    className="ghost-btn flex items-center gap-1.5 flex-1 justify-center"
                    style={{ fontSize: "12px", padding: "6px 12px" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelect(w);
                    }}
                  >
                    <Pencil size={14} />
                    {t("common.edit" as any)}
                  </button>
                  <button
                    className="ghost-btn flex items-center justify-center"
                    style={{
                      fontSize: "12px",
                      padding: "6px 10px",
                      borderColor: "rgba(180,60,60,0.25)",
                      color: "rgba(180,60,60,0.6)",
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(w.id);
                    }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          /* ══════════ EDITOR VIEW (world selected) ══════════ */
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Selected world card (compact) */}
            <div className="game-card selected p-5 mb-6">
              <div className="flex items-start gap-4">
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center shrink-0"
                  style={{ background: "rgba(194,58,46,0.1)" }}
                >
                  <Globe size={24} style={{ color: "rgba(194,58,46,0.7)" }} />
                </div>
                <div className="flex-1 min-w-0">
                  <h2
                    className="text-2xl tracking-wide mb-1"
                    style={{
                      color: "rgba(194,58,46,0.8)",
                      fontFamily: "Cinzel, serif",
                    }}
                  >
                    {selected.name}
                  </h2>
                  {selected.description && (
                    <p style={{ color: "rgba(230,237,243,0.5)", fontSize: "14px" }}>
                      {selected.description}
                    </p>
                  )}
                  <div
                    className="flex items-center gap-5 mt-3"
                    style={{ color: "rgba(230,237,243,0.35)" }}
                  >
                    <span
                      className="flex items-center gap-1.5"
                      style={{ fontSize: "13px" }}
                    >
                      <MapPin size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                      {worldLocations(selected)} locations
                    </span>
                    <span
                      className="flex items-center gap-1.5"
                      style={{ fontSize: "13px" }}
                    >
                      <Users size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                      {worldNpcs(selected)} NPCs
                    </span>
                    <span
                      className="flex items-center gap-1.5"
                      style={{ fontSize: "13px" }}
                    >
                      <Flag size={14} style={{ color: "rgba(194,58,46,0.5)" }} />
                      {worldFactions(selected)} factions
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button
                    className="btn-stone flex items-center gap-1.5"
                    style={{ fontSize: "12px", padding: "6px 14px" }}
                    onClick={() => handleLoad(selected.id)}
                  >
                    <Play size={14} />
                    {t("worlds.load")}
                  </button>
                  <button
                    className="ghost-btn"
                    style={{ padding: "6px 10px", fontSize: "12px" }}
                    onClick={() => setSelected(null)}
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div
              className="flex gap-6 mb-6"
              style={{ borderBottom: "1px solid rgba(48,54,61,0.5)" }}
            >
              {tabs.map((t_item) => (
                <button
                  key={t_item.key}
                  onClick={() => setTab(t_item.key)}
                  className="relative pb-3 uppercase tracking-widest transition-colors"
                  style={{
                    fontFamily: "Cinzel, serif",
                    fontSize: "13px",
                    color:
                      tab === t_item.key
                        ? "rgba(194,58,46,0.8)"
                        : "rgba(194,58,46,0.35)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    letterSpacing: "3px",
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

            {/* Tab content */}
            <AnimatePresence mode="wait">
              {tab === "locations" && (
                <motion.div
                  key="locations"
                  variants={fade}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  {/* Existing locations */}
                  <div className="mb-6">
                    {(selected.locations ?? []).length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {(selected.locations ?? []).map((loc: any, i: number) => (
                          <div
                            key={loc.id ?? i}
                            className="game-card p-4 flex items-start gap-3"
                          >
                            <div
                              className="w-9 h-9 rounded flex items-center justify-center shrink-0 mt-0.5"
                              style={{ background: "rgba(194,58,46,0.06)" }}
                            >
                              <MapPin
                                size={16}
                                style={{ color: "rgba(194,58,46,0.5)" }}
                              />
                            </div>
                            <div className="flex-1 min-w-0">
                              <span
                                className="font-semibold"
                                style={{
                                  color: "rgba(230,237,243,0.8)",
                                  fontSize: "14px",
                                }}
                              >
                                {loc.name}
                              </span>
                              {loc.type && (
                                <span
                                  className="ml-2"
                                  style={{
                                    color: "rgba(194,58,46,0.4)",
                                    fontSize: "12px",
                                  }}
                                >
                                  {loc.type}
                                </span>
                              )}
                              {loc.description && (
                                <p
                                  className="mt-1 line-clamp-2"
                                  style={{
                                    color: "rgba(230,237,243,0.35)",
                                    fontSize: "13px",
                                  }}
                                >
                                  {loc.description}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div
                        className="text-center py-8"
                        style={{ color: "rgba(194,58,46,0.35)" }}
                      >
                        <MapPin
                          size={32}
                          className="mx-auto mb-3"
                          style={{ opacity: 0.35 }}
                        />
                        <p style={{ fontSize: "14px" }}>
                          {t("worlds.noLocations" as any)}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Add location form */}
                  <div className="glass-panel p-5">
                    <span className="section-title mb-4 block">
                      {t("worlds.addLocation")}
                    </span>
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
                      <button
                        className="btn-stone self-start"
                        onClick={handleAddLocation}
                      >
                        {t("common.create")}
                      </button>
                    </div>
                  </div>

                  {/* AI generate location */}
                  <div className="glass-panel p-5 mt-4">
                    <span className="section-title mb-4 flex items-center gap-2">
                      <Sparkles
                        size={14}
                        style={{ color: "rgba(194,58,46,0.6)" }}
                      />
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
                      {aiLoading && (
                        <Loader2 size={14} className="animate-spin" />
                      )}
                      {t("worlds.aiGenerate")}
                    </button>
                  </div>
                </motion.div>
              )}

              {tab === "npcs" && (
                <motion.div
                  key="npcs"
                  variants={fade}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  {/* Existing NPCs */}
                  <div className="mb-6">
                    {(selected.npcs ?? []).length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {(selected.npcs ?? []).map((npc: any, i: number) => (
                          <div
                            key={npc.id ?? i}
                            className="game-card p-4 flex items-start gap-3"
                          >
                            <div
                              className="w-9 h-9 rounded flex items-center justify-center shrink-0 mt-0.5"
                              style={{ background: "rgba(194,58,46,0.06)" }}
                            >
                              <Users
                                size={16}
                                style={{ color: "rgba(194,58,46,0.5)" }}
                              />
                            </div>
                            <div className="flex-1 min-w-0">
                              <span
                                className="font-semibold"
                                style={{
                                  color: "rgba(230,237,243,0.8)",
                                  fontSize: "14px",
                                }}
                              >
                                {npc.name}
                              </span>
                              {npc.type && (
                                <span
                                  className="ml-2"
                                  style={{
                                    color: "rgba(194,58,46,0.4)",
                                    fontSize: "12px",
                                  }}
                                >
                                  {npc.type}
                                </span>
                              )}
                              {npc.description && (
                                <p
                                  className="mt-1 line-clamp-2"
                                  style={{
                                    color: "rgba(230,237,243,0.35)",
                                    fontSize: "13px",
                                  }}
                                >
                                  {npc.description}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div
                        className="text-center py-8"
                        style={{ color: "rgba(194,58,46,0.35)" }}
                      >
                        <Users
                          size={32}
                          className="mx-auto mb-3"
                          style={{ opacity: 0.35 }}
                        />
                        <p style={{ fontSize: "14px" }}>
                          {t("worlds.noNpcs" as any)}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Add NPC form */}
                  <div className="glass-panel p-5">
                    <span className="section-title mb-4 block">
                      {t("worlds.addNpc")}
                    </span>
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
                      <button
                        className="btn-stone self-start"
                        onClick={handleAddNpc}
                      >
                        {t("common.create")}
                      </button>
                    </div>
                  </div>

                  {/* AI generate NPC */}
                  <div className="glass-panel p-5 mt-4">
                    <span className="section-title mb-4 flex items-center gap-2">
                      <Sparkles
                        size={14}
                        style={{ color: "rgba(194,58,46,0.6)" }}
                      />
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
                      {aiLoading && (
                        <Loader2 size={14} className="animate-spin" />
                      )}
                      {t("worlds.aiGenerate")}
                    </button>
                  </div>
                </motion.div>
              )}

              {tab === "overview" && (
                <motion.div
                  key="overview"
                  variants={fade}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <div className="glass-panel p-6">
                    <div className="mb-5">
                      <span className="section-title block mb-2">
                        {t("worlds.worldName")}
                      </span>
                      <p
                        className="text-lg"
                        style={{ color: "rgba(194,58,46,0.8)" }}
                      >
                        {selected.name}
                      </p>
                    </div>
                    {selected.description && (
                      <div className="mb-5">
                        <span className="section-title block mb-2">
                          {t("common.description")}
                        </span>
                        <p
                          style={{
                            color: "rgba(230,237,243,0.5)",
                            fontSize: "14px",
                          }}
                        >
                          {selected.description}
                        </p>
                      </div>
                    )}
                    <div className="divider-ornament" />
                    <div className="grid grid-cols-3 gap-4 mt-5">
                      <div className="text-center">
                        <MapPin
                          size={20}
                          className="mx-auto mb-2"
                          style={{ color: "rgba(194,58,46,0.5)" }}
                        />
                        <p
                          className="text-2xl font-bold"
                          style={{ color: "rgba(194,58,46,0.8)" }}
                        >
                          {worldLocations(selected)}
                        </p>
                        <p style={{ color: "rgba(194,58,46,0.35)", fontSize: "12px" }}>
                          {t("worlds.locations")}
                        </p>
                      </div>
                      <div className="text-center">
                        <Users
                          size={20}
                          className="mx-auto mb-2"
                          style={{ color: "rgba(194,58,46,0.5)" }}
                        />
                        <p
                          className="text-2xl font-bold"
                          style={{ color: "rgba(194,58,46,0.8)" }}
                        >
                          {worldNpcs(selected)}
                        </p>
                        <p style={{ color: "rgba(194,58,46,0.35)", fontSize: "12px" }}>
                          {t("worlds.npcs")}
                        </p>
                      </div>
                      <div className="text-center">
                        <Flag
                          size={20}
                          className="mx-auto mb-2"
                          style={{ color: "rgba(194,58,46,0.5)" }}
                        />
                        <p
                          className="text-2xl font-bold"
                          style={{ color: "rgba(194,58,46,0.8)" }}
                        >
                          {worldFactions(selected)}
                        </p>
                        <p style={{ color: "rgba(194,58,46,0.35)", fontSize: "12px" }}>
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
                <h3
                  className="text-lg tracking-wide"
                  style={{ color: "rgba(194,58,46,0.8)" }}
                >
                  {t("worlds.createNew")}
                </h3>
                <button
                  className="ghost-btn"
                  style={{
                    padding: "4px 8px",
                    border: "none",
                    color: "rgba(194,58,46,0.4)",
                  }}
                  onClick={() => setShowCreate(false)}
                >
                  <X size={18} />
                </button>
              </div>

              <div className="flex flex-col gap-4">
                <div>
                  <label className="section-title block mb-1.5">
                    {t("worlds.worldName")}
                  </label>
                  <input
                    className="input-fantasy input-scroll"
                    placeholder={t("common.name")}
                    value={createName}
                    onChange={(e) => setCreateName(e.target.value)}
                    autoFocus
                  />
                </div>
                <div>
                  <label className="section-title block mb-1.5">
                    {t("common.description")}
                  </label>
                  <textarea
                    className="input-fantasy input-scroll min-h-[80px] resize-none"
                    placeholder={t("common.description")}
                    value={createDesc}
                    onChange={(e) => setCreateDesc(e.target.value)}
                  />
                </div>
                <div className="flex gap-3 justify-end mt-2">
                  <button
                    className="ghost-btn"
                    style={{ fontSize: "13px" }}
                    onClick={() => setShowCreate(false)}
                  >
                    {t("common.cancel")}
                  </button>
                  <button
                    className="btn-stone"
                    disabled={creating || !createName.trim()}
                    onClick={handleCreate}
                  >
                    {creating && (
                      <Loader2
                        size={14}
                        className="animate-spin mr-2 inline"
                      />
                    )}
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
