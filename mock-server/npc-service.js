// ============================================
// NPC Life Service — Central module for living NPCs
// Each NPC: psychology + biography + memory + goals + evolution
// ============================================

const psychology = require('./psychology-engine');
const bio = require('./biography-generator');
const { StoryTree } = require('./story-tree');

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function clamp(val, min, max) { return Math.min(max, Math.max(min, val)); }

class NPCLifeService {
  constructor() {
    this.npcs = new Map(); // id → full NPC state
    this.storyTree = new StoryTree();
    this.worldDay = 1;
  }

  // --- CREATE NPC with full psychology + biography ---
  createNPC(params = {}) {
    const id = params.id || `npc-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;

    // Generate psychology profile
    const psychProfile = psychology.generatePsychProfile({
      accentuation: params.accentuation,
      attitude: params.jungAttitude,
      function: params.jungFunction,
      maslowLevel: params.maslowLevel,
      psychopathic: params.psychopathic || false,
    });

    // Generate biography
    const biography = bio.generateBiography({
      origin: params.origin || 'medieval_earth',
      age: params.age,
      disability: params.disability,
      parentType: params.parentType,
    });

    // Apply biography cumulative effects to psychology
    const bioEffects = biography.cumulativePsychEffect;
    psychProfile.emotionalStability = clamp(psychProfile.emotionalStability + (bioEffects.emotionalStability || 0), 0, 1);
    psychProfile.empathy = clamp(psychProfile.empathy + (bioEffects.empathy || 0), 0, 1);
    psychProfile.willpower = clamp(psychProfile.willpower + (bioEffects.willpower || 0), 0, 1);
    psychProfile.stressLevel = clamp(psychProfile.stressLevel + (bioEffects.stressLevel || 0), 0, 1);

    // Generate goals based on Maslow level + accentuation
    const goals = this._generateGoals(psychProfile, biography, params);

    // Memory system
    const memory = [
      { id: 1, content: `Born and raised. ${biography.summary}`, day: 0, importance: 1.0, emotion: 'neutral', type: 'backstory' },
    ];

    const npc = {
      id,
      name: params.name || 'Unknown',
      occupation: params.occupation || 'villager',
      age: biography.age,

      // D&D stats
      level: params.level || 1,
      class_id: params.class_id || 'commoner',
      ability_scores: params.ability_scores || { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHA: 10 },
      max_hp: params.max_hp || 10,
      hp: params.hp || params.max_hp || 10,
      ac: params.ac || 10,
      equipment_ids: params.equipment_ids || [],

      // Location
      location_id: params.location_id || 'loc-tavern',

      // Psychology
      psychProfile,

      // Biography
      biography,

      // Memory
      memory,
      nextMemoryId: 2,

      // Goals (dynamic, from Maslow + situation)
      goals,

      // Relationships
      relationships: params.relationships || {},

      // State
      alive: true,
      currentActivity: 'idle',
      mood: psychProfile.currentMood,

      // Physical state
      physicalState: {
        disability: biography.disability.key,
        injuries: [],
        conditions: [],
      },

      // Faction
      faction: params.faction || null,

      // Tracking
      createdAt: new Date().toISOString(),
      lastTickDay: 0,
      actionHistory: [],
    };

    this.npcs.set(id, npc);

    // Story tree event
    this.storyTree.addEvent({
      title: `${npc.name} enters the story`,
      description: `${npc.name}, ${biography.age}-year-old ${npc.occupation}. ${biography.summary}`,
      day: this.worldDay,
      participants: [npc.name],
      category: 'npc_created',
    });

    return npc;
  }

  // --- GENERATE GOALS based on Maslow + psychology ---
  _generateGoals(psychProfile, biography, params) {
    const maslow = psychProfile.maslowLevel;
    const goals = [];

    // Primary Maslow-driven goal
    const maslowGoals = {
      survival: ['find food and shelter', 'survive another day', 'avoid danger at all costs'],
      safety: ['protect my home', 'earn enough gold to be secure', 'find a safe place to live'],
      belonging: ['make true friends', 'find a partner', 'be accepted by the community'],
      esteem: ['gain respect and recognition', 'prove my worth', 'become the best at my craft'],
      selfActualization: ['find my true purpose', 'create something lasting', 'transcend my limitations'],
    };
    goals.push(randomChoice(maslowGoals[maslow.key] || maslowGoals.safety));

    // Accentuation-driven goal
    const accentGoals = {
      demonstrative: 'become the center of attention',
      stuck: 'achieve justice for past wrongs',
      pedantic: 'establish perfect order in my domain',
      excitable: 'find a worthy fight',
      hyperthymic: 'experience every adventure possible',
      dysthymic: 'find meaning in this suffering',
      anxious: 'find a protector I can trust',
      emotive: 'help everyone I can',
      cyclothymic: 'find stability within myself',
      exalted: 'pursue the most beautiful ideal',
    };
    if (accentGoals[psychProfile.accentuation.key]) {
      goals.push(accentGoals[psychProfile.accentuation.key]);
    }

    // Disability-driven goal
    if (biography.disability.key !== 'none') {
      goals.push(biography.disability.goalModifier || 'overcome my limitations');
    }

    // Origin-driven goal
    if (biography.origin.key !== 'medieval_earth') {
      goals.push(`adapt to this world (from ${biography.origin.name})`);
    }

    // Occupation goal
    if (params.occupation) {
      const occGoals = {
        blacksmith: 'forge a masterwork weapon',
        healer: 'cure the incurable',
        merchant: 'build a trading empire',
        guard: 'protect the village from all threats',
        farmer: 'ensure a bountiful harvest',
        priest: 'spread faith and comfort',
        hunter: 'track the legendary beast',
        thief: 'pull off the perfect heist',
      };
      if (occGoals[params.occupation]) goals.push(occGoals[params.occupation]);
    }

    return goals;
  }

  // --- ADD MEMORY ---
  addMemory(npcId, content, importance = 0.5, emotion = 'neutral', type = 'event') {
    const npc = this.npcs.get(npcId);
    if (!npc) return;

    npc.memory.push({
      id: npc.nextMemoryId++,
      content,
      day: this.worldDay,
      importance: clamp(importance, 0, 1),
      emotion, // happy, sad, angry, fearful, neutral, disgusted, surprised
      type, // event, dialogue, combat, relationship, backstory
    });

    // Memory consolidation: keep max 50, remove least important
    if (npc.memory.length > 50) {
      npc.memory.sort((a, b) => b.importance - a.importance);
      npc.memory = npc.memory.slice(0, 40);
    }
  }

  // --- GET RELEVANT MEMORIES ---
  getRelevantMemories(npcId, context = '', limit = 5) {
    const npc = this.npcs.get(npcId);
    if (!npc) return [];

    // Simple relevance: recent + high importance + keyword match
    const contextWords = context.toLowerCase().split(/\s+/);
    return npc.memory
      .map(m => {
        let relevance = m.importance;
        // Recency boost
        const dayDiff = this.worldDay - m.day;
        relevance += Math.max(0, 1 - dayDiff * 0.1);
        // Keyword boost
        const contentLower = m.content.toLowerCase();
        for (const word of contextWords) {
          if (word.length > 3 && contentLower.includes(word)) relevance += 0.3;
        }
        return { ...m, relevance };
      })
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, limit);
  }

  // --- TICK NPC (one day of life) ---
  tickNPC(npcId, worldContext = {}) {
    const npc = this.npcs.get(npcId);
    if (!npc || !npc.alive) return null;
    if (npc.lastTickDay >= this.worldDay) return null; // already ticked today

    npc.lastTickDay = this.worldDay;

    // Decide behavior based on psychology
    const decision = psychology.decideBehavior(npc.psychProfile, {
      nearby: worldContext.nearbyNPCs || [],
      enemy: worldContext.threatsNearby,
      someoneHurt: worldContext.someoneNeedsHelp,
    });

    // Apply decision
    npc.currentActivity = `${decision.action}${decision.target ? ` (${decision.target})` : ''}`;
    npc.mood = decision.emotionalState;

    // Record action
    npc.actionHistory.push({
      day: this.worldDay,
      action: decision.action,
      motivation: decision.motivation,
      reasoning: decision.reasoning,
    });

    // Add memory
    this.addMemory(npcId, `Day ${this.worldDay}: I decided to ${decision.action}. ${decision.reasoning}`, 0.3, decision.emotionalState, 'event');

    // Evolve psychology (time passes)
    npc.psychProfile = psychology.evolvePsychology(npc.psychProfile, { type: 'time_passes' });

    // Physical condition effects
    if (npc.physicalState.disability !== 'none') {
      // Chronic conditions increase stress over time
      npc.psychProfile.stressLevel = clamp(npc.psychProfile.stressLevel + 0.02, 0, 1);
    }

    // Injury effects
    for (const injury of npc.physicalState.injuries) {
      if (!injury.healed) {
        npc.psychProfile.stressLevel = clamp(npc.psychProfile.stressLevel + 0.05, 0, 1);
      }
    }

    return {
      npcId,
      name: npc.name,
      action: decision.action,
      motivation: decision.motivation,
      mood: npc.mood,
      activity: npc.currentActivity,
    };
  }

  // --- TICK ALL NPCs ---
  tickAll(worldContext = {}) {
    this.worldDay++;
    const results = [];
    for (const [id, npc] of this.npcs) {
      if (npc.alive) {
        const result = this.tickNPC(id, worldContext);
        if (result) results.push(result);
      }
    }

    // Story tree: day event
    if (results.length > 0) {
      this.storyTree.addEvent({
        title: `Day ${this.worldDay}`,
        description: `${results.length} NPCs acted. ${results.map(r => `${r.name}: ${r.action}`).join('; ')}`,
        day: this.worldDay,
        participants: results.map(r => r.name),
        category: 'world_tick',
      });
    }

    return { day: this.worldDay, npcActions: results };
  }

  // --- APPLY EVENT to NPC ---
  applyEvent(npcId, event) {
    const npc = this.npcs.get(npcId);
    if (!npc) return null;

    // Evolve psychology
    const oldMood = npc.psychProfile.currentMood;
    npc.psychProfile = psychology.evolvePsychology(npc.psychProfile, event);
    npc.mood = npc.psychProfile.currentMood;

    // Apply injury if physical
    if (event.injury) {
      const updatedBio = bio.applyGameInjury(npc.biography, {
        type: event.injury,
        context: event.description || 'an incident',
        day: this.worldDay,
      });
      npc.biography = updatedBio;
      npc.physicalState.injuries.push({
        type: event.injury,
        day: this.worldDay,
        healed: false,
        description: event.description,
      });

      // Disability effects on psychology
      const disabilityEffects = bio.DISABILITIES[updatedBio.disability.key];
      if (disabilityEffects && disabilityEffects.psychEffects) {
        for (const [key, val] of Object.entries(disabilityEffects.psychEffects)) {
          npc.psychProfile[key] = clamp((npc.psychProfile[key] || 0.5) + val, 0, 1);
        }
      }
    }

    // Update goals based on new state
    if (event.type === 'violence' || event.injury) {
      // Maslow regression: drop to safety/survival
      npc.psychProfile.maslowLevel = { key: 'safety', ...psychology.MASLOW_LEVELS.safety };
      npc.goals = ['survive and recover', ...npc.goals.slice(0, 2)];
    }

    // Add memory
    const importance = event.type === 'violence' ? 0.9 : event.type === 'betrayal' ? 0.95 : 0.6;
    this.addMemory(npcId, `Day ${this.worldDay}: ${event.description || event.type}`, importance, npc.mood, 'event');

    // Story tree
    if (oldMood !== npc.mood) {
      this.storyTree.addPsychChange({
        npcName: npc.name,
        changeType: 'mood',
        from: oldMood,
        to: npc.mood,
        cause: event.description || event.type,
        day: this.worldDay,
      });
    }

    return {
      npcId,
      name: npc.name,
      previousMood: oldMood,
      newMood: npc.mood,
      psychProfile: npc.psychProfile,
      injuries: npc.physicalState.injuries,
      goals: npc.goals,
    };
  }

  // --- GENERATE DIALOGUE based on psychology ---
  generateDialogue(npcId, playerMessage = '') {
    const npc = this.npcs.get(npcId);
    if (!npc) return { error: 'NPC not found' };

    // Get relevant memories
    const memories = this.getRelevantMemories(npcId, playerMessage, 3);

    // Generate dialogue from psychology engine
    const dialogue = psychology.generateDialogue(npc.psychProfile, playerMessage);

    // Memory context enrichment
    let memoryContext = '';
    if (memories.length > 0) {
      const importantMemory = memories.find(m => m.importance > 0.7);
      if (importantMemory) {
        memoryContext = ` *remembers: ${importantMemory.content}*`;
      }
    }

    // Record interaction in memory
    this.addMemory(npcId, `Day ${this.worldDay}: Talked with the adventurer. They said: "${playerMessage.slice(0, 100)}"`, 0.4, npc.mood, 'dialogue');

    return {
      npcId,
      npcName: npc.name,
      dialogue: dialogue + memoryContext,
      mood: npc.mood,
      accentuation: npc.psychProfile.accentuation.name,
      memoryUsed: memories.length > 0 ? memories[0].content : null,
    };
  }

  // --- NPC-NPC INTERACTION ---
  interactNPCs(npcAId, npcBId) {
    const a = this.npcs.get(npcAId);
    const b = this.npcs.get(npcBId);
    if (!a || !b) return null;

    // Determine interaction type based on psychology
    const aProfile = a.psychProfile;
    const bProfile = b.psychProfile;

    // Sentiment between them
    const aSentiment = a.relationships[npcBId]?.sentiment || 0;
    const bSentiment = b.relationships[npcAId]?.sentiment || 0;

    let interactionType, summary;

    if (aSentiment < -0.5 || bSentiment < -0.5) {
      // Hostile
      if (aProfile.accentuation.key === 'excitable' || bProfile.accentuation.key === 'excitable') {
        interactionType = 'fight';
        summary = `${a.name} and ${b.name} came to blows over old grievances.`;
      } else {
        interactionType = 'argument';
        summary = `${a.name} and ${b.name} exchanged heated words.`;
      }
    } else if (aSentiment > 0.5 && bSentiment > 0.5) {
      // Close friends
      interactionType = 'help';
      summary = `${a.name} and ${b.name} supported each other.`;
    } else {
      // Neutral
      interactionType = randomChoice(['trade', 'talk', 'gossip']);
      summary = `${a.name} and ${b.name} had a ${interactionType}.`;
    }

    // Update sentiments
    const sentimentDelta = interactionType === 'fight' ? -0.15 : interactionType === 'help' ? 0.1 : 0.02;
    if (!a.relationships[npcBId]) a.relationships[npcBId] = { sentiment: 0, history: [] };
    if (!b.relationships[npcAId]) b.relationships[npcAId] = { sentiment: 0, history: [] };
    a.relationships[npcBId].sentiment = clamp(a.relationships[npcBId].sentiment + sentimentDelta, -1, 1);
    b.relationships[npcAId].sentiment = clamp(b.relationships[npcAId].sentiment + sentimentDelta, -1, 1);
    a.relationships[npcBId].history.push({ day: this.worldDay, type: interactionType });
    b.relationships[npcAId].history.push({ day: this.worldDay, type: interactionType });

    // Memories
    this.addMemory(npcAId, `Day ${this.worldDay}: ${summary}`, 0.5, interactionType === 'fight' ? 'angry' : 'neutral', 'relationship');
    this.addMemory(npcBId, `Day ${this.worldDay}: ${summary}`, 0.5, interactionType === 'fight' ? 'angry' : 'neutral', 'relationship');

    // Story tree
    this.storyTree.addRelationshipEvent({
      npcA: a.name,
      npcB: b.name,
      change: sentimentDelta,
      reason: summary,
      day: this.worldDay,
    });

    return { interactionType, summary, sentimentDelta };
  }

  // --- GET DEEP PROFILE (for player inspection) ---
  getDeepProfile(npcId) {
    const npc = this.npcs.get(npcId);
    if (!npc) return null;

    return {
      // Identity
      id: npc.id,
      name: npc.name,
      occupation: npc.occupation,
      age: npc.biography.age,
      alive: npc.alive,

      // Psychology
      accentuation: npc.psychProfile.accentuation.name,
      accentuationTraits: npc.psychProfile.accentuation.traits,
      jungType: npc.psychProfile.jungType.label,
      maslowLevel: npc.psychProfile.maslowLevel.name,
      freudBalance: npc.psychProfile.freudBalance,
      berneState: npc.psychProfile.berneState,
      defenses: npc.psychProfile.defenses,
      emotionalStability: npc.psychProfile.emotionalStability,
      empathy: npc.psychProfile.empathy,
      willpower: npc.psychProfile.willpower,
      psychopathyPotential: npc.psychProfile.psychopathyPotential,
      currentMood: npc.mood,
      stressLevel: npc.psychProfile.stressLevel,
      innerConflicts: npc.psychProfile.innerConflicts,

      // Biography
      origin: npc.biography.origin.name,
      originTraits: npc.biography.origin.culturalTraits,
      physiology: npc.biography.origin.physiology,
      parents: npc.biography.parents,
      childhood: npc.biography.childhood,
      formativeEvents: npc.biography.formativeEvents,
      disability: npc.biography.disability,
      narrativeSummary: npc.biography.summary,

      // Current state
      goals: npc.goals,
      physicalState: npc.physicalState,
      currentActivity: npc.currentActivity,

      // Memory (recent 10)
      recentMemories: npc.memory.slice(-10),

      // Relationships
      relationships: Object.entries(npc.relationships).map(([targetId, rel]) => {
        const target = this.npcs.get(targetId);
        return {
          targetId,
          targetName: target?.name || targetId,
          sentiment: rel.sentiment,
          history: (rel.history || []).slice(-5),
        };
      }),

      // Action history (last 10)
      recentActions: npc.actionHistory.slice(-10),

      // Speech style
      speechStyle: npc.psychProfile.speechStyle,
      underStress: npc.psychProfile.underStress,

      // D&D stats
      level: npc.level,
      class_id: npc.class_id,
      ability_scores: npc.ability_scores,
      hp: npc.hp,
      max_hp: npc.max_hp,
      ac: npc.ac,
    };
  }

  // --- IMPORT existing NPCs from JSON ---
  importFromJSON(npcsData, existingRelationships = true) {
    for (const npcData of npcsData) {
      const npc = this.createNPC({
        id: npcData.id,
        name: npcData.name,
        occupation: npcData.occupation,
        age: npcData.age,
        level: npcData.level,
        class_id: npcData.class_id,
        ability_scores: npcData.ability_scores,
        max_hp: npcData.max_hp,
        ac: npcData.ac,
        equipment_ids: npcData.equipment_ids,
        location_id: npcData.location_id,
        faction: npcData.faction,
        // Map existing archetype to accentuation
        accentuation: this._archetypeToAccentuation(npcData.archetype),
        origin: 'medieval_earth',
      });

      // Import existing goals
      if (npcData.goals) npc.goals = npcData.goals;
      // Import backstory as memory
      if (npcData.backstory) {
        this.addMemory(npc.id, npcData.backstory, 1.0, 'neutral', 'backstory');
      }
    }

    // Import relationships
    if (existingRelationships) {
      for (const npcData of npcsData) {
        if (npcData.relationships) {
          for (const rel of npcData.relationships) {
            const npc = this.npcs.get(npcData.id);
            if (npc) {
              npc.relationships[rel.target_id] = {
                sentiment: rel.sentiment,
                history: [{ day: 0, type: 'pre-existing', reason: rel.reason }],
              };
            }
          }
        }
      }
    }
  }

  // Map archetype → Leonhard accentuation
  _archetypeToAccentuation(archetype) {
    const map = {
      guardian: 'dysthymic', sage: 'pedantic', trickster: 'hyperthymic',
      zealot: 'stuck', caretaker: 'emotive', merchant_soul: 'hyperthymic',
      hermit: 'anxious', brawler: 'excitable', schemer: 'stuck',
      idealist: 'exalted', stoic: 'dysthymic', gossip: 'demonstrative',
      coward: 'anxious', rebel: 'excitable', romantic: 'exalted',
      sentinel: 'pedantic', hedonist: 'hyperthymic', martyr: 'emotive',
      predator: 'stuck', jester: 'hyperthymic', curator: 'pedantic',
      survivalist: 'anxious', empath: 'emotive',
    };
    return map[archetype] || undefined;
  }

  // --- GET ALL NPCs summary ---
  getAllNPCs() {
    return Array.from(this.npcs.values()).map(npc => ({
      id: npc.id,
      name: npc.name,
      occupation: npc.occupation,
      mood: npc.mood,
      alive: npc.alive,
      location_id: npc.location_id,
      accentuation: npc.psychProfile.accentuation.name,
      maslowLevel: npc.psychProfile.maslowLevel.name,
      origin: npc.biography.origin.name,
      disability: npc.biography.disability.name,
      stressLevel: npc.psychProfile.stressLevel,
      currentActivity: npc.currentActivity,
    }));
  }
}

module.exports = { NPCLifeService };
