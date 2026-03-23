"use client";
import { motion } from "framer-motion";

interface CharacterData {
  name: string; race: string; class: string; level: number;
  hp: number; max_hp: number; ac: number; xp: number;
  ability_scores: Record<string, number>;
  gold: number; silver: number; copper: number;
  proficiency_bonus: number;
  equipment: { name: string; type: string }[];
  spell_slots?: Record<number, number>;
}

function AbilityScore({ name, value }: { name: string; value: number }) {
  const mod = Math.floor((value - 10) / 2);
  return (
    <div className="text-center">
      <div className="text-[9px] text-amber-600 font-bold">{name}</div>
      <div className="text-sm font-bold text-gray-200">{value}</div>
      <div className="text-[10px] text-gray-500">{mod >= 0 ? '+' : ''}{mod}</div>
    </div>
  );
}

export function CharacterQuickPanel({ character }: { character: CharacterData | null }) {
  if (!character) {
    return (
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
        <span className="text-2xl opacity-15 block mb-2">⚔</span>
        <p className="text-xs text-gray-500 mb-2">No character</p>
        <a href="/character" className="text-xs text-amber-400 hover:underline">Create Character</a>
      </div>
    );
  }

  const hpPct = character.max_hp > 0 ? (character.hp / character.max_hp) * 100 : 0;

  return (
    <div className="space-y-3">
      {/* Character Header */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-800 to-red-900 flex items-center justify-center text-lg font-bold font-[Cinzel] text-amber-200 border-2 border-amber-700/50">
            {character.name[0]}
          </div>
          <div>
            <div className="text-sm font-bold font-[Cinzel] text-gray-200">{character.name}</div>
            <div className="text-[10px] text-gray-500">Lv.{character.level} {character.race} {character.class}</div>
          </div>
        </div>

        {/* HP Bar */}
        <div className="mb-2">
          <div className="flex justify-between text-[10px] mb-0.5">
            <span className="text-gray-500">HP</span>
            <span className={`font-bold ${hpPct > 60 ? 'text-green-400' : hpPct > 30 ? 'text-yellow-400' : 'text-red-400'}`}>
              {character.hp}/{character.max_hp}
            </span>
          </div>
          <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
            <motion.div animate={{ width: `${hpPct}%` }} transition={{ duration: 0.5 }}
              className={`h-full rounded-full ${hpPct > 60 ? 'bg-green-500' : hpPct > 30 ? 'bg-yellow-500' : 'bg-red-500'}`} />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-[#0d1117] rounded p-1.5">
            <div className="text-[9px] text-gray-600">AC</div>
            <div className="text-sm font-bold text-amber-400">{character.ac}</div>
          </div>
          <div className="bg-[#0d1117] rounded p-1.5">
            <div className="text-[9px] text-gray-600">Prof</div>
            <div className="text-sm font-bold text-blue-400">+{character.proficiency_bonus}</div>
          </div>
          <div className="bg-[#0d1117] rounded p-1.5">
            <div className="text-[9px] text-gray-600">XP</div>
            <div className="text-sm font-bold text-purple-400">{character.xp}</div>
          </div>
        </div>
      </div>

      {/* Ability Scores */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
        <div className="text-[9px] text-gray-600 font-[Cinzel] uppercase tracking-wider mb-2">Abilities</div>
        <div className="grid grid-cols-6 gap-1">
          {['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'].map(stat => (
            <AbilityScore key={stat} name={stat} value={character.ability_scores[stat] || 10} />
          ))}
        </div>
      </div>

      {/* Gold */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
        <div className="text-[9px] text-gray-600 font-[Cinzel] uppercase tracking-wider mb-2">Wealth</div>
        <div className="flex items-center gap-3">
          <span className="text-xs"><span className="text-amber-400">★</span> {character.gold}g</span>
          <span className="text-xs"><span className="text-gray-400">●</span> {character.silver}s</span>
          <span className="text-xs"><span className="text-orange-700">●</span> {character.copper}c</span>
        </div>
      </div>

      {/* Equipment */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
        <div className="text-[9px] text-gray-600 font-[Cinzel] uppercase tracking-wider mb-2">Equipment</div>
        <div className="space-y-0.5">
          {character.equipment.map((item, i) => (
            <div key={i} className="text-[11px] text-gray-400 flex items-center gap-1.5">
              <span className="text-[10px]">{item.type === 'weapon' ? '⚔' : item.type === 'armor' ? '🛡' : '📦'}</span>
              {item.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
