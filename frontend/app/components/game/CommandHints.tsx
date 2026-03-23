"use client";
import { useState } from "react";

const COMMANDS = [
  { cmd: 'look', desc: 'Examine surroundings', icon: '👁', category: 'explore' },
  { cmd: 'go [place]', desc: 'Travel to location', icon: '🚶', category: 'explore' },
  { cmd: 'talk [npc]', desc: 'Start conversation', icon: '💬', category: 'social' },
  { cmd: 'attack [npc]', desc: 'Start combat', icon: '⚔', category: 'combat' },
  { cmd: 'cast [spell]', desc: 'Cast a spell', icon: '✨', category: 'combat' },
  { cmd: 'cast [spell] on [npc]', desc: 'Cast at target', icon: '🔥', category: 'combat' },
  { cmd: 'check [skill]', desc: 'Skill check', icon: '🎲', category: 'skills' },
  { cmd: 'roll [dice]', desc: 'Roll dice (e.g. 2d6+3)', icon: '🎲', category: 'skills' },
  { cmd: 'rest', desc: 'Short rest (heal)', icon: '💤', category: 'rest' },
  { cmd: 'long rest', desc: 'Full rest (restore all)', icon: '🌙', category: 'rest' },
  { cmd: 'status', desc: 'View your stats', icon: '📊', category: 'info' },
  { cmd: 'spells', desc: 'List available spells', icon: '📜', category: 'info' },
];

export function CommandHints({ onCommand }: { onCommand: (cmd: string) => void }) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative">
      <button onClick={() => setShow(!show)}
        className="text-[10px] text-gray-600 hover:text-amber-400 transition-colors px-2 py-1">
        {show ? 'Hide commands' : '? Commands'}
      </button>
      {show && (
        <div className="absolute bottom-full left-0 mb-2 w-80 bg-[#161b22] border border-[#30363d] rounded-lg shadow-xl z-30 p-3 max-h-60 overflow-y-auto">
          <div className="grid grid-cols-2 gap-1">
            {COMMANDS.map(c => (
              <button key={c.cmd} onClick={() => { onCommand(c.cmd.split(' ')[0]); setShow(false); }}
                className="flex items-center gap-1.5 px-2 py-1.5 rounded text-left hover:bg-amber-900/10 transition-colors">
                <span className="text-xs">{c.icon}</span>
                <div>
                  <div className="text-[10px] text-amber-400 font-mono">{c.cmd}</div>
                  <div className="text-[9px] text-gray-600">{c.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
