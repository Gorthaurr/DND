"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Tab = "npcs" | "locations" | "events" | "scenarios" | "prompts" | "world";

interface NPC {
  id: string;
  name: string;
  archetype: string;
  personality: string;
  backstory: string;
  goals: string[];
  mood: string;
  occupation: string;
  age: number;
  location_id: string;
  level?: number;
  class_id?: string;
  ability_scores?: Record<string, number>;
  max_hp?: number;
  ac?: number;
  secret_power?: string;
  relationships?: any[];
  faction?: { id: string; role: string };
  equipment_ids?: string[];
}

interface Location {
  id: string;
  name: string;
  type: string;
  description: string;
}

interface GameEvent {
  id: string;
  type: string;
  description: string;
  location_id: string;
  severity: string;
  tags: string[];
}

interface Scenario {
  title: string;
  description: string;
  type: string;
  phases: string[];
  tension: string;
  tags: string[];
}

interface Prompt {
  name: string;
  filename: string;
  content: string;
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return res.json();
}

// --- Shared UI Components ---
function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-[#161b22] border border-[#30363d] rounded-lg p-4 ${className}`}>
      {children}
    </div>
  );
}

function Badge({ children, color = "amber" }: { children: React.ReactNode; color?: string }) {
  const colors: Record<string, string> = {
    amber: "bg-amber-900/40 text-amber-400 border-amber-700/50",
    green: "bg-green-900/40 text-green-400 border-green-700/50",
    red: "bg-red-900/40 text-red-400 border-red-700/50",
    blue: "bg-blue-900/40 text-blue-400 border-blue-700/50",
    purple: "bg-purple-900/40 text-purple-400 border-purple-700/50",
  };
  return <span className={`px-2 py-0.5 rounded text-xs border ${colors[color] || colors.amber}`}>{children}</span>;
}

function FieldInput({ label, value, onChange, type = "text", textarea = false }: {
  label: string; value: string | number; onChange: (v: string) => void; type?: string; textarea?: boolean;
}) {
  return (
    <div className="mb-3">
      <label className="block text-xs text-gray-400 mb-1 font-[Cinzel]">{label}</label>
      {textarea ? (
        <textarea value={value} onChange={(e) => onChange(e.target.value)} rows={4}
          className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-sm text-gray-200 focus:border-amber-600 focus:outline-none resize-y" />
      ) : (
        <input type={type} value={value} onChange={(e) => onChange(e.target.value)}
          className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-sm text-gray-200 focus:border-amber-600 focus:outline-none" />
      )}
    </div>
  );
}

function SelectInput({ label, value, onChange, options }: {
  label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[];
}) {
  return (
    <div className="mb-3">
      <label className="block text-xs text-gray-400 mb-1 font-[Cinzel]">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-sm text-gray-200 focus:border-amber-600 focus:outline-none">
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function SaveButton({ onClick, saving }: { onClick: () => void; saving: boolean }) {
  return (
    <button onClick={onClick} disabled={saving}
      className="px-4 py-2 bg-amber-700 hover:bg-amber-600 disabled:bg-gray-700 text-white rounded text-sm font-[Cinzel] transition-colors">
      {saving ? "Saving..." : "Save Changes"}
    </button>
  );
}

function DeleteButton({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="px-4 py-2 bg-red-900/60 hover:bg-red-800 text-red-300 rounded text-sm font-[Cinzel] transition-colors">
      Delete
    </button>
  );
}

function CreateButton({ onClick, label }: { onClick: () => void; label: string }) {
  return (
    <button onClick={onClick}
      className="px-4 py-2 bg-green-900/60 hover:bg-green-800 text-green-300 rounded text-sm font-[Cinzel] transition-colors flex items-center gap-2">
      <span>+</span> {label}
    </button>
  );
}

// --- NPC Editor ---
function NPCEditor({ locations }: { locations: Location[] }) {
  const [npcs, setNpcs] = useState<NPC[]>([]);
  const [selected, setSelected] = useState<NPC | null>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<{ npcs: NPC[] }>("/api/editor/npcs").then(d => setNpcs(d.npcs));
  }, []);

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    await fetchApi(`/api/editor/npc/${selected.id}`, { method: "PUT", body: JSON.stringify(selected) });
    setNpcs(npcs.map(n => n.id === selected.id ? selected : n));
    setSaving(false);
    setToast("NPC saved!");
    setTimeout(() => setToast(""), 2000);
  };

  const create = async () => {
    const npc: Partial<NPC> = {
      name: "New NPC", occupation: "villager", archetype: "stoic", personality: "O:mid, C:mid, E:mid, A:mid, N:mid",
      backstory: "A mysterious newcomer to the village.", goals: ["survive"], mood: "content", age: 30,
      location_id: locations[0]?.id || "loc-tavern", relationships: [], level: 1, class_id: "commoner",
      ability_scores: { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHA: 10 }, max_hp: 10, ac: 10,
    };
    const result = await fetchApi<NPC>("/api/editor/npc", { method: "POST", body: JSON.stringify(npc) });
    setNpcs([...npcs, result]);
    setSelected(result);
    setToast("NPC created!");
    setTimeout(() => setToast(""), 2000);
  };

  const remove = async () => {
    if (!selected || !confirm(`Delete ${selected.name}?`)) return;
    await fetchApi(`/api/editor/npc/${selected.id}`, { method: "DELETE" });
    setNpcs(npcs.filter(n => n.id !== selected.id));
    setSelected(null);
  };

  const update = (field: keyof NPC, value: any) => {
    if (!selected) return;
    setSelected({ ...selected, [field]: value });
  };

  return (
    <div className="flex gap-4 h-full">
      {/* NPC List */}
      <div className="w-64 shrink-0">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-[Cinzel] text-amber-400 text-sm">NPCs ({npcs.length})</h3>
          <CreateButton onClick={create} label="New" />
        </div>
        <div className="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
          {npcs.map(n => (
            <button key={n.id} onClick={() => setSelected(n)}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${selected?.id === n.id ? "bg-amber-900/30 border border-amber-700/50 text-amber-300" : "hover:bg-[#1c2128] text-gray-300"}`}>
              <div className="font-semibold">{n.name}</div>
              <div className="text-xs text-gray-500">{n.occupation} | {n.mood}</div>
            </button>
          ))}
        </div>
      </div>

      {/* NPC Details */}
      <div className="flex-1">
        {selected ? (
          <Panel>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-[Cinzel] text-lg text-amber-400">{selected.name}</h3>
              <div className="flex gap-2">
                <DeleteButton onClick={remove} />
                <SaveButton onClick={save} saving={saving} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-x-4">
              <FieldInput label="Name" value={selected.name} onChange={v => update("name", v)} />
              <FieldInput label="Occupation" value={selected.occupation} onChange={v => update("occupation", v)} />
              <FieldInput label="Archetype" value={selected.archetype} onChange={v => update("archetype", v)} />
              <SelectInput label="Mood" value={selected.mood} onChange={v => update("mood", v)}
                options={["content","concerned","excited","angry","fearful","scheming","hopeful","sad"].map(m => ({ value: m, label: m }))} />
              <FieldInput label="Age" value={selected.age} onChange={v => update("age", parseInt(v) || 0)} type="number" />
              <SelectInput label="Location" value={selected.location_id} onChange={v => update("location_id", v)}
                options={locations.map(l => ({ value: l.id, label: l.name }))} />
              <FieldInput label="Level" value={selected.level || 1} onChange={v => update("level", parseInt(v) || 1)} type="number" />
              <FieldInput label="Class" value={selected.class_id || ""} onChange={v => update("class_id", v)} />
              <FieldInput label="Max HP" value={selected.max_hp || 10} onChange={v => update("max_hp", parseInt(v) || 10)} type="number" />
              <FieldInput label="AC" value={selected.ac || 10} onChange={v => update("ac", parseInt(v) || 10)} type="number" />
            </div>
            <FieldInput label="Personality (Big Five)" value={selected.personality} onChange={v => update("personality", v)} />
            <FieldInput label="Backstory" value={selected.backstory} onChange={v => update("backstory", v)} textarea />
            <FieldInput label="Goals (comma-separated)" value={(selected.goals || []).join(", ")}
              onChange={v => update("goals", v.split(",").map(s => s.trim()).filter(Boolean))} />
            <FieldInput label="Secret Power" value={selected.secret_power || ""} onChange={v => update("secret_power", v)} textarea />

            {/* Ability Scores */}
            {selected.ability_scores && (
              <div className="mt-3">
                <label className="block text-xs text-gray-400 mb-2 font-[Cinzel]">Ability Scores</label>
                <div className="grid grid-cols-6 gap-2">
                  {["STR", "DEX", "CON", "INT", "WIS", "CHA"].map(stat => (
                    <div key={stat} className="text-center">
                      <div className="text-xs text-amber-400 font-bold">{stat}</div>
                      <input type="number" value={selected.ability_scores![stat] || 10}
                        onChange={e => update("ability_scores", { ...selected.ability_scores, [stat]: parseInt(e.target.value) || 10 })}
                        className="w-full bg-[#0d1117] border border-[#30363d] rounded px-1 py-1 text-sm text-center text-gray-200 focus:border-amber-600 focus:outline-none" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relationships */}
            {selected.relationships && selected.relationships.length > 0 && (
              <div className="mt-4">
                <label className="block text-xs text-gray-400 mb-2 font-[Cinzel]">Relationships</label>
                <div className="space-y-2">
                  {selected.relationships.map((r, i) => (
                    <div key={i} className="flex gap-2 items-center text-sm">
                      <span className="text-gray-300 w-24">{r.target_id}</span>
                      <input type="number" value={r.sentiment} min={-1} max={1} step={0.1}
                        onChange={e => {
                          const rels = [...selected.relationships!];
                          rels[i] = { ...rels[i], sentiment: parseFloat(e.target.value) };
                          update("relationships", rels);
                        }}
                        className="w-16 bg-[#0d1117] border border-[#30363d] rounded px-1 py-1 text-center text-gray-200 text-xs" />
                      <input value={r.reason}
                        onChange={e => {
                          const rels = [...selected.relationships!];
                          rels[i] = { ...rels[i], reason: e.target.value };
                          update("relationships", rels);
                        }}
                        className="flex-1 bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-gray-200 text-xs" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Panel>
        ) : (
          <Panel className="flex items-center justify-center h-64 text-gray-500">
            Select an NPC to edit
          </Panel>
        )}
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </div>
  );
}

// --- Location Editor ---
function LocationEditor() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selected, setSelected] = useState<Location | null>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<any>("/api/editor/world").then(d => setLocations(d.locations));
  }, []);

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    await fetchApi(`/api/editor/location/${selected.id}`, { method: "PUT", body: JSON.stringify(selected) });
    setLocations(locations.map(l => l.id === selected.id ? selected : l));
    setSaving(false);
    setToast("Location saved!");
    setTimeout(() => setToast(""), 2000);
  };

  const create = async () => {
    const loc = { name: "New Location", type: "ruins", description: "A mysterious place..." };
    const result = await fetchApi<Location>("/api/editor/location", { method: "POST", body: JSON.stringify(loc) });
    setLocations([...locations, result]);
    setSelected(result);
  };

  const remove = async () => {
    if (!selected || !confirm(`Delete ${selected.name}?`)) return;
    await fetchApi(`/api/editor/location/${selected.id}`, { method: "DELETE" });
    setLocations(locations.filter(l => l.id !== selected.id));
    setSelected(null);
  };

  return (
    <div className="flex gap-4">
      <div className="w-64 shrink-0">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-[Cinzel] text-amber-400 text-sm">Locations ({locations.length})</h3>
          <CreateButton onClick={create} label="New" />
        </div>
        <div className="space-y-1 max-h-[70vh] overflow-y-auto">
          {locations.map(l => (
            <button key={l.id} onClick={() => setSelected(l)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${selected?.id === l.id ? "bg-amber-900/30 border border-amber-700/50 text-amber-300" : "hover:bg-[#1c2128] text-gray-300"}`}>
              <div className="font-semibold">{l.name}</div>
              <div className="text-xs text-gray-500">{l.type}</div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1">
        {selected ? (
          <Panel>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-[Cinzel] text-lg text-amber-400">{selected.name}</h3>
              <div className="flex gap-2"><DeleteButton onClick={remove} /><SaveButton onClick={save} saving={saving} /></div>
            </div>
            <FieldInput label="Name" value={selected.name} onChange={v => setSelected({ ...selected, name: v })} />
            <SelectInput label="Type" value={selected.type} onChange={v => setSelected({ ...selected, type: v })}
              options={["tavern","market","smithy","square","forest","chapel","farm","barracks","mill","ruins","cave","tower","dungeon","camp"].map(t => ({ value: t, label: t }))} />
            <FieldInput label="Description" value={selected.description} onChange={v => setSelected({ ...selected, description: v })} textarea />
          </Panel>
        ) : <Panel className="flex items-center justify-center h-64 text-gray-500">Select a location</Panel>}
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </div>
  );
}

// --- Event Editor ---
function EventEditor({ locations }: { locations: Location[] }) {
  const [events, setEvents] = useState<GameEvent[]>([]);
  const [selected, setSelected] = useState<GameEvent | null>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<{ events: GameEvent[] }>("/api/editor/events").then(d => setEvents(d.events));
  }, []);

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    await fetchApi(`/api/editor/event/${selected.id}`, { method: "PUT", body: JSON.stringify(selected) });
    setEvents(events.map(e => e.id === selected.id ? selected : e));
    setSaving(false);
    setToast("Event saved!");
    setTimeout(() => setToast(""), 2000);
  };

  const create = async () => {
    const evt = { type: "social", description: "Something happened...", location_id: locations[0]?.id || "loc-tavern", severity: "low", tags: [] };
    const result = await fetchApi<GameEvent>("/api/editor/event", { method: "POST", body: JSON.stringify(evt) });
    setEvents([...events, result]);
    setSelected(result);
  };

  const remove = async () => {
    if (!selected || !confirm("Delete this event?")) return;
    await fetchApi(`/api/editor/event/${selected.id}`, { method: "DELETE" });
    setEvents(events.filter(e => e.id !== selected.id));
    setSelected(null);
  };

  return (
    <div className="flex gap-4">
      <div className="w-72 shrink-0">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-[Cinzel] text-amber-400 text-sm">Events ({events.length})</h3>
          <CreateButton onClick={create} label="New" />
        </div>
        <div className="space-y-1 max-h-[70vh] overflow-y-auto">
          {events.map(e => (
            <button key={e.id} onClick={() => setSelected(e)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${selected?.id === e.id ? "bg-amber-900/30 border border-amber-700/50 text-amber-300" : "hover:bg-[#1c2128] text-gray-300"}`}>
              <div className="flex gap-2 items-center">
                <Badge color={e.severity === "high" ? "red" : e.severity === "medium" ? "amber" : "green"}>{e.severity}</Badge>
                <Badge color="blue">{e.type}</Badge>
              </div>
              <div className="text-xs mt-1 text-gray-400 line-clamp-2">{e.description}</div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1">
        {selected ? (
          <Panel>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-[Cinzel] text-lg text-amber-400">Edit Event</h3>
              <div className="flex gap-2"><DeleteButton onClick={remove} /><SaveButton onClick={save} saving={saving} /></div>
            </div>
            <FieldInput label="Description" value={selected.description} onChange={v => setSelected({ ...selected, description: v })} textarea />
            <div className="grid grid-cols-3 gap-4">
              <SelectInput label="Type" value={selected.type} onChange={v => setSelected({ ...selected, type: v })}
                options={["natural","social","conflict","trade"].map(t => ({ value: t, label: t }))} />
              <SelectInput label="Severity" value={selected.severity} onChange={v => setSelected({ ...selected, severity: v })}
                options={["low","medium","high"].map(t => ({ value: t, label: t }))} />
              <SelectInput label="Location" value={selected.location_id} onChange={v => setSelected({ ...selected, location_id: v })}
                options={locations.map(l => ({ value: l.id, label: l.name }))} />
            </div>
            <FieldInput label="Tags (comma-separated)" value={(selected.tags || []).join(", ")}
              onChange={v => setSelected({ ...selected, tags: v.split(",").map(s => s.trim()).filter(Boolean) })} />
          </Panel>
        ) : <Panel className="flex items-center justify-center h-64 text-gray-500">Select an event</Panel>}
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </div>
  );
}

// --- Scenario Editor ---
function ScenarioEditor() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<Scenario[]>("/api/editor/scenarios").then(setScenarios);
  }, []);

  const selected = selectedIdx !== null ? scenarios[selectedIdx] : null;

  const save = async () => {
    if (selectedIdx === null || !selected) return;
    setSaving(true);
    await fetchApi(`/api/editor/scenario/${selectedIdx}`, { method: "PUT", body: JSON.stringify(selected) });
    setSaving(false);
    setToast("Scenario saved!");
    setTimeout(() => setToast(""), 2000);
  };

  const create = async () => {
    const sc: Scenario = { title: "New Scenario", description: "A new story arc...", type: "side",
      phases: ["Beginning", "Rising tension", "Climax", "Resolution"], tension: "slow burn", tags: [] };
    await fetchApi("/api/editor/scenario", { method: "POST", body: JSON.stringify(sc) });
    setScenarios([...scenarios, sc]);
    setSelectedIdx(scenarios.length);
  };

  const remove = async () => {
    if (selectedIdx === null || !confirm(`Delete "${selected?.title}"?`)) return;
    await fetchApi(`/api/editor/scenario/${selectedIdx}`, { method: "DELETE" });
    setScenarios(scenarios.filter((_, i) => i !== selectedIdx));
    setSelectedIdx(null);
  };

  const update = (field: keyof Scenario, value: any) => {
    if (selectedIdx === null) return;
    const updated = [...scenarios];
    updated[selectedIdx] = { ...updated[selectedIdx], [field]: value };
    setScenarios(updated);
  };

  return (
    <div className="flex gap-4">
      <div className="w-64 shrink-0">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-[Cinzel] text-amber-400 text-sm">Scenarios ({scenarios.length})</h3>
          <CreateButton onClick={create} label="New" />
        </div>
        <div className="space-y-1 max-h-[70vh] overflow-y-auto">
          {scenarios.map((s, i) => (
            <button key={i} onClick={() => setSelectedIdx(i)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${selectedIdx === i ? "bg-amber-900/30 border border-amber-700/50 text-amber-300" : "hover:bg-[#1c2128] text-gray-300"}`}>
              <div className="font-semibold">{s.title}</div>
              <div className="text-xs text-gray-500">{s.type} | {s.tension}</div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1">
        {selected ? (
          <Panel>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-[Cinzel] text-lg text-amber-400">{selected.title}</h3>
              <div className="flex gap-2"><DeleteButton onClick={remove} /><SaveButton onClick={save} saving={saving} /></div>
            </div>
            <FieldInput label="Title" value={selected.title} onChange={v => update("title", v)} />
            <FieldInput label="Description" value={selected.description} onChange={v => update("description", v)} textarea />
            <div className="grid grid-cols-2 gap-4">
              <SelectInput label="Type" value={selected.type} onChange={v => update("type", v)}
                options={[{ value: "main", label: "Main" }, { value: "side", label: "Side" }]} />
              <SelectInput label="Tension" value={selected.tension} onChange={v => update("tension", v)}
                options={["rising to climax","slow burn","mystery to horror","social intrigue","escalating","urgent","festive then dramatic","moral dilemma"].map(t => ({ value: t, label: t }))} />
            </div>
            <FieldInput label="Phases (comma-separated)" value={selected.phases.join(", ")}
              onChange={v => update("phases", v.split(",").map(s => s.trim()).filter(Boolean))} />
            <FieldInput label="Tags (comma-separated)" value={(selected.tags || []).join(", ")}
              onChange={v => update("tags", v.split(",").map(s => s.trim()).filter(Boolean))} />
          </Panel>
        ) : <Panel className="flex items-center justify-center h-64 text-gray-500">Select a scenario</Panel>}
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </div>
  );
}

// --- Prompt Editor ---
function PromptEditor() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selected, setSelected] = useState<Prompt | null>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<{ prompts: Prompt[] }>("/api/editor/prompts").then(d => setPrompts(d.prompts));
  }, []);

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    await fetchApi(`/api/editor/prompt/${selected.name}`, { method: "PUT", body: JSON.stringify({ content: selected.content }) });
    setPrompts(prompts.map(p => p.name === selected.name ? selected : p));
    setSaving(false);
    setToast("Prompt saved!");
    setTimeout(() => setToast(""), 2000);
  };

  const promptLabels: Record<string, string> = {
    dm_narrate: "DM Narration (main game logic)",
    dm_quest: "Quest Generation from DM",
    event_generate: "World Event Generator",
    npc_decision: "NPC Decision Making (AI brain)",
    npc_dialogue: "NPC Dialogue Responses",
    npc_interact: "NPC-to-NPC Interactions",
    quest_generate: "Quest Generator",
    scenario_advance: "Scenario Progression",
    scenario_generate: "Scenario Creator",
  };

  return (
    <div className="flex gap-4">
      <div className="w-72 shrink-0">
        <h3 className="font-[Cinzel] text-amber-400 text-sm mb-3">Agent Prompts ({prompts.length})</h3>
        <div className="space-y-1">
          {prompts.map(p => (
            <button key={p.name} onClick={() => setSelected(p)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${selected?.name === p.name ? "bg-amber-900/30 border border-amber-700/50 text-amber-300" : "hover:bg-[#1c2128] text-gray-300"}`}>
              <div className="font-semibold">{p.name}.j2</div>
              <div className="text-xs text-gray-500">{promptLabels[p.name] || p.filename}</div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1">
        {selected ? (
          <Panel>
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="font-[Cinzel] text-lg text-amber-400">{selected.name}.j2</h3>
                <p className="text-xs text-gray-500">{promptLabels[selected.name]}</p>
              </div>
              <SaveButton onClick={save} saving={saving} />
            </div>
            <textarea value={selected.content}
              onChange={e => setSelected({ ...selected, content: e.target.value })}
              rows={30}
              className="w-full bg-[#0d1117] border border-[#30363d] rounded px-4 py-3 text-sm text-gray-200 font-mono focus:border-amber-600 focus:outline-none resize-y leading-relaxed"
              spellCheck={false} />
          </Panel>
        ) : <Panel className="flex items-center justify-center h-64 text-gray-500">Select a prompt to edit</Panel>}
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </div>
  );
}

// --- World Overview ---
function WorldOverview() {
  const [world, setWorld] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetchApi<any>("/api/editor/world").then(setWorld);
  }, []);

  const save = async () => {
    if (!world) return;
    setSaving(true);
    await fetchApi("/api/editor/world", { method: "PUT", body: JSON.stringify({ name: world.name, description: world.description, start_location: world.start_location }) });
    setSaving(false);
    setToast("World saved!");
    setTimeout(() => setToast(""), 2000);
  };

  if (!world) return <div className="text-gray-500">Loading...</div>;

  return (
    <Panel>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-[Cinzel] text-lg text-amber-400">World Settings</h3>
        <SaveButton onClick={save} saving={saving} />
      </div>
      <FieldInput label="World Name" value={world.name} onChange={v => setWorld({ ...world, name: v })} />
      <FieldInput label="Description" value={world.description} onChange={v => setWorld({ ...world, description: v })} textarea />
      <SelectInput label="Start Location" value={world.start_location} onChange={v => setWorld({ ...world, start_location: v })}
        options={(world.locations || []).map((l: any) => ({ value: l.id, label: l.name }))} />

      <div className="mt-6 grid grid-cols-4 gap-4">
        <div className="bg-[#0d1117] rounded-lg p-4 text-center border border-[#30363d]">
          <div className="text-2xl font-bold text-amber-400">{world.locations?.length || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Locations</div>
        </div>
        <div className="bg-[#0d1117] rounded-lg p-4 text-center border border-[#30363d]">
          <div className="text-2xl font-bold text-green-400">{world.connections?.length || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Connections</div>
        </div>
        <div className="bg-[#0d1117] rounded-lg p-4 text-center border border-[#30363d]">
          <div className="text-2xl font-bold text-blue-400">{world.factions?.length || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Factions</div>
        </div>
        <div className="bg-[#0d1117] rounded-lg p-4 text-center border border-[#30363d]">
          <div className="text-2xl font-bold text-purple-400">{world.items?.length || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Items</div>
        </div>
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-green-900 text-green-300 px-4 py-2 rounded shadow-lg text-sm">{toast}</div>}
    </Panel>
  );
}

// --- Main Editor Page ---
export default function EditorPage() {
  const [tab, setTab] = useState<Tab>("npcs");
  const [locations, setLocations] = useState<Location[]>([]);

  useEffect(() => {
    fetchApi<any>("/api/editor/world").then(d => setLocations(d.locations || []));
  }, []);

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: "npcs", label: "NPCs", icon: "👤" },
    { id: "locations", label: "Locations", icon: "🏰" },
    { id: "events", label: "Events", icon: "⚡" },
    { id: "scenarios", label: "Scenarios", icon: "📜" },
    { id: "prompts", label: "AI Prompts", icon: "🧠" },
    { id: "world", label: "World", icon: "🌍" },
  ];

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-200">
      {/* Header */}
      <header className="border-b border-[#30363d] bg-[#161b22]">
        <div className="max-w-[1600px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-gray-400 hover:text-amber-400 text-sm transition-colors">
              ← Back to Game
            </a>
            <h1 className="font-[Cinzel] text-xl text-amber-400 font-bold">World Editor</h1>
          </div>
          <div className="text-xs text-gray-500">All changes save to disk automatically</div>
        </div>
      </header>

      {/* Tabs */}
      <nav className="border-b border-[#30363d] bg-[#161b22]/50">
        <div className="max-w-[1600px] mx-auto px-6 flex gap-1">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-4 py-3 text-sm font-[Cinzel] transition-colors border-b-2 ${tab === t.id
                ? "border-amber-500 text-amber-400"
                : "border-transparent text-gray-400 hover:text-gray-200"}`}>
              <span className="mr-2">{t.icon}</span>{t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-[1600px] mx-auto p-6">
        <AnimatePresence mode="wait">
          <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
            {tab === "npcs" && <NPCEditor locations={locations} />}
            {tab === "locations" && <LocationEditor />}
            {tab === "events" && <EventEditor locations={locations} />}
            {tab === "scenarios" && <ScenarioEditor />}
            {tab === "prompts" && <PromptEditor />}
            {tab === "world" && <WorldOverview />}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
