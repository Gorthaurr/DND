"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DeepProfile {
  id: string; name: string; occupation: string; age: number; alive: boolean;
  accentuation: string; accentuationTraits: string[]; jungType: string;
  maslowLevel: string; freudBalance: { id: number; ego: number; superego: number };
  berneState: string; defenses: string[]; emotionalStability: number;
  empathy: number; willpower: number; psychopathyPotential: number;
  currentMood: string; stressLevel: number; innerConflicts: string[];
  origin: string; originTraits: string[]; physiology: string;
  parents: { type: string; description: string };
  childhood: { age: number; event: string; impact: string; category: string }[];
  formativeEvents: { age: number; event: string; impact: string }[];
  disability: { key: string; name: string; description: string; story?: any };
  narrativeSummary: string; goals: string[];
  physicalState: { disability: string; injuries: any[]; conditions: string[] };
  currentActivity: string;
  recentMemories: { content: string; day: number; importance: number; emotion: string }[];
  relationships: { targetId: string; targetName: string; sentiment: number; history: any[] }[];
  recentActions: { day: number; action: string; motivation: string; reasoning: string }[];
  speechStyle: string; underStress: string;
  level: number; class_id: string;
  ability_scores: Record<string, number>;
  hp: number; max_hp: number; ac: number;
}

function ProgressBar({ value, max = 1, color = "amber", label }: { value: number; max?: number; color?: string; label?: string }) {
  const pct = Math.round((value / max) * 100);
  const colors: Record<string, string> = {
    amber: "bg-amber-500", red: "bg-red-500", green: "bg-green-500",
    blue: "bg-blue-500", purple: "bg-purple-500", cyan: "bg-cyan-500",
  };
  return (
    <div className="mb-2">
      {label && <div className="flex justify-between text-xs mb-1"><span className="text-gray-400">{label}</span><span className="text-gray-300">{pct}%</span></div>}
      <div className="h-2 bg-[#1c2128] rounded-full overflow-hidden">
        <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8 }}
          className={`h-full rounded-full ${colors[color] || colors.amber}`} />
      </div>
    </div>
  );
}

function StatBlock({ label, value, icon }: { label: string; value: string | number; icon?: string }) {
  return (
    <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-center">
      {icon && <div className="text-lg mb-1">{icon}</div>}
      <div className="text-lg font-bold font-[Cinzel] text-amber-400">{value}</div>
      <div className="text-xs text-gray-500 uppercase tracking-wider">{label}</div>
    </div>
  );
}

function TimelineEvent({ event, index }: { event: any; index: number }) {
  const categoryColors: Record<string, string> = {
    happy: 'border-green-600', traumatic: 'border-red-600', formative: 'border-amber-600',
  };
  return (
    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}
      className={`relative pl-6 pb-4 border-l-2 ${categoryColors[event.category] || 'border-[#30363d]'}`}>
      <div className="absolute -left-[7px] top-0 w-3 h-3 rounded-full bg-[#161b22] border-2 border-amber-600" />
      <div className="text-xs text-amber-400 font-[Cinzel] mb-1">Age {event.age}</div>
      <div className="text-sm text-gray-200">{event.event}</div>
      <div className="text-xs text-gray-500 mt-1 italic">{event.impact}</div>
    </motion.div>
  );
}

export function NPCDeepProfile({ npcId, onClose }: { npcId: string; onClose: () => void }) {
  const [profile, setProfile] = useState<DeepProfile | null>(null);
  const [tab, setTab] = useState<'psychology' | 'biography' | 'memory' | 'combat'>('psychology');
  const [shadow, setShadow] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/api/npc-life/${npcId}/deep-profile`).then(r => r.json()).then(setProfile);
    fetch(`${API}/api/shadow/${npcId}`).then(r => r.json()).then(setShadow);
  }, [npcId]);

  if (!profile) return <div className="flex items-center justify-center h-64 text-gray-500">Loading...</div>;

  const moodColors: Record<string, string> = {
    content: 'text-green-400', excited: 'text-yellow-400', angry: 'text-red-400',
    sad: 'text-blue-400', fearful: 'text-purple-400', anxious: 'text-orange-400',
    scheming: 'text-amber-400', hopeful: 'text-cyan-400',
  };

  const tabs = [
    { id: 'psychology' as const, label: 'Psychology', icon: '🧠' },
    { id: 'biography' as const, label: 'Biography', icon: '📜' },
    { id: 'memory' as const, label: 'Memory', icon: '💭' },
    { id: 'combat' as const, label: 'Combat', icon: '⚔' },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
        className="bg-[#0d1117] border border-[#30363d] rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl">

        {/* Header */}
        <div className="relative p-6 border-b border-[#30363d] bg-gradient-to-r from-[#161b22] to-[#0d1117]">
          <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-white text-xl">✕</button>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-amber-900 to-red-900 flex items-center justify-center text-2xl font-bold font-[Cinzel] text-amber-300">
              {profile.name[0]}
            </div>
            <div>
              <h2 className="text-2xl font-[Cinzel] text-amber-400 font-bold">{profile.name}</h2>
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <span>{profile.age} y/o {profile.occupation}</span>
                <span>|</span>
                <span className="text-xs bg-[#1c2128] px-2 py-0.5 rounded border border-[#30363d]">{profile.accentuation}</span>
                <span className={`font-bold ${moodColors[profile.currentMood] || 'text-gray-300'}`}>{profile.currentMood}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">{profile.origin} | Maslow: {profile.maslowLevel} | Jung: {profile.jungType}</div>
            </div>
          </div>
          {shadow?.isShadow && (
            <div className="mt-3 bg-red-900/20 border border-red-800/30 rounded px-3 py-1.5 text-xs text-red-400 flex items-center gap-2">
              <span>💀</span> SHADOW — {shadow.obsessionName}: {shadow.obsessionDescription} | Encounters: {shadow.encounters} | Deaths: {shadow.npcDeaths}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[#30363d] bg-[#161b22]/50">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex-1 px-4 py-3 text-xs font-[Cinzel] uppercase tracking-wider transition-colors ${tab === t.id ? 'text-amber-400 border-b-2 border-amber-500 bg-[#0d1117]' : 'text-gray-500 hover:text-gray-300'}`}>
              <span className="mr-1">{t.icon}</span> {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[55vh]">
          <AnimatePresence mode="wait">
            {tab === 'psychology' && (
              <motion.div key="psych" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* Freud Balance */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Psychic Structure (Freud)</h3>
                <div className="grid grid-cols-3 gap-3 mb-6">
                  <div className="text-center">
                    <div className="text-xs text-red-400 mb-1">ID (Desire)</div>
                    <div className="text-xl font-bold text-red-400">{Math.round(profile.freudBalance.id * 100)}%</div>
                    <ProgressBar value={profile.freudBalance.id} color="red" />
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-green-400 mb-1">EGO (Rational)</div>
                    <div className="text-xl font-bold text-green-400">{Math.round(profile.freudBalance.ego * 100)}%</div>
                    <ProgressBar value={profile.freudBalance.ego} color="green" />
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-blue-400 mb-1">SUPEREGO (Moral)</div>
                    <div className="text-xl font-bold text-blue-400">{Math.round(profile.freudBalance.superego * 100)}%</div>
                    <ProgressBar value={profile.freudBalance.superego} color="blue" />
                  </div>
                </div>

                {/* Psychological Metrics */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Psychological Metrics</h3>
                <div className="grid grid-cols-2 gap-x-6 mb-6">
                  <ProgressBar value={profile.emotionalStability} color="cyan" label="Emotional Stability" />
                  <ProgressBar value={profile.empathy} color="green" label="Empathy" />
                  <ProgressBar value={profile.willpower} color="amber" label="Willpower" />
                  <ProgressBar value={profile.stressLevel} color="red" label="Stress Level" />
                  {profile.psychopathyPotential > 0.1 && (
                    <ProgressBar value={profile.psychopathyPotential} color="purple" label="Psychopathy Potential" />
                  )}
                </div>

                {/* Traits & Defenses */}
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2">Personality Traits</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.accentuationTraits.map(t => (
                        <span key={t} className="px-2 py-0.5 bg-amber-900/20 border border-amber-800/30 rounded text-xs text-amber-300">{t}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2">Defense Mechanisms</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.defenses.map(d => (
                        <span key={d} className="px-2 py-0.5 bg-purple-900/20 border border-purple-800/30 rounded text-xs text-purple-300">{d}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Goals */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2 mt-6">Goals (Maslow: {profile.maslowLevel})</h3>
                <ul className="space-y-1">
                  {profile.goals.map((g, i) => (
                    <li key={i} className="text-sm text-gray-300 flex items-center gap-2">
                      <span className="text-amber-600">▸</span> {g}
                    </li>
                  ))}
                </ul>

                {/* Speech */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2 mt-6">Speech Style</h3>
                <p className="text-sm text-gray-400 italic bg-[#161b22] p-3 rounded border border-[#30363d]">{profile.speechStyle}</p>

                {/* Inner Conflicts */}
                {profile.innerConflicts.length > 0 && (
                  <>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2 mt-6">Inner Conflicts</h3>
                    {profile.innerConflicts.map((c, i) => (
                      <div key={i} className="text-sm text-red-300 bg-red-900/10 p-2 rounded border border-red-900/20 mb-1">{c}</div>
                    ))}
                  </>
                )}
              </motion.div>
            )}

            {tab === 'biography' && (
              <motion.div key="bio" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* Summary */}
                <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 mb-6">
                  <p className="text-sm text-gray-300 italic">{profile.narrativeSummary}</p>
                </div>

                {/* Origin */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2">Origin: {profile.origin}</h3>
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {profile.originTraits.map(t => (
                    <span key={t} className="px-2 py-0.5 bg-blue-900/20 border border-blue-800/30 rounded text-xs text-blue-300">{t}</span>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mb-6">{profile.physiology}</p>

                {/* Parents */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2">Parents</h3>
                <p className="text-sm text-gray-300 mb-6 bg-[#161b22] p-3 rounded border border-[#30363d]">
                  <span className="text-amber-400 capitalize">{profile.parents.type}</span>: {profile.parents.description}
                </p>

                {/* Childhood Timeline */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Childhood</h3>
                <div className="ml-2 mb-6">
                  {profile.childhood.map((e, i) => <TimelineEvent key={i} event={e} index={i} />)}
                </div>

                {/* Formative Events */}
                {profile.formativeEvents.length > 0 && (
                  <>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Formative Events</h3>
                    <div className="ml-2 mb-6">
                      {profile.formativeEvents.map((e, i) => <TimelineEvent key={i} event={{ ...e, category: 'formative' }} index={i} />)}
                    </div>
                  </>
                )}

                {/* Disability */}
                {profile.disability.key !== 'none' && (
                  <>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2">Physical Condition</h3>
                    <div className="bg-red-900/10 border border-red-900/20 rounded p-3 text-sm">
                      <span className="text-red-400 font-bold">{profile.disability.name}</span>: {profile.disability.description}
                      {profile.disability.story && <p className="text-xs text-gray-500 mt-1">{profile.disability.story.description}</p>}
                    </div>
                  </>
                )}
              </motion.div>
            )}

            {tab === 'memory' && (
              <motion.div key="memory" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Memories ({profile.recentMemories.length})</h3>
                <div className="space-y-2">
                  {profile.recentMemories.slice().reverse().map((m, i) => (
                    <div key={i} className="bg-[#161b22] border border-[#30363d] rounded p-3 flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 text-center">
                        <div className="text-lg">{m.emotion === 'angry' ? '😡' : m.emotion === 'sad' ? '😢' : m.emotion === 'fearful' ? '😰' : m.emotion === 'happy' ? '😊' : '📝'}</div>
                        <div className="text-xs text-gray-600">D{m.day}</div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-300">{m.content}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <ProgressBar value={m.importance} color={m.importance > 0.7 ? 'red' : 'amber'} />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Relationships */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3 mt-6">Relationships</h3>
                <div className="space-y-2">
                  {profile.relationships.map((r, i) => (
                    <div key={i} className="flex items-center gap-3 bg-[#161b22] border border-[#30363d] rounded p-2">
                      <div className="w-8 h-8 rounded-full bg-[#0d1117] border border-[#30363d] flex items-center justify-center text-xs font-bold text-amber-400">
                        {(r.targetName || '?')[0]}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300">{r.targetName}</div>
                        <div className="h-1.5 bg-[#1c2128] rounded-full mt-1 overflow-hidden">
                          <div className={`h-full rounded-full ${r.sentiment > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                            style={{ width: `${Math.abs(r.sentiment) * 100}%`, marginLeft: r.sentiment < 0 ? 'auto' : 0 }} />
                        </div>
                      </div>
                      <div className={`text-xs font-bold ${r.sentiment > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {r.sentiment > 0 ? '+' : ''}{r.sentiment.toFixed(1)}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {tab === 'combat' && (
              <motion.div key="combat" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* D&D Stats */}
                <div className="grid grid-cols-4 gap-3 mb-6">
                  <StatBlock label="Level" value={profile.level} icon="⚡" />
                  <StatBlock label="HP" value={`${profile.hp}/${profile.max_hp}`} icon="❤" />
                  <StatBlock label="AC" value={profile.ac} icon="🛡" />
                  <StatBlock label="Class" value={profile.class_id} icon="⚔" />
                </div>

                {/* Ability Scores */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Ability Scores</h3>
                <div className="grid grid-cols-6 gap-2 mb-6">
                  {['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'].map(stat => (
                    <div key={stat} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 text-center">
                      <div className="text-xs text-amber-400 font-bold mb-1">{stat}</div>
                      <div className="text-2xl font-bold text-gray-200">{profile.ability_scores[stat] || 10}</div>
                      <div className="text-xs text-gray-500">{Math.floor(((profile.ability_scores[stat] || 10) - 10) / 2) >= 0 ? '+' : ''}{Math.floor(((profile.ability_scores[stat] || 10) - 10) / 2)}</div>
                    </div>
                  ))}
                </div>

                {/* Shadow Combat Info */}
                {shadow?.traitsDetails?.length > 0 && (
                  <>
                    <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Shadow Traits</h3>
                    <div className="space-y-2">
                      {shadow.traitsDetails.map((t: any, i: number) => (
                        <div key={i} className="bg-red-900/10 border border-red-900/20 rounded p-3">
                          <div className="text-sm font-bold text-red-400">{t.name}</div>
                          <div className="text-xs text-gray-400">{t.description}</div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {/* Under Stress */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-2 mt-6">Behavior Under Stress</h3>
                <p className="text-sm text-gray-400 bg-[#161b22] p-3 rounded border border-[#30363d]">{profile.underStress}</p>

                {/* Recent Actions */}
                <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3 mt-6">Recent Actions</h3>
                <div className="space-y-1">
                  {profile.recentActions.map((a, i) => (
                    <div key={i} className="text-xs text-gray-400 flex gap-2">
                      <span className="text-amber-600 w-12">Day {a.day}</span>
                      <span className="text-gray-300">{a.action}</span>
                      <span className="text-gray-600">— {a.motivation}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}
