export interface Location {
  id: string;
  name: string;
  type: string;
  description: string;
}

export interface NPC {
  id: string;
  name: string;
  occupation: string;
  mood: string;
  description?: string;
}

export interface NPCFull {
  id: string;
  name: string;
  personality: string;
  backstory: string;
  goals: string[];
  mood: string;
  occupation: string;
  age: number;
  alive: boolean;
  location: Location | null;
  relationships: Relationship[];
  recent_memories: string[];
}

export interface Relationship {
  id: string;
  name: string;
  sentiment: number;
  reason: string;
}

export interface Item {
  id: string;
  name: string;
  type: string;
  description: string;
  value: number;
}

export interface LookResponse {
  location: Location;
  npcs: NPC[];
  items: Item[];
  exits: Location[];
}

export interface ActionResponse {
  narration: string;
  npcs_involved: string[];
  npcs_killed: string[];
  location: Location | null;
  items_changed: string[];
}

export interface DialogueResponse {
  npc_name: string;
  dialogue: string;
  mood: string;
}

export interface WorldState {
  day: number;
  player_location: Location;
  player_gold: number;
  player_inventory: Item[];
  player_hp?: number;
  player_max_hp?: number;
  player_level?: number;
  player_class?: string;
  player_xp?: number;
}

export interface WorldMap {
  locations: Location[];
  connections: { from_id: string; to_id: string; distance: number }[];
  player_location_id: string;
  npc_locations: Record<string, string>;
}

export interface ScenarioInfo {
  title: string;
  description: string;
  phase_name: string;
  tension_level: "low" | "rising" | "climax" | "resolution";
  narrative_update?: string;
}

export interface TickResult {
  day: number;
  events: { description: string; type: string }[];
  npc_actions: {
    npc_id: string;
    npc_name: string;
    action: string;
    target: string | null;
    dialogue: string | null;
    reasoning: string;
  }[];
  interactions: {
    npc_a: string;
    npc_b: string;
    summary: string;
    interaction_type?: string;
    action?: string;
  }[];
  active_scenarios?: ScenarioInfo[];
}

export interface NPCGraphNode {
  id: string;
  name: string;
  occupation: string;
  mood: string;
  level: number | null;
  archetype: string | null;
  known: boolean;
  alive: boolean;
}

export interface NPCGraphEdge {
  from: string;
  to: string;
  sentiment: number;
  reason: string;
  visible: boolean;
}

export interface NPCGraphData {
  nodes: NPCGraphNode[];
  edges: NPCGraphEdge[];
}

export interface ChatMessage {
  id: string;
  type: "player" | "dm" | "npc" | "system";
  content: string;
  npc_name?: string;
  timestamp: number;
}
