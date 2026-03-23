// ============================================
// D&D 5e Game Engine - Core Mechanics
// ============================================

// --- Dice System ---
function rollDie(sides) {
  return Math.floor(Math.random() * sides) + 1;
}

function rollDice(count, sides) {
  const rolls = [];
  for (let i = 0; i < count; i++) rolls.push(rollDie(sides));
  return rolls;
}

function rollD20() { return rollDie(20); }

// Roll with advantage (2d20, take highest)
function rollWithAdvantage() {
  const rolls = [rollD20(), rollD20()];
  return { rolls, result: Math.max(...rolls), type: 'advantage' };
}

// Roll with disadvantage (2d20, take lowest)
function rollWithDisadvantage() {
  const rolls = [rollD20(), rollD20()];
  return { rolls, result: Math.min(...rolls), type: 'disadvantage' };
}

// Parse dice notation: "2d6+3", "1d20", "4d6"
function parseDiceNotation(notation) {
  const match = notation.match(/(\d+)d(\d+)([+-]\d+)?/i);
  if (!match) return null;
  return { count: parseInt(match[1]), sides: parseInt(match[2]), modifier: parseInt(match[3] || 0) };
}

function rollNotation(notation) {
  const parsed = parseDiceNotation(notation);
  if (!parsed) return { total: 0, rolls: [], modifier: 0, notation };
  const rolls = rollDice(parsed.count, parsed.sides);
  const total = rolls.reduce((a, b) => a + b, 0) + parsed.modifier;
  return { total, rolls, modifier: parsed.modifier, notation };
}

// --- Ability Score Modifiers ---
function abilityModifier(score) {
  return Math.floor((score - 10) / 2);
}

// --- Proficiency Bonus (by level) ---
function proficiencyBonus(level) {
  if (level <= 4) return 2;
  if (level <= 8) return 3;
  if (level <= 12) return 4;
  if (level <= 16) return 5;
  return 6;
}

// --- Skill to Ability mapping ---
const SKILL_ABILITIES = {
  athletics: 'STR',
  acrobatics: 'DEX', sleight_of_hand: 'DEX', stealth: 'DEX',
  arcana: 'INT', history: 'INT', investigation: 'INT', nature: 'INT', religion: 'INT',
  animal_handling: 'WIS', insight: 'WIS', medicine: 'WIS', perception: 'WIS', survival: 'WIS',
  deception: 'CHA', intimidation: 'CHA', performance: 'CHA', persuasion: 'CHA',
};

// --- Skill Check ---
function skillCheck(abilityScores, level, skillName, proficientSkills = [], advantageType = 'normal') {
  const ability = SKILL_ABILITIES[skillName] || 'STR';
  const mod = abilityModifier(abilityScores[ability] || 10);
  const profBonus = proficientSkills.includes(skillName) ? proficiencyBonus(level) : 0;

  let roll;
  if (advantageType === 'advantage') roll = rollWithAdvantage();
  else if (advantageType === 'disadvantage') roll = rollWithDisadvantage();
  else roll = { rolls: [rollD20()], result: rollD20(), type: 'normal' };
  // Fix: use the actual roll result
  const d20 = roll.result;

  const isCritSuccess = d20 === 20;
  const isCritFail = d20 === 1;
  const total = d20 + mod + profBonus;

  return {
    d20, total, modifier: mod, proficiency: profBonus,
    skill: skillName, ability, rolls: roll.rolls,
    isCritSuccess, isCritFail, advantageType,
    breakdown: `${d20} (d20) + ${mod} (${ability}) ${profBonus ? `+ ${profBonus} (prof)` : ''} = ${total}`
  };
}

// --- Saving Throw ---
function savingThrow(abilityScores, level, ability, proficientSaves = [], dc = 10) {
  const mod = abilityModifier(abilityScores[ability] || 10);
  const profBonus = proficientSaves.includes(ability) ? proficiencyBonus(level) : 0;
  const d20 = rollD20();
  const total = d20 + mod + profBonus;
  const success = d20 === 20 || (d20 !== 1 && total >= dc);

  return {
    d20, total, dc, success, modifier: mod, proficiency: profBonus, ability,
    isCritSuccess: d20 === 20, isCritFail: d20 === 1,
    breakdown: `${d20} (d20) + ${mod} (${ability}) ${profBonus ? `+ ${profBonus} (prof)` : ''} = ${total} vs DC ${dc}`
  };
}

// --- Attack Roll ---
function attackRoll(abilityScores, level, weaponAbility = 'STR', proficient = true, targetAC = 10, advantageType = 'normal') {
  const mod = abilityModifier(abilityScores[weaponAbility] || 10);
  const profBonus = proficient ? proficiencyBonus(level) : 0;

  let roll;
  if (advantageType === 'advantage') roll = rollWithAdvantage();
  else if (advantageType === 'disadvantage') roll = rollWithDisadvantage();
  else { const r = rollD20(); roll = { rolls: [r], result: r, type: 'normal' }; }

  const d20 = roll.result;
  const isCritHit = d20 === 20;
  const isCritMiss = d20 === 1;
  const total = d20 + mod + profBonus;
  const hits = isCritHit || (!isCritMiss && total >= targetAC);

  return {
    d20, total, targetAC, hits, modifier: mod, proficiency: profBonus,
    isCritHit, isCritMiss, advantageType, rolls: roll.rolls,
    breakdown: `${d20} (d20) + ${mod} (${weaponAbility}) + ${profBonus} (prof) = ${total} vs AC ${targetAC}`
  };
}

// --- Damage Roll ---
function damageRoll(damageDice, abilityMod, isCritical = false) {
  const parsed = parseDiceNotation(damageDice);
  if (!parsed) return { total: abilityMod, rolls: [], modifier: abilityMod, isCritical };

  const diceCount = isCritical ? parsed.count * 2 : parsed.count;
  const rolls = rollDice(diceCount, parsed.sides);
  const total = rolls.reduce((a, b) => a + b, 0) + abilityMod; // modifier added only once even on crit

  return {
    total, rolls, modifier: abilityMod, isCritical, diceCount, sides: parsed.sides,
    breakdown: `${rolls.join('+')} (${diceCount}d${parsed.sides}) + ${abilityMod} (mod) = ${total}`
  };
}

// --- Initiative Roll ---
function initiativeRoll(abilityScores) {
  const dexMod = abilityModifier(abilityScores.DEX || 10);
  const d20 = rollD20();
  return { d20, total: d20 + dexMod, modifier: dexMod };
}

// --- AC Calculation ---
function calculateAC(armorType, armorBase, dexMod, hasShield = false) {
  let ac = armorBase;
  if (armorType === 'light') ac += dexMod;
  else if (armorType === 'medium') ac += Math.min(dexMod, 2);
  // heavy: no DEX bonus
  if (hasShield) ac += 2;
  return ac;
}

// --- Death Saving Throws ---
function deathSavingThrow() {
  const d20 = rollD20();
  return {
    d20,
    isNat20: d20 === 20, // regain 1 HP
    isNat1: d20 === 1, // 2 failures
    success: d20 >= 10,
  };
}

// --- Weapons Database ---
const WEAPONS = {
  longsword: { name: 'Longsword', damage: '1d8', type: 'slashing', ability: 'STR', properties: ['versatile'] },
  shortsword: { name: 'Shortsword', damage: '1d6', type: 'piercing', ability: 'DEX', properties: ['finesse', 'light'] },
  greataxe: { name: 'Greataxe', damage: '1d12', type: 'slashing', ability: 'STR', properties: ['heavy', 'two-handed'] },
  dagger: { name: 'Dagger', damage: '1d4', type: 'piercing', ability: 'DEX', properties: ['finesse', 'light', 'thrown'] },
  shortbow: { name: 'Shortbow', damage: '1d6', type: 'piercing', ability: 'DEX', properties: ['ranged', 'two-handed'] },
  longbow: { name: 'Longbow', damage: '1d8', type: 'piercing', ability: 'DEX', properties: ['ranged', 'heavy', 'two-handed'] },
  mace: { name: 'Mace', damage: '1d6', type: 'bludgeoning', ability: 'STR', properties: [] },
  quarterstaff: { name: 'Quarterstaff', damage: '1d6', type: 'bludgeoning', ability: 'STR', properties: ['versatile'] },
  handaxe: { name: 'Handaxe', damage: '1d6', type: 'slashing', ability: 'STR', properties: ['light', 'thrown'] },
  rapier: { name: 'Rapier', damage: '1d8', type: 'piercing', ability: 'DEX', properties: ['finesse'] },
  unarmed: { name: 'Unarmed Strike', damage: '1d1', type: 'bludgeoning', ability: 'STR', properties: [] },
};

// --- Spells Database (Level 0-2) ---
const SPELLS = {
  // Cantrips (Level 0)
  fire_bolt: { name: 'Fire Bolt', level: 0, damage: '1d10', type: 'fire', range: 120, ability: 'INT', attackRoll: true, description: 'A mote of fire streaks toward a creature. Make a ranged spell attack.' },
  sacred_flame: { name: 'Sacred Flame', level: 0, damage: '1d8', type: 'radiant', range: 60, ability: 'WIS', saveDC: true, saveAbility: 'DEX', description: 'Flame descends on a creature. Target must succeed on a DEX saving throw.' },
  eldritch_blast: { name: 'Eldritch Blast', level: 0, damage: '1d10', type: 'force', range: 120, ability: 'CHA', attackRoll: true, description: 'A beam of crackling energy streaks toward a creature.' },
  mending: { name: 'Mending', level: 0, range: 0, ability: 'INT', description: 'Repair a single break or tear in an object.' },
  light: { name: 'Light', level: 0, range: 0, ability: 'INT', description: 'An object you touch sheds bright light in a 20-foot radius.' },
  // Level 1
  magic_missile: { name: 'Magic Missile', level: 1, damage: '1d4+1', type: 'force', range: 120, ability: 'INT', autoHit: true, missiles: 3, description: 'Three darts of magical force hit automatically. Each deals 1d4+1.' },
  cure_wounds: { name: 'Cure Wounds', level: 1, healing: '1d8', range: 0, ability: 'WIS', description: 'Touch a creature to restore 1d8 + spellcasting modifier HP.' },
  shield: { name: 'Shield', level: 1, range: 0, reaction: true, description: '+5 AC until the start of your next turn. Cast as a reaction.' },
  thunderwave: { name: 'Thunderwave', level: 1, damage: '2d8', type: 'thunder', range: 15, ability: 'INT', saveDC: true, saveAbility: 'CON', description: 'Wave of thunderous force. Creatures must make CON save or take 2d8 thunder and be pushed 10 feet.' },
  healing_word: { name: 'Healing Word', level: 1, healing: '1d4', range: 60, ability: 'WIS', bonusAction: true, description: 'Bonus action. Heal a creature you can see within 60 feet for 1d4 + modifier.' },
  // Level 2
  scorching_ray: { name: 'Scorching Ray', level: 2, damage: '2d6', type: 'fire', range: 120, ability: 'INT', attackRoll: true, rays: 3, description: 'Create three rays of fire. Make a ranged spell attack for each.' },
  hold_person: { name: 'Hold Person', level: 2, range: 60, ability: 'WIS', saveDC: true, saveAbility: 'WIS', concentration: true, description: 'Target humanoid must succeed on WIS save or be paralyzed.' },
  misty_step: { name: 'Misty Step', level: 2, range: 30, bonusAction: true, description: 'Bonus action. Teleport up to 30 feet to an unoccupied space you can see.' },
};

// --- Spell Slots by class and level ---
const SPELL_SLOTS = {
  1: { 1: 2, 2: 0, 3: 0 },
  2: { 1: 3, 2: 0, 3: 0 },
  3: { 1: 4, 2: 2, 3: 0 },
  4: { 1: 4, 2: 3, 3: 0 },
  5: { 1: 4, 2: 3, 3: 2 },
};

// --- Class features ---
const CLASS_FEATURES = {
  fighter: { hitDie: 10, primaryAbility: 'STR', saves: ['STR', 'CON'], proficientWeapons: ['all'], skills: ['athletics', 'intimidation'] },
  wizard: { hitDie: 6, primaryAbility: 'INT', saves: ['INT', 'WIS'], proficientWeapons: ['dagger', 'quarterstaff'], skills: ['arcana', 'history'] },
  rogue: { hitDie: 8, primaryAbility: 'DEX', saves: ['DEX', 'INT'], proficientWeapons: ['shortsword', 'rapier', 'dagger', 'shortbow'], skills: ['stealth', 'sleight_of_hand', 'acrobatics', 'deception'] },
  cleric: { hitDie: 8, primaryAbility: 'WIS', saves: ['WIS', 'CHA'], proficientWeapons: ['mace', 'quarterstaff'], skills: ['medicine', 'religion', 'insight'] },
  ranger: { hitDie: 10, primaryAbility: 'DEX', saves: ['STR', 'DEX'], proficientWeapons: ['all'], skills: ['survival', 'nature', 'stealth', 'perception'] },
  barbarian: { hitDie: 12, primaryAbility: 'STR', saves: ['STR', 'CON'], proficientWeapons: ['all'], skills: ['athletics', 'intimidation', 'survival'] },
};

// --- Combat Manager ---
class CombatManager {
  constructor() {
    this.inCombat = false;
    this.combatants = [];
    this.currentTurn = 0;
    this.round = 1;
    this.log = [];
  }

  startCombat(playerChar, enemies) {
    this.inCombat = true;
    this.round = 1;
    this.currentTurn = 0;
    this.log = [];
    this.combatants = [];

    // Roll initiative for player
    const playerInit = initiativeRoll(playerChar.ability_scores);
    this.combatants.push({
      id: 'player', name: playerChar.name, type: 'player',
      initiative: playerInit.total, initiativeRoll: playerInit,
      hp: playerChar.hp, maxHp: playerChar.max_hp, ac: playerChar.ac,
      abilityScores: playerChar.ability_scores, level: playerChar.level,
      classId: playerChar.class?.toLowerCase() || 'fighter',
      weapon: playerChar.weapon || 'longsword',
      deathSaves: { successes: 0, failures: 0 },
      conditions: [],
    });

    // Roll initiative for enemies
    enemies.forEach(e => {
      const init = initiativeRoll(e.ability_scores || { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHA: 10 });
      this.combatants.push({
        id: e.id, name: e.name, type: 'npc',
        initiative: init.total, initiativeRoll: init,
        hp: e.max_hp || 10, maxHp: e.max_hp || 10, ac: e.ac || 10,
        abilityScores: e.ability_scores || { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHA: 10 },
        level: e.level || 1, classId: e.class_id || 'commoner',
        weapon: (e.equipment_ids && e.equipment_ids[0]) || 'unarmed',
        deathSaves: { successes: 0, failures: 0 },
        conditions: [],
      });
    });

    // Sort by initiative (highest first)
    this.combatants.sort((a, b) => b.initiative - a.initiative);

    this.log.push(`=== COMBAT BEGINS (Round ${this.round}) ===`);
    this.log.push(`Initiative order: ${this.combatants.map(c => `${c.name} (${c.initiative})`).join(', ')}`);

    return {
      combatants: this.combatants.map(c => ({ id: c.id, name: c.name, initiative: c.initiative, hp: c.hp, maxHp: c.maxHp, ac: c.ac })),
      initiativeOrder: this.combatants.map(c => c.name),
      log: [...this.log],
    };
  }

  getCurrentCombatant() {
    return this.combatants[this.currentTurn % this.combatants.length];
  }

  nextTurn() {
    this.currentTurn++;
    if (this.currentTurn % this.combatants.length === 0) {
      this.round++;
      this.log.push(`\n=== ROUND ${this.round} ===`);
    }
    // Skip dead combatants
    let safety = 0;
    while (this.getCurrentCombatant().hp <= 0 && safety < this.combatants.length) {
      this.currentTurn++;
      safety++;
    }
    return this.getCurrentCombatant();
  }

  playerAttack(targetId, weaponName = null) {
    const player = this.combatants.find(c => c.id === 'player');
    const target = this.combatants.find(c => c.id === targetId);
    if (!player || !target) return { error: 'Invalid target' };
    if (target.hp <= 0) return { error: `${target.name} is already down!` };

    const weapon = WEAPONS[weaponName || player.weapon] || WEAPONS.unarmed;
    const attack = attackRoll(player.abilityScores, player.level, weapon.ability, true, target.ac);

    const result = {
      attacker: player.name, target: target.name, weapon: weapon.name,
      attackRoll: attack, hit: attack.hits, damage: null, targetHp: target.hp,
      narration: '',
    };

    if (attack.hits) {
      const dmg = damageRoll(weapon.damage, abilityModifier(player.abilityScores[weapon.ability] || 10), attack.isCritHit);
      target.hp = Math.max(0, target.hp - dmg.total);
      result.damage = dmg;
      result.targetHp = target.hp;

      if (attack.isCritHit) {
        result.narration = `CRITICAL HIT! ${player.name} strikes ${target.name} with ${weapon.name} for ${dmg.total} ${weapon.type} damage! [${dmg.breakdown}] ${target.name} has ${target.hp}/${target.maxHp} HP.`;
      } else {
        result.narration = `${player.name} hits ${target.name} with ${weapon.name}! [${attack.breakdown}] Dealing ${dmg.total} ${weapon.type} damage. [${dmg.breakdown}] ${target.name}: ${target.hp}/${target.maxHp} HP.`;
      }

      if (target.hp <= 0) {
        result.narration += ` ${target.name} falls!`;
        result.killed = true;
      }
    } else {
      if (attack.isCritMiss) {
        result.narration = `CRITICAL MISS! ${player.name} swings wildly with ${weapon.name} and stumbles! [${attack.breakdown}]`;
      } else {
        result.narration = `${player.name} attacks ${target.name} with ${weapon.name} but misses! [${attack.breakdown}]`;
      }
    }

    this.log.push(result.narration);
    return result;
  }

  npcAttack(npcId) {
    const npc = this.combatants.find(c => c.id === npcId);
    const player = this.combatants.find(c => c.id === 'player');
    if (!npc || !player || npc.hp <= 0 || player.hp <= 0) return null;

    const weapon = WEAPONS[npc.weapon] || WEAPONS.unarmed;
    const attack = attackRoll(npc.abilityScores, npc.level, weapon.ability, true, player.ac);

    const result = { attacker: npc.name, target: player.name, weapon: weapon.name, attackRoll: attack, hit: attack.hits, damage: null, narration: '' };

    if (attack.hits) {
      const dmg = damageRoll(weapon.damage, abilityModifier(npc.abilityScores[weapon.ability] || 10), attack.isCritHit);
      player.hp = Math.max(0, player.hp - dmg.total);
      result.damage = dmg;
      result.targetHp = player.hp;
      result.narration = `${npc.name} ${attack.isCritHit ? 'CRITICALLY HITS' : 'hits'} ${player.name} with ${weapon.name} for ${dmg.total} damage! [${dmg.breakdown}] Player HP: ${player.hp}/${player.maxHp}`;
      if (player.hp <= 0) {
        result.narration += ` ${player.name} falls unconscious!`;
        result.playerDown = true;
      }
    } else {
      result.narration = `${npc.name} attacks with ${weapon.name} but misses! [${attack.breakdown}]`;
    }

    this.log.push(result.narration);
    return result;
  }

  castSpell(spellName, targetId, casterType = 'player') {
    const spell = SPELLS[spellName];
    if (!spell) return { error: `Unknown spell: ${spellName}` };

    const caster = this.combatants.find(c => c.id === (casterType === 'player' ? 'player' : targetId));
    const target = targetId ? this.combatants.find(c => c.id === targetId) : caster;

    if (!caster) return { error: 'Caster not found' };

    const spellMod = abilityModifier(caster.abilityScores[spell.ability] || 10);
    const spellDC = 8 + proficiencyBonus(caster.level) + spellMod;
    const result = { spell: spell.name, caster: caster.name, target: target?.name, narration: '', rolls: [] };

    if (spell.healing) {
      const heal = rollNotation(spell.healing);
      const healTotal = heal.total + spellMod;
      if (target) {
        target.hp = Math.min(target.maxHp, target.hp + healTotal);
        result.narration = `${caster.name} casts ${spell.name} on ${target.name}, healing for ${healTotal} HP! [${heal.rolls.join('+')} + ${spellMod}] ${target.name}: ${target.hp}/${target.maxHp} HP`;
      }
      result.healing = healTotal;
      result.rolls.push(heal);
    } else if (spell.damage && target) {
      if (spell.autoHit) {
        // Magic Missile
        const missiles = spell.missiles || 1;
        let totalDmg = 0;
        for (let i = 0; i < missiles; i++) {
          const dmg = rollNotation(spell.damage);
          totalDmg += dmg.total;
          result.rolls.push(dmg);
        }
        target.hp = Math.max(0, target.hp - totalDmg);
        result.narration = `${caster.name} casts ${spell.name}! ${missiles} darts strike ${target.name} for ${totalDmg} ${spell.type} damage! ${target.name}: ${target.hp}/${target.maxHp} HP`;
        result.totalDamage = totalDmg;
      } else if (spell.attackRoll) {
        const attack = attackRoll(caster.abilityScores, caster.level, spell.ability, true, target.ac);
        result.rolls.push(attack);
        if (attack.hits) {
          const dmg = damageRoll(spell.damage, 0, attack.isCritHit);
          target.hp = Math.max(0, target.hp - dmg.total);
          result.narration = `${caster.name} casts ${spell.name}! ${attack.isCritHit ? 'CRITICAL! ' : ''}Hits ${target.name} for ${dmg.total} ${spell.type} damage! [${attack.breakdown}] ${target.name}: ${target.hp}/${target.maxHp} HP`;
          result.totalDamage = dmg.total;
          result.rolls.push(dmg);
        } else {
          result.narration = `${caster.name} casts ${spell.name} at ${target.name} but misses! [${attack.breakdown}]`;
        }
      } else if (spell.saveDC) {
        const save = savingThrow(target.abilityScores || { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHA: 10 }, target.level, spell.saveAbility, [], spellDC);
        result.rolls.push(save);
        if (!save.success) {
          const dmg = rollNotation(spell.damage);
          target.hp = Math.max(0, target.hp - dmg.total);
          result.narration = `${caster.name} casts ${spell.name}! ${target.name} fails the ${spell.saveAbility} save (${save.breakdown})! Takes ${dmg.total} ${spell.type} damage! ${target.name}: ${target.hp}/${target.maxHp} HP`;
          result.totalDamage = dmg.total;
          result.rolls.push(dmg);
        } else {
          result.narration = `${caster.name} casts ${spell.name}! ${target.name} succeeds on the ${spell.saveAbility} save (${save.breakdown}) and avoids the effect!`;
        }
      }
    } else {
      result.narration = `${caster.name} casts ${spell.name}! ${spell.description}`;
    }

    if (target && target.hp <= 0) {
      result.narration += ` ${target.name} is down!`;
      result.killed = true;
    }

    this.log.push(result.narration);
    return result;
  }

  getState() {
    return {
      inCombat: this.inCombat,
      round: this.round,
      currentTurn: this.currentTurn,
      currentCombatant: this.getCurrentCombatant(),
      combatants: this.combatants.map(c => ({
        id: c.id, name: c.name, type: c.type,
        hp: c.hp, maxHp: c.maxHp, ac: c.ac,
        initiative: c.initiative, conditions: c.conditions,
        isDown: c.hp <= 0,
      })),
      log: this.log.slice(-10),
    };
  }

  endCombat() {
    const survivors = this.combatants.filter(c => c.hp > 0);
    const fallen = this.combatants.filter(c => c.hp <= 0);
    this.inCombat = false;

    // Calculate XP
    const enemiesDefeated = fallen.filter(c => c.type === 'npc');
    const xpGained = enemiesDefeated.reduce((sum, e) => sum + (e.level || 1) * 50, 0);

    return {
      survivors: survivors.map(s => ({ id: s.id, name: s.name, hp: s.hp, maxHp: s.maxHp })),
      fallen: fallen.map(f => ({ id: f.id, name: f.name })),
      rounds: this.round,
      xpGained,
      log: this.log,
    };
  }
}

module.exports = {
  rollDie, rollDice, rollD20, rollWithAdvantage, rollWithDisadvantage,
  parseDiceNotation, rollNotation, abilityModifier, proficiencyBonus,
  SKILL_ABILITIES, skillCheck, savingThrow, attackRoll, damageRoll,
  initiativeRoll, calculateAC, deathSavingThrow,
  WEAPONS, SPELLS, SPELL_SLOTS, CLASS_FEATURES,
  CombatManager,
};
