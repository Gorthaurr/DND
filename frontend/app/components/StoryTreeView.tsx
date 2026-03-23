"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StoryNode {
  id: string; type: 'event' | 'choice' | 'consequence';
  title: string; description: string; day: number;
  participants: string[]; category: string;
  metadata: any; timestamp: string;
}

interface StoryEdge { from: string; to: string; label: string; }
interface StoryBranch { id: string; name: string; status: string; }

interface StoryTree {
  nodes: StoryNode[]; edges: StoryEdge[]; branches: StoryBranch[];
  stats: { totalEvents: number; choices: number; deaths: number; activeBranches: number; lockedBranches: number };
}

const categoryIcons: Record<string, string> = {
  story_start: '🏰', npc_created: '👤', world_tick: '🌍', player_choice: '🔀',
  chosen_path: '✅', locked_path: '🔒', relationship: '💬', death: '💀',
  combat: '⚔', psych_change: '🧠', shadow_death_cheat: '👻', faction_event: '⚡',
};

const categoryColors: Record<string, string> = {
  story_start: 'border-amber-600 bg-amber-900/20',
  npc_created: 'border-blue-600 bg-blue-900/20',
  world_tick: 'border-gray-600 bg-gray-900/20',
  player_choice: 'border-purple-600 bg-purple-900/20',
  chosen_path: 'border-green-600 bg-green-900/20',
  locked_path: 'border-gray-700 bg-gray-900/10 opacity-50',
  relationship: 'border-cyan-600 bg-cyan-900/20',
  death: 'border-red-600 bg-red-900/20',
  combat: 'border-orange-600 bg-orange-900/20',
  psych_change: 'border-violet-600 bg-violet-900/20',
  shadow_death_cheat: 'border-red-500 bg-red-900/30',
  faction_event: 'border-yellow-600 bg-yellow-900/20',
};

function StoryNodeCard({ node, isSelected, onClick }: { node: StoryNode; isSelected: boolean; onClick: () => void }) {
  const icon = categoryIcons[node.category] || '📌';
  const colorClass = categoryColors[node.category] || 'border-[#30363d] bg-[#161b22]';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`border rounded-lg p-3 cursor-pointer transition-all ${colorClass} ${isSelected ? 'ring-2 ring-amber-500 shadow-lg shadow-amber-900/20' : ''}`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm">{icon}</span>
        <span className="text-xs text-gray-500 font-[Cinzel]">Day {node.day}</span>
        {node.type === 'choice' && <span className="text-xs bg-purple-900/40 text-purple-300 px-1.5 rounded">CHOICE</span>}
        {node.type === 'consequence' && <span className={`text-xs px-1.5 rounded ${node.category === 'chosen_path' ? 'bg-green-900/40 text-green-300' : 'bg-gray-800 text-gray-500'}`}>
          {node.category === 'chosen_path' ? 'TAKEN' : 'LOCKED'}
        </span>}
      </div>
      <h4 className="text-sm font-bold text-gray-200 leading-tight">{node.title}</h4>
      {isSelected && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mt-2">
          <p className="text-xs text-gray-400 leading-relaxed">{node.description}</p>
          {node.participants.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {node.participants.map(p => (
                <span key={p} className="text-xs bg-[#0d1117] border border-[#30363d] rounded px-1.5 py-0.5 text-amber-400">{p}</span>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

export function StoryTreeView() {
  const [tree, setTree] = useState<StoryTree | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [timelineNpc, setTimelineNpc] = useState<string>('');
  const [timeline, setTimeline] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/api/story/tree`).then(r => r.json()).then(setTree);
  }, []);

  useEffect(() => {
    if (timelineNpc) {
      fetch(`${API}/api/story/timeline/${encodeURIComponent(timelineNpc)}`).then(r => r.json()).then(setTimeline);
    } else {
      setTimeline(null);
    }
  }, [timelineNpc]);

  if (!tree) return <div className="text-gray-500 text-center py-10">Loading story tree...</div>;

  const filteredNodes = filter === 'all'
    ? tree.nodes
    : tree.nodes.filter(n => n.category === filter);

  const displayNodes = timeline ? timeline.nodes : filteredNodes;

  // Group by day
  const dayGroups: Record<number, StoryNode[]> = {};
  for (const node of displayNodes) {
    if (!dayGroups[node.day]) dayGroups[node.day] = [];
    dayGroups[node.day].push(node);
  }

  const categories = [...new Set(tree.nodes.map(n => n.category))];

  // Get all participants for timeline search
  const allParticipants = [...new Set(tree.nodes.flatMap(n => n.participants))].filter(p => p !== 'player');

  return (
    <div className="h-full flex flex-col">
      {/* Stats Bar */}
      <div className="flex items-center gap-4 mb-4 p-3 bg-[#161b22] border border-[#30363d] rounded-lg">
        <div className="flex items-center gap-6 text-xs">
          <span className="text-gray-400">Events: <span className="text-amber-400 font-bold">{tree.stats.totalEvents}</span></span>
          <span className="text-gray-400">Choices: <span className="text-purple-400 font-bold">{tree.stats.choices}</span></span>
          <span className="text-gray-400">Deaths: <span className="text-red-400 font-bold">{tree.stats.deaths}</span></span>
          <span className="text-gray-400">Active Branches: <span className="text-green-400 font-bold">{tree.stats.activeBranches}</span></span>
          <span className="text-gray-400">Locked: <span className="text-gray-500 font-bold">{tree.stats.lockedBranches}</span></span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <button onClick={() => { setFilter('all'); setTimelineNpc(''); }}
          className={`px-3 py-1 rounded text-xs transition-colors ${filter === 'all' && !timelineNpc ? 'bg-amber-700 text-white' : 'bg-[#161b22] text-gray-400 hover:text-white border border-[#30363d]'}`}>
          All Events
        </button>
        {categories.map(c => (
          <button key={c} onClick={() => { setFilter(c); setTimelineNpc(''); }}
            className={`px-2 py-1 rounded text-xs transition-colors ${filter === c && !timelineNpc ? 'bg-amber-700 text-white' : 'bg-[#161b22] text-gray-400 hover:text-white border border-[#30363d]'}`}>
            {categoryIcons[c] || '📌'} {c.replace(/_/g, ' ')}
          </button>
        ))}
        <span className="text-gray-600 mx-2">|</span>
        <select value={timelineNpc} onChange={e => { setTimelineNpc(e.target.value); setFilter('all'); }}
          className="bg-[#161b22] border border-[#30363d] rounded px-2 py-1 text-xs text-gray-300">
          <option value="">NPC Timeline...</option>
          {allParticipants.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto pr-2">
        {timeline && (
          <div className="mb-4 bg-blue-900/10 border border-blue-800/20 rounded p-3 text-sm text-blue-300">
            Timeline of <span className="font-bold">{timeline.participant}</span>: {timeline.eventCount} events
          </div>
        )}

        {Object.entries(dayGroups)
          .sort(([a], [b]) => parseInt(a) - parseInt(b))
          .map(([day, nodes]) => (
            <div key={day} className="mb-6">
              {/* Day Header */}
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-900 to-red-900 flex items-center justify-center text-sm font-bold font-[Cinzel] text-amber-300 border-2 border-amber-700">
                  {day}
                </div>
                <div className="h-px flex-1 bg-[#30363d]" />
                <span className="text-xs text-gray-600 font-[Cinzel]">Day {day}</span>
              </div>

              {/* Events for this day */}
              <div className="ml-5 pl-5 border-l-2 border-[#30363d] space-y-2">
                {nodes.map(node => (
                  <StoryNodeCard key={node.id} node={node}
                    isSelected={selectedNode === node.id}
                    onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)} />
                ))}
              </div>
            </div>
          ))}

        {displayNodes.length === 0 && (
          <div className="text-center py-10 text-gray-500">
            <div className="text-4xl mb-3">📜</div>
            <p>No events match this filter.</p>
          </div>
        )}
      </div>
    </div>
  );
}
