// ============================================
// ADVANCED GAME SYSTEMS
// Puzzles, Artifacts, Boss Encounters, Summons, Companions
// ============================================

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

// ============================================
// 1. PUZZLE / RIDDLE SYSTEM
// ============================================
const PUZZLE_TYPES = {
  order: { name: 'Sequence Puzzle', description: 'Activate elements in correct order', hint: 'Look for inscriptions near each element' },
  anagram: { name: 'Anagram', description: 'Rearrange letters to form the answer', hint: 'The answer hides within the question' },
  riddle: { name: 'Riddle', description: 'Answer the riddle to proceed', hint: 'Think literally and metaphorically' },
  cipher: { name: 'Cipher', description: 'Decode the message using the key', hint: 'Find the cipher disk or key nearby' },
  physical: { name: 'Physical Puzzle', description: 'Manipulate objects in the environment', hint: 'Strength and Dexterity may help' },
  musical: { name: 'Musical Puzzle', description: 'Play the correct sequence of notes', hint: 'Sheet music or murals may contain the answer' },
};

const PUZZLES = [
  { id: 'lamps_of_names', type: 'order', title: 'The Eight Lamps', description: 'Eight oil lamps on pedestals, each with an ancient name inscribed. Two have fallen. Speak the names in correct order to open the sealed door.', solution: ['naja', 'ken_almond', 'senna_simha', 'kah', 'no_fruity', 'rah_hotep', 'marketer', 'mocked'], hints: ['The fallen lamps may need to be replaced first', 'Light them as you speak', 'The order follows the royal bloodline'], reward: 'Door opens, guardian appears', dc: 15, skillCheck: 'history' },
  { id: 'lotus_cipher', type: 'cipher', title: 'The Lotus Cipher', description: 'A cipher disk with ancient symbols found on a sphinx pedestal. Rotating rings align symbols to decode a message on the sarcophagus.', solution: 'beneath_the_roots', hints: ['Match the ankh symbols along the two lines', 'The lotus represents what grows underground'], reward: 'Reveals hidden compartment', dc: 14, skillCheck: 'investigation' },
  { id: 'three_doors', type: 'riddle', title: 'The Three Doors', description: 'Three identical doors. Above each, an inscription: "I always lie", "I always tell truth", "I alternate". One door leads forward, one leads to a trap, one leads back.', solution: 'middle_door', hints: ['Ask each door about the others', 'The liar will point you wrong'], reward: 'Safe passage', dc: 13, skillCheck: 'insight' },
  { id: 'weight_scales', type: 'physical', title: 'Scales of Ma\'at', description: 'A giant scale with a feather on one side. Place something of equal weight to the feather — the weight of your conscience.', solution: 'confession', hints: ['It is not about physical weight', 'Speak your greatest regret', 'The feather weighs as much as truth'], reward: 'Blessing of the ancients (+2 WIS for 24h)', dc: 12, skillCheck: 'religion' },
  { id: 'blood_runes', type: 'order', title: 'Runes of Blood', description: 'Five runes carved into the wall, each glowing faintly. Touch them in wrong order = damage. Right order = the wall opens.', solution: ['fire', 'earth', 'water', 'air', 'void'], hints: ['Elements of creation in order of their birth', 'Fire was first, void was last'], reward: 'Hidden treasure vault', dc: 16, skillCheck: 'arcana' },
  { id: 'mirror_maze', type: 'physical', title: 'Hall of Mirrors', description: 'A corridor of mirrors where your reflection moves independently. Find which mirror shows your TRUE self to proceed.', solution: 'the_cracked_mirror', hints: ['Perfection is a lie', 'The true self has flaws', 'Cast light on the imperfect one'], reward: 'Mirror becomes a portal', dc: 14, skillCheck: 'perception' },
  { id: 'song_stones', type: 'musical', title: 'The Singing Stones', description: 'Seven stones that emit musical notes when struck. Play the melody depicted in the wall carving to unlock the gate.', solution: ['do', 're', 'mi', 'fa', 'sol', 'la', 'ti'], hints: ['The birds on the mural sit at different heights', 'Each height is a note', 'Performance check to play correctly'], reward: 'Gate opens peacefully', dc: 13, skillCheck: 'performance' },
  { id: 'word_door', type: 'riddle', title: 'The Speaking Door', description: 'A door with a face carved in stone that asks: "I have cities but no houses, forests but no trees, water but no fish. What am I?"', solution: 'a_map', hints: ['Think of representations, not reality', 'What shows the world without being the world?'], reward: 'Door opens', dc: 11, skillCheck: 'intelligence' },
];

class PuzzleManager {
  constructor() {
    this.activePuzzles = new Map();
    this.solvedPuzzles = [];
    this.attempts = new Map();
  }

  getPuzzle(puzzleId) {
    return PUZZLES.find(p => p.id === puzzleId) || null;
  }

  startPuzzle(puzzleId) {
    const puzzle = this.getPuzzle(puzzleId);
    if (!puzzle) return null;
    this.activePuzzles.set(puzzleId, { ...puzzle, startedAt: Date.now(), hintIndex: 0 });
    this.attempts.set(puzzleId, 0);
    return { id: puzzle.id, title: puzzle.title, description: puzzle.description, type: puzzle.type };
  }

  attemptSolve(puzzleId, answer, skillBonus = 0) {
    const puzzle = this.activePuzzles.get(puzzleId);
    if (!puzzle) return { error: 'No active puzzle' };
    const attempts = (this.attempts.get(puzzleId) || 0) + 1;
    this.attempts.set(puzzleId, attempts);

    const d20 = randomInt(1, 20);
    const total = d20 + skillBonus;
    const normalizedAnswer = (answer || '').toLowerCase().replace(/[\s_-]+/g, '_').trim();
    const correctAnswer = Array.isArray(puzzle.solution) ? puzzle.solution.join('_') : puzzle.solution;
    const isCorrect = normalizedAnswer.includes(correctAnswer.replace(/[\s_-]+/g, '_')) || total >= puzzle.dc + 5;

    if (isCorrect || total >= puzzle.dc) {
      this.solvedPuzzles.push(puzzleId);
      this.activePuzzles.delete(puzzleId);
      return { solved: true, narration: `SUCCESS! ${puzzle.reward}`, d20, total, dc: puzzle.dc, attempts, reward: puzzle.reward, breakdown: `${d20} + ${skillBonus} = ${total} vs DC ${puzzle.dc}` };
    }

    return { solved: false, narration: 'The puzzle remains unsolved. Try a different approach.', d20, total, dc: puzzle.dc, attempts, hint: attempts >= 2 ? puzzle.hints[Math.min(attempts - 2, puzzle.hints.length - 1)] : null, breakdown: `${d20} + ${skillBonus} = ${total} vs DC ${puzzle.dc}` };
  }

  getHint(puzzleId) {
    const puzzle = this.activePuzzles.get(puzzleId);
    if (!puzzle) return null;
    const hint = puzzle.hints[puzzle.hintIndex] || 'No more hints available.';
    puzzle.hintIndex = Math.min(puzzle.hintIndex + 1, puzzle.hints.length - 1);
    return hint;
  }

  getRandomPuzzle() { return randomChoice(PUZZLES); }
}

// ============================================
// 2. TRINKETS / ARTIFACTS
// ============================================
const ARTIFACTS = {
  // Trinkets (minor, single-use or limited)
  picture_frame: { name: 'Enchanted Picture Frame', rarity: 'uncommon', type: 'trinket', charges: 1, effect: 'Capture an image of someone. Use it to cast Disguise Self as that person once.', mechanicEffect: { spell: 'disguise_self', uses: 1 } },
  knit_blanket: { name: 'Knit Blanket of Imagery', rarity: 'uncommon', type: 'trinket', charges: 3, effect: 'Project any image onto the blanket. The image is convincing but still looks like a blanket.', mechanicEffect: { spell: 'minor_illusion', uses: 3 } },
  pocket_watch: { name: 'Temporal Pocket Watch', rarity: 'rare', type: 'trinket', charges: 1, effect: 'Slow time for yourself. Advantage on DEX saves, ignore difficult terrain, Dodge as reaction.', mechanicEffect: { dexAdvantage: true, duration: '1 minute', uses: 1 } },
  sheet_music: { name: 'Enchanted Sheet Music', rarity: 'uncommon', type: 'trinket', charges: 3, effect: 'Sing to the tune for +5 to Charisma checks.', mechanicEffect: { charismaBonus: 5, uses: 3 } },
  dark_glasses: { name: 'Goggles of Night', rarity: 'uncommon', type: 'trinket', charges: -1, effect: 'Darkvision 60ft. Permanent while worn.', mechanicEffect: { darkvision: 60, permanent: true } },
  compass_crystal: { name: 'Compass and Crystal Set', rarity: 'rare', type: 'trinket', charges: -1, effect: 'Compass always points to the crystal. Plant the crystal and find your way back.', mechanicEffect: { tracking: true, permanent: true } },
  bag_of_tricks: { name: 'Bag of Tricks', rarity: 'uncommon', type: 'trinket', charges: 3, effect: 'Pull out a fuzzy ball. Throw it to summon a random beast that obeys you for 1 hour.', mechanicEffect: { summonBeast: true, uses: 3 } },
  // Weapons (permanent)
  dragon_wing_bow: { name: 'Dragon Wing Longbow', rarity: 'very_rare', type: 'weapon', charges: -1, effect: 'Longbow that looks like dragon wings when drawn. Arrows burst into flames on impact. +2 to attack, +1d6 fire damage.', mechanicEffect: { attackBonus: 2, bonusDamage: '1d6', damageType: 'fire' } },
  rapier_of_wounding: { name: 'Rapier of Wounding', rarity: 'very_rare', type: 'weapon', charges: -1, effect: 'Wounds from this blade do not heal naturally. Target loses 1d4 HP at start of each turn until magically healed.', mechanicEffect: { bleedDamage: '1d4', permanent: true } },
  flaming_greatsword: { name: 'Flame Tongue Greatsword', rarity: 'rare', type: 'weapon', charges: -1, effect: 'Command word ignites the blade. +2d6 fire damage while lit. Sheds bright light 40ft.', mechanicEffect: { bonusDamage: '2d6', damageType: 'fire', light: 40 } },
  // Armor
  shield_of_faith: { name: 'Shield of the Faithful', rarity: 'rare', type: 'armor', charges: -1, effect: '+2 AC. Can reroll failed saves against spells once per short rest.', mechanicEffect: { acBonus: 2, spellSaveReroll: true } },
  cloak_of_displacement: { name: 'Cloak of Displacement', rarity: 'rare', type: 'armor', charges: -1, effect: 'Illusion makes you appear slightly shifted. Attackers have disadvantage against you until you are hit.', mechanicEffect: { attackDisadvantage: true } },
  // Wondrous Items
  book_of_vile_darkness: { name: 'Book of Vile Darkness', rarity: 'artifact', type: 'wondrous', charges: -1, effect: 'The most evil book in existence. Grants immense power but corrupts the reader. +2 to all saves, can cast any necromancy spell, but WIS save DC 17 each day or alignment shifts toward evil.', mechanicEffect: { saveBonus: 2, corruption: true, wisdomSaveDC: 17 } },
  tear_of_zariel: { name: 'Tear of Zariel', rarity: 'artifact', type: 'wondrous', charges: 1, effect: 'A crystallized tear of the fallen angel. Radiates holy light. Can cure any curse or restore any petrified creature. The bearer loses the ability to cry.', mechanicEffect: { cureAll: true, cost: 'cannot_cry' } },
  soul_coin: { name: 'Soul Coin', rarity: 'uncommon', type: 'currency', charges: 1, effect: 'A coin containing a trapped, screaming soul. Powers infernal machines for 24h. Holding it requires WIS save DC 10 or feel compelled to use it.', mechanicEffect: { fuel: 24, wisdomSave: 10 } },
  hearthstone: { name: 'Hearthstone', rarity: 'very_rare', type: 'wondrous', charges: -1, effect: 'A night hag\'s source of power. Pulsating green light. Allows plane shift to the Ethereal Plane once per day.', mechanicEffect: { planeShift: true, uses: 1, rechargeable: true } },
};

const BAG_OF_TRICKS_TABLE = [
  { roll: 1, beast: 'Weasel', hp: 1, ac: 13, attack: '+3', damage: '1' },
  { roll: 2, beast: 'Giant Rat', hp: 7, ac: 12, attack: '+4', damage: '1d4+2' },
  { roll: 3, beast: 'Badger', hp: 3, ac: 10, attack: '+2', damage: '1' },
  { roll: 4, beast: 'Boar', hp: 11, ac: 11, attack: '+3', damage: '1d6+1' },
  { roll: 5, beast: 'Panther', hp: 13, ac: 12, attack: '+4', damage: '1d6+2' },
  { roll: 6, beast: 'Giant Elk', hp: 42, ac: 14, attack: '+6', damage: '2d6+4' },
  { roll: 7, beast: 'Brown Bear', hp: 34, ac: 11, attack: '+5', damage: '2d6+4' },
  { roll: 8, beast: 'Dire Wolf', hp: 37, ac: 14, attack: '+5', damage: '2d6+3' },
];

// ============================================
// 3. BOSS ENCOUNTER MECHANICS
// ============================================
const BOSS_TEMPLATES = {
  djinn: {
    name: 'Djinn', cr: 11, hp: 161, ac: 17, speed: '30ft, fly 90ft',
    abilities: { STR: 21, DEX: 15, CON: 22, INT: 15, WIS: 16, CHA: 20 },
    attacks: [{ name: 'Scimitar', bonus: 9, damage: '2d6+5', type: 'slashing', multiattack: 3 }],
    spells: ['thunderwave', 'create_food_and_water', 'wind_wall', 'gaseous_form', 'invisibility', 'plane_shift'],
    legendaryActions: 2,
    legendaryOptions: ['Thunderclap (costs 1): All within 5ft take 2d6 thunder', 'Whirlwind (costs 2): 60ft cone, STR save DC 18 or knocked prone'],
    immunities: ['lightning', 'thunder'],
    description: 'A powerful genie freed from an oil lamp. Wrathful and proud.',
  },
  vecna: {
    name: 'Vecna', cr: 26, hp: 272, ac: 18, speed: '30ft, fly 40ft',
    abilities: { STR: 14, DEX: 16, CON: 22, INT: 30, WIS: 24, CHA: 22 },
    attacks: [{ name: 'Dagger of Vecna', bonus: 12, damage: '2d4+5', type: 'necrotic', multiattack: 2 }],
    spells: ['finger_of_death', 'dominate_monster', 'power_word_kill', 'teleport', 'animate_dead'],
    legendaryActions: 3,
    legendaryOptions: ['Fell Rebuke (costs 1): 3d6 necrotic to attacker', 'Rotten Fate (costs 1): Target makes WIS save DC 22 or frightened', 'Touch of Death (costs 2): Melee, 6d6 necrotic', 'Life Drain (costs 3): All within 60ft, CON save DC 22, 42 necrotic on fail'],
    immunities: ['necrotic', 'poison', 'nonmagical weapons'],
    resistances: ['cold', 'lightning'],
    description: 'The Whispered One. Archlich. God of secrets and undeath.',
  },
  night_hag: {
    name: 'Night Hag', cr: 5, hp: 112, ac: 17, speed: '30ft',
    abilities: { STR: 18, DEX: 15, CON: 16, INT: 16, WIS: 14, CHA: 16 },
    attacks: [{ name: 'Claws', bonus: 7, damage: '2d8+4', type: 'slashing', multiattack: 2 }],
    spells: ['detect_magic', 'magic_missile', 'ray_of_enfeeblement', 'sleep', 'plane_shift'],
    legendaryActions: 0,
    specialAbilities: ['Change Shape', 'Etherealness', 'Nightmare Haunting'],
    description: 'A fiend that feeds on fear and despair. Collects souls.',
  },
  wear_boar_king: {
    name: 'Raggadragga, King of Avernus', cr: 8, hp: 170, ac: 16, speed: '40ft',
    abilities: { STR: 22, DEX: 12, CON: 20, INT: 10, WIS: 12, CHA: 18 },
    attacks: [{ name: 'Tusks', bonus: 9, damage: '2d10+6', type: 'piercing', multiattack: 2 }, { name: 'Charge', bonus: 9, damage: '3d10+6', type: 'bludgeoning' }],
    legendaryActions: 1,
    legendaryOptions: ['Boar Charge (costs 1): Move 20ft and attack, target knocked prone on fail STR DC 17'],
    specialAbilities: ['Shapechanger (full boar form)', 'Lycanthropy Bite (target must save or become wereboar)'],
    description: 'Self-proclaimed king of Avernus. Wereboar warlord. Hopeless romantic.',
  },
};

class BossEncounter {
  constructor(bossKey) {
    const template = BOSS_TEMPLATES[bossKey];
    if (!template) return;
    this.boss = { ...template, currentHp: template.hp, legendaryActionsUsed: 0, conditions: [], phaseIndex: 0 };
    this.round = 0;
    this.log = [];
    this.phases = this._generatePhases(template);
  }

  _generatePhases(template) {
    const hp = template.hp;
    return [
      { threshold: hp, name: 'Full Strength', dialogue: `"You dare face ${template.name}?"`, behavior: 'confident' },
      { threshold: Math.floor(hp * 0.75), name: 'Wounded', dialogue: '"You are stronger than expected..."', behavior: 'cautious' },
      { threshold: Math.floor(hp * 0.5), name: 'Bloodied', dialogue: '"ENOUGH! I will show you TRUE power!"', behavior: 'aggressive' },
      { threshold: Math.floor(hp * 0.25), name: 'Desperate', dialogue: '"No... this cannot be... I am ETERNAL!"', behavior: 'desperate' },
      { threshold: 0, name: 'Defeated', dialogue: '"Impossible..."', behavior: 'defeated' },
    ];
  }

  takeDamage(amount) {
    this.boss.currentHp = Math.max(0, this.boss.currentHp - amount);
    const newPhase = this.phases.findIndex(p => this.boss.currentHp > p.threshold);
    const actualPhase = Math.max(0, newPhase - 1);
    if (actualPhase > this.boss.phaseIndex) {
      this.boss.phaseIndex = actualPhase;
      const phase = this.phases[actualPhase];
      this.log.push(`PHASE CHANGE: ${phase.name} — ${phase.dialogue}`);
      return { phaseChange: true, phase: phase.name, dialogue: phase.dialogue, behavior: phase.behavior, hp: this.boss.currentHp, maxHp: this.boss.hp };
    }
    return { phaseChange: false, hp: this.boss.currentHp, maxHp: this.boss.hp };
  }

  useLegendaryAction(actionIndex) {
    if (this.boss.legendaryActionsUsed >= this.boss.legendaryActions) return { error: 'No legendary actions remaining this round' };
    const action = this.boss.legendaryOptions?.[actionIndex];
    if (!action) return { error: 'Invalid action' };
    this.boss.legendaryActionsUsed++;
    this.log.push(`LEGENDARY ACTION: ${action}`);
    return { action, remaining: this.boss.legendaryActions - this.boss.legendaryActionsUsed };
  }

  newRound() {
    this.round++;
    this.boss.legendaryActionsUsed = 0;
    return { round: this.round, bossHp: this.boss.currentHp, phase: this.phases[this.boss.phaseIndex]?.name };
  }

  getState() {
    return {
      name: this.boss.name,
      hp: this.boss.currentHp, maxHp: this.boss.hp, ac: this.boss.ac,
      phase: this.phases[this.boss.phaseIndex],
      round: this.round,
      legendaryActionsRemaining: this.boss.legendaryActions - this.boss.legendaryActionsUsed,
      log: this.log.slice(-10),
      isDefeated: this.boss.currentHp <= 0,
    };
  }
}

// ============================================
// 4. SUMMON / COMPANION SYSTEM
// ============================================
const SUMMONS = {
  griffin: { name: 'Griffin', hp: 59, ac: 12, speed: '30ft, fly 80ft', attacks: [{ name: 'Beak', bonus: 6, damage: '1d8+4' }, { name: 'Claws', bonus: 6, damage: '2d6+4' }], type: 'celestial' },
  pegasus: { name: 'Pegasus', hp: 59, ac: 12, speed: '60ft, fly 90ft', attacks: [{ name: 'Hooves', bonus: 6, damage: '2d6+4' }], type: 'celestial' },
  dire_wolf: { name: 'Dire Wolf', hp: 37, ac: 14, speed: '50ft', attacks: [{ name: 'Bite', bonus: 5, damage: '2d6+3' }], type: 'beast', special: 'Pack Tactics, Knockdown' },
  saber_tooth: { name: 'Saber-Toothed Tiger', hp: 52, ac: 12, speed: '40ft', attacks: [{ name: 'Bite', bonus: 6, damage: '1d10+5' }, { name: 'Claws', bonus: 6, damage: '2d6+5' }], type: 'beast', special: 'Pounce' },
  rhino: { name: 'Rhinoceros', hp: 45, ac: 11, speed: '40ft', attacks: [{ name: 'Gore', bonus: 7, damage: '2d8+5' }], type: 'beast', special: 'Charge (extra 2d8 on 20ft+ move)' },
  war_horse: { name: 'War Horse', hp: 19, ac: 11, speed: '60ft', attacks: [{ name: 'Hooves', bonus: 4, damage: '2d6+4' }], type: 'beast', special: 'Trampling Charge' },
};

class CompanionManager {
  constructor() { this.active = []; }

  summon(creatureKey, summonerName, customName = null) {
    const template = SUMMONS[creatureKey] || BAG_OF_TRICKS_TABLE.find(b => b.beast.toLowerCase().replace(/\s/g, '_') === creatureKey);
    if (!template) return null;
    const companion = {
      id: `companion-${Date.now()}`, ...template, customName: customName || template.name || template.beast,
      currentHp: template.hp, summoner: summonerName, summonedAt: Date.now(), active: true,
    };
    this.active.push(companion);
    return companion;
  }

  bagOfTricks() {
    const roll = randomInt(1, 8);
    const beast = BAG_OF_TRICKS_TABLE.find(b => b.roll === roll);
    return { roll, beast: beast.beast, hp: beast.hp, ac: beast.ac, companion: this.summon(beast.beast.toLowerCase().replace(/\s/g, '_'), 'player', beast.beast) || beast };
  }

  dismiss(companionId) {
    this.active = this.active.filter(c => c.id !== companionId);
  }

  getActive() { return this.active.filter(c => c.active); }
}

// ============================================
// 5. RIVAL PARTY SYSTEM (like reverse R&R)
// ============================================
const RIVAL_PARTIES = [
  {
    name: 'The Obsidian Hand', symbol: 'reversed_RnR', description: 'A dark mirror of the heroes. They arrived first, took the treasures, left taunting notes.',
    members: [
      { name: 'Tall H', role: 'leader', class: 'rogue', personality: 'arrogant, leaves calling cards' },
      { name: 'Grimjaw', role: 'muscle', class: 'barbarian', personality: 'brutal, smashes everything' },
      { name: 'Whisper', role: 'infiltrator', class: 'wizard', personality: 'silent, leaves traps behind' },
    ],
    taunt: 'Good luck catching up, Tall H.',
    recurringVillain: true,
  },
  {
    name: 'Kovac\'s Devils', symbol: 'chain_8', description: 'Mercenary company that operates in the Nine Hells. Barbed devils in uniform.',
    members: [
      { name: 'Kovac', role: 'commander', class: 'fighter', personality: 'military discipline, cruel efficiency' },
      { name: 'The Accountant', role: 'quartermaster', class: 'wizard', personality: 'counts everything, values souls as currency' },
    ],
    taunt: 'Property of Kovac. Trespassers will be collected.',
    recurringVillain: true,
  },
];

// ============================================
// 6. EXPLORATION TOOLS
// ============================================
const EXPLORATION_ACTIONS = {
  detect_traps: { name: 'Find Traps', skill: 'perception', dc: 14, description: 'Scan the area for hidden traps and mechanisms.' },
  detect_magic: { name: 'Detect Magic', skill: 'arcana', dc: 12, description: 'Sense magical auras in the vicinity.' },
  detect_undead: { name: 'Sense Undead', skill: 'religion', dc: 10, description: 'Feel the presence of undead creatures nearby. (Cleric/Paladin)' },
  detect_spirits: { name: 'Detect Spirits', skill: 'religion', dc: 14, description: 'Commune with lingering spirits in this place.' },
  search_secret: { name: 'Search for Secrets', skill: 'investigation', dc: 15, description: 'Thoroughly search for hidden doors, compartments, or messages.' },
  nature_check: { name: 'Nature Knowledge', skill: 'nature', dc: 12, description: 'Identify flora, fauna, or natural phenomena.' },
  track: { name: 'Track Creatures', skill: 'survival', dc: 13, description: 'Follow footprints, traces, or other signs of passage.' },
  mend_object: { name: 'Mend', skill: 'arcana', dc: 0, description: 'Magically repair a broken object. (Cantrip)' },
  identify_item: { name: 'Identify Item', skill: 'arcana', dc: 14, description: 'Determine the magical properties of an item.' },
};

module.exports = {
  PUZZLE_TYPES, PUZZLES, PuzzleManager,
  ARTIFACTS, BAG_OF_TRICKS_TABLE,
  BOSS_TEMPLATES, BossEncounter,
  SUMMONS, CompanionManager,
  RIVAL_PARTIES,
  EXPLORATION_ACTIONS,
};
