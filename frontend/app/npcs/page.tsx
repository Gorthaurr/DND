"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { NPCDeepProfile } from "../components/NPCDeepProfile";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface NPCSummary {
  id: string; name: string; occupation: string; mood: string;
  alive: boolean; location_id: string; accentuation: string;
  maslowLevel: string; origin: string; disability: string;
  stressLevel: number; currentActivity: string;
}

const moodEmojis: Record<string, string> = {
  content: '😌', excited: '😄', angry: '😡', sad: '😢',
  fearful: '😰', anxious: '😟', scheming: '🤨', hopeful: '🌟',
};

const moodColors: Record<string, string> = {
  content: 'text-green-400', excited: 'text-yellow-400', angry: 'text-red-400',
  sad: 'text-blue-400', fearful: 'text-purple-400', anxious: 'text-orange-400',
  scheming: 'text-amber-400', hopeful: 'text-cyan-400',
};

export default function NPCExplorerPage() {
  const [npcs, setNpcs] = useState<NPCSummary[]>([]);
  const [selectedNpc, setSelectedNpc] = useState<string | null>(null);
  const [filter, setFilter] = useState('');
  const [nemeses, setNemeses] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [genForm, setGenForm] = useState({ name: '', occupation: 'villager', origin: 'medieval_earth', accentuation: '', disability: 'none', age: 30 });

  useEffect(() => {
    fetch(`${API}/api/npc-life/all`).then(r => r.json()).then(d => setNpcs(d.npcs || []));
    fetch(`${API}/api/shadow/all`).then(r => r.json()).then(d => setNemeses(d.nemeses || []));
  }, []);

  const generateNPC = async () => {
    setGenerating(true);
    const res = await fetch(`${API}/api/npc-life/generate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(genForm),
    });
    const npc = await res.json();
    setNpcs(prev => [...prev, { id: npc.id, name: npc.name || genForm.name, occupation: genForm.occupation, mood: npc.mood, alive: true, location_id: 'loc-tavern', accentuation: npc.accentuation, maslowLevel: npc.maslowLevel, origin: npc.origin, disability: npc.disability, stressLevel: 0.3, currentActivity: 'idle' }]);
    setGenerating(false);
  };

  const tickWorld = async () => {
    await fetch(`${API}/api/npc-life/tick`, { method: 'POST' });
    const d = await fetch(`${API}/api/npc-life/all`).then(r => r.json());
    setNpcs(d.npcs || []);
  };

  const filteredNpcs = npcs.filter(n =>
    !filter || n.name.toLowerCase().includes(filter.toLowerCase()) ||
    n.accentuation.toLowerCase().includes(filter.toLowerCase()) ||
    n.origin.toLowerCase().includes(filter.toLowerCase())
  );

  const shadowIds = new Set(nemeses.map(n => n.npcId));

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-200">
      {/* Header */}
      <header className="border-b border-[#30363d] bg-[#161b22]">
        <div className="max-w-[1600px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-gray-400 hover:text-amber-400 text-sm transition-colors">← Back</a>
            <h1 className="font-[Cinzel] text-xl text-amber-400 font-bold">NPC Explorer</h1>
            <span className="text-xs text-gray-500">{npcs.length} NPCs | {nemeses.length} Nemeses</span>
          </div>
          <div className="flex gap-2">
            <button onClick={tickWorld} className="text-xs bg-amber-800 hover:bg-amber-700 text-white px-3 py-1.5 rounded font-[Cinzel] transition-colors">
              Tick World
            </button>
            <a href="/story" className="text-xs text-gray-400 hover:text-amber-400 bg-[#0d1117] border border-[#30363d] px-3 py-1.5 rounded transition-colors">Story Tree</a>
            <a href="/editor" className="text-xs text-gray-400 hover:text-amber-400 bg-[#0d1117] border border-[#30363d] px-3 py-1.5 rounded transition-colors">Editor</a>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto p-6">
        <div className="flex gap-6">
          {/* Left: NPC Grid */}
          <div className="flex-1">
            {/* Search */}
            <input type="text" value={filter} onChange={e => setFilter(e.target.value)}
              placeholder="Search NPCs by name, accentuation, origin..."
              className="w-full mb-4 bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:border-amber-600 focus:outline-none placeholder-gray-600" />

            {/* NPC Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredNpcs.map((npc, i) => (
                <motion.div key={npc.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.02 }}
                  onClick={() => setSelectedNpc(npc.id)}
                  className={`bg-[#161b22] border rounded-lg p-4 cursor-pointer transition-all hover:border-amber-700 hover:shadow-lg hover:shadow-amber-900/10 ${shadowIds.has(npc.id) ? 'border-red-800' : 'border-[#30363d]'} ${!npc.alive ? 'opacity-40' : ''}`}>

                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-900/80 to-red-900/80 flex items-center justify-center text-lg font-bold font-[Cinzel] text-amber-300">
                      {npc.name[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-gray-200 truncate">{npc.name}</h3>
                        {shadowIds.has(npc.id) && <span className="text-xs bg-red-900/40 text-red-400 px-1.5 rounded">SHADOW</span>}
                        {!npc.alive && <span className="text-xs bg-gray-800 text-gray-500 px-1.5 rounded">DEAD</span>}
                      </div>
                      <div className="text-xs text-gray-500">{npc.occupation}</div>
                    </div>
                    <div className="text-xl" title={npc.mood}>{moodEmojis[npc.mood] || '😐'}</div>
                  </div>

                  <div className="flex flex-wrap gap-1 text-xs">
                    <span className="bg-amber-900/20 border border-amber-800/30 text-amber-300 px-1.5 py-0.5 rounded">{npc.accentuation}</span>
                    <span className="bg-blue-900/20 border border-blue-800/30 text-blue-300 px-1.5 py-0.5 rounded">{npc.maslowLevel}</span>
                    {npc.origin !== 'Medieval Earth' && (
                      <span className="bg-purple-900/20 border border-purple-800/30 text-purple-300 px-1.5 py-0.5 rounded">{npc.origin}</span>
                    )}
                    {npc.disability !== 'No Disability' && (
                      <span className="bg-red-900/20 border border-red-800/30 text-red-300 px-1.5 py-0.5 rounded">{npc.disability}</span>
                    )}
                  </div>

                  {/* Stress bar */}
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                      <span>Stress</span>
                      <span>{Math.round(npc.stressLevel * 100)}%</span>
                    </div>
                    <div className="h-1 bg-[#0d1117] rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${npc.stressLevel > 0.7 ? 'bg-red-500' : npc.stressLevel > 0.4 ? 'bg-amber-500' : 'bg-green-500'}`}
                        style={{ width: `${npc.stressLevel * 100}%` }} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right: Generator */}
          <div className="w-80 shrink-0">
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 sticky top-6">
              <h3 className="font-[Cinzel] text-amber-400 text-sm uppercase tracking-wider mb-4">Generate NPC</h3>

              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Name</label>
                  <input type="text" value={genForm.name} onChange={e => setGenForm({ ...genForm, name: e.target.value })}
                    placeholder="NPC name..." className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Occupation</label>
                  <select value={genForm.occupation} onChange={e => setGenForm({ ...genForm, occupation: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200">
                    {['villager','blacksmith','merchant','healer','guard','farmer','priest','hunter','thief','philosopher','warrior','bard','innkeeper','alchemist'].map(o =>
                      <option key={o} value={o}>{o}</option>
                    )}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Origin World</label>
                  <select value={genForm.origin} onChange={e => setGenForm({ ...genForm, origin: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200">
                    {['medieval_earth','nitrogen_world','high_gravity','low_gravity','toxic_atmosphere','eternal_night','water_world','fey_realm','underdark','astral_plane'].map(o =>
                      <option key={o} value={o}>{o.replace(/_/g, ' ')}</option>
                    )}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Accentuation (Leonhard)</label>
                  <select value={genForm.accentuation} onChange={e => setGenForm({ ...genForm, accentuation: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200">
                    <option value="">Random</option>
                    {['demonstrative','stuck','pedantic','excitable','hyperthymic','dysthymic','anxious','emotive','cyclothymic','exalted'].map(a =>
                      <option key={a} value={a}>{a}</option>
                    )}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Disability</label>
                  <select value={genForm.disability} onChange={e => setGenForm({ ...genForm, disability: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200">
                    {['none','blindness','deafness','lost_arm','lost_leg','chronic_pain','scarring','mental_illness'].map(d =>
                      <option key={d} value={d}>{d.replace(/_/g, ' ')}</option>
                    )}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Age</label>
                  <input type="number" value={genForm.age} onChange={e => setGenForm({ ...genForm, age: parseInt(e.target.value) || 30 })}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-gray-200" />
                </div>

                <button onClick={generateNPC} disabled={generating || !genForm.name}
                  className="w-full py-2 bg-amber-700 hover:bg-amber-600 disabled:bg-gray-700 text-white rounded text-sm font-[Cinzel] uppercase tracking-wider transition-colors">
                  {generating ? 'Generating...' : 'Generate NPC'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Deep Profile Modal */}
      {selectedNpc && (
        <NPCDeepProfile npcId={selectedNpc} onClose={() => setSelectedNpc(null)} />
      )}
    </div>
  );
}
