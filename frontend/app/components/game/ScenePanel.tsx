"use client";
import { motion } from "framer-motion";

interface SceneProps {
  locationName: string;
  locationType: string;
  description: string;
  npcsPresent: { id: string; name: string; occupation: string; mood: string }[];
  exits: { id: string; name: string; distance: number }[];
  onGoTo?: (locationName: string) => void;
  onTalkTo?: (npcId: string) => void;
}

const locationImages: Record<string, string> = {
  tavern: '🍺', market: '🏪', smithy: '🔨', square: '🏛', forest: '🌲',
  chapel: '⛪', farm: '🌾', barracks: '⚔', mill: '🏭', ruins: '🏚',
  cave: '🕳', tower: '🗼', dungeon: '💀', camp: '🏕',
};

const moodEmojis: Record<string, string> = {
  content: '😌', excited: '😄', angry: '😡', sad: '😢',
  fearful: '😰', anxious: '😟', scheming: '🤨', hopeful: '🌟',
};

export function ScenePanel({ locationName, locationType, description, npcsPresent, exits, onGoTo, onTalkTo }: SceneProps) {
  const icon = locationImages[locationType] || '📍';

  return (
    <div className="space-y-3">
      {/* Location Header */}
      <div className="bg-gradient-to-br from-[#161b22] to-[#0d1117] border border-[#30363d] rounded-lg p-4">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">{icon}</span>
          <div>
            <h3 className="font-[Cinzel] text-amber-400 font-bold text-sm">{locationName}</h3>
            <span className="text-[10px] text-gray-600 uppercase tracking-wider">{locationType}</span>
          </div>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">{description}</p>
      </div>

      {/* NPCs Present */}
      {npcsPresent.length > 0 && (
        <div>
          <h4 className="text-[10px] text-gray-600 font-[Cinzel] uppercase tracking-wider mb-1.5 px-1">People Here</h4>
          <div className="space-y-1">
            {npcsPresent.map(npc => (
              <motion.button key={npc.id} whileHover={{ x: 4 }}
                onClick={() => onTalkTo?.(npc.id)}
                className="w-full flex items-center gap-2 px-3 py-2 bg-[#161b22] border border-[#30363d] rounded-lg text-left hover:border-amber-800/40 transition-colors group">
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-900/60 to-red-900/60 flex items-center justify-center text-xs font-bold text-amber-300 shrink-0">
                  {npc.name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-gray-200 truncate group-hover:text-amber-400 transition-colors">{npc.name}</div>
                  <div className="text-[10px] text-gray-600">{npc.occupation}</div>
                </div>
                <span className="text-sm" title={npc.mood}>{moodEmojis[npc.mood] || '😐'}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Exits */}
      {exits.length > 0 && (
        <div>
          <h4 className="text-[10px] text-gray-600 font-[Cinzel] uppercase tracking-wider mb-1.5 px-1">Exits</h4>
          <div className="grid grid-cols-2 gap-1">
            {exits.map(exit => (
              <motion.button key={exit.id} whileHover={{ scale: 1.02 }}
                onClick={() => onGoTo?.(exit.name)}
                className="flex items-center gap-2 px-2.5 py-1.5 bg-[#161b22] border border-[#30363d] rounded text-left hover:border-green-800/40 hover:bg-green-900/5 transition-colors">
                <span className="text-green-600 text-xs">→</span>
                <span className="text-xs text-gray-300 truncate">{exit.name}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
