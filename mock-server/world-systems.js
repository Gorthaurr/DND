// ============================================
// WORLD SYSTEMS — Vehicles, Hazards, Mutations, Deals, Soul Coins
// Based on D&D Descent into Avernus sessions
// ============================================

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }

// ============================================
// INFERNAL WAR MACHINES
// ============================================
const VEHICLE_TYPES = {
  devil_ride: { name: "Devil's Ride", type: 'motorcycle', seats: 1, platforms: 0, ac: 19, hp: 100, speed: 120, fuelPerCoin: 24, weapons: [], description: 'Infernal motorcycle. Fast, nimble, dangerous.' },
  tormentor: { name: 'Tormentor', type: 'buggy', seats: 4, platforms: 2, ac: 19, hp: 150, speed: 100, fuelPerCoin: 24, weapons: ['acid_sprayer'], description: 'Armored dune buggy with acid sprayer. The workhorse of Avernus.' },
  demon_grinder: { name: 'Demon Grinder', type: 'bus', seats: 8, platforms: 4, ac: 21, hp: 300, speed: 60, fuelPerCoin: 48, weapons: ['wrecking_ball', 'chomper', 'harpoon'], description: 'Massive war bus with crane, chains, and crushing jaws. Mad Maggie drives one.' },
  scavenger: { name: 'Scavenger', type: 'truck', seats: 6, platforms: 2, ac: 18, hp: 200, speed: 80, fuelPerCoin: 36, weapons: ['harpoon'], description: 'Salvage truck with harpoon launcher and storage.' },
};

const VEHICLE_WEAPONS = {
  acid_sprayer: { name: 'Acidic Bile Sprayer', damage: '4d8', type: 'acid', range: 60, description: 'Sprays corrosive demon bile in a cone.' },
  wrecking_ball: { name: 'Wrecking Ball', damage: '6d8', type: 'bludgeoning', range: 15, description: 'Massive spiked ball on a chain.' },
  chomper: { name: 'Chomper', damage: '4d10', type: 'piercing', range: 5, description: 'Mechanical jaws that snap shut.' },
  harpoon: { name: 'Harpoon Launcher', damage: '3d8', type: 'piercing', range: 120, description: 'Fires a chained harpoon that can reel in targets.' },
};

class VehicleManager {
  constructor() { this.vehicles = new Map(); }

  createVehicle(typeKey, ownerId = null) {
    const template = VEHICLE_TYPES[typeKey];
    if (!template) return null;
    const id = `vehicle-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`;
    const vehicle = {
      id, ...template, typeKey, currentHp: template.hp, fuel: 0,
      driver: null, passengers: [], platformRiders: [],
      ownerId, damaged: false, customName: null,
    };
    this.vehicles.set(id, vehicle);
    return vehicle;
  }

  fuelVehicle(vehicleId, soulCoins = 1) {
    const v = this.vehicles.get(vehicleId);
    if (!v) return null;
    v.fuel += soulCoins * v.fuelPerCoin;
    return { fuel: v.fuel, hoursRemaining: v.fuel };
  }

  driveCheck(vehicleId, dexterity, proficient = false) {
    const v = this.vehicles.get(vehicleId);
    if (!v || v.fuel <= 0) return { success: false, reason: 'No fuel or vehicle not found' };
    const d20 = randomInt(1, 20);
    const mod = Math.floor((dexterity - 10) / 2);
    const prof = proficient ? 2 : 0;
    const total = d20 + mod + prof;
    const isCrit = d20 === 20;
    const isFail = d20 === 1;
    let result;
    if (isCrit) result = { success: true, flair: true, description: 'Perfect maneuver! Vehicle handles like an extension of your body.' };
    else if (isFail) result = { success: false, crash: true, description: 'You lose control! The vehicle clips an obstacle.' };
    else if (total >= 15) result = { success: true, description: 'Smooth driving. You navigate hazards with ease.' };
    else if (total >= 10) result = { success: true, rough: true, description: 'You keep it on course, but it\'s bumpy.' };
    else result = { success: false, description: 'You swerve dangerously. Passengers must hold on!' };
    return { ...result, d20, total, modifier: mod, proficiency: prof, breakdown: `${d20} + ${mod}${prof ? ` + ${prof}` : ''} = ${total}` };
  }
}

// ============================================
// SOUL COINS
// ============================================
const SOUL_COIN_EFFECTS = {
  onPickup: { wisdomSave: 14, failEffect: 'You hear screaming souls. Resist the urge to use them.' },
  onBite: { conSave: 12, failEffect: 'Hundreds of screaming voices deafen you for 1 round.' },
  onUse: { description: 'The soul coin screams as it powers the machine. One more soul consumed.' },
  value: 'Powers infernal machines for ~24 hours. Also a currency in the Nine Hells.',
};

// ============================================
// ENVIRONMENTAL HAZARDS
// ============================================
const HAZARDS = {
  sandstorm: {
    name: 'Sandstorm', save: 'CON', dc: 14, damage: '2d8', type: 'acid',
    description: 'Burning sand tears at flesh. Constitution save or take acid damage from soul-infused particles.',
    onFail: 'Sand seeps into skin, causing burning pain and possible memory fragments.',
    advantage: 'Vehicles provide advantage on the save.',
  },
  demon_ichor: {
    name: 'Demon Ichor Pool', save: 'CON', dc: 12, damage: '1d6', type: 'necrotic',
    description: 'Black viscous pools of liquefied demon corpses. Contact causes random mutations.',
    onFail: 'Roll on the mutation table. Something... changes.',
    mutationChance: 0.6,
  },
  fire_tornado: {
    name: 'Fire Tornado', save: 'DEX', dc: 16, damage: '4d6', type: 'fire',
    description: 'Columns of burning fire sweep the landscape. Dodge or burn.',
    onFail: 'Engulfed in flames. Everything flammable ignites.',
  },
  river_styx: {
    name: 'River Styx Water', save: 'INT', dc: 15, damage: '0', type: 'psychic',
    description: 'The waters of forgetting. Contact erases memories.',
    onFail: 'Lose memories. Specific effects depend on amount of contact.',
    memoryLoss: true,
  },
  lemure_horde: {
    name: 'Lemure Horde', save: 'DEX', dc: 10, damage: '1d4', type: 'bludgeoning',
    description: 'A crawling mass of the lowest devils. Disgusting but mostly harmless.',
    onFail: 'Covered in lemure ichor. Smells terrible for hours.',
  },
  meteor: {
    name: 'Falling Meteor', save: 'DEX', dc: 18, damage: '6d6', type: 'fire',
    description: 'A chunk of burning rock falls from the amber sky.',
    onFail: 'Direct hit. Massive fire damage.',
  },
  ghost_sentries: {
    name: 'Spectral Sentries', save: 'CHA', dc: 14, damage: '2d8', type: 'necrotic',
    description: 'Ghostly knights that guard ancient sites. They ask questions before allowing passage.',
    onFail: 'Cold necrotic damage as the ghost\'s sorrow flows through you.',
    hasDialogue: true,
  },
};

// ============================================
// MUTATION SYSTEM (from Demon Ichor contact)
// ============================================
const MUTATIONS = [
  { id: 'ear_wings', name: 'Ear Wings', description: 'Your ears grow into leathery wings. Flying speed 5ft. Cannot hear normally until cured.', effect: { flySpeed: 5, deafened: true }, severity: 'minor', cure: 'Lesser Restoration' },
  { id: 'scales', name: 'Demon Scales', description: 'Patches of dark scales grow on your skin. +1 AC but disadvantage on Charisma checks.', effect: { acBonus: 1, chaDisadvantage: true }, severity: 'minor', cure: 'Remove Curse' },
  { id: 'third_eye', name: 'Third Eye', description: 'A glowing eye opens on your forehead. Darkvision 60ft but NPCs find you unsettling.', effect: { darkvision: 60 }, severity: 'moderate', cure: 'Greater Restoration' },
  { id: 'claws', name: 'Demon Claws', description: 'Your fingernails harden into claws. Unarmed strikes deal 1d6 slashing but can\'t hold delicate objects.', effect: { unarmedDamage: '1d6' }, severity: 'minor', cure: 'Lesser Restoration' },
  { id: 'horns', name: 'Horns', description: 'Small horns sprout from your forehead. Can use as a natural weapon (1d4+STR).', effect: { naturalWeapon: '1d4' }, severity: 'minor', cure: 'Remove Curse' },
  { id: 'tail', name: 'Barbed Tail', description: 'A thin, barbed tail grows. Bonus action tail attack (1d4 piercing).', effect: { bonusAttack: '1d4' }, severity: 'moderate', cure: 'Greater Restoration' },
  { id: 'ember_blood', name: 'Ember Blood', description: 'Your blood glows orange. Resistance to fire but vulnerability to cold.', effect: { fireResistance: true, coldVulnerability: true }, severity: 'moderate', cure: 'Greater Restoration' },
  { id: 'shadow_skin', name: 'Shadow Skin', description: 'Skin darkens to near-black. Advantage on stealth in darkness, disadvantage in bright light.', effect: { stealthAdvDark: true, stealthDisadvLight: true }, severity: 'minor', cure: 'Lesser Restoration' },
  { id: 'swollen_limb', name: 'Swollen Limb', description: 'One limb swells grotesquely. +2 STR but speed reduced by 5ft.', effect: { strBonus: 2, speedPenalty: 5 }, severity: 'moderate', cure: 'Lesser Restoration' },
  { id: 'voice_change', name: 'Infernal Voice', description: 'Voice becomes deep and echoing. Advantage on Intimidation, disadvantage on Persuasion.', effect: { intimidationAdv: true, persuasionDisadv: true }, severity: 'minor', cure: 'Remove Curse' },
];

function rollMutation() { return randomChoice(MUTATIONS); }

// ============================================
// DEAL / CONTRACT SYSTEM
// ============================================
class DealManager {
  constructor() { this.activeDeals = []; this.completedDeals = []; }

  createDeal({ title, npcName, description, tasks, rewards, penalties, expiresDay = null }) {
    const deal = {
      id: `deal-${Date.now()}`,
      title, npcName, description,
      tasks: tasks.map((t, i) => ({ id: i, description: t, completed: false })),
      rewards: rewards || [],
      penalties: penalties || ['Death. In Avernus, that\'s permanent.'],
      expiresDay,
      status: 'active', // active, completed, failed, broken
      createdDay: 0,
      consequences: [],
    };
    this.activeDeals.push(deal);
    return deal;
  }

  completeTask(dealId, taskIndex) {
    const deal = this.activeDeals.find(d => d.id === dealId);
    if (!deal) return null;
    deal.tasks[taskIndex].completed = true;
    if (deal.tasks.every(t => t.completed)) {
      deal.status = 'completed';
      this.completedDeals.push(deal);
      this.activeDeals = this.activeDeals.filter(d => d.id !== dealId);
    }
    return deal;
  }

  breakDeal(dealId) {
    const deal = this.activeDeals.find(d => d.id === dealId);
    if (!deal) return null;
    deal.status = 'broken';
    deal.consequences = deal.penalties;
    this.completedDeals.push(deal);
    this.activeDeals = this.activeDeals.filter(d => d.id !== dealId);
    return deal;
  }

  getActiveDeals() { return this.activeDeals; }
  getAllDeals() { return [...this.activeDeals, ...this.completedDeals]; }
}

// ============================================
// PARTY MANAGER
// ============================================
class PartyManager {
  constructor() {
    this.members = []; // { id, name, type: 'player'|'npc'|'companion', role: 'driver'|'guard'|'healer'|'scout' }
    this.vehicle = null;
    this.location = null;
    this.travelLog = [];
  }

  addMember(member) {
    if (!this.members.find(m => m.id === member.id)) {
      this.members.push({ ...member, joinedDay: 0 });
    }
    return this.members;
  }

  removeMember(memberId) {
    this.members = this.members.filter(m => m.id !== memberId);
    return this.members;
  }

  assignRole(memberId, role) {
    const member = this.members.find(m => m.id === memberId);
    if (member) member.role = role;
    return member;
  }

  setVehicle(vehicle) { this.vehicle = vehicle; }

  travel(destination, distance, hazards = []) {
    const entry = {
      from: this.location, to: destination, distance,
      day: 0, hazardsEncountered: hazards,
      survived: true, casualties: [],
    };
    this.travelLog.push(entry);
    this.location = destination;
    return entry;
  }

  getState() {
    return {
      members: this.members,
      vehicle: this.vehicle,
      location: this.location,
      partySize: this.members.length,
      hasVehicle: !!this.vehicle,
    };
  }
}

// ============================================
// MEMORY WIPE (River Styx)
// ============================================
function riverStyxEffect(intScore, amount = 'splash') {
  const save = randomInt(1, 20);
  const mod = Math.floor((intScore - 10) / 2);
  const total = save + mod;
  const dc = amount === 'splash' ? 12 : amount === 'submerge' ? 18 : 15;
  const success = total >= dc;

  const effects = {
    splash: { memoriesLost: 'recent', description: 'You forget the last few hours. Names and faces blur.' },
    contact: { memoriesLost: 'partial', description: 'Significant memories vanish. You forget why you\'re here and who your companions are.' },
    submerge: { memoriesLost: 'total', description: 'Nearly all memories gone. You know your name and basic skills, but everything else is a blank slate.' },
  };

  return {
    d20: save, total, dc, success, intMod: mod,
    effect: success ? 'You resist the waters of forgetting.' : effects[amount].description,
    memoriesLost: success ? 'none' : effects[amount].memoriesLost,
    breakdown: `${save} (d20) + ${mod} (INT) = ${total} vs DC ${dc}`,
  };
}

module.exports = {
  VEHICLE_TYPES, VEHICLE_WEAPONS, VehicleManager,
  SOUL_COIN_EFFECTS,
  HAZARDS,
  MUTATIONS, rollMutation,
  DealManager,
  PartyManager,
  riverStyxEffect,
};
