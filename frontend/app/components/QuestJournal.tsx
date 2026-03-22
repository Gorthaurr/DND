"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Quest {
  id: string;
  title: string;
  description: string;
  giver_npc_name: string | null;
  objectives: { description: string; completed: boolean }[];
  reward_gold: number;
  reward_description: string;
  difficulty: string;
  status: string;
}

const statusLabels: Record<string, string> = {
  available: "Available",
  active: "Active",
  completed: "Completed",
  failed: "Failed",
};

export function QuestJournal() {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getQuests().then((data: any) => {
      setQuests(data.quests || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleAccept = async (questId: string) => {
    try {
      await api.acceptQuest(questId);
      setQuests(qs => qs.map(q => q.id === questId ? { ...q, status: "active" } : q));
    } catch (e) {
      console.error(e);
    }
  };

  const handleComplete = async (questId: string) => {
    try {
      await api.completeQuest(questId);
      setQuests(qs => qs.map(q => q.id === questId ? { ...q, status: "completed" } : q));
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <span style={{ color: "rgba(230,237,243,0.3)" }}>Loading quests...</span>
      </div>
    );
  }

  if (quests.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center w-full min-w-0">
        <div className="text-center">
          <div className="mb-4 opacity-20">
            <svg viewBox="0 0 40 40" width="48" height="48">
              <rect x="8" y="4" width="24" height="32" rx="2" fill="none" stroke="rgba(194,58,46,0.6)" strokeWidth="1.5"/>
              <line x1="13" y1="12" x2="27" y2="12" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
              <line x1="13" y1="18" x2="27" y2="18" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
              <line x1="13" y1="24" x2="22" y2="24" stroke="rgba(194,58,46,0.4)" strokeWidth="1"/>
            </svg>
          </div>
          <h3 className="font-medieval text-lg mb-2" style={{ color: "rgba(194,58,46,0.5)" }}>No Quests Yet</h3>
          <p className="text-sm font-body max-w-xs" style={{ color: "rgba(230,237,243,0.25)" }}>
            Quests will appear as the world&apos;s story unfolds. Keep adventuring!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto overflow-visible p-6 w-full min-w-0 relative">
      {/* Ruins background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-[0.06]"
          style={{ backgroundImage: "url(/images/ruins.jpg)" }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0D1117] via-transparent to-[#0D1117]" />
      </div>
      <div className="mb-6 relative z-10">
        <h2 className="font-medieval text-xl tracking-wider" style={{ color: "rgba(194,58,46,0.8)" }}>Quest Journal</h2>
        <p className="text-xs font-body mt-1" style={{ color: "rgba(230,237,243,0.3)" }}>
          {quests.length} quest{quests.length !== 1 ? "s" : ""}
        </p>
      </div>
      <div className="space-y-4 w-full min-w-0 relative z-10">
        {quests.map((quest) => (
          <div
            key={quest.id}
            className="p-4 w-full min-w-0"
            style={{
              background: "rgba(194, 58, 46, 0.03)",
              borderLeft: "3px solid rgba(194, 58, 46, 0.3)",
              borderRadius: "4px",
            }}
          >
            <div className="flex items-start justify-between mb-2 w-full min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                <h3 className="font-medieval text-sm font-bold" style={{ color: "rgba(194,58,46,0.8)" }}>{quest.title}</h3>
                <span className="text-xs" style={{ color: "rgba(194,58,46,0.4)" }}>
                  {statusLabels[quest.status] || quest.status}
                </span>
              </div>
              <span style={{ color: "rgba(194,58,46,0.5)", fontSize: 11 }}>{quest.difficulty}</span>
            </div>
            <p className="text-xs font-body mb-3" style={{ color: "rgba(230,237,243,0.5)" }}>{quest.description}</p>
            {quest.giver_npc_name && (
              <p className="text-2xs font-body mb-2" style={{ color: "rgba(230,237,243,0.3)" }}>Quest giver: {quest.giver_npc_name}</p>
            )}
            {/* Objectives */}
            <div className="mb-3">
              {quest.objectives.map((obj, i) => (
                <div key={i} className="flex items-center gap-2 text-xs font-body mb-1.5">
                  <span style={{ color: obj.completed ? "rgba(194,58,46,0.6)" : "rgba(194,58,46,0.25)", fontSize: 8 }}>
                    &#9670;
                  </span>
                  <span style={{ color: obj.completed ? "rgba(230,237,243,0.4)" : "rgba(230,237,243,0.6)", textDecoration: obj.completed ? "line-through" : "none" }}>
                    {obj.description}
                  </span>
                </div>
              ))}
            </div>
            {/* Reward */}
            <div className="flex items-center gap-2 text-2xs mb-3" style={{ color: "rgba(230,237,243,0.3)" }}>
              <span>Reward:</span>
              {quest.reward_gold > 0 && <span style={{ color: "rgba(194,58,46,0.6)" }}>{quest.reward_gold} gold</span>}
              {quest.reward_description && <span>{quest.reward_description}</span>}
            </div>
            {/* Actions */}
            <div className="flex gap-2">
              {quest.status === "available" && (
                <button onClick={() => handleAccept(quest.id)} className="btn-stone text-xs px-3 py-1.5">
                  Accept Quest
                </button>
              )}
              {quest.status === "active" && (
                <button onClick={() => handleComplete(quest.id)} className="btn-stone text-xs px-3 py-1.5">
                  Complete Quest
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
