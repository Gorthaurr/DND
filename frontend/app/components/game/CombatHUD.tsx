"use client";
import { motion } from "framer-motion";

interface CombatLog { narration: string; attackRoll?: any; damage?: any; hit?: boolean; }

export function CombatHUD({ log, playerHp, playerMaxHp, playerAc }: {
  log: CombatLog[]; playerHp: number; playerMaxHp: number; playerAc: number;
}) {
  const hpPct = playerMaxHp > 0 ? (playerHp / playerMaxHp) * 100 : 0;
  const hpColor = hpPct > 60 ? 'from-green-500 to-green-600' : hpPct > 30 ? 'from-yellow-500 to-yellow-600' : 'from-red-500 to-red-600';

  return (
    <div className="bg-[#0d1117] border border-[#30363d] rounded-lg overflow-hidden">
      {/* Player HP Bar */}
      <div className="p-3 border-b border-[#30363d]">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400 font-[Cinzel]">Your HP</span>
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500">AC <span className="text-amber-400 font-bold">{playerAc}</span></span>
            <span className={`text-sm font-bold ${hpPct > 60 ? 'text-green-400' : hpPct > 30 ? 'text-yellow-400' : 'text-red-400'}`}>
              {playerHp}/{playerMaxHp}
            </span>
          </div>
        </div>
        <div className="h-3 bg-[#1c2128] rounded-full overflow-hidden">
          <motion.div initial={{ width: '100%' }} animate={{ width: `${hpPct}%` }} transition={{ duration: 0.5 }}
            className={`h-full rounded-full bg-gradient-to-r ${hpColor}`} />
        </div>
      </div>

      {/* Combat Log */}
      <div className="max-h-40 overflow-y-auto p-2 space-y-1.5">
        {log.slice(-5).map((entry, i) => (
          <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
            className="text-xs text-gray-300 bg-[#161b22] rounded p-2 border border-[#30363d]">
            {entry.narration}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
