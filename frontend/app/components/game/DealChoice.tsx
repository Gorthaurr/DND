"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface DealOption {
  title: string;
  description: string;
  cost?: string;
  reward?: string;
  risk?: 'low' | 'medium' | 'high';
}

interface Deal {
  title: string;
  description: string;
  npcName: string;
  options: DealOption[];
}

const riskColors = {
  low: 'border-green-800/30 bg-green-900/5',
  medium: 'border-yellow-800/30 bg-yellow-900/5',
  high: 'border-red-800/30 bg-red-900/5',
};

export function DealChoice({ deal, onChoose, onDismiss }: {
  deal: Deal; onChoose: (index: number) => void; onDismiss: () => void;
}) {
  const [hoveredOption, setHoveredOption] = useState<number | null>(null);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <motion.div initial={{ scale: 0.9, y: 30 }} animate={{ scale: 1, y: 0 }}
        className="bg-[#0d1117] border border-amber-900/30 rounded-xl w-full max-w-lg shadow-2xl shadow-amber-900/10 overflow-hidden">

        {/* Header */}
        <div className="bg-gradient-to-r from-amber-950/40 via-[#161b22] to-amber-950/40 p-5 border-b border-amber-900/20">
          <div className="text-xs text-amber-600 font-[Cinzel] uppercase tracking-wider mb-1">Decision Required</div>
          <h2 className="text-xl font-[Cinzel] text-amber-400 font-bold">{deal.title}</h2>
          <p className="text-sm text-gray-400 mt-2">{deal.description}</p>
          <div className="text-xs text-gray-600 mt-2">— {deal.npcName}</div>
        </div>

        {/* Options */}
        <div className="p-4 space-y-2">
          {deal.options.map((option, i) => (
            <motion.button key={i}
              onHoverStart={() => setHoveredOption(i)} onHoverEnd={() => setHoveredOption(null)}
              whileHover={{ x: 4 }}
              onClick={() => onChoose(i)}
              className={`w-full text-left p-4 rounded-lg border transition-all ${
                hoveredOption === i ? 'border-amber-600 bg-amber-900/10' : `${riskColors[option.risk || 'medium']} border-[#30363d]`
              }`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-bold text-gray-200">{option.title}</span>
                {option.risk && (
                  <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded ${
                    option.risk === 'low' ? 'bg-green-900/30 text-green-400' :
                    option.risk === 'medium' ? 'bg-yellow-900/30 text-yellow-400' :
                    'bg-red-900/30 text-red-400'
                  }`}>{option.risk} risk</span>
                )}
              </div>
              <p className="text-xs text-gray-400">{option.description}</p>
              <div className="flex gap-4 mt-2">
                {option.cost && <span className="text-[10px] text-red-400">Cost: {option.cost}</span>}
                {option.reward && <span className="text-[10px] text-green-400">Reward: {option.reward}</span>}
              </div>
            </motion.button>
          ))}
        </div>

        {/* Dismiss */}
        <div className="p-3 border-t border-[#30363d] text-center">
          <button onClick={onDismiss} className="text-xs text-gray-600 hover:text-gray-400 transition-colors">
            Ignore (walk away)
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
