"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send } from "lucide-react";
import { useT } from "@/lib/i18n";
import { DiamondDivider } from "./ui/Ornament";
import type { ChatMessage, NPC } from "@/lib/types";

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  loading: boolean;
  selectedNpc: NPC | null;
}

const messageVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: "easeOut" } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const t = useT();
  const isPlayer = msg.type === "player";
  const isDm = msg.type === "dm";
  const isSystem = msg.type === "system";

  const time = new Date(msg.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (isSystem) {
    return (
      <motion.div
        variants={messageVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
        className="flex justify-start"
      >
        <div className="system-message message-fade-in max-w-[85%]">
          <p
            className="text-sm italic text-left"
            style={{ color: "rgba(230,237,243,0.4)", fontSize: "14px" }}
          >
            {msg.content}
          </p>
        </div>
      </motion.div>
    );
  }

  const senderLabel = isPlayer
    ? t("chat.you")
    : isDm
      ? t("chat.dm")
      : msg.npc_name ?? "NPC";

  const messageClass = isPlayer
    ? "player-message message-fade-in"
    : "dm-message message-fade-in";

  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={`flex ${isPlayer ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-left ${messageClass}`}
      >
        {/* Sender label */}
        <div className={`flex items-center gap-1.5 mb-1.5 ${isPlayer ? "justify-end" : ""}`}>
          <span
            className="font-medieval uppercase"
            style={{
              color: "rgba(194, 58, 46, 0.7)",
              fontSize: "12px",
              letterSpacing: "0.15em",
              fontWeight: 600,
            }}
          >
            {senderLabel}
          </span>
        </div>

        {/* Content */}
        <p
          className="leading-relaxed font-body"
          style={{ color: "#E6EDF3", fontSize: "16px" }}
        >
          {msg.content}
        </p>

        {/* Timestamp */}
        <div
          className={`mt-1.5 ${isPlayer ? "text-right" : ""}`}
          style={{ color: "rgba(255,255,255,0.25)", fontSize: "11px" }}
        >
          {time}
        </div>
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  const t = useT();
  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="flex justify-start"
    >
      <div
        className="rounded-lg px-4 py-3"
        style={{
          background: "rgba(194, 58, 46, 0.08)",
          borderLeft: "2px solid rgba(194, 58, 46, 0.3)",
        }}
      >
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: "rgba(194, 58, 46, 0.4)" }}
                animate={{ opacity: [0.3, 1, 0.3], scale: [0.85, 1.15, 0.85] }}
                transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
          <span style={{ color: "rgba(230,237,243,0.3)", fontSize: "13px" }} className="ml-1">
            {t("chat.worldStirs")}
          </span>
        </div>
      </div>
    </motion.div>
  );
}

function EmptyState() {
  const t = useT();
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex-1 flex flex-col items-center justify-center h-full text-center py-20 relative"
    >
      {/* Hero background image */}
      <div className="absolute inset-0 z-0">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-[0.12]"
          style={{ backgroundImage: "url(/images/hero-bg.jpg)" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0D1117] via-[#0D1117]/80 to-transparent" />
      </div>
      {/* Fantasy castle/torch SVG illustration */}
      <div className="relative mb-8 z-10">
        <svg viewBox="0 0 120 100" className="w-32 h-28 " fill="none">
          <rect x="20" y="40" width="16" height="45" rx="2" fill="rgba(48, 54, 61, 0.15)" stroke="rgba(194, 58, 46, 0.2)" strokeWidth="1"/>
          <rect x="84" y="40" width="16" height="45" rx="2" fill="rgba(48, 54, 61, 0.15)" stroke="rgba(194, 58, 46, 0.2)" strokeWidth="1"/>
          <rect x="36" y="50" width="48" height="35" rx="2" fill="rgba(48, 54, 61, 0.1)" stroke="rgba(194, 58, 46, 0.15)" strokeWidth="1"/>
          <path d="M52 85 V68 A8 8 0 0 1 68 68 V85" fill="rgba(0,0,0,0.3)" stroke="rgba(194, 58, 46, 0.25)" strokeWidth="1"/>
          <rect x="20" y="36" width="5" height="6" fill="rgba(48, 54, 61, 0.2)"/>
          <rect x="27" y="36" width="5" height="6" fill="rgba(48, 54, 61, 0.2)"/>
          <rect x="84" y="36" width="5" height="6" fill="rgba(48, 54, 61, 0.2)"/>
          <rect x="91" y="36" width="5" height="6" fill="rgba(48, 54, 61, 0.2)"/>
          <ellipse cx="28" cy="32" rx="4" ry="6" fill="rgba(194, 58, 46, 0.15)"/>
          <ellipse cx="28" cy="33" rx="2" ry="3" fill="rgba(194, 58, 46, 0.2)"/>
          <ellipse cx="92" cy="32" rx="4" ry="6" fill="rgba(194, 58, 46, 0.15)"/>
          <ellipse cx="92" cy="33" rx="2" ry="3" fill="rgba(194, 58, 46, 0.2)"/>
          <circle cx="15" cy="15" r="1" fill="rgba(230, 237, 243, 0.3)"/>
          <circle cx="50" cy="8" r="1.2" fill="rgba(230, 237, 243, 0.25)"/>
          <circle cx="105" cy="12" r="0.8" fill="rgba(230, 237, 243, 0.2)"/>
          <circle cx="75" cy="5" r="1" fill="rgba(230, 237, 243, 0.15)"/>
          <circle cx="95" cy="18" r="6" fill="rgba(230, 237, 243, 0.08)" stroke="rgba(230, 237, 243, 0.12)" strokeWidth="0.5"/>
        </svg>
        <div className="absolute inset-0 -z-10" style={{ background: "radial-gradient(ellipse at 50% 60%, rgba(194, 58, 46, 0.06) 0%, transparent 70%)" }} />
      </div>

      <h2
        className="font-medieval font-bold mb-6 relative z-10"
        style={{
          color: "#E6EDF3",
          fontSize: "48px",
          letterSpacing: "0.12em",
          lineHeight: 1.1,
        }}
      >
        {t("chat.emptyTitle")}
      </h2>
      {/* Decorative divider with sword motif */}
      <div className="flex items-center justify-center gap-3 mb-6 relative z-10">
        <div className="h-px w-16 bg-gradient-to-r from-transparent to-gold/30" />
        <svg viewBox="0 0 24 24" className="w-4 h-4 text-gold/40" fill="currentColor">
          <path d="M14.5 17.5L3 6V3h3l11.5 11.5M13 19l6-6m3 3l-2 2m-3-3l2-2"/>
        </svg>
        <div className="h-px w-16 bg-gradient-to-l from-transparent to-gold/30" />
      </div>
      <p
        className="text-lg max-w-md font-body leading-relaxed relative z-10"
        style={{ color: "rgba(230,237,243,0.45)" }}
      >
        {t("chat.emptyDesc")}
      </p>
    </motion.div>
  );
}

export function ChatPanel({ messages, onSend, loading, selectedNpc }: Props) {
  const t = useT();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput("");
    }
  };

  const placeholder = selectedNpc
    ? `${t("chat.placeholderNpc")} ${selectedNpc.name}...`
    : t("chat.placeholder");

  return (
    <div className="flex-1 flex flex-col min-h-0 h-full overflow-hidden">
      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto px-6 py-4 space-y-3">
        {messages.length === 0 && (
          <>
            <EmptyState />
            <DiamondDivider className="my-6" />
          </>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          {loading && <TypingIndicator key="typing" />}
        </AnimatePresence>
      </div>

      {/* Input area */}
      <div
        className="shrink-0"
        style={{
          borderTop: "1px solid #30363D",
          background: "#161B22",
          backdropFilter: "blur(12px)",
        }}
      >
        {/* NPC context bar */}
        {selectedNpc && (
          <div
            className="flex items-center gap-2 px-6 py-2"
            style={{
              borderBottom: "1px solid rgba(194, 58, 46, 0.15)",
              background: "rgba(194, 58, 46, 0.08)",
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full animate-pulse"
              style={{ background: "rgba(194, 58, 46, 0.6)" }}
            />
            <span style={{ color: "rgba(194, 58, 46, 0.6)", fontSize: "13px" }}>
              {t("chat.speakingWith")}{" "}
              <span className="font-bold" style={{ color: "rgba(194, 58, 46, 0.8)" }}>
                {selectedNpc.name}
              </span>
              {" — "}{t("chat.typeSay")}{" "}
              <span className="font-mono" style={{ color: "rgba(194, 58, 46, 0.4)" }}>
                say &lt;message&gt;
              </span>
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex items-center gap-3 p-4 px-6">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="What do you do? (Type 'look' to observe, 'go' to travel, 'talk' to converse...)"
            className="input-scroll flex-1"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn-stone flex items-center gap-2 px-5 py-2.5 text-sm font-medieval uppercase tracking-wider"
          >
            <Send className="w-4 h-4" />
            <span>{t("common.send")}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
