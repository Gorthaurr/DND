"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RollResult {
  total: number; rolls: number[]; modifier: number; notation: string;
  breakdown?: string; isCritSuccess?: boolean; isCritFail?: boolean;
  skill?: string; ability?: string;
}

const DICE = [
  { sides: 4, color: 'from-purple-600 to-purple-800', label: 'D4' },
  { sides: 6, color: 'from-blue-600 to-blue-800', label: 'D6' },
  { sides: 8, color: 'from-green-600 to-green-800', label: 'D8' },
  { sides: 10, color: 'from-yellow-600 to-yellow-800', label: 'D10' },
  { sides: 12, color: 'from-orange-600 to-orange-800', label: 'D12' },
  { sides: 20, color: 'from-red-600 to-red-800', label: 'D20' },
];

const SKILLS = [
  'athletics', 'acrobatics', 'stealth', 'arcana', 'history',
  'investigation', 'perception', 'insight', 'persuasion',
  'intimidation', 'deception', 'survival', 'medicine',
];

export function DiceRoller({ onRoll }: { onRoll?: (result: string) => void }) {
  const [lastRoll, setLastRoll] = useState<RollResult | null>(null);
  const [rolling, setRolling] = useState(false);
  const [showPanel, setShowPanel] = useState(false);

  const rollDice = async (notation: string) => {
    setRolling(true);
    try {
      const res = await fetch(`${API}/api/dnd/roll`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notation }),
      });
      const data = await res.json();
      setLastRoll({ ...data, notation });
      setTimeout(() => setRolling(false), 300);
    } catch { setRolling(false); }
  };

  const rollSkillCheck = async (skill: string) => {
    setRolling(true);
    try {
      const res = await fetch(`${API}/api/dnd/skill-check`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skill }),
      });
      const data = await res.json();
      setLastRoll(data);
      onRoll?.(`check ${skill}`);
      setTimeout(() => setRolling(false), 300);
    } catch { setRolling(false); }
  };

  return (
    <div className="relative">
      {/* Toggle Button */}
      <button onClick={() => setShowPanel(!showPanel)}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#161b22] border border-[#30363d] rounded-lg text-xs text-gray-400 hover:text-amber-400 hover:border-amber-800 transition-colors">
        <span>🎲</span>
        {lastRoll && <span className="text-amber-400 font-bold">{lastRoll.total}</span>}
        {!lastRoll && <span>Dice</span>}
      </button>

      {/* Panel */}
      <AnimatePresence>
        {showPanel && (
          <motion.div initial={{ opacity: 0, scale: 0.9, y: -10 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="absolute right-0 top-full mt-2 w-72 bg-[#161b22] border border-[#30363d] rounded-lg shadow-xl z-50 p-3">

            {/* Quick Dice */}
            <div className="text-xs text-gray-500 font-[Cinzel] uppercase tracking-wider mb-2">Quick Roll</div>
            <div className="grid grid-cols-6 gap-1.5 mb-3">
              {DICE.map(d => (
                <motion.button key={d.sides} whileTap={{ scale: 0.9, rotate: 360 }}
                  onClick={() => rollDice(`1d${d.sides}`)}
                  className={`bg-gradient-to-br ${d.color} rounded-lg p-2 text-center text-white text-xs font-bold hover:brightness-110 transition-all shadow-md`}>
                  {d.label}
                </motion.button>
              ))}
            </div>

            {/* Skill Checks */}
            <div className="text-xs text-gray-500 font-[Cinzel] uppercase tracking-wider mb-2">Skill Check</div>
            <div className="grid grid-cols-3 gap-1 mb-3">
              {SKILLS.map(s => (
                <button key={s} onClick={() => rollSkillCheck(s)}
                  className="text-[10px] text-gray-400 hover:text-amber-400 bg-[#0d1117] hover:bg-amber-900/10 border border-[#30363d] hover:border-amber-800/30 rounded px-1.5 py-1 transition-colors capitalize truncate">
                  {s}
                </button>
              ))}
            </div>

            {/* Last Result */}
            {lastRoll && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className={`mt-2 rounded-lg p-3 text-center ${
                  lastRoll.isCritSuccess ? 'bg-green-900/30 border border-green-700/40' :
                  lastRoll.isCritFail ? 'bg-red-900/30 border border-red-700/40' :
                  'bg-[#0d1117] border border-[#30363d]'
                }`}>
                <motion.div key={lastRoll.total} initial={{ scale: 2, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                  className={`text-3xl font-bold font-[Cinzel] ${
                    lastRoll.isCritSuccess ? 'text-green-400' :
                    lastRoll.isCritFail ? 'text-red-400' : 'text-amber-400'
                  }`}>
                  {rolling ? '...' : lastRoll.total}
                </motion.div>
                {lastRoll.isCritSuccess && <div className="text-xs text-green-400 font-bold mt-1">CRITICAL SUCCESS!</div>}
                {lastRoll.isCritFail && <div className="text-xs text-red-400 font-bold mt-1">CRITICAL FAIL!</div>}
                {lastRoll.breakdown && <div className="text-[10px] text-gray-500 mt-1">{lastRoll.breakdown}</div>}
                {lastRoll.rolls && <div className="text-[10px] text-gray-600 mt-0.5">Rolls: [{lastRoll.rolls.join(', ')}]</div>}
                {lastRoll.skill && <div className="text-[10px] text-amber-600 mt-0.5 uppercase">{lastRoll.skill} ({lastRoll.ability})</div>}
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
