import type {
  ActionResponse,
  DialogueResponse,
  LookResponse,
  NPCFull,
  TickResult,
  WorldMap,
  WorldState,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/game";

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  getChatHistory: () => fetchJson<{ messages: any[] }>("/chat/history"),

  look: () => fetchJson<LookResponse>("/look"),

  action: (action: string) =>
    fetchJson<ActionResponse>("/action", {
      method: "POST",
      body: JSON.stringify({ action }),
    }),

  dialogue: (npc_id: string, message: string) =>
    fetchJson<DialogueResponse>("/dialogue", {
      method: "POST",
      body: JSON.stringify({ npc_id, message }),
    }),

  worldState: () => fetchJson<WorldState>("/world/state"),

  worldLog: () => fetchJson<{ entries: any[] }>("/world/log"),

  worldMap: () => fetchJson<WorldMap>("/world/map"),

  npcGraph: () => fetchJson<any>("/npcs/graph"),

  npcInfo: (id: string) => fetchJson<any>(`/npc/${id}`),

  npcObserve: (id: string) => fetchJson<NPCFull>(`/npc/${id}/observe`),

  tick: () => fetchJson<TickResult>("/world/tick", { method: "POST" }),

  async tickStream(onEvent: (data: any) => void): Promise<TickResult> {
    const response = await fetch(`${API_URL}/api/world/tick/stream`, { method: "POST" });
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullResult: TickResult | null = null;

    if (reader) {
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(data);
              if (data.phase === "complete") {
                fullResult = data.data;
              }
            } catch {}
          }
        }
      }
    }

    return fullResult || await this.tick();
  },

  respawn: () => fetchJson<any>("/player/respawn", { method: "POST" }),

  reset: () => fetchJson<any>("/world/reset", { method: "POST" }),

  // Save/Load
  saveWorld: () => fetchJson<any>("/world/save", { method: "POST" }),
  listSaves: () => fetchJson<any>("/world/saves"),
  loadSave: (filename: string) =>
    fetchJson<any>(`/world/load/${filename}`, { method: "POST" }),

  // D&D Reference
  dndRaces: () => fetchJson<any>("/dnd/races"),
  dndClasses: () => fetchJson<any>("/dnd/classes"),
  dndWeapons: () => fetchJson<any>("/dnd/weapons"),
  dndArmors: () => fetchJson<any>("/dnd/armors"),
  rollStats: () => fetchJson<any>("/character/roll-stats", { method: "POST" }),
  rollDice: (notation: string) =>
    fetchJson<any>("/dnd/roll", {
      method: "POST",
      body: JSON.stringify({ notation }),
    }),

  // Character
  createCharacter: (data: any) =>
    fetchJson<any>("/character/create", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getCharacter: () => fetchJson<any>("/character"),
  updateCharacter: (data: any) =>
    fetchJson<any>("/character", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  levelUp: () => fetchJson<any>("/character/level-up", { method: "POST" }),

  // Quests
  getQuests: () => fetchJson<any>("/quests"),
  acceptQuest: (questId: string) =>
    fetchJson<any>(`/quests/${questId}/accept`, { method: "POST" }),
  completeQuest: (questId: string) =>
    fetchJson<any>(`/quests/${questId}/complete`, { method: "POST" }),

  // Worlds
  listWorlds: () => fetchJson<any>("/worlds"),
  getWorld: (id: string) => fetchJson<any>(`/worlds/${id}`),
  createWorld: (data: any) =>
    fetchJson<any>("/worlds", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteWorld: (id: string) =>
    fetchJson<any>(`/worlds/${id}`, { method: "DELETE" }),
  loadWorld: (id: string) =>
    fetchJson<any>(`/worlds/${id}/load`, { method: "POST" }),
  addLocation: (worldId: string, data: any) =>
    fetchJson<any>(`/worlds/${worldId}/locations`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  addNpc: (worldId: string, data: any) =>
    fetchJson<any>(`/worlds/${worldId}/npcs`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  generateNpc: (worldId: string, description: string) =>
    fetchJson<any>(`/worlds/${worldId}/generate/npc`, {
      method: "POST",
      body: JSON.stringify({ description }),
    }),
  generateLocation: (worldId: string, description: string) =>
    fetchJson<any>(`/worlds/${worldId}/generate/location`, {
      method: "POST",
      body: JSON.stringify({ description }),
    }),
};

export function createGameSocket(
  onMessage: (data: any) => void,
  onError?: (e: Event) => void
): WebSocket {
  const ws = new WebSocket(WS_URL);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // ignore parse errors
    }
  };

  ws.onerror = (e) => onError?.(e);

  // Heartbeat
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "ping" }));
    }
  }, 30000);

  const originalClose = ws.close.bind(ws);
  ws.close = (...args) => {
    clearInterval(interval);
    originalClose(...args);
  };

  return ws;
}
