"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { InitiativeTracker } from "../components/game/InitiativeTracker";
import { DiceRoller } from "../components/game/DiceRoller";
import { ScenePanel } from "../components/game/ScenePanel";
import { CharacterQuickPanel } from "../components/game/CharacterQuickPanel";
import { CommandHints } from "../components/game/CommandHints";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Tab = 'adventure' | 'map' | 'npcs' | 'quests' | 'puzzles' | 'inventory';

interface ChatMessage { id: string; type: 'player' | 'dm' | 'npc' | 'system'; content: string; npc_name?: string; timestamp: string; }

export default function GamePage() {
  const [tab, setTab] = useState<Tab>('adventure');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [worldState, setWorldState] = useState<any>(null);
  const [lookData, setLookData] = useState<any>(null);
  const [character, setCharacter] = useState<any>(null);
  const [combat, setCombat] = useState<any>(null);
  const [quests, setQuests] = useState<any[]>([]);
  const [puzzlesList, setPuzzlesList] = useState<any[]>([]);
  const [artifacts, setArtifacts] = useState<any[]>([]);
  const [companions, setCompanions] = useState<any[]>([]);
  const [bossState, setBossState] = useState<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load initial data
  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/chat/history`).then(r => r.json()),
      fetch(`${API}/api/world/state`).then(r => r.json()),
      fetch(`${API}/api/look`).then(r => r.json()),
      fetch(`${API}/api/character`).then(r => r.json()),
      fetch(`${API}/api/quests`).then(r => r.json()),
      fetch(`${API}/api/puzzles`).then(r => r.json()),
      fetch(`${API}/api/artifacts`).then(r => r.json()),
      fetch(`${API}/api/companions`).then(r => r.json()),
      fetch(`${API}/api/boss/state`).then(r => r.json()),
    ]).then(([chat, state, look, char, q, pz, art, comp, boss]) => {
      setMessages(chat.messages || []);
      setWorldState(state);
      setLookData(look);
      setCharacter(char);
      setQuests(q.quests || []);
      setPuzzlesList(pz.puzzles || []);
      setArtifacts(art.artifacts || []);
      setCompanions(comp.active || []);
      if (boss.name) setBossState(boss);
    }).catch(() => {});
  }, []);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const sendAction = async (action: string) => {
    if (!action.trim()) return;
    const playerMsg: ChatMessage = { id: String(Date.now()), type: 'player', content: action, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, playerMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/action`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action }) });
      const data = await res.json();
      const dmMsg: ChatMessage = { id: String(Date.now() + 1), type: 'dm', content: data.narration, timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, dmMsg]);
      if (data.combat_data?.combatState) setCombat(data.combat_data.combatState);
      if (data.player_hp !== undefined) setWorldState((s: any) => ({ ...s, player_hp: data.player_hp, player_max_hp: data.player_max_hp }));

      // Refresh look data
      fetch(`${API}/api/look`).then(r => r.json()).then(setLookData);
      fetch(`${API}/api/world/state`).then(r => r.json()).then(setWorldState);
      fetch(`${API}/api/boss/state`).then(r => r.json()).then(b => { if (b.name) setBossState(b); });
    } catch (e) {
      setMessages(prev => [...prev, { id: String(Date.now()), type: 'system', content: 'Connection error. Is the server running?', timestamp: new Date().toISOString() }]);
    }
    setLoading(false);
  };

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'adventure', label: 'Adventure', icon: '⚔' },
    { id: 'map', label: 'Map', icon: '🗺' },
    { id: 'npcs', label: 'NPCs', icon: '👤' },
    { id: 'quests', label: 'Quests', icon: '📜' },
    { id: 'puzzles', label: 'Puzzles', icon: '🧩' },
    { id: 'inventory', label: 'Items', icon: '🎒' },
  ];

  const hpPct = worldState ? ((worldState.player_hp || 10) / (worldState.player_max_hp || 10)) * 100 : 100;

  return (
    <div className="h-screen flex flex-col bg-[#0d1117] text-gray-200 overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 border-b border-[#30363d] bg-[#161b22] shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="font-[Cinzel] text-lg text-amber-400 font-bold tracking-wider">Living World Engine</h1>
          <span className="text-xs text-gray-600">D&D 5e</span>
        </div>

        {/* Nav Tabs */}
        <nav className="flex gap-0.5">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-3 py-1.5 text-xs font-[Cinzel] uppercase tracking-wider rounded transition-colors ${tab === t.id ? 'bg-amber-900/30 text-amber-400 border border-amber-800/40' : 'text-gray-500 hover:text-gray-300'}`}>
              <span className="mr-1">{t.icon}</span>{t.label}
            </button>
          ))}
        </nav>

        {/* Quick Stats + Links */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 text-xs">
            <span className="text-gray-500">Day <span className="text-amber-400 font-bold">{worldState?.day || 1}</span></span>
            <span className="text-amber-500">★{worldState?.player_gold || 0}</span>
            <div className="flex items-center gap-1">
              <span className={`font-bold ${hpPct > 60 ? 'text-green-400' : hpPct > 30 ? 'text-yellow-400' : 'text-red-400'}`}>
                ♥{worldState?.player_hp || '?'}/{worldState?.player_max_hp || '?'}
              </span>
            </div>
          </div>
          <DiceRoller onRoll={(cmd) => sendAction(cmd)} />
          <div className="flex gap-1">
            <Link href="/npcs" className="text-[10px] text-gray-600 hover:text-amber-400 px-1.5 py-0.5 rounded border border-transparent hover:border-[#30363d]">Explorer</Link>
            <Link href="/story" className="text-[10px] text-gray-600 hover:text-amber-400 px-1.5 py-0.5 rounded border border-transparent hover:border-[#30363d]">Story</Link>
            <Link href="/editor" className="text-[10px] text-gray-600 hover:text-amber-400 px-1.5 py-0.5 rounded border border-transparent hover:border-[#30363d]">Editor</Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Left: Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Combat Initiative Tracker */}
          {combat?.inCombat && (
            <div className="px-4 pt-2">
              <InitiativeTracker combat={combat} onAttack={(id) => sendAction(`attack ${id}`)} />
            </div>
          )}

          {/* Boss HUD */}
          {bossState?.name && !bossState.isDefeated && (
            <div className="px-4 pt-2">
              <div className="bg-gradient-to-r from-purple-950/40 via-[#161b22] to-purple-950/40 border border-purple-900/30 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 text-sm font-bold">BOSS</span>
                    <span className="text-sm font-[Cinzel] text-purple-300">{bossState.name}</span>
                    <span className="text-xs text-gray-500">Phase: {bossState.phase?.name}</span>
                  </div>
                  <span className="text-xs text-purple-400">{bossState.hp}/{bossState.maxHp} HP | AC {bossState.ac}</span>
                </div>
                <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                  <motion.div animate={{ width: `${(bossState.hp / bossState.maxHp) * 100}%` }}
                    className="h-full rounded-full bg-gradient-to-r from-purple-600 to-red-600" />
                </div>
                {bossState.phase?.dialogue && <div className="text-xs text-purple-300 italic mt-1">{bossState.phase.dialogue}</div>}
              </div>
            </div>
          )}

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            <AnimatePresence mode="wait">
              {tab === 'adventure' && (
                <motion.div key="adv" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col">
                  {/* Chat Messages */}
                  <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
                    {messages.map(msg => (
                      <motion.div key={msg.id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
                        className={`flex ${msg.type === 'player' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed ${
                          msg.type === 'player' ? 'bg-amber-900/20 border border-amber-800/30 text-amber-200' :
                          msg.type === 'dm' ? 'bg-[#161b22] border border-[#30363d] text-gray-300' :
                          msg.type === 'npc' ? 'bg-blue-900/10 border border-blue-800/20 text-blue-200' :
                          'bg-gray-900/50 border border-gray-800 text-gray-500 text-xs'
                        }`}>
                          {msg.type === 'dm' && <div className="text-[10px] text-amber-600 font-[Cinzel] uppercase mb-1">Dungeon Master</div>}
                          {msg.type === 'npc' && msg.npc_name && <div className="text-[10px] text-blue-500 font-[Cinzel] uppercase mb-1">{msg.npc_name}</div>}
                          <div className="whitespace-pre-wrap">{msg.content}</div>
                        </div>
                      </motion.div>
                    ))}
                    {loading && <div className="text-xs text-gray-600 animate-pulse px-4">The DM is thinking...</div>}
                    <div ref={chatEndRef} />
                  </div>

                  {/* Input */}
                  <div className="shrink-0 border-t border-[#30363d] bg-[#161b22] px-4 py-3">
                    <form onSubmit={e => { e.preventDefault(); sendAction(input); }} className="flex items-center gap-2">
                      <CommandHints onCommand={(cmd) => setInput(cmd + ' ')} />
                      <input type="text" value={input} onChange={e => setInput(e.target.value)} placeholder="What do you do? (attack, cast, go, look, check, roll...)"
                        className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:border-amber-600 focus:outline-none placeholder-gray-600" />
                      <button type="submit" disabled={loading || !input.trim()}
                        className="px-4 py-2.5 bg-amber-800 hover:bg-amber-700 disabled:bg-gray-800 text-white rounded-lg text-sm font-[Cinzel] uppercase tracking-wider transition-colors">
                        Send
                      </button>
                    </form>
                  </div>
                </motion.div>
              )}

              {tab === 'quests' && (
                <motion.div key="quests" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 overflow-y-auto h-full">
                  <h2 className="font-[Cinzel] text-amber-400 text-lg mb-4">Quest Journal</h2>
                  <div className="space-y-3">
                    {quests.map(q => (
                      <div key={q.id} className={`bg-[#161b22] border rounded-lg p-4 ${q.status === 'active' ? 'border-amber-800/30' : q.status === 'completed' ? 'border-green-800/30' : 'border-[#30363d]'}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-[Cinzel] text-sm font-bold text-gray-200">{q.title}</h3>
                          <span className={`text-[10px] uppercase px-2 py-0.5 rounded ${q.status === 'active' ? 'bg-amber-900/30 text-amber-400' : q.status === 'completed' ? 'bg-green-900/30 text-green-400' : 'bg-[#0d1117] text-gray-500'}`}>{q.status}</span>
                        </div>
                        <p className="text-xs text-gray-400">{q.description}</p>
                        {q.objectives && <ul className="mt-2 space-y-0.5">{q.objectives.map((o: string, i: number) => <li key={i} className="text-xs text-gray-500 flex items-center gap-1"><span className="text-amber-600">▸</span>{o}</li>)}</ul>}
                        <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-600">
                          {q.giver && <span>From: {q.giver}</span>}
                          {q.reward && <span className="text-green-600">Reward: {q.reward}</span>}
                          {q.difficulty && <span className={`${q.difficulty === 'hard' ? 'text-red-600' : q.difficulty === 'medium' ? 'text-amber-600' : 'text-green-600'}`}>{q.difficulty}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {tab === 'puzzles' && (
                <motion.div key="puzzles" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 overflow-y-auto h-full">
                  <h2 className="font-[Cinzel] text-amber-400 text-lg mb-4">Puzzles & Riddles</h2>
                  <div className="grid grid-cols-2 gap-3">
                    {puzzlesList.map(p => (
                      <div key={p.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 hover:border-amber-800/30 transition-colors">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">🧩</span>
                          <h3 className="font-[Cinzel] text-sm font-bold text-gray-200">{p.title}</h3>
                        </div>
                        <span className="text-[10px] bg-amber-900/20 text-amber-400 px-1.5 py-0.5 rounded">{p.type}</span>
                        <span className="text-[10px] text-gray-600 ml-2">DC {p.dc}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {tab === 'inventory' && (
                <motion.div key="inv" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 overflow-y-auto h-full">
                  <h2 className="font-[Cinzel] text-amber-400 text-lg mb-4">Artifacts & Items</h2>
                  <div className="grid grid-cols-2 gap-3">
                    {artifacts.slice(0, 12).map(a => {
                      const rarityColors: Record<string, string> = { uncommon: 'text-green-400 border-green-800/30', rare: 'text-blue-400 border-blue-800/30', very_rare: 'text-purple-400 border-purple-800/30', artifact: 'text-amber-400 border-amber-500/30' };
                      return (
                        <div key={a.key} className={`bg-[#161b22] border rounded-lg p-3 ${rarityColors[a.rarity]?.split(' ')[1] || 'border-[#30363d]'}`}>
                          <div className="flex items-center justify-between mb-1">
                            <h3 className={`text-xs font-bold ${rarityColors[a.rarity]?.split(' ')[0] || 'text-gray-300'}`}>{a.name}</h3>
                            <span className="text-[9px] text-gray-600 uppercase">{a.rarity?.replace('_', ' ')}</span>
                          </div>
                          <p className="text-[10px] text-gray-500 leading-relaxed">{a.effect?.substring(0, 100)}...</p>
                          {a.charges > 0 && <span className="text-[9px] text-amber-600 mt-1 inline-block">Charges: {a.charges}</span>}
                        </div>
                      );
                    })}
                  </div>

                  {/* Companions */}
                  {companions.length > 0 && (
                    <>
                      <h2 className="font-[Cinzel] text-amber-400 text-lg mt-6 mb-3">Active Companions</h2>
                      {companions.map((c: any) => (
                        <div key={c.id} className="bg-[#161b22] border border-green-800/20 rounded-lg p-3 mb-2">
                          <div className="text-sm font-bold text-green-400">{c.customName || c.name}</div>
                          <div className="text-xs text-gray-500">HP: {c.currentHp}/{c.hp} | AC: {c.ac} | Speed: {c.speed}</div>
                        </div>
                      ))}
                    </>
                  )}
                </motion.div>
              )}

              {tab === 'npcs' && (
                <motion.div key="npcs" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 text-center">
                  <p className="text-gray-500 mb-4">Full NPC Explorer with psychology profiles</p>
                  <Link href="/npcs" className="px-6 py-3 bg-amber-800 hover:bg-amber-700 text-white rounded-lg font-[Cinzel] transition-colors">
                    Open NPC Explorer
                  </Link>
                </motion.div>
              )}

              {tab === 'map' && (
                <motion.div key="map" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 text-center">
                  <p className="text-gray-500 mb-4">Interactive world map</p>
                  <Link href="/" className="px-6 py-3 bg-amber-800 hover:bg-amber-700 text-white rounded-lg font-[Cinzel] transition-colors">
                    Open World Map
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right Sidebar */}
        <aside className="w-72 border-l border-[#30363d] bg-[#0d1117] overflow-y-auto shrink-0">
          <div className="p-3">
            {/* Scene */}
            {lookData && (
              <ScenePanel
                locationName={lookData.location?.name || 'Unknown'}
                locationType={lookData.location?.type || 'unknown'}
                description={lookData.location?.description || ''}
                npcsPresent={(lookData.npcs || []).map((n: any) => ({ id: n.id, name: n.name, occupation: n.occupation, mood: n.mood || 'content' }))}
                exits={(lookData.exits || []).map((e: any) => ({ id: e.id, name: e.name, distance: e.distance }))}
                onGoTo={(name) => sendAction(`go ${name}`)}
                onTalkTo={(id) => { const npc = lookData.npcs?.find((n: any) => n.id === id); if (npc) sendAction(`talk ${npc.name.split(' ')[0]}`); }}
              />
            )}

            {/* Divider */}
            <div className="h-px bg-[#30363d] my-3" />

            {/* Character */}
            <CharacterQuickPanel character={character} />
          </div>
        </aside>
      </div>
    </div>
  );
}
