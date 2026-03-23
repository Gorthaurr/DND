"use client";
import { motion } from "framer-motion";

interface Combatant {
  id: string; name: string; type: 'player' | 'npc';
  hp: number; maxHp: number; ac: number;
  initiative: number; isDown: boolean; conditions: string[];
}

interface CombatState {
  inCombat: boolean; round: number; currentTurn: number;
  combatants: Combatant[]; currentCombatant: Combatant;
}

export function InitiativeTracker({ combat, onAttack }: { combat: CombatState | null; onAttack?: (targetId: string) => void }) {
  if (!combat || !combat.inCombat) return null;

  return (
    <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-red-950/40 via-[#161b22] to-red-950/40 border border-red-900/30 rounded-lg p-3 mb-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-red-400 text-sm font-bold animate-pulse">COMBAT</span>
          <span className="text-xs text-gray-500 font-[Cinzel]">Round {combat.round}</span>
        </div>
        <span className="text-xs text-amber-400 font-[Cinzel]">
          {combat.currentCombatant?.name}'s turn
        </span>
      </div>
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {combat.combatants.map((c, i) => {
          const isCurrent = c.id === combat.currentCombatant?.id;
          const hpPct = c.maxHp > 0 ? (c.hp / c.maxHp) * 100 : 0;
          const hpColor = hpPct > 60 ? 'bg-green-500' : hpPct > 30 ? 'bg-yellow-500' : 'bg-red-500';

          return (
            <motion.button key={c.id}
              initial={{ scale: 0.8 }} animate={{ scale: isCurrent ? 1.05 : 1 }}
              onClick={() => c.type === 'npc' && !c.isDown && onAttack?.(c.id)}
              className={`flex-shrink-0 rounded-lg p-2 text-center transition-all min-w-[80px] ${
                isCurrent ? 'bg-amber-900/30 border-2 border-amber-500 shadow-lg shadow-amber-900/20' :
                c.isDown ? 'bg-gray-900/50 border border-gray-800 opacity-40' :
                c.type === 'npc' ? 'bg-red-900/10 border border-red-900/20 hover:border-red-600 cursor-pointer' :
                'bg-blue-900/10 border border-blue-900/20'
              }`}>
              <div className="text-xs font-bold text-gray-200 truncate">{c.name.split(' ')[0]}</div>
              <div className="flex items-center justify-center gap-1 mt-1">
                <span className="text-[10px] text-gray-500">Init</span>
                <span className="text-xs text-amber-400 font-bold">{c.initiative}</span>
              </div>
              {/* HP Bar */}
              <div className="h-1.5 bg-[#0d1117] rounded-full mt-1 overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-500 ${hpColor}`} style={{ width: `${hpPct}%` }} />
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5">
                {c.isDown ? 'DOWN' : `${c.hp}/${c.maxHp}`}
              </div>
              {c.type === 'npc' && !c.isDown && (
                <div className="text-[10px] text-gray-600">AC {c.ac}</div>
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
