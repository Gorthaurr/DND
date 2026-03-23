"use client";

import { useCallback, useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { ChatMessage, LookResponse, NPC, WorldMap } from "@/lib/types";
import { useT, useI18n } from "@/lib/i18n";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { CharacterSheet } from "./components/CharacterSheet";
import { InventoryPanel } from "./components/InventoryPanel";
import { ChatPanel } from "./components/ChatPanel";
import { WorldMapView } from "./components/WorldMap";
import { NPCPanel } from "./components/NPCPanel";
import { WorldLog } from "./components/WorldLog";
import { NPCGraph } from "./components/NPCGraph";
import { QuestJournal } from "./components/QuestJournal";
import { SectionDivider } from "./components/ui/Ornament";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sword,
  Map,
  ScrollText,
  Eye,
  ChevronRight,
  BookOpen,
  Users,
  MoreHorizontal,
} from "lucide-react";

/* ━━━━━━━━━━━━━━ Location Image Helper ━━━━━━━━━━━━━━ */

function getLocationImage(locId: string): string {
  const map: Record<string, string> = {
    "loc-tavern": "tavern.jpg",
    "loc-market": "village.jpg",
    "loc-square": "village.jpg",
    "loc-chapel": "chapel.jpg",
    "loc-smithy": "smithy.jpg",
    "loc-farm": "farm.jpg",
    "loc-forest": "forest.jpg",
    "loc-woods": "forest.jpg",
    "loc-ruins": "ruins.jpg",
    "loc-graveyard": "dungeon.jpg",
  };
  return map[locId] || "hero-bg.jpg";
}

/* ━━━━━━━━━━━━━━ Types & Config ━━━━━━━━━━━━━━ */

type Tab = "chat" | "map" | "observer" | "log" | "quests";

const TAB_CONFIG: {
  key: Tab;
  labelKey: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "chat", labelKey: "nav.adventure", icon: Sword },
  { key: "map", labelKey: "nav.worldMap", icon: Map },
  { key: "observer", labelKey: "nav.observer", icon: Eye },
  { key: "log", labelKey: "nav.chronicles", icon: ScrollText },
  { key: "quests", labelKey: "nav.quests", icon: BookOpen },
];

/* ━━━━━━━━━━━━━━ Particles — very subtle ━━━━━━━━━━━━━━ */

function Particles() {
  const dots = useMemo(
    () =>
      Array.from({ length: 12 }).map((_, i) => ({
        id: i,
        left: `${Math.random() * 100}%`,
        delay: `${Math.random() * 15}s`,
        duration: `${18 + Math.random() * 12}s`,
        size: `${1 + Math.random() * 1.5}px`,
      })),
    []
  );
  return (
    <div className="particles-container" aria-hidden>
      {dots.map((d) => (
        <div
          key={d.id}
          className="particle"
          style={{
            left: d.left,
            animationDelay: d.delay,
            animationDuration: d.duration,
            width: d.size,
            height: d.size,
          }}
        />
      ))}
    </div>
  );
}

/* ━━━━━━━━━━━━━━ Connection Indicator ━━━━━━━━━━━━━━ */

function ConnectionDot({ connected }: { connected: boolean }) {
  return (
    <span className="relative flex items-center">
      <span
        className="w-2 h-2 rounded-full"
        style={{ background: connected ? "rgba(100,180,100,0.8)" : "rgba(180,60,60,0.8)" }}
      />
      {connected && (
        <span
          className="absolute w-2 h-2 rounded-full animate-ping opacity-30"
          style={{ background: "rgba(100,180,100,0.8)" }}
        />
      )}
    </span>
  );
}

/* ━━━━━━━━━━━━━━ Tab Content Animations ━━━━━━━━━━━━━━ */

const tabVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: "easeOut" } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.15 } },
};

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MAIN PAGE COMPONENT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

export default function Home() {
  const t = useT();
  const { locale } = useI18n();

  /* ── state ── */
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [lookData, setLookData] = useState<LookResponse | null>(null);
  const [worldMap, setWorldMap] = useState<WorldMap | null>(null);
  const [worldLog, setWorldLog] = useState<any[]>([]);
  const [selectedNpc, setSelectedNpc] = useState<NPC | null>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [gold, setGold] = useState(50);
  const [playerHp, setPlayerHp] = useState(10);
  const [playerMaxHp, setPlayerMaxHp] = useState(10);
  const [xp, setXp] = useState(0);
  const [day, setDay] = useState(1);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [connected, setConnected] = useState(false);
  const [isDead, setIsDead] = useState(false);
  const [showNpcGraph, setShowNpcGraph] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  /* ── helpers ── */
  const addMessage = useCallback(
    (type: ChatMessage["type"], content: string, npc_name?: string) => {
      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-${Math.random()}`,
          type,
          content,
          npc_name,
          timestamp: Date.now(),
        },
      ]);
    },
    []
  );

  /* ── close dropdown on outside click ── */
  useEffect(() => {
    if (!menuOpen) return;
    const close = () => setMenuOpen(false);
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, [menuOpen]);

  /* ── init ── */
  useEffect(() => {
    const init = async () => {
      try {
        const [look, state] = await Promise.all([api.look(), api.worldState()]);
        setLookData(look);
        setGold(state.player_gold);
        setDay(state.day);
        setInventory(state.player_inventory);
        setPlayerHp(state.player_hp || 10);
        setPlayerMaxHp(state.player_max_hp || 10);
        setXp(state.player_xp || 0);
        if (state.player_hp !== undefined && state.player_hp <= 0) setIsDead(true);
        setConnected(true);

        // Load chat history
        try {
          const chatData = await api.getChatHistory();
          if (chatData.messages && chatData.messages.length > 0) {
            const restored = chatData.messages.map((m: any) => ({
              id: `restored-${m.timestamp}-${Math.random()}`,
              type: m.type || "system",
              content: m.content || "",
              npc_name: m.npc_name,
              timestamp: m.timestamp || Date.now(),
            }));
            setMessages(restored);
          }
        } catch (e) {
          console.error("Failed to load chat history:", e);
        }

        // Load world log (chronicles)
        try {
          const logData = await api.worldLog();
          if (logData.entries) setWorldLog(logData.entries);
        } catch (e) {
          console.error("Failed to load world log:", e);
        }

        addMessage(
          "system",
          `${t("sys.welcomeTo" as any)} ${look.location.name}. ${look.location.description}`
        );
        if (look.npcs.length > 0) {
          addMessage(
            "system",
            `${t("sys.youSee" as any)} ${look.npcs.map((n) => `${n.name} (${n.occupation})`).join(", ")}`
          );
        }
      } catch {
        addMessage("system", t("sys.cannotConnect" as any));
      }
    };
    init();
  }, [addMessage]);

  /* ── periodic health check — every 15s ── */
  useEffect(() => {
    let alive = true;
    const check = () => {
      api
        .worldState()
        .then((state) => {
          if (!alive) return;
          setConnected(true);
          setDay(state.day);
          setGold(state.player_gold);
          setPlayerHp(state.player_hp || 10);
          setPlayerMaxHp(state.player_max_hp || 10);
          setXp(state.player_xp || 0);
          setInventory(state.player_inventory);
          if (state.player_hp !== undefined && state.player_hp <= 0) setIsDead(true);
        })
        .catch(() => {
          if (alive) setConnected(false);
        });
    };
    const id = setInterval(check, 15_000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  /* ── action handler ── */
  const handleAction = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    addMessage("player", text);

    try {
      const parts = text.trim().split(" ");
      const cmd = parts[0].toLowerCase();
      const arg = parts.slice(1).join(" ");

      /** Helper: refresh world state after any successful API call */
      const syncWorld = async () => {
        try {
          const ws = await api.worldState();
          setDay(ws.day);
          setGold(ws.player_gold);
          setPlayerHp(ws.player_hp || 10);
          setPlayerMaxHp(ws.player_max_hp || 10);
          setXp(ws.player_xp || 0);
          setInventory(ws.player_inventory);
          if (ws.player_hp !== undefined && ws.player_hp <= 0) setIsDead(true);
        } catch {
          /* non-critical */
        }
      };

      if (cmd === "talk" && arg) {
        const npc = lookData?.npcs.find(
          (n) => n.name.toLowerCase().includes(arg.toLowerCase()) || n.id === arg
        );
        if (npc) {
          setSelectedNpc(npc);
          addMessage("system", `${t("sys.approach" as any)} ${npc.name}.`);
        } else {
          addMessage("system", `${t("sys.dontSee" as any)} "${arg}"`);
        }
      } else if (cmd === "say" && selectedNpc) {
        const resp = await api.dialogue(selectedNpc.id, arg, locale);
        addMessage("npc", resp.dialogue, resp.npc_name);
        if (resp.interjections && resp.interjections.length > 0) {
          for (const inter of resp.interjections) {
            addMessage("npc", inter.dialogue, inter.npc_name);
          }
        }
        setConnected(true);
      } else if (cmd === "look") {
        const look = await api.look();
        setLookData(look);
        setConnected(true);
        addMessage("dm", look.location.description);
        if (look.npcs.length > 0) {
          addMessage("system", `${t("sys.peopleHere" as any)} ${look.npcs.map((n) => n.name).join(", ")}`);
        }
        if (look.exits.length > 0) {
          addMessage("system", `${t("sys.exitsLabel" as any)} ${look.exits.map((e) => e.name).join(", ")}`);
        }
      } else if (cmd === "tick") {
        addMessage("system", t("sys.worldAdvances" as any));
        setLoading(true);

        const result = await api.tickStream((event) => {
          if (event.phase === "scenario") {
            const sc = event.data;
            const tension = sc.tension_level?.toUpperCase() || "";
            addMessage("system", `[${tension}] ${sc.title} — ${sc.narrative_update || sc.phase_name}`);
          } else if (event.phase === "event") {
            addMessage("system", `[${event.data.type}] ${event.data.description}`);
          } else if (event.phase === "interaction") {
            const i = event.data;
            const tag = i.action && i.action !== "none" ? `[${i.action}] ` : "";
            addMessage("system", `${tag}${i.summary}`);
          } else if (event.phase === "actions") {
            const s = event.data.summary;
            const parts = Object.entries(s).map(([k, v]) => `${k}: ${v}`).join(", ");
            addMessage("system", `NPCs acted: ${parts}`);
          }
        });

        setDay(result.day);
        setConnected(true);
        const look = await api.look();
        setLookData(look);
        await syncWorld();
      } else if (cmd === "map") {
        const map = await api.worldMap();
        setWorldMap(map);
        setConnected(true);
        setActiveTab("map");
      } else if (cmd === "leave" || cmd === "отойти" || cmd === "уйти") {
        setSelectedNpc(null);
        addMessage("system", t("sys.leaveConversation" as any) || "You step away.");
      } else if (selectedNpc && !["go", "move", "look", "tick", "map", "talk", "attack", "fight", "kill", "save", "load", "reset", "respawn", "stats", "inventory", "quests", "spells", "cast"].includes(cmd) && !/\b(убиваю|атакую|бью|ударяю|нападаю|убить|дерусь|режу|стреляю|attack|kill|fight|hit|strike|stab)\b/i.test(text)) {
        // NPC is selected and text is not a known command or combat → treat as dialogue
        const resp = await api.dialogue(selectedNpc.id, text, locale);
        addMessage("npc", resp.dialogue, resp.npc_name);
        if (resp.interjections && resp.interjections.length > 0) {
          for (const interj of resp.interjections) {
            addMessage("npc", interj.dialogue, interj.npc_name);
          }
        }
        setConnected(true);
      } else {
        const resp = await api.action(text, locale);
        addMessage("dm", resp.narration);
        setConnected(true);

        // Show HP change
        if (resp.player_hp_change && resp.player_hp_change !== 0) {
          if (resp.player_hp_change < 0) {
            addMessage("system", `\u2764 You lost ${Math.abs(resp.player_hp_change)} HP!`);
          } else {
            addMessage("system", `\u2764 You gained ${resp.player_hp_change} HP!`);
          }
        }

        // Show player death
        if (resp.player_killed) {
          addMessage("system", `\uD83D\uDC80 You have been killed!`);
          setIsDead(true);
        }

        // Show kills in chat (Problem 6)
        if (resp.npcs_killed && resp.npcs_killed.length > 0) {
          addMessage("system", `\u2620 ${resp.npcs_killed.length} NPC${resp.npcs_killed.length > 1 ? "s" : ""} killed`);
        }

        // Clear selectedNpc if they were killed (Problem 4)
        if (resp.npcs_killed && selectedNpc && resp.npcs_killed.includes(selectedNpc.id)) {
          setSelectedNpc(null);
        }

        const look = await api.look();
        setLookData(look);

        // Clear selectedNpc if no longer in alive NPC list (Problem 4)
        if (selectedNpc && look.npcs && !look.npcs.find((n: any) => n.id === selectedNpc.id)) {
          setSelectedNpc(null);
        }

        await syncWorld();
      }
    } catch (e: any) {
      addMessage("system", `Error: ${e.message}`);
      if (e.message?.includes("fetch") || e.message?.includes("Failed") || e.message?.includes("NetworkError")) {
        setConnected(false);
      }
    } finally {
      setLoading(false);
    }
  };

  /* ━━━━━━━━━━━━━━ RENDER ━━━━━━━━━━━━━━ */
  return (
    <main className="h-screen flex flex-col relative overflow-hidden " style={{ background: "#0D1117" }}>
      <Particles />

      {/* ═══════════ DEATH OVERLAY ═══════════ */}
      {isDead && (
        <div className="absolute inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.85)" }}>
          <div className="text-center">
            <div className="text-6xl mb-6">{"\uD83D\uDC80"}</div>
            <h2 className="font-medieval text-4xl mb-4" style={{ color: "#C23A2E" }}>You Have Fallen</h2>
            <p className="font-body mb-6" style={{ color: "rgba(230,237,243,0.4)" }}>Your vision fades as darkness claims you...</p>
            <button
              onClick={async () => {
                try {
                  await api.respawn();
                  setIsDead(false);
                  const state = await api.worldState();
                  setDay(state.day);
                  setGold(state.player_gold);
                  setPlayerHp(state.player_hp || 10);
                  setPlayerMaxHp(state.player_max_hp || 10);
                  setXp(state.player_xp || 0);
                  const look = await api.look();
                  setLookData(look);
                  addMessage("system", "You awaken at The Rusty Flagon, battered but alive...");
                } catch (e) { console.error(e); }
              }}
              className="btn-fantasy px-8 py-3 text-lg"
            >
              Rise Again
            </button>
          </div>
        </div>
      )}

      {/* ═══════════ HEADER — 60px Clean Bar ═══════════ */}
      <header
        className="relative z-20 flex items-center justify-between px-6 py-0 h-[60px]"
        style={{
          background: "rgba(13, 17, 23, 0.85)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          borderBottom: "1px solid #30363D",
        }}
      >
        {/* Left — Logo & Title */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="relative w-10 h-10 flex items-center justify-center">
            <Sword className="w-6 h-6" style={{ color: "#C23A2E" }} />
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background: "radial-gradient(circle, rgba(194,58,46,0.15) 0%, transparent 70%)",
              }}
            />
          </div>
          <div>
            <h1
              className="font-medieval text-xl font-bold leading-none"
              style={{ color: "#E6EDF3", letterSpacing: "0.15em" }}
            >
              {t("nav.title")}
            </h1>
            <p className="text-xs mt-0.5" style={{ color: "rgba(230,237,243,0.35)" }}>
              {t("nav.subtitle")}
            </p>
          </div>
        </div>

        {/* Center — Tab Navigation + Dropdown */}
        <nav className="flex items-center gap-0">
          {TAB_CONFIG.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className="nav-tab-btn relative flex items-center gap-2 px-3 py-0 h-[60px] transition-all duration-200"
                style={{
                  color: isActive ? "#E6EDF3" : "rgba(230,237,243,0.4)",
                  fontSize: "12px",
                  fontFamily: "'Cinzel', Georgia, serif",
                  textTransform: "uppercase",
                  letterSpacing: "2px",
                  fontWeight: 600,
                  background: "transparent",
                  border: "none",
                }}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden lg:inline">{t(tab.labelKey as any)}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTabLine"
                    className="absolute bottom-0 left-2 right-2 h-[2px]"
                    style={{ background: "rgba(194, 58, 46, 0.6)" }}
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            );
          })}

          {/* Dropdown Menu */}
          <div className="relative">
            <button
              onClick={(e) => { e.stopPropagation(); setMenuOpen(!menuOpen); }}
              className="flex items-center justify-center w-8 h-8 rounded transition-all duration-200"
              style={{ color: "rgba(230,237,243,0.4)", background: menuOpen ? "rgba(194,58,46,0.1)" : "transparent" }}
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {menuOpen && (
              <div
                className="absolute right-0 top-full mt-2 w-48 rounded-lg py-2 z-50"
                style={{ background: "#161B22", border: "1px solid #30363D", backdropFilter: "blur(12px)" }}
                onClick={(e) => e.stopPropagation()}
              >
                <Link href="/character" className="block px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgba(230,237,243,0.6)" }} onClick={() => setMenuOpen(false)}>
                  Create Character
                </Link>
                <Link href="/worldbuilder" className="block px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgba(230,237,243,0.6)" }} onClick={() => setMenuOpen(false)}>
                  World Builder
                </Link>
                <Link href="/editor" className="block px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgb(217, 160, 60)" }} onClick={() => setMenuOpen(false)}>
                  World Editor
                </Link>
                <Link href="/npcs" className="block px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgb(120, 200, 255)" }} onClick={() => setMenuOpen(false)}>
                  NPC Explorer
                </Link>
                <Link href="/story" className="block px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgb(180, 120, 255)" }} onClick={() => setMenuOpen(false)}>
                  Story Tree
                </Link>
                <button className="block w-full text-left px-4 py-2 text-sm font-body hover:bg-[rgba(194,58,46,0.08)] transition-colors" style={{ color: "rgba(230,237,243,0.6)" }} onClick={() => { setActiveTab("observer"); setMenuOpen(false); }}>
                  NPC Graph
                </button>
              </div>
            )}
          </div>
        </nav>

        {/* Right — Stats & Language */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-sm" style={{ color: "rgba(230,237,243,0.35)" }}>
              {t("common.day")}
            </span>
            <span
              className="font-medieval font-bold text-base"
              style={{ color: "#E6EDF3" }}
            >
              {day}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span style={{ color: "#C23A2E", fontSize: "14px" }}>&#9733;</span>
            <span className="font-medieval font-bold text-base" style={{ color: "#C23A2E" }}>{gold}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span style={{ color: "#C23A2E", fontSize: "14px" }}>{"\u2665"}</span>
            <span className="font-medieval font-bold text-base" style={{ color: "#E6EDF3" }}>{playerHp}</span>
            <span className="text-sm" style={{ color: "rgba(194,58,46,0.4)" }}>/{playerMaxHp}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span style={{ color: "#C23A2E", fontSize: "14px" }}>{"\u2727"}</span>
            <span className="font-medieval font-bold text-base" style={{ color: "#E6EDF3" }}>{xp}</span>
          </div>
          <ConnectionDot connected={connected} />
          <LanguageSwitcher />
        </div>
      </header>
      <div className="ornament-border relative z-20" />

      {/* ═══════════ CONTENT ═══════════ */}
      <div className="flex-1 flex overflow-hidden relative z-10 min-h-0">

        {/* ── Main Panel ── */}
        <div className="flex-1 flex flex-col overflow-y-auto overflow-x-hidden min-h-0 min-w-0 relative">
          {/* Location background image */}
          {lookData?.location && (
            <div className="absolute inset-0 z-0 pointer-events-none">
              <div
                className="absolute inset-0 bg-cover bg-center opacity-[0.07]"
                style={{
                  backgroundImage: `url(/images/${getLocationImage(lookData.location.id)})`,
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-[#0D1117] via-transparent to-[#0D1117]" />
            </div>
          )}
          <AnimatePresence mode="wait">
            {activeTab === "chat" && (
              <motion.div key="chat" className="flex-1 flex flex-col overflow-hidden min-h-0 w-full relative z-10" {...tabVariants}>
                <ChatPanel messages={messages} onSend={handleAction} loading={loading} selectedNpc={selectedNpc} />
              </motion.div>
            )}

            {activeTab === "map" && (
              <motion.div key="map" className="flex-1 overflow-hidden w-full relative z-10" {...tabVariants}>
                <WorldMapView data={worldMap} />
              </motion.div>
            )}

            {activeTab === "log" && (
              <motion.div key="log" className="flex-1 overflow-hidden w-full relative z-10" {...tabVariants}>
                <WorldLog entries={worldLog} />
              </motion.div>
            )}

            {activeTab === "observer" && (
              <motion.div key="observer" className="flex-1 flex flex-col overflow-hidden min-h-0 relative z-10" {...tabVariants}>
                <NPCPanel npcs={lookData?.npcs || []} />
                {/* NPC Relationship Graph accessible from Observer tab */}
                <div className="border-t" style={{ borderColor: "#30363D" }}>
                  <button
                    onClick={() => setShowNpcGraph((v) => !v)}
                    className="flex items-center gap-2 px-4 py-2 text-xs font-medieval uppercase tracking-wider w-full transition-colors"
                    style={{ color: "rgba(230,237,243,0.4)" }}
                  >
                    <Users className="w-3.5 h-3.5" />
                    {t("nav.npcs" as any)}
                  </button>
                </div>
                {showNpcGraph && (
                  <div className="flex-1 min-h-[300px] overflow-hidden">
                    <NPCGraph />
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === "quests" && (
              <motion.div key="quests" className="flex-1 flex flex-col overflow-hidden min-h-0 w-full relative z-10" {...tabVariants}>
                <QuestJournal />
              </motion.div>
            )}

          </AnimatePresence>
        </div>

        {/* ── Right Sidebar — Dark Panel ── */}
        <aside
          className="w-80 flex flex-col overflow-hidden"
          style={{
            background: "#0D1117",
            borderLeft: "1px solid #30363D",
          }}
        >
          <div className="flex-1 overflow-y-auto">
            {/* Location Card */}
            {lookData && (
              <div className="p-5 scroll-panel m-3">
                <h3
                  className="font-medieval font-bold mb-2"
                  style={{ color: "#E6EDF3", letterSpacing: "0.15em", textTransform: "uppercase", fontSize: "14px" }}
                >
                  {lookData.location.name}
                </h3>
                {/* Location image preview */}
                <div className="relative h-24 rounded overflow-hidden mb-3">
                  <div
                    className="absolute inset-0 bg-cover bg-center"
                    style={{ backgroundImage: `url(/images/${getLocationImage(lookData.location.id)})` }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#161B22] to-transparent" />
                  <div className="absolute bottom-2 left-3">
                    <span className="text-xs font-body" style={{ color: "rgba(230,237,243,0.6)" }}>
                      {lookData.location.type}
                    </span>
                  </div>
                </div>
                <p className="leading-relaxed" style={{ color: "rgba(230, 237, 243, 0.4)", fontSize: "13px" }}>
                  {lookData.location.description}
                </p>
              </div>
            )}

            <SectionDivider className="mx-3" />

            {/* NPCs — People Here */}
            {lookData?.npcs && lookData.npcs.length > 0 && (
              <div className="p-5 scroll-panel m-3">
                <h3 className="section-title mb-3">
                  {t("sidebar.peopleHere")}
                </h3>
                {selectedNpc && (
                  <button
                    onClick={() => {
                      addMessage("system", t("sys.leaveConversation" as any) || "You step away.");
                      setSelectedNpc(null);
                    }}
                    className="w-full mb-2 px-3 py-2 rounded text-xs font-body transition-colors"
                    style={{ background: "rgba(194, 58, 46, 0.1)", color: "#C23A2E", border: "1px solid rgba(194, 58, 46, 0.2)" }}
                  >
                    {locale === "ru" ? "\u2190 \u041e\u0442\u043e\u0439\u0442\u0438 \u043e\u0442 " + selectedNpc.name : "\u2190 Leave " + selectedNpc.name}
                  </button>
                )}
                <div className="space-y-1">
                  {lookData.npcs.map((npc) => (
                    <button
                      key={npc.id}
                      onClick={() => {
                        setSelectedNpc(npc);
                        addMessage("system", `${t("sys.turnTo" as any)} ${npc.name}.`);
                      }}
                      className="npc-sidebar-btn block w-full text-left px-3.5 py-2.5 rounded transition-colors"
                      style={{
                        background: selectedNpc?.id === npc.id ? "rgba(194, 58, 46, 0.06)" : "transparent",
                      }}
                    >
                      <span
                        className="font-medieval font-semibold block"
                        style={{ color: "#E6EDF3", fontSize: "15px" }}
                      >
                        {npc.name}
                      </span>
                      <span style={{ color: "rgba(230,237,243,0.35)", fontSize: "12px" }}>
                        {npc.occupation}
                      </span>
                    </button>
                  ))}
                </div>
                {/* Dead NPCs */}
                {lookData.dead_npcs && lookData.dead_npcs.length > 0 && (
                  <div className="mt-3 space-y-1">
                    <h4 className="text-xs font-medieval uppercase tracking-wider" style={{ color: "rgba(194,58,46,0.5)" }}>
                      {"\uD83D\uDC80"} Dead
                    </h4>
                    {lookData.dead_npcs.map((npc) => (
                      <div
                        key={npc.id}
                        className="block w-full text-left px-3.5 py-2 rounded"
                        style={{ opacity: 0.4 }}
                      >
                        <span
                          className="font-medieval font-semibold block"
                          style={{ color: "#C23A2E", fontSize: "15px", textDecoration: "line-through" }}
                        >
                          {npc.name}
                        </span>
                        <span style={{ color: "rgba(230,237,243,0.25)", fontSize: "12px", textDecoration: "line-through" }}>
                          {npc.occupation}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            <SectionDivider className="mx-3" />

            {/* Exits */}
            {lookData?.exits && lookData.exits.length > 0 && (
              <div className="p-5 scroll-panel m-3">
                <h3 className="section-title mb-3">
                  {t("sidebar.exits")}
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {lookData.exits.map((exit) => (
                    <button
                      key={exit.id}
                      onClick={() => handleAction(`go ${exit.name}`)}
                      className="exit-btn group flex items-center gap-2 px-3 py-2.5 rounded text-left min-h-[44px] transition-colors"
                      style={{
                        border: "1px solid rgba(194, 58, 46, 0.15)",
                        background: "transparent",
                        fontSize: "12px",
                      }}
                    >
                      <ChevronRight className="w-3.5 h-3.5 opacity-40 group-hover:opacity-100 transition-opacity flex-shrink-0" style={{ color: "#C23A2E" }} />
                      <span style={{ color: "rgba(230,237,243,0.6)" }}>{exit.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <SectionDivider className="mx-3" />

            {/* Character Sheet */}
            <CharacterSheet />

            <SectionDivider className="mx-3" />

            {/* Inventory — hide if empty items AND gold is 0 */}
            {(inventory.length > 0 || gold > 0) && (
              <InventoryPanel items={inventory} gold={gold} />
            )}
          </div>
        </aside>
      </div>

      <div className="fire-ambience fixed inset-0 pointer-events-none z-0" />
    </main>
  );
}
