// ============================================
// SHADOW SYSTEM
// Based on: Shadow of Mordor/War patent US20160279522A1
// NPCs remember, evolve, hold grudges, rise in power
// ============================================

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function clamp(val, min, max) { return Math.min(max, Math.max(min, val)); }

// --- FACTION HIERARCHY ---
// Overlord → Warchief → Captain → Soldier
const RANKS = {
  soldier: { name: 'Soldier', tier: 0, powerRange: [1, 5], maxBodyguards: 0 },
  captain: { name: 'Captain', tier: 1, powerRange: [5, 15], maxBodyguards: 2 },
  warchief: { name: 'Warchief', tier: 2, powerRange: [15, 30], maxBodyguards: 4 },
  overlord: { name: 'Overlord', tier: 3, powerRange: [25, 50], maxBodyguards: 6 },
};

// --- DEATH CHEATING: how NPCs come back from "death" ---
const DEATH_CHEATS = [
  { method: 'survived_wounds', description: 'barely survived, covered in scars', chance: 0.4 },
  { method: 'necromancy', description: 'brought back by dark magic, partly undead', chance: 0.1 },
  { method: 'sheer_will', description: 'refused to die out of pure hatred', chance: 0.25 },
  { method: 'rescued', description: 'dragged away by allies before death', chance: 0.2 },
  { method: 'mechanical', description: 'rebuilt with metal parts replacing lost flesh', chance: 0.05 },
];

// --- KILL METHOD → SCAR/TRAIT ---
const KILL_METHOD_EFFECTS = {
  fire: {
    scars: ['burn_scars_face', 'burn_scars_body', 'melted_features'],
    traits_gained: ['fire_rage', 'fire_fear'],
    traits_weights: { fire_rage: 0.6, fire_fear: 0.4 },
    appearance: 'Severe burn scars cover their face and body',
    dialogue_reference: 'fire',
  },
  sword: {
    scars: ['sword_slash_face', 'missing_ear', 'deep_chest_scar'],
    traits_gained: ['blade_proof_armor', 'sword_phobia'],
    traits_weights: { blade_proof_armor: 0.7, sword_phobia: 0.3 },
    appearance: 'A massive sword scar runs across their face',
    dialogue_reference: 'blade',
  },
  poison: {
    scars: ['discolored_veins', 'chemical_burns', 'raspy_voice'],
    traits_gained: ['poison_immunity', 'poison_master'],
    traits_weights: { poison_immunity: 0.5, poison_master: 0.5 },
    appearance: 'Veins visible and darkened from poison exposure',
    dialogue_reference: 'poison',
  },
  fall: {
    scars: ['broken_bones_healed_wrong', 'limp', 'crushed_leg'],
    traits_gained: ['height_fear', 'unbreakable_bones'],
    traits_weights: { height_fear: 0.5, unbreakable_bones: 0.5 },
    appearance: 'Walks with a permanent limp from shattered bones',
    dialogue_reference: 'fall',
  },
  stealth: {
    scars: ['throat_scar', 'back_stab_scar'],
    traits_gained: ['paranoid_vigilance', 'stealth_detector'],
    traits_weights: { paranoid_vigilance: 0.6, stealth_detector: 0.4 },
    appearance: 'A vicious scar across the throat, always looking over shoulder',
    dialogue_reference: 'ambush',
  },
  magic: {
    scars: ['arcane_burns', 'glowing_wound', 'white_streak_hair'],
    traits_gained: ['magic_resistance', 'magic_hatred'],
    traits_weights: { magic_resistance: 0.5, magic_hatred: 0.5 },
    appearance: 'Strange arcane burns glow faintly on their skin',
    dialogue_reference: 'magic',
  },
  beast: {
    scars: ['claw_marks', 'bite_scars', 'missing_fingers'],
    traits_gained: ['beast_slayer', 'beast_fear'],
    traits_weights: { beast_slayer: 0.6, beast_fear: 0.4 },
    appearance: 'Deep claw marks rake across their body',
    dialogue_reference: 'beast',
  },
  unarmed: {
    scars: ['broken_jaw', 'flattened_nose', 'cauliflower_ear'],
    traits_gained: ['brawler_rage', 'humiliation_fury'],
    traits_weights: { brawler_rage: 0.4, humiliation_fury: 0.6 },
    appearance: 'Face permanently disfigured from brutal beating',
    dialogue_reference: 'fists',
  },
  humiliation: {
    scars: [],
    traits_gained: ['shame_rage', 'desperate_power'],
    traits_weights: { shame_rage: 0.7, desperate_power: 0.3 },
    appearance: 'Eyes burn with barely contained rage and humiliation',
    dialogue_reference: 'shame',
  },
};

// --- NPC COMBAT TRAITS ---
const COMBAT_TRAITS = {
  fire_rage: { name: 'Fire Rage', description: 'Burns with fury, attacks are fire-infused', bonusDamage: 'fire', behavior: 'aggressive when fire is used' },
  fire_fear: { name: 'Fire Fear', description: 'Terrified of fire, flees from flames', weakness: 'fire', behavior: 'panics and retreats near fire' },
  blade_proof_armor: { name: 'Blade-Proof', description: 'Wears heavy armor specifically to stop swords', resistances: ['slashing'], behavior: 'confident against blade weapons' },
  sword_phobia: { name: 'Sword Phobia', description: 'Flinches at drawn blades', weakness: 'slashing', behavior: 'hesitates when facing swords' },
  poison_immunity: { name: 'Poison Immune', description: 'Body has adapted to toxins', immunities: ['poison'], behavior: 'laughs at poison attempts' },
  poison_master: { name: 'Poison Master', description: 'Coats weapons in deadly poison', bonusDamage: 'poison', behavior: 'uses poisoned weapons' },
  paranoid_vigilance: { name: 'Ever-Watchful', description: 'Cannot be surprised or backstabbed', immunities: ['stealth'], behavior: 'constantly checking surroundings' },
  stealth_detector: { name: 'Stealth Detector', description: 'Enhanced senses detect hidden enemies', bonusPerception: 10, behavior: 'sniffs the air, listens intently' },
  magic_resistance: { name: 'Magic Resistant', description: 'Partially resistant to magical effects', resistances: ['magic'], behavior: 'shrugs off minor spells' },
  magic_hatred: { name: 'Mage Hunter', description: 'Specifically targets spellcasters first', behavior: 'charges at anyone casting spells' },
  brawler_rage: { name: 'Brawler', description: 'Prefers fists, grapples and throws', bonusDamage: 'bludgeoning', behavior: 'throws away weapons to use fists' },
  humiliation_fury: { name: 'Humiliation Fury', description: 'Driven by shame, fights with reckless abandon', bonusDamage: 'all', behavior: 'screams about past defeat' },
  shame_rage: { name: 'Shame Rage', description: 'So humiliated that hatred has made them stronger', bonusLevel: 5, behavior: 'shaking with rage, mentions being mocked by others' },
  desperate_power: { name: 'Desperate Power', description: 'Has nothing left to lose', bonusHP: 20, behavior: 'fights like a cornered animal' },
  height_fear: { name: 'Acrophobia', description: 'Terrified of heights and falling', weakness: 'fall', behavior: 'avoids elevated positions' },
  unbreakable_bones: { name: 'Iron Bones', description: 'Bones healed denser than before', resistances: ['bludgeoning'], behavior: 'laughs at blunt weapons' },
  beast_slayer: { name: 'Beast Slayer', description: 'Has learned to fight monsters', bonusDamage: 'vs_beasts', behavior: 'hunts dangerous creatures' },
  beast_fear: { name: 'Beast Fear', description: 'Traumatized by animal attacks', weakness: 'beasts', behavior: 'panics around large animals' },
};

// --- OBSESSION LEVELS ---
const OBSESSION_LEVELS = {
  0: { name: 'Indifferent', description: 'Doesn\'t care about the player' },
  1: { name: 'Aware', description: 'Knows about the player, casual interest' },
  2: { name: 'Grudge', description: 'Has a score to settle' },
  3: { name: 'Vendetta', description: 'Actively hunting the player' },
  4: { name: 'Obsessed', description: 'Life revolves around killing the player' },
  5: { name: 'Blood Oath', description: 'Will follow to the ends of the earth' },
};

// --- ENCOUNTER DIALOGUE TEMPLATES ---
const ENCOUNTER_DIALOGUES = {
  first_meeting: [
    '"Fresh meat for the wolves! You chose the wrong village to visit."',
    '"Well well... an adventurer. This should be... entertaining."',
  ],
  defeated_once: [
    '"YOU! I\'ve been waiting for this. Do you remember what you did to me?!"',
    '"*touches scar* Every night I dream of our last meeting. Tonight, it ends differently."',
    '"They told me you\'d come back. I\'ve prepared something special."',
  ],
  defeated_twice: [
    '"AGAIN?! How many times must I kill you before you stay dead?!"',
    '"*laughing maniacally* We keep meeting like this. It\'s almost romantic, isn\'t it?"',
    '"I\'ve lost count of how many times I\'ve beaten you. Are you enjoying this?"',
  ],
  defeated_many: [
    '"Am I cursed? Must I fight you EVERY day?! *exhausted*"',
    '"Oh. It\'s you. Again. *sighs deeply* Let\'s just get this over with."',
    '"I used to hate you. Now I just... pity us both. We\'re trapped in this dance."',
  ],
  player_killed_them_once: [
    '"*snarling through new scars* YOU THOUGHT I WAS DEAD?! I crawled back from the void for THIS!"',
    '"Remember me? You left me for dead. That was a mistake."',
    '"I survived. Barely. But surviving you... it changed me."',
  ],
  player_killed_them_many: [
    '"HOW MANY TIMES?! How many times will you kill me and I\'ll keep coming back?!"',
    '"*barely recognizable under scars* I don\'t even know why I keep fighting you. But I can\'t stop."',
    '"You\'ve killed me {death_count} times. Each time I come back... different. Stronger. Angrier."',
  ],
  humiliated: [
    '"*trembling with rage* The others LAUGH at me because of you! They call me your pet!"',
    '"You didn\'t even bother to kill me. That\'s worse. SO MUCH WORSE."',
    '"I was someone before you came along. Now I\'m a joke. But jokes can bite."',
  ],
  leveled_up_from_kills: [
    '"Every time you die, I grow stronger. Thank you for the promotion!"',
    '"Your failures have made ME the most powerful warrior here. Ironic, isn\'t it?"',
  ],
  obsessed: [
    '"I see your face when I close my eyes. I hear your footsteps in every shadow. This ends NOW."',
    '"My entire purpose is YOU. Nothing else matters. Not food, not sleep, not glory. Just. You."',
  ],
};

// ============================================
// SHADOW MANAGER
// ============================================

class ShadowManager {
  constructor() {
    this.factionHierarchy = {
      overlord: null,
      warchiefs: [],
      captains: [],
      soldiers: [],
    };
    this.encounters = new Map(); // npcId → encounter history
    this.deadPool = []; // NPCs that "died" but may return
    this.powerStruggles = []; // pending promotions/coups
  }

  // --- RECORD ENCOUNTER ---
  recordEncounter(npcId, encounter) {
    if (!this.encounters.has(npcId)) {
      this.encounters.set(npcId, {
        npcId,
        playerDeaths: 0, // times player died to this NPC
        npcDeaths: 0, // times this NPC "died"
        npcDefeats: 0, // defeated but not killed
        encounters: 0,
        killMethods: [],
        obsessionLevel: 0,
        lastEncounterDay: 0,
        firstEncounterDay: encounter.day,
        fled: 0,
        traits: [],
        scars: [],
        levelUps: 0,
      });
    }

    const record = this.encounters.get(npcId);
    record.encounters++;
    record.lastEncounterDay = encounter.day;

    switch (encounter.result) {
      case 'player_killed_npc':
        record.npcDeaths++;
        record.killMethods.push(encounter.killMethod || 'sword');
        break;
      case 'player_defeated_npc':
        record.npcDefeats++;
        break;
      case 'npc_killed_player':
        record.playerDeaths++;
        record.levelUps++;
        break;
      case 'npc_defeated_player':
        record.playerDeaths++;
        break;
      case 'player_fled':
        record.fled++;
        break;
    }

    // Update obsession
    record.obsessionLevel = this._calculateObsession(record);

    return record;
  }

  // --- CALCULATE OBSESSION ---
  _calculateObsession(record) {
    let obsession = 0;
    obsession += Math.min(record.encounters * 0.5, 2); // encounters
    obsession += record.npcDeaths * 1.5; // being killed fuels rage
    obsession += record.npcDefeats * 0.8; // defeats too
    obsession += record.playerDeaths * 0.3; // killing player is satisfying but addictive
    return Math.min(5, Math.floor(obsession));
  }

  // --- NPC DIES: decide if they cheat death ---
  processNPCDeath(npcId, killMethod, day) {
    const record = this.recordEncounter(npcId, {
      result: 'player_killed_npc',
      killMethod,
      day,
    });

    // Chance to cheat death increases with encounters
    const baseCheathChance = 0.3;
    const encounterBonus = Math.min(record.encounters * 0.1, 0.4);
    const cheatChance = baseCheathChance + encounterBonus;

    const cheated = Math.random() < cheatChance;

    if (cheated) {
      // Select death cheat method
      const method = randomChoice(DEATH_CHEATS);

      // Get kill method effects
      const effects = KILL_METHOD_EFFECTS[killMethod] || KILL_METHOD_EFFECTS.sword;
      const newScar = randomChoice(effects.scars || ['battle_scar']);
      const newTraitKey = this._weightedTraitChoice(effects.traits_gained, effects.traits_weights);
      const newTrait = COMBAT_TRAITS[newTraitKey];

      // Store in dead pool
      this.deadPool.push({
        npcId,
        deathDay: day,
        returnDay: day + randomInt(2, 7), // come back in 2-7 days
        method: method.method,
        methodDescription: method.description,
        newScar,
        newTraitKey,
        newTrait,
        appearance: effects.appearance,
        killMethod,
        levelBonus: Math.min(record.npcDeaths * 2, 10), // stronger each return
      });

      record.scars.push(newScar);
      if (!record.traits.includes(newTraitKey)) record.traits.push(newTraitKey);

      return {
        cheatedDeath: true,
        method: method.method,
        description: method.description,
        returnsIn: `${this.deadPool[this.deadPool.length - 1].returnDay - day} days`,
        willReturn: true,
      };
    }

    return { cheatedDeath: false, permanentDeath: true };
  }

  _weightedTraitChoice(traits, weights) {
    const r = Math.random();
    let cumulative = 0;
    for (const trait of traits) {
      cumulative += weights[trait] || (1 / traits.length);
      if (r <= cumulative) return trait;
    }
    return traits[traits.length - 1];
  }

  // --- CHECK FOR RETURNING NEMESES ---
  checkReturns(currentDay) {
    const returning = [];
    const remaining = [];

    for (const dead of this.deadPool) {
      if (currentDay >= dead.returnDay) {
        returning.push(dead);
      } else {
        remaining.push(dead);
      }
    }

    this.deadPool = remaining;
    return returning;
  }

  // --- PLAYER DIES TO NPC: NPC levels up ---
  processPlayerDeath(npcId, day) {
    const record = this.recordEncounter(npcId, {
      result: 'npc_killed_player',
      day,
    });

    return {
      npcId,
      playerDeathCount: record.playerDeaths,
      npcLevelUp: true,
      newLevel: record.levelUps,
      obsession: OBSESSION_LEVELS[record.obsessionLevel],
    };
  }

  // --- GENERATE ENCOUNTER DIALOGUE ---
  generateEncounterDialogue(npcId, npcName) {
    const record = this.encounters.get(npcId);
    if (!record) {
      return randomChoice(ENCOUNTER_DIALOGUES.first_meeting);
    }

    let dialoguePool;

    if (record.npcDeaths >= 3) {
      dialoguePool = ENCOUNTER_DIALOGUES.player_killed_them_many;
    } else if (record.npcDeaths >= 1) {
      dialoguePool = ENCOUNTER_DIALOGUES.player_killed_them_once;
    } else if (record.playerDeaths >= 5) {
      dialoguePool = ENCOUNTER_DIALOGUES.defeated_many;
    } else if (record.playerDeaths >= 2) {
      dialoguePool = ENCOUNTER_DIALOGUES.defeated_twice;
    } else if (record.npcDefeats >= 2) {
      dialoguePool = ENCOUNTER_DIALOGUES.humiliated;
    } else if (record.obsessionLevel >= 4) {
      dialoguePool = ENCOUNTER_DIALOGUES.obsessed;
    } else if (record.encounters >= 2) {
      dialoguePool = ENCOUNTER_DIALOGUES.defeated_once;
    } else {
      dialoguePool = ENCOUNTER_DIALOGUES.first_meeting;
    }

    let dialogue = randomChoice(dialoguePool);
    dialogue = dialogue.replace('{death_count}', String(record.npcDeaths));
    dialogue = dialogue.replace('{npc_name}', npcName);

    return dialogue;
  }

  // --- GET SHADOW INFO ---
  getShadowInfo(npcId) {
    const record = this.encounters.get(npcId);
    if (!record) return null;

    return {
      ...record,
      obsessionName: OBSESSION_LEVELS[record.obsessionLevel].name,
      obsessionDescription: OBSESSION_LEVELS[record.obsessionLevel].description,
      traitsDetails: record.traits.map(t => COMBAT_TRAITS[t]).filter(Boolean),
      isShadow: record.obsessionLevel >= 3,
      threatLevel: record.encounters + record.levelUps * 2,
    };
  }

  // --- GET ALL NEMESES ---
  getAllShadows() {
    const nemeses = [];
    for (const [npcId, record] of this.encounters) {
      if (record.obsessionLevel >= 2) {
        nemeses.push({
          npcId,
          encounters: record.encounters,
          obsession: OBSESSION_LEVELS[record.obsessionLevel],
          playerDeaths: record.playerDeaths,
          npcDeaths: record.npcDeaths,
          traits: record.traits.map(t => COMBAT_TRAITS[t]?.name).filter(Boolean),
          scars: record.scars,
          isInDeadPool: this.deadPool.some(d => d.npcId === npcId),
        });
      }
    }
    return nemeses.sort((a, b) => b.obsession - a.obsession);
  }

  // --- FACTION POWER STRUGGLE ---
  triggerPowerStruggle(eventType = 'random') {
    const events = [
      { type: 'promotion', description: 'A soldier has risen to captain through strength' },
      { type: 'coup', description: 'A captain challenges the warchief for dominance' },
      { type: 'betrayal', description: 'An ally has turned traitor' },
      { type: 'duel', description: 'Two captains duel for territory' },
      { type: 'recruitment', description: 'A powerful warrior joins the faction' },
    ];

    return randomChoice(events);
  }

  // --- SERIALIZE ---
  toJSON() {
    return {
      encounters: Object.fromEntries(this.encounters),
      deadPool: this.deadPool,
      factionHierarchy: this.factionHierarchy,
    };
  }

  static fromJSON(data) {
    const nm = new ShadowManager();
    if (data.encounters) {
      nm.encounters = new Map(Object.entries(data.encounters));
    }
    nm.deadPool = data.deadPool || [];
    nm.factionHierarchy = data.factionHierarchy || nm.factionHierarchy;
    return nm;
  }
}

module.exports = {
  ShadowManager,
  RANKS, DEATH_CHEATS, KILL_METHOD_EFFECTS, COMBAT_TRAITS,
  OBSESSION_LEVELS, ENCOUNTER_DIALOGUES,
};
