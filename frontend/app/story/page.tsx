"use client";

import { StoryTreeView } from "../components/StoryTreeView";

export default function StoryPage() {
  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-200">
      <header className="border-b border-[#30363d] bg-[#161b22]">
        <div className="max-w-[1400px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-gray-400 hover:text-amber-400 text-sm transition-colors">← Back</a>
            <h1 className="font-[Cinzel] text-xl text-amber-400 font-bold">Story Tree</h1>
            <span className="text-xs text-gray-500">Detroit: Become Human style narrative tracking</span>
          </div>
          <div className="flex gap-2">
            <a href="/npcs" className="text-xs text-gray-400 hover:text-amber-400 bg-[#0d1117] border border-[#30363d] px-3 py-1.5 rounded transition-colors">NPC Explorer</a>
            <a href="/editor" className="text-xs text-gray-400 hover:text-amber-400 bg-[#0d1117] border border-[#30363d] px-3 py-1.5 rounded transition-colors">Editor</a>
          </div>
        </div>
      </header>
      <main className="max-w-[1400px] mx-auto p-6">
        <StoryTreeView />
      </main>
    </div>
  );
}
