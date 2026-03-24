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
  const [tab, setTab] = useState<'psychology' | 'biography' | 'memory' | 'combat' | 'evolution'>('psychology');
  const [shadow, setShadow] = useState<any>(null);
  const [evo, setEvo] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/api/npc-life/${npcId}/deep-profile`).then(r => r.json()).then(setProfile).catch(() => {});
    fetch(`${API}/api/shadow/${npcId}`).then(r => r.json()).then(setShadow).catch(() => {});
    fetch(`${API}/api/npc/${npcId}/observe`).then(r => r.json()).then(setEvo).catch(() => {});
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
    { id: 'evolution' as const, label: 'Evolution', icon: '🧬' },
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
            {tab === 'evolution' && (
              <motion.div key="evolution" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {!evo ? (
                  <div className="text-gray-500 text-center py-8">Loading evolution data...</div>
                ) : (
                  <>
                    {/* Nemesis Panel */}
                    {evo.nemesis && (
                      <div className={`mb-6 p-4 rounded-lg border ${
                        evo.nemesis.stage === 'broken' ? 'bg-gray-900/30 border-gray-700' :
                        evo.nemesis.stage === 'arch_nemesis' ? 'bg-red-900/30 border-red-600 shadow-lg shadow-red-900/20' :
                        evo.nemesis.stage === 'nemesis' ? 'bg-red-900/20 border-red-800' :
                        evo.nemesis.stage === 'rival' ? 'bg-orange-900/20 border-orange-800' :
                        'bg-yellow-900/20 border-yellow-800'
                      }`}>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{
                            evo.nemesis.stage === 'broken' ? '💔' :
                            evo.nemesis.stage === 'arch_nemesis' ? '💀' :
                            evo.nemesis.stage === 'nemesis' ? '🔥' :
                            evo.nemesis.stage === 'rival' ? '⚔' : '😤'
                          }</span>
                          <h3 className="text-sm font-[Cinzel] text-red-400 uppercase tracking-wider">
                            Nemesis: {evo.nemesis.target_name}
                          </h3>
                          <span className={`ml-auto text-xs px-2 py-0.5 rounded font-bold uppercase ${
                            evo.nemesis.stage === 'broken' ? 'bg-gray-800 text-gray-400' :
                            evo.nemesis.stage === 'arch_nemesis' ? 'bg-red-900 text-red-300' :
                            evo.nemesis.stage === 'nemesis' ? 'bg-red-900/50 text-red-400' :
                            evo.nemesis.stage === 'rival' ? 'bg-orange-900/50 text-orange-400' :
                            'bg-yellow-900/50 text-yellow-400'
                          }`}>{evo.nemesis.stage.replace('_', ' ')}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-center text-xs mb-2">
                          <div><span className="text-red-400 font-bold text-lg">{evo.nemesis.defeats_suffered}</span><br /><span className="text-gray-500">Defeats</span></div>
                          <div><span className="text-green-400 font-bold text-lg">{evo.nemesis.victories_achieved}</span><br /><span className="text-gray-500">Victories</span></div>
                          <div><span className="text-amber-400 font-bold text-lg">{evo.nemesis.encounters}</span><br /><span className="text-gray-500">Encounters</span></div>
                        </div>
                        {evo.nemesis.adaptation && (
                          <div className="text-xs text-amber-300 bg-amber-900/20 rounded p-2 mt-2">
                            <span className="text-amber-500 font-bold">Adaptation:</span> {evo.nemesis.adaptation}
                          </div>
                        )}
                        {/* Escalation bar */}
                        <div className="mt-3">
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>Grudge</span><span>Rival</span><span>Nemesis</span><span>Arch</span><span>Broken</span>
                          </div>
                          <div className="h-2 bg-[#1c2128] rounded-full overflow-hidden flex">
                            {['grudge','rival','nemesis','arch_nemesis','broken'].map((s, i) => (
                              <div key={s} className={`flex-1 h-full ${
                                s === evo.nemesis.stage ? (s === 'broken' ? 'bg-gray-500' : 'bg-red-500') :
                                ['grudge','rival','nemesis','arch_nemesis','broken'].indexOf(evo.nemesis.stage) > i ? 'bg-red-900' : 'bg-transparent'
                              } ${i > 0 ? 'border-l border-[#30363d]' : ''}`} />
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Big Five Trait Scale */}
                    {evo.trait_scale && (
                      <>
                        <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Personality Traits (Big Five)</h3>
                        <div className="grid grid-cols-1 gap-2 mb-6">
                          {[
                            { key: 'O', label: 'Openness', color: 'cyan' },
                            { key: 'C', label: 'Conscientiousness', color: 'green' },
                            { key: 'E', label: 'Extraversion', color: 'amber' },
                            { key: 'A', label: 'Agreeableness', color: 'blue' },
                            { key: 'N', label: 'Neuroticism', color: 'red' },
                          ].map(t => (
                            <ProgressBar key={t.key} value={evo.trait_scale[t.key] || 0.5} color={t.color} label={t.label} />
                          ))}
                        </div>
                      </>
                    )}

                    {/* Fears */}
                    {evo.fears && evo.fears.length > 0 && (
                      <>
                        <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Fears</h3>
                        <div className="space-y-2 mb-6">
                          {evo.fears.map((f: any, i: number) => (
                            <div key={i} className="flex items-center gap-3 bg-purple-900/10 border border-purple-900/20 rounded p-2">
                              <span className="text-lg">😰</span>
                              <div className="flex-1">
                                <div className="text-sm text-purple-300 font-bold capitalize">{f.trigger}</div>
                                <div className="text-xs text-gray-500">{f.origin_event}</div>
                              </div>
                              <div className="text-right">
                                <div className={`text-xs font-bold ${f.intensity > 0.7 ? 'text-red-400' : f.intensity > 0.4 ? 'text-orange-400' : 'text-yellow-400'}`}>
                                  {f.intensity > 0.7 ? 'OVERWHELMING' : f.intensity > 0.4 ? 'STRONG' : 'MILD'}
                                </div>
                                <ProgressBar value={f.intensity} color={f.intensity > 0.7 ? 'red' : 'purple'} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </>
                    )}

                    {/* Active Goals */}
                    {evo.active_goals && evo.active_goals.length > 0 && (
                      <>
                        <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Active Goals</h3>
                        <div className="space-y-2 mb-6">
                          {evo.active_goals.map((g: any, i: number) => (
                            <div key={i} className="bg-[#161b22] border border-[#30363d] rounded p-3">
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-gray-200">{g.description}</span>
                                <span className={`text-xs px-2 py-0.5 rounded ${
                                  g.priority > 0.7 ? 'bg-red-900/30 text-red-400' :
                                  g.priority > 0.4 ? 'bg-amber-900/30 text-amber-400' :
                                  'bg-gray-800 text-gray-400'
                                }`}>{g.priority > 0.7 ? 'CRITICAL' : g.priority > 0.4 ? 'IMPORTANT' : 'MINOR'}</span>
                              </div>
                              <ProgressBar value={g.progress || 0} color={g.priority > 0.7 ? 'red' : 'amber'} label={`Progress: ${Math.round((g.progress || 0) * 100)}%`} />
                            </div>
                          ))}
                        </div>
                      </>
                    )}

                    {/* Relationship Tags */}
                    {evo.relationship_tags && Object.keys(evo.relationship_tags).length > 0 && (
                      <>
                        <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Relationship Tags</h3>
                        <div className="space-y-1 mb-6">
                          {Object.entries(evo.relationship_tags).map(([npcId, tags]: [string, any]) => (
                            <div key={npcId} className="flex items-center gap-2 text-sm">
                              <span className="text-gray-400">{npcId}:</span>
                              {(tags as any[]).map((t: any, i: number) => (
                                <span key={i} className={`px-2 py-0.5 rounded text-xs ${
                                  t.tag === 'nemesis' ? 'bg-red-900/30 text-red-400 border border-red-800' :
                                  t.tag === 'enemy' ? 'bg-red-900/20 text-red-300' :
                                  t.tag === 'ally' || t.tag === 'savior' ? 'bg-green-900/20 text-green-300' :
                                  t.tag === 'betrayer' ? 'bg-purple-900/20 text-purple-300' :
                                  'bg-[#1c2128] text-gray-300'
                                }`}>{t.tag} ({t.strength?.toFixed(1)})</span>
                              ))}
                            </div>
                          ))}
                        </div>
                      </>
                    )}

                    {/* Evolution Log */}
                    {evo.evolution_log && evo.evolution_log.length > 0 && (
                      <>
                        <h3 className="text-sm font-[Cinzel] text-gray-400 uppercase tracking-wider mb-3">Evolution Timeline</h3>
                        <div className="space-y-1">
                          {evo.evolution_log.slice().reverse().map((e: any, i: number) => {
                            const typeColors: Record<string, string> = {
                              trait_shift: 'text-cyan-400', fear_acquired: 'text-purple-400', fear_faded: 'text-gray-400',
                              goal_completed: 'text-green-400', goal_failed: 'text-red-400', goal_new: 'text-amber-400',
                              archetype_drift: 'text-yellow-400', relationship_tag: 'text-blue-400',
                              nemesis_escalation: 'text-red-500', nemesis_broken: 'text-gray-500', nemesis_adaptation: 'text-orange-400',
                            };
                            return (
                              <div key={i} className="flex gap-2 text-xs border-l-2 border-[#30363d] pl-3 py-1">
                                <span className="text-gray-600 w-10">D{e.day}</span>
                                <span className={`w-24 ${typeColors[e.change_type] || 'text-gray-400'}`}>[{e.change_type}]</span>
                                <span className="text-gray-300 flex-1">{e.description}</span>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    )}

                    {/* No evolution data */}
                    {(!evo.fears || evo.fears.length === 0) && (!evo.active_goals || evo.active_goals.length === 0) && !evo.nemesis && (!evo.evolution_log || evo.evolution_log.length === 0) && (
                      <div className="text-gray-500 text-center py-8">No evolution data yet. Events will shape this NPC over time.</div>
                    )}
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}
