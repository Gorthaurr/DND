const express = require('express');
const cors = require('cors');
const { WebSocketServer } = require('ws');
const fs = require('fs');
const path = require('path');
const http = require('http');

const dnd = require('./dnd-engine');
const { NPCLifeService } = require('./npc-service');
const { StoryTree } = require('./story-tree');
const biogen = require('./biography-generator');
const { ShadowManager } = require('./shadow-system');
const worldSys = require('./world-systems');
const advSys = require('./advanced-systems');

const app = express();
app.use(cors());
app.use(express.json());

// NPC Life Service — центральный модуль живых NPC
const npcLife = new NPCLifeService();
// Shadow System — враги помнят, возвращаются, эволюционируют
const shadow = new ShadowManager();
// World Systems
const vehicles = new worldSys.VehicleManager();
const deals = new worldSys.DealManager();
const party = new worldSys.PartyManager();
// Advanced Systems
const puzzles = new advSys.PuzzleManager();
const companions = new advSys.CompanionManager();
let activeBoss = null;

// Load world data
const worldsDir = path.join(__dirname, '..', 'worlds', 'medieval_village');
const world = JSON.parse(fs.readFileSync(path.join(worldsDir, 'world.json'), 'utf-8'));
const npcsData = JSON.parse(fs.readFileSync(path.join(worldsDir, 'npcs.json'), 'utf-8'));
const events = JSON.parse(fs.readFileSync(path.join(worldsDir, 'events.json'), 'utf-8'));
const scenarios = JSON.parse(fs.readFileSync(path.join(worldsDir, 'scenarios.json'), 'utf-8'));

// Game state
let gameState = {
  day: 1,
  player_location: world.start_location,
  player_gold: 50,
  player_inventory: [],
  player_hp: 28,
  player_max_hp: 28,
  player_level: 3,
  player_class: 'Fighter',
  player_xp: 900,
};

let chatHistory = [
  { id: '1', type: 'system', content: 'Welcome to Oakhollow Village. The ancient oaks whisper of adventure...', timestamp: new Date().toISOString() },
  { id: '2', type: 'dm', content: 'You find yourself at The Rusty Flagon, a warm tavern filled with the scent of roasted meat and ale. Locals murmur around their tables. What do you do?', timestamp: new Date().toISOString() },
];

let character = {
  name: 'Adventurer',
  race: 'Human',
  class: 'Fighter',
  level: 3,
  xp: 900,
  hp: 28,
  max_hp: 28,
  ac: 16,
  initiative: 2,
  proficiency_bonus: dnd.proficiencyBonus(3),
  ability_scores: { STR: 16, DEX: 14, CON: 14, INT: 10, WIS: 12, CHA: 8 },
  equipment: [
    { name: 'Longsword', type: 'weapon' },
    { name: 'Chain Mail', type: 'armor' },
    { name: 'Shield', type: 'armor' },
    { name: 'Explorer\'s Pack', type: 'gear' },
  ],
  weapon: 'longsword',
  proficient_skills: ['athletics', 'intimidation'],
  proficient_saves: ['STR', 'CON'],
  spell_slots: {},
  gold: 50, silver: 20, copper: 45,
  death_saves: { successes: 0, failures: 0 },
};

// Combat manager
const combat = new dnd.CombatManager();

let quests = [
  { id: 'q1', title: 'Wolf Hunt', description: 'Wolves have been spotted near the forest edge. The village elder asks you to investigate.', status: 'available', giver: 'Elder Marta', reward: '25 gold', difficulty: 'medium', objectives: ['Investigate wolf sightings in the forest', 'Deal with the wolf pack', 'Report back to Elder Marta'] },
  { id: 'q2', title: 'The Missing Locket', description: 'Elder Marta lost a silver locket. She thinks it fell somewhere in the market.', status: 'available', giver: 'Elder Marta', reward: '15 gold', difficulty: 'easy', objectives: ['Search the market for the locket', 'Return the locket to Marta'] },
  { id: 'q3', title: 'Forge Supplies', description: 'Torvin needs rare ore for a special commission. A merchant at the market might have some.', status: 'available', giver: 'Torvin the Smith', reward: 'Masterwork weapon', difficulty: 'medium', objectives: ['Find a merchant selling rare ore', 'Negotiate a fair price', 'Deliver the ore to Torvin'] },
  { id: 'q4', title: 'Strange Tracks', description: 'Unusual tracks have been found near the forest. Something unknown lurks in the woods.', status: 'available', giver: 'Finn the Hunter', reward: '30 gold + reputation', difficulty: 'hard', objectives: ['Follow the strange tracks', 'Identify the creature', 'Decide how to handle the threat'] },
];

// Helper
function findLocation(id) { return world.locations.find(l => l.id === id); }
function findNpc(id) { return npcsData.npcs.find(n => n.id === id); }
function npcsAtLocation(locId) { return npcsData.npcs.filter(n => n.location_id === locId && n.alive !== false); }

// --- API Routes ---

// Look
app.get('/api/look', (req, res) => {
  const loc = findLocation(gameState.player_location);
  const npcs = npcsAtLocation(gameState.player_location).map(n => ({ id: n.id, name: n.name, occupation: n.occupation, mood: n.mood }));
  const exits = world.connections.filter(c => c.from === gameState.player_location || c.to === gameState.player_location)
    .map(c => {
      const targetId = c.from === gameState.player_location ? c.to : c.from;
      const target = findLocation(targetId);
      return { id: targetId, name: target?.name || targetId, distance: c.distance };
    });
  const items = world.items.filter(i => i.owner_id && npcsAtLocation(gameState.player_location).some(n => n.id === i.owner_id));
  res.json({ location: loc, npcs, items, exits });
});

// Action - Full D&D mechanics
app.post('/api/action', (req, res) => {
  const { action } = req.body;
  if (!action) return res.json({ narration: 'What do you want to do?', npcs_involved: [], npcs_killed: [], location: findLocation(gameState.player_location), items_changed: [] });

  const actionLower = action.toLowerCase().trim();
  let narration = '';
  let npcs_killed = [];
  let npcs_involved = [];
  let combat_data = null;

  // --- MOVEMENT ---
  const goMatch = actionLower.match(/^(go|move|иду|идти|пойти|перейти)\s+(.+)/i);
  if (goMatch) {
    const target = (goMatch[2] || goMatch[1]).toLowerCase().replace(/^(to|the|в|на|к)\s+/i, '');
    const exits = world.connections.filter(c => c.from === gameState.player_location || c.to === gameState.player_location);
    for (const conn of exits) {
      const targetId = conn.from === gameState.player_location ? conn.to : conn.from;
      const loc = findLocation(targetId);
      if (loc && loc.name.toLowerCase().includes(target)) {
        gameState.player_location = targetId;
        const npcsHere = npcsAtLocation(targetId);
        narration = `You travel to ${loc.name}. ${loc.description}`;
        if (npcsHere.length > 0) narration += `\n\nYou see: ${npcsHere.map(n => `${n.name} (${n.occupation})`).join(', ')}.`;
        const msg = { id: String(Date.now()), type: 'dm', content: narration, timestamp: new Date().toISOString() };
        chatHistory.push(msg);
        return res.json({ narration, npcs_involved: npcsHere.map(n => n.id), npcs_killed: [], location: loc, items_changed: [] });
      }
    }
    narration = `You can't find a path to "${goMatch[1]}". Available exits: ${world.connections.filter(c => c.from === gameState.player_location || c.to === gameState.player_location).map(c => { const tid = c.from === gameState.player_location ? c.to : c.from; return findLocation(tid)?.name; }).filter(Boolean).join(', ')}`;
  }

  // --- ATTACK ---
  else if (actionLower.match(/^(attack|fight|hit|strike|kill)\s+(.+)/i) || actionLower.match(/(атакую|убиваю|бью|ударяю|дерусь с|нападаю на|пытаюсь убить|режу|стреляю в)\s+(.+)/i)) {
    const targetName = actionLower.replace(/^(attack|fight|hit|strike|kill)\s+/i, '').replace(/(атакую|убиваю|бью|ударяю|дерусь с|нападаю на|пытаюсь убить|режу|стреляю в)\s+/i, '').replace(/^(я\s+)/i, '').trim();
    const npcsHere = npcsAtLocation(gameState.player_location);
    const targetNpc = npcsHere.find(n => n.name.toLowerCase().includes(targetName));

    if (!targetNpc) {
      narration = `There's no "${targetName}" here. NPCs present: ${npcsHere.map(n => n.name).join(', ') || 'none'}`;
    } else {
      // Start combat if not in combat
      if (!combat.inCombat) {
        const combatStart = combat.startCombat(character, [targetNpc]);
        narration = `=== COMBAT BEGINS! ===\n${combatStart.log.join('\n')}\n\n`;
      }

      // Player attacks
      const result = combat.playerAttack(targetNpc.id);
      narration += result.narration;
      combat_data = { ...result, combatState: combat.getState() };

      if (result.killed) {
        npcs_killed.push(targetNpc.id);
        // End combat if all enemies down
        const aliveEnemies = combat.combatants.filter(c => c.type === 'npc' && c.hp > 0);
        if (aliveEnemies.length === 0) {
          const endResult = combat.endCombat();
          narration += `\n\n=== COMBAT ENDS ===\nVictory! XP gained: ${endResult.xpGained}`;
          gameState.player_xp = (gameState.player_xp || character.xp) + endResult.xpGained;
          combat_data.combatEnd = endResult;
        }
      } else {
        // Enemy counterattacks
        const aliveEnemies = combat.combatants.filter(c => c.type === 'npc' && c.hp > 0);
        for (const enemy of aliveEnemies) {
          const npcResult = combat.npcAttack(enemy.id);
          if (npcResult) {
            narration += `\n${npcResult.narration}`;
            if (npcResult.playerDown) {
              gameState.player_hp = 0;
              narration += `\nYou fall unconscious! Use "respawn" to continue.`;
            }
          }
        }
        combat_data.combatState = combat.getState();
      }

      // Update player HP from combat
      const playerCombatant = combat.combatants.find(c => c.id === 'player');
      if (playerCombatant) {
        gameState.player_hp = playerCombatant.hp;
        character.hp = playerCombatant.hp;
      }

      npcs_involved = [targetNpc.id];
    }
  }

  // --- SKILL CHECK ---
  else if (actionLower.match(/^(check|roll|use)\s+(stealth|perception|persuasion|intimidation|deception|athletics|acrobatics|insight|investigation|arcana|history|religion|medicine|nature|survival|performance|sleight_of_hand|animal_handling)/i)) {
    const skillName = actionLower.match(/(stealth|perception|persuasion|intimidation|deception|athletics|acrobatics|insight|investigation|arcana|history|religion|medicine|nature|survival|performance|sleight_of_hand|animal_handling)/i)[1].toLowerCase();
    const check = dnd.skillCheck(character.ability_scores, character.level, skillName, character.proficient_skills);

    let outcome = '';
    if (check.isCritSuccess) outcome = 'CRITICAL SUCCESS! An extraordinary result!';
    else if (check.isCritFail) outcome = 'CRITICAL FAILURE! Something goes terribly wrong...';
    else if (check.total >= 20) outcome = 'Exceptional success!';
    else if (check.total >= 15) outcome = 'Success!';
    else if (check.total >= 10) outcome = 'Partial success.';
    else outcome = 'Failure.';

    narration = `[${skillName.toUpperCase()} CHECK] ${check.breakdown}\n${outcome}`;

    // Contextual narration
    if (skillName === 'stealth' && check.total >= 15) narration += '\nYou move like a shadow, unseen and unheard.';
    else if (skillName === 'perception' && check.total >= 15) narration += '\nYour keen senses pick up every detail of your surroundings.';
    else if (skillName === 'persuasion' && check.total >= 15) narration += '\nYour words carry conviction and charm.';
    else if (skillName === 'intimidation' && check.total >= 15) narration += '\nYour presence is menacing. Others cower before you.';

    combat_data = { skillCheck: check };
  }

  // --- CAST SPELL ---
  else if (actionLower.match(/^cast\s+(.+?)(\s+on\s+(.+))?$/i)) {
    const spellMatch = actionLower.match(/^cast\s+(.+?)(\s+on\s+(.+))?$/i);
    const spellKey = spellMatch[1].trim().replace(/\s+/g, '_');
    const targetName = spellMatch[3]?.trim();
    const spell = dnd.SPELLS[spellKey];

    if (!spell) {
      const available = Object.values(dnd.SPELLS).map(s => s.name).join(', ');
      narration = `Unknown spell "${spellMatch[1]}". Available spells: ${available}`;
    } else {
      // Check spell slots
      if (spell.level > 0) {
        const slots = character.spell_slots[spell.level] || (dnd.SPELL_SLOTS[character.level]?.[spell.level] || 0);
        if (slots <= 0) {
          narration = `No spell slots remaining for level ${spell.level} spells!`;
        }
      }

      if (!narration) {
        let targetId = null;
        if (targetName) {
          const npcsHere = npcsAtLocation(gameState.player_location);
          const targetNpc = npcsHere.find(n => n.name.toLowerCase().includes(targetName));
          if (targetNpc) {
            targetId = targetNpc.id;
            if (!combat.inCombat && spell.damage) {
              combat.startCombat(character, [targetNpc]);
            }
          }
        }

        if (combat.inCombat) {
          const result = combat.castSpell(spellKey, targetId || combat.combatants.find(c => c.type === 'npc' && c.hp > 0)?.id);
          narration = result.narration || result.error;
          combat_data = result;

          // Deduct spell slot
          if (spell.level > 0 && !result.error) {
            if (!character.spell_slots[spell.level]) character.spell_slots[spell.level] = dnd.SPELL_SLOTS[character.level]?.[spell.level] || 0;
            character.spell_slots[spell.level]--;
          }
        } else {
          // Out of combat casting
          if (spell.healing) {
            const heal = dnd.rollNotation(spell.healing);
            const spellMod = dnd.abilityModifier(character.ability_scores[spell.ability] || 10);
            const healTotal = heal.total + spellMod;
            character.hp = Math.min(character.max_hp, character.hp + healTotal);
            gameState.player_hp = character.hp;
            narration = `You cast ${spell.name}! Healed for ${healTotal} HP. [${heal.rolls.join('+')} + ${spellMod}] HP: ${character.hp}/${character.max_hp}`;
          } else {
            narration = `You cast ${spell.name}. ${spell.description}`;
          }
          combat_data = { spell: spell.name };
        }
      }
    }
  }

  // --- ROLL DICE ---
  else if (actionLower.match(/^roll\s+(\d+d\d+([+-]\d+)?)/i)) {
    const notation = actionLower.match(/^roll\s+(\d+d\d+([+-]\d+)?)/i)[1];
    const result = dnd.rollNotation(notation);
    narration = `[DICE ROLL] ${notation}: ${result.rolls.join(' + ')}${result.modifier ? ` + ${result.modifier}` : ''} = ${result.total}`;
    combat_data = { diceRoll: result };
  }

  // --- LOOK ---
  else if (actionLower === 'look' || actionLower === 'examine') {
    const loc = findLocation(gameState.player_location);
    const npcs = npcsAtLocation(gameState.player_location);
    narration = `${loc.name}\n${loc.description}`;
    if (npcs.length > 0) narration += `\n\nPresent: ${npcs.map(n => `${n.name} (${n.occupation}, mood: ${n.mood})`).join(', ')}`;
    const exits = world.connections.filter(c => c.from === gameState.player_location || c.to === gameState.player_location)
      .map(c => findLocation(c.from === gameState.player_location ? c.to : c.from)?.name).filter(Boolean);
    narration += `\n\nExits: ${exits.join(', ')}`;
  }

  // --- REST ---
  else if (actionLower.match(/^(rest|sleep|short rest|long rest)/i)) {
    const isLongRest = actionLower.includes('long');
    if (isLongRest) {
      character.hp = character.max_hp;
      gameState.player_hp = character.max_hp;
      // Restore spell slots
      const classData = dnd.CLASS_FEATURES[character.class?.toLowerCase()];
      if (classData) {
        character.spell_slots = { ...(dnd.SPELL_SLOTS[character.level] || {}) };
      }
      narration = `You take a long rest. HP fully restored to ${character.max_hp}. Spell slots restored. A new day dawns over Oakhollow.`;
      gameState.day++;
    } else {
      // Short rest: spend hit dice
      const classData = dnd.CLASS_FEATURES[character.class?.toLowerCase()] || { hitDie: 8 };
      const hitDieRoll = dnd.rollDie(classData.hitDie);
      const conMod = dnd.abilityModifier(character.ability_scores.CON);
      const healed = Math.max(1, hitDieRoll + conMod);
      character.hp = Math.min(character.max_hp, character.hp + healed);
      gameState.player_hp = character.hp;
      narration = `You take a short rest. Spent 1 Hit Die (d${classData.hitDie}): rolled ${hitDieRoll} + ${conMod} (CON) = ${healed} HP restored. HP: ${character.hp}/${character.max_hp}`;
    }
  }

  // --- COMBAT STATUS ---
  else if (actionLower === 'combat' || actionLower === 'status') {
    if (combat.inCombat) {
      const state = combat.getState();
      narration = `=== COMBAT STATUS (Round ${state.round}) ===\n`;
      state.combatants.forEach(c => {
        narration += `${c.name}: ${c.hp}/${c.maxHp} HP | AC ${c.ac}${c.isDown ? ' [DOWN]' : ''}\n`;
      });
    } else {
      narration = `HP: ${character.hp}/${character.max_hp} | AC: ${character.ac} | Level ${character.level} ${character.class}\nSTR:${character.ability_scores.STR} DEX:${character.ability_scores.DEX} CON:${character.ability_scores.CON} INT:${character.ability_scores.INT} WIS:${character.ability_scores.WIS} CHA:${character.ability_scores.CHA}`;
    }
  }

  // --- SPELLS LIST ---
  else if (actionLower === 'spells' || actionLower === 'spell list') {
    narration = '=== AVAILABLE SPELLS ===\n';
    Object.entries(dnd.SPELLS).forEach(([key, s]) => {
      narration += `${s.name} (Lv${s.level}): ${s.description}\n`;
    });
  }

  // --- DEFAULT: check if it might be combat in another language ---
  else {
    // Try to match combat intent from any language by checking if NPC names appear in the action
    const npcsHere = npcsAtLocation(gameState.player_location);
    const combatWords = ['убиваю', 'атакую', 'бью', 'ударяю', 'нападаю', 'убить', 'дерусь', 'режу', 'стреляю', 'attack', 'kill', 'fight', 'hit', 'strike'];
    const isCombatIntent = combatWords.some(w => actionLower.includes(w));

    if (isCombatIntent && npcsHere.length > 0) {
      // Find target NPC by name match in any language
      const targetNpc = npcsHere.find(n => actionLower.includes(n.name.toLowerCase()) || actionLower.includes(n.name.split(' ')[0].toLowerCase()));

      if (targetNpc) {
        // Start combat
        if (!combat.inCombat) {
          const combatStart = combat.startCombat(character, [targetNpc]);
          narration = `=== COMBAT BEGINS! ===\n${combatStart.log.join('\n')}\n\n`;
        }
        const result = combat.playerAttack(targetNpc.id);
        narration += result.narration;
        combat_data = { ...result, combatState: combat.getState() };

        if (result.killed) {
          npcs_killed.push(targetNpc.id);
          const aliveEnemies = combat.combatants.filter(c => c.type === 'npc' && c.hp > 0);
          if (aliveEnemies.length === 0) {
            const endResult = combat.endCombat();
            narration += `\n\n=== COMBAT ENDS ===\nVictory! XP gained: ${endResult.xpGained}`;
            gameState.player_xp = (gameState.player_xp || character.xp) + endResult.xpGained;
          }
        } else {
          // Enemy counterattacks
          const aliveEnemies = combat.combatants.filter(c => c.type === 'npc' && c.hp > 0);
          for (const enemy of aliveEnemies) {
            const npcResult = combat.npcAttack(enemy.id);
            if (npcResult) {
              narration += `\n${npcResult.narration}`;
              if (npcResult.playerDown) {
                gameState.player_hp = 0;
                narration += `\nYou fall unconscious!`;
              }
            }
          }
          combat_data.combatState = combat.getState();
        }

        const playerCombatant = combat.combatants.find(c => c.id === 'player');
        if (playerCombatant) {
          gameState.player_hp = playerCombatant.hp;
          character.hp = playerCombatant.hp;
        }
        npcs_involved = [targetNpc.id];
      } else {
        narration = `You look around for a target but can't find one matching your intent. NPCs here: ${npcsHere.map(n => n.name).join(', ')}`;
      }
    } else {
      // Truly unrecognized action — narrate generically
      narration = `You attempt to "${action}". Nothing notable happens.`;
    }
  }

  const msg = { id: String(Date.now()), type: 'dm', content: narration, timestamp: new Date().toISOString() };
  chatHistory.push(msg);
  res.json({
    narration, npcs_involved, npcs_killed,
    location: findLocation(gameState.player_location),
    items_changed: [],
    combat_data,
    player_hp: character.hp,
    player_max_hp: character.max_hp,
  });
});

// Dialogue - with D&D skill checks and language support
app.post('/api/dialogue', (req, res) => {
  const { npc_id, message, lang } = req.body;
  const npc = findNpc(npc_id);
  if (!npc) return res.status(404).json({ error: 'NPC not found' });

  const isRu = lang === 'ru';
  const msgLower = (message || '').toLowerCase();
  let dialogue = '';
  let skillCheckResult = null;

  // Check for persuasion/intimidation/deception (EN + RU keywords)
  if (msgLower.match(/persuad|please|convince|убеди|пожалуйста|прошу/)) {
    skillCheckResult = dnd.skillCheck(character.ability_scores, character.level, 'persuasion', character.proficient_skills);
    if (skillCheckResult.total >= 15) {
      dialogue = isRu
        ? `*${npc.name} задумчиво кивает* "Хм, в твоих словах есть смысл. Хорошо, я помогу тебе."`
        : `*${npc.name} considers your words carefully* "You make a compelling argument. Very well, I'll help you."`;
    } else {
      dialogue = isRu
        ? `*${npc.name} качает головой* "Нет, ты меня не убедил. Попробуй другой подход."`
        : `*${npc.name} shakes their head* "I appreciate your effort, but I'm not convinced."`;
    }
  } else if (msgLower.match(/threaten|or else|scare|угрожа|пугаю|запугива/)) {
    skillCheckResult = dnd.skillCheck(character.ability_scores, character.level, 'intimidation', character.proficient_skills);
    if (skillCheckResult.total >= 15) {
      dialogue = isRu
        ? `*${npc.name} бледнеет* "Л-ладно! Не надо угроз! Я сделаю, что ты просишь!"`
        : `*${npc.name} pales* "A-alright! No need for threats! I'll do what you ask!"`;
    } else {
      dialogue = isRu
        ? `*${npc.name} стоит твёрдо* "Ты меня не напугаешь, путник. Я видал и похуже."`
        : `*${npc.name} stands firm* "You don't scare me, adventurer. I've seen worse than you."`;
    }
  } else if (msgLower.match(/lie|trick|pretend|обман|вру|хитр/)) {
    skillCheckResult = dnd.skillCheck(character.ability_scores, character.level, 'deception', character.proficient_skills);
    const insightCheck = dnd.skillCheck(npc.ability_scores || { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 14, CHA: 10 }, npc.level || 1, 'insight', []);
    if (skillCheckResult.total > insightCheck.total) {
      dialogue = isRu
        ? `*${npc.name} верит тебе* "Правда? Я и не знал! Спасибо, что рассказал."`
        : `*${npc.name} nods, believing your words* "Really? I had no idea! Thank you for telling me."`;
    } else {
      dialogue = isRu
        ? `*${npc.name} прищуривается* "Подожди... что-то тут не сходится. Ты пытаешься меня обмануть?"`
        : `*${npc.name} narrows their eyes* "Wait... something doesn't add up. Are you trying to deceive me?"`;
    }
  } else {
    // Context-aware dialogue based on mood, backstory and message content
    const backstorySnippet = npc.backstory?.split('.')[0] || '';
    const goalSnippet = npc.goals?.[0] || '';

    // Detect question types
    const isQuestion = msgLower.match(/\?|почему|зачем|кто ты|как дела|что |where|why|who|how|what/);
    const isAboutDrinking = msgLower.match(/пьёшь|пьешь|бухаешь|алкаш|выпивк|drink|drunk|ale|beer/);
    const isGreeting = msgLower.match(/привет|здравствуй|здорово|hello|hi |hey|greet/);
    const isInsult = msgLower.match(/дурак|идиот|ебан|блядь|сука|хуй|пизд|fuck|shit|asshole|idiot|stupid/);
    const isAboutSelf = msgLower.match(/кто ты|расскажи о себе|who are you|tell me about/);

    if (isInsult) {
      const responses = isRu ? [
        `*${npc.name} хмурится* "Следи за языком, путник. В этой деревне за такие слова можно и по зубам получить."`,
        `*${npc.name} сжимает кулаки* "Ещё одно слово — и пожалеешь, что зашёл сюда."`,
        `*${npc.name} отворачивается* "Я не собираюсь разговаривать с тем, кто не умеет вести себя."`,
      ] : [
        `*${npc.name} frowns* "Watch your tongue, traveler. Words like that can get you hurt around here."`,
        `*${npc.name} clenches their fists* "One more word like that and you'll regret stepping in here."`,
        `*${npc.name} turns away* "I don't talk to people who can't show basic respect."`,
      ];
      dialogue = responses[Math.floor(Math.random() * responses.length)];
    } else if (isAboutDrinking && npc.occupation?.includes('soldier')) {
      dialogue = isRu
        ? `*${npc.name} смотрит в кружку* "Пью? А что мне ещё делать? Война забрала у меня всё — товарищей, здоровье, смысл. Эль — единственное, что притупляет воспоминания. ${backstorySnippet ? backstorySnippet + '.' : ''}"`
        : `*${npc.name} stares into the mug* "Why do I drink? What else is there? The war took everything — my comrades, my health, my purpose. Ale is the only thing that dulls the memories. ${backstorySnippet ? backstorySnippet + '.' : ''}"`;
    } else if (isAboutDrinking) {
      dialogue = isRu
        ? `*${npc.name} пожимает плечами* "А тебе-то какое дело до моей выпивки? У каждого свои способы справляться с этим миром."`
        : `*${npc.name} shrugs* "What's it to you how much I drink? Everyone has their own way of coping."`;
    } else if (isAboutSelf) {
      dialogue = isRu
        ? `*${npc.name}* "Меня зовут ${npc.name}. Я ${npc.occupation} здесь, в Оакхоллоу. ${backstorySnippet ? backstorySnippet + '.' : ''} ${goalSnippet ? 'Сейчас я хочу ' + goalSnippet + '.' : ''}"`
        : `*${npc.name}* "I'm ${npc.name}, the village ${npc.occupation}. ${backstorySnippet ? backstorySnippet + '.' : ''} ${goalSnippet ? 'Right now I want to ' + goalSnippet + '.' : ''}"`;
    } else if (isGreeting) {
      dialogue = isRu
        ? `*${npc.name} кивает* "Привет, путник. Я ${npc.name}, ${npc.occupation}. ${npc.mood === 'concerned' ? 'Неспокойные нынче времена...' : 'Чем могу помочь?'}"`
        : `*${npc.name} nods* "Hello, traveler. I'm ${npc.name}, ${npc.occupation}. ${npc.mood === 'concerned' ? 'Troubled times these days...' : 'How can I help?'}"`;
    } else if (isQuestion) {
      // Generic question — answer based on personality and backstory
      dialogue = isRu
        ? `*${npc.name}* "${backstorySnippet ? backstorySnippet + '. ' : ''}${goalSnippet ? 'Меня сейчас больше всего заботит — ' + goalSnippet + '.' : 'Трудно сказать... жизнь в деревне непростая.'}"`
        : `*${npc.name}* "${backstorySnippet ? backstorySnippet + '. ' : ''}${goalSnippet ? 'What concerns me most right now is ' + goalSnippet + '.' : 'Hard to say... village life isn\'t easy.'}"`
    } else {
      // Mood-based fallback
      const moodResponses = isRu ? {
        concerned: [`*${npc.name} хмурится* "Тёмные нынче времена. ${goalSnippet ? 'Мне нужно ' + goalSnippet + '.' : 'Я беспокоюсь о том, что будет дальше.'}"`,],
        content: [`*${npc.name} улыбается* "Жизнь в Оакхоллоу имеет свои прелести. ${backstorySnippet || 'Мне нравится моя работа.'}."`,],
        excited: [`*${npc.name} оживляется* "${goalSnippet ? 'Я так близок к своей цели — ' + goalSnippet + '!' : 'Происходит что-то замечательное!'}"`,],
        angry: [`*${npc.name} рычит* "Чего тебе надо? Мне не до разговоров."`,],
        fearful: [`*${npc.name} оглядывается* "Тише... что-то неладно в деревне."`,],
        scheming: [`*${npc.name} наклоняется ближе* "У меня есть кое-что интересное... но информация стоит денег."`,],
      } : {
        concerned: [`*${npc.name} furrows their brow* "Dark times. ${goalSnippet ? 'I must ' + goalSnippet + '.' : 'I worry about what comes next.'}"`,],
        content: [`*${npc.name} smiles* "Life here has its charms. ${backstorySnippet || 'I enjoy my work.'}."`,],
        excited: [`*${npc.name}'s eyes light up* "${goalSnippet ? 'I\'m so close to ' + goalSnippet + '!' : 'Something wonderful is happening!'}"`,],
        angry: [`*${npc.name} scowls* "What do you want? I'm not in the mood."`,],
        fearful: [`*${npc.name} glances around nervously* "Keep your voice down... something isn't right."`,],
        scheming: [`*${npc.name} leans in* "I might know something useful... but information has a price."`,],
      };
      const options = moodResponses[npc.mood] || moodResponses.content;
      dialogue = options[Math.floor(Math.random() * options.length)];
    }
  }

  const chatMsg = { id: String(Date.now()), type: 'npc', content: dialogue, npc_name: npc.name, timestamp: new Date().toISOString() };
  chatHistory.push(chatMsg);
  res.json({ npc_name: npc.name, dialogue, mood: npc.mood, interjections: [], skill_check: skillCheckResult });
});

// World State
app.get('/api/world/state', (req, res) => res.json(gameState));

// World Log
app.get('/api/world/log', (req, res) => {
  const entries = [];
  for (let d = 1; d <= gameState.day; d++) {
    const dayEvents = events.events.slice((d - 1) * 2, d * 2).map(e => ({ description: e.description, type: e.type }));
    entries.push({
      day: d,
      events: dayEvents,
      npc_actions: [`${npcsData.npcs[d % npcsData.npcs.length]?.name || 'A villager'} went about their daily routine.`],
      interactions: [],
      active_scenarios: d > 2 ? [{ title: scenarios[0].title, description: scenarios[0].description, phase_name: scenarios[0].phases[Math.min(d - 2, 4)], tension_level: d > 4 ? 'climax' : 'rising' }] : [],
    });
  }
  res.json({ entries });
});

// World Map
app.get('/api/world/map', (req, res) => {
  const npc_locations = {};
  npcsData.npcs.forEach(n => { npc_locations[n.id] = n.location_id; });
  res.json({
    locations: world.locations,
    connections: world.connections.map(c => ({ from_id: c.from, to_id: c.to, distance: c.distance })),
    player_location_id: gameState.player_location,
    npc_locations,
  });
});

// Tick
app.post('/api/world/tick', (req, res) => {
  gameState.day++;
  const dayEvents = events.events.slice(((gameState.day - 1) * 2) % events.events.length, ((gameState.day - 1) * 2 + 2) % events.events.length);
  // Move some NPCs randomly
  npcsData.npcs.forEach(n => {
    if (Math.random() > 0.6) {
      const conns = world.connections.filter(c => c.from === n.location_id || c.to === n.location_id);
      if (conns.length) {
        const conn = conns[Math.floor(Math.random() * conns.length)];
        n.location_id = conn.from === n.location_id ? conn.to : conn.from;
      }
    }
  });
  res.json({
    day: gameState.day,
    events: dayEvents.map(e => ({ description: e.description, type: e.type })),
    npc_actions: npcsData.npcs.slice(0, 3).map(n => `${n.name} is at ${findLocation(n.location_id)?.name || 'unknown'}.`),
    interactions: [],
    active_scenarios: gameState.day > 2 ? [{ title: scenarios[0].title, description: scenarios[0].description, phase_name: scenarios[0].phases[Math.min(gameState.day - 2, 4)], tension_level: gameState.day > 4 ? 'climax' : 'rising' }] : [],
  });
});

// Tick Stream (simplified - just returns SSE)
app.post('/api/world/tick/stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  gameState.day++;
  const dayEvents = events.events.slice(((gameState.day - 1) * 2) % events.events.length, ((gameState.day - 1) * 2 + 2) % events.events.length);
  const result = {
    day: gameState.day,
    events: dayEvents.map(e => ({ description: e.description, type: e.type })),
    npc_actions: npcsData.npcs.slice(0, 3).map(n => `${n.name} is at ${findLocation(n.location_id)?.name || 'unknown'}.`),
    interactions: [],
    active_scenarios: [],
  };
  res.write(`data: ${JSON.stringify({ phase: 'scenarios', data: { title: 'World advances...' } })}\n\n`);
  setTimeout(() => {
    res.write(`data: ${JSON.stringify({ phase: 'events', data: result.events })}\n\n`);
    setTimeout(() => {
      res.write(`data: ${JSON.stringify({ phase: 'complete', data: result })}\n\n`);
      res.end();
    }, 500);
  }, 500);
});

// NPC Graph
app.get('/api/npcs/graph', (req, res) => {
  const nodes = npcsData.npcs.map(n => ({
    id: n.id, name: n.name, occupation: n.occupation, mood: n.mood,
    level: n.level || 1, archetype: n.archetype, known: true, alive: n.alive !== false,
  }));
  const edges = [];
  npcsData.npcs.forEach(n => {
    (n.relationships || []).forEach(r => {
      edges.push({ from: n.id, to: r.target_id, sentiment: r.sentiment, reason: r.reason, visible: true });
    });
  });
  res.json({ nodes, edges });
});

// NPC Info
app.get('/api/npc/:id', (req, res) => {
  const npc = findNpc(req.params.id);
  if (!npc) return res.status(404).json({ error: 'NPC not found' });
  res.json({ id: npc.id, name: npc.name, occupation: npc.occupation, mood: npc.mood, description: npc.backstory });
});

// NPC Observe
app.get('/api/npc/:id/observe', (req, res) => {
  const npc = findNpc(req.params.id);
  if (!npc) return res.status(404).json({ error: 'NPC not found' });
  res.json({
    id: npc.id, name: npc.name, personality: npc.personality, backstory: npc.backstory,
    goals: npc.goals, mood: npc.mood, occupation: npc.occupation, age: npc.age,
    alive: npc.alive !== false, location: findLocation(npc.location_id)?.name || npc.location_id,
    relationships: (npc.relationships || []).map(r => {
      const target = findNpc(r.target_id);
      return { id: r.target_id, name: target?.name || r.target_id, sentiment: r.sentiment, reason: r.reason };
    }),
    recent_memories: [`Day ${gameState.day}: Went about daily tasks as ${npc.occupation}.`],
  });
});

// Character
app.get('/api/character', (req, res) => res.json(character));
app.post('/api/character/create', (req, res) => {
  Object.assign(character, req.body);
  res.json(character);
});
app.put('/api/character', (req, res) => {
  Object.assign(character, req.body);
  res.json(character);
});
app.post('/api/character/level-up', (req, res) => {
  character.level++;
  character.max_hp += 6;
  character.hp = character.max_hp;
  res.json(character);
});
app.post('/api/character/roll-stats', (req, res) => {
  const roll4d6 = () => {
    const rolls = Array.from({ length: 4 }, () => Math.floor(Math.random() * 6) + 1);
    rolls.sort((a, b) => a - b);
    return rolls.slice(1).reduce((a, b) => a + b, 0);
  };
  res.json({ stats: [roll4d6(), roll4d6(), roll4d6(), roll4d6(), roll4d6(), roll4d6()] });
});

// DnD Reference
app.get('/api/dnd/races', (req, res) => res.json({ races: [
  { id: 'human', name: 'Human', description: 'Versatile and ambitious.', ability_bonuses: { all: 1 } },
  { id: 'elf', name: 'Elf', description: 'Graceful and long-lived.', ability_bonuses: { DEX: 2 } },
  { id: 'dwarf', name: 'Dwarf', description: 'Sturdy and resilient.', ability_bonuses: { CON: 2 } },
  { id: 'halfling', name: 'Halfling', description: 'Small but brave.', ability_bonuses: { DEX: 2 } },
  { id: 'half-orc', name: 'Half-Orc', description: 'Strong and fierce.', ability_bonuses: { STR: 2, CON: 1 } },
  { id: 'tiefling', name: 'Tiefling', description: 'Touched by the infernal.', ability_bonuses: { CHA: 2, INT: 1 } },
]}));

app.get('/api/dnd/classes', (req, res) => res.json({ classes: [
  { id: 'fighter', name: 'Fighter', description: 'Master of martial combat.', hit_die: 10, primary_ability: 'STR' },
  { id: 'wizard', name: 'Wizard', description: 'Scholarly magic user.', hit_die: 6, primary_ability: 'INT' },
  { id: 'rogue', name: 'Rogue', description: 'Stealthy and cunning.', hit_die: 8, primary_ability: 'DEX' },
  { id: 'cleric', name: 'Cleric', description: 'Divine healer and warrior.', hit_die: 8, primary_ability: 'WIS' },
  { id: 'ranger', name: 'Ranger', description: 'Wilderness warrior.', hit_die: 10, primary_ability: 'DEX' },
  { id: 'barbarian', name: 'Barbarian', description: 'Primal fury unleashed.', hit_die: 12, primary_ability: 'STR' },
]}));

app.get('/api/dnd/weapons', (req, res) => res.json({ weapons: [
  { name: 'Longsword', damage: '1d8', type: 'slashing', properties: ['versatile'] },
  { name: 'Shortbow', damage: '1d6', type: 'piercing', properties: ['ranged', 'two-handed'] },
  { name: 'Dagger', damage: '1d4', type: 'piercing', properties: ['finesse', 'light', 'thrown'] },
  { name: 'Greataxe', damage: '1d12', type: 'slashing', properties: ['heavy', 'two-handed'] },
  { name: 'Mace', damage: '1d6', type: 'bludgeoning', properties: [] },
]}));

app.get('/api/dnd/armors', (req, res) => res.json({ armors: [
  { name: 'Leather Armor', ac: 11, type: 'light', stealth_disadvantage: false },
  { name: 'Chain Mail', ac: 16, type: 'heavy', stealth_disadvantage: true },
  { name: 'Shield', ac: 2, type: 'shield', stealth_disadvantage: false },
  { name: 'Studded Leather', ac: 12, type: 'light', stealth_disadvantage: false },
  { name: 'Plate Armor', ac: 18, type: 'heavy', stealth_disadvantage: true },
]}));

app.post('/api/dnd/roll', (req, res) => {
  const { notation } = req.body;
  const result = dnd.rollNotation(notation || '1d20');
  res.json({ result: result.total, rolls: result.rolls, modifier: result.modifier, notation: result.notation });
});

// --- D&D COMBAT ENDPOINTS ---
app.get('/api/combat/state', (req, res) => {
  res.json(combat.inCombat ? combat.getState() : { inCombat: false });
});

app.post('/api/combat/attack', (req, res) => {
  const { target_id, weapon } = req.body;
  if (!combat.inCombat) return res.json({ error: 'Not in combat. Use "attack [npc]" to start.' });
  const result = combat.playerAttack(target_id, weapon);
  res.json({ ...result, combatState: combat.getState() });
});

app.post('/api/combat/cast', (req, res) => {
  const { spell, target_id } = req.body;
  const result = combat.castSpell(spell, target_id);
  res.json({ ...result, combatState: combat.getState() });
});

app.post('/api/combat/end', (req, res) => {
  const result = combat.endCombat();
  res.json(result);
});

// Skill check endpoint
app.post('/api/dnd/skill-check', (req, res) => {
  const { skill, advantage } = req.body;
  const result = dnd.skillCheck(character.ability_scores, character.level, skill, character.proficient_skills, advantage || 'normal');
  res.json(result);
});

// Saving throw endpoint
app.post('/api/dnd/saving-throw', (req, res) => {
  const { ability, dc } = req.body;
  const result = dnd.savingThrow(character.ability_scores, character.level, ability, character.proficient_saves, dc || 10);
  res.json(result);
});

// Get all spells
app.get('/api/dnd/spells', (req, res) => {
  res.json({ spells: Object.entries(dnd.SPELLS).map(([key, s]) => ({ id: key, ...s })) });
});

// Quests
app.get('/api/quests', (req, res) => res.json({ quests }));
app.post('/api/quests/:id/accept', (req, res) => {
  const quest = quests.find(q => q.id === req.params.id);
  if (quest) quest.status = 'active';
  res.json(quest || { error: 'Not found' });
});
app.post('/api/quests/:id/complete', (req, res) => {
  const quest = quests.find(q => q.id === req.params.id);
  if (quest) quest.status = 'completed';
  res.json(quest || { error: 'Not found' });
});

// Saves
app.post('/api/world/save', (req, res) => res.json({ filename: `save_day${gameState.day}.json`, saved: true }));
app.get('/api/world/saves', (req, res) => {
  const savesDir = path.join(__dirname, '..', 'worlds', 'saves');
  const files = fs.existsSync(savesDir) ? fs.readdirSync(savesDir).filter(f => f.endsWith('.json')) : [];
  res.json({ saves: files });
});
app.post('/api/world/load/:filename', (req, res) => res.json({ loaded: true, filename: req.params.filename }));
app.post('/api/world/reset', (req, res) => {
  gameState.day = 1;
  gameState.player_location = world.start_location;
  res.json({ reset: true });
});
app.post('/api/player/respawn', (req, res) => {
  gameState.player_hp = gameState.player_max_hp;
  gameState.player_location = world.start_location;
  res.json({ respawned: true });
});

// Chat history
app.get('/api/chat/history', (req, res) => res.json({ messages: chatHistory }));

// Worlds
app.get('/api/worlds', (req, res) => res.json({ worlds: [{ id: 'oakhollow', name: world.name, description: world.description, location_count: world.locations.length, npc_count: npcsData.npcs.length }] }));
app.get('/api/worlds/:id', (req, res) => res.json({ id: req.params.id, ...world, npcs: npcsData.npcs }));
app.post('/api/worlds', (req, res) => res.json({ id: 'new-world', ...req.body }));
app.delete('/api/worlds/:id', (req, res) => res.json({ deleted: true }));
app.post('/api/worlds/:id/load', (req, res) => res.json({ loaded: true }));
app.post('/api/worlds/:id/locations', (req, res) => {
  const loc = { id: `loc-${Date.now()}`, ...req.body };
  world.locations.push(loc);
  res.json(loc);
});
app.post('/api/worlds/:id/npcs', (req, res) => {
  const npc = { id: `npc-${Date.now()}`, ...req.body };
  npcsData.npcs.push(npc);
  res.json(npc);
});
app.post('/api/worlds/:id/generate/npc', (req, res) => {
  res.json({ id: `npc-gen-${Date.now()}`, name: 'Generated NPC', occupation: 'wanderer', mood: 'content', backstory: `[Mock] Generated from: ${req.body.description}`, goals: ['survive'], personality: 'O:mid, C:mid, E:mid, A:mid, N:mid', age: 30, location_id: world.start_location });
});
app.post('/api/worlds/:id/generate/location', (req, res) => {
  res.json({ id: `loc-gen-${Date.now()}`, name: 'Generated Location', type: 'ruins', description: `[Mock] Generated from: ${req.body.description}` });
});

// ===== NPC LIFE SERVICE API =====

// Initialize NPC Life Service with existing world data
let npcLifeInitialized = false;
function initNPCLife() {
  if (npcLifeInitialized) return;
  npcLife.importFromJSON(npcsData.npcs);
  npcLife.worldDay = gameState.day;
  npcLifeInitialized = true;
}

// Get all living NPCs with psychology summary
app.get('/api/npc-life/all', (req, res) => {
  initNPCLife();
  res.json({ npcs: npcLife.getAllNPCs(), day: npcLife.worldDay });
});

// Get deep psychological profile of NPC
app.get('/api/npc-life/:id/deep-profile', (req, res) => {
  initNPCLife();
  const profile = npcLife.getDeepProfile(req.params.id);
  if (!profile) return res.status(404).json({ error: 'NPC not found' });
  res.json(profile);
});

// Generate new NPC with full psychology
app.post('/api/npc-life/generate', (req, res) => {
  initNPCLife();
  const npc = npcLife.createNPC(req.body);
  res.json({
    id: npc.id,
    name: npc.name,
    summary: npc.biography.summary,
    accentuation: npc.psychProfile.accentuation.name,
    maslowLevel: npc.psychProfile.maslowLevel.name,
    origin: npc.biography.origin.name,
    mood: npc.mood,
    goals: npc.goals,
    disability: npc.biography.disability.name,
  });
});

// Apply event to NPC (trauma, kindness, violence, etc.)
app.post('/api/npc-life/:id/event', (req, res) => {
  initNPCLife();
  const result = npcLife.applyEvent(req.params.id, req.body);
  if (!result) return res.status(404).json({ error: 'NPC not found' });
  res.json(result);
});

// Get NPC dialogue (psychology-based)
app.post('/api/npc-life/:id/dialogue', (req, res) => {
  initNPCLife();
  const result = npcLife.generateDialogue(req.params.id, req.body.message || '');
  res.json(result);
});

// Tick all NPCs (world simulation step)
app.post('/api/npc-life/tick', (req, res) => {
  initNPCLife();
  const result = npcLife.tickAll();
  gameState.day = npcLife.worldDay;
  res.json(result);
});

// NPC-NPC interaction
app.post('/api/npc-life/interact', (req, res) => {
  initNPCLife();
  const { npcA, npcB } = req.body;
  const result = npcLife.interactNPCs(npcA, npcB);
  if (!result) return res.status(400).json({ error: 'Invalid NPCs' });
  res.json(result);
});

// Get NPC memories
app.get('/api/npc-life/:id/memories', (req, res) => {
  initNPCLife();
  const npc = npcLife.npcs.get(req.params.id);
  if (!npc) return res.status(404).json({ error: 'NPC not found' });
  res.json({ memories: npc.memory, total: npc.memory.length });
});

// ===== STORY TREE API =====

app.get('/api/story/tree', (req, res) => {
  initNPCLife();
  res.json(npcLife.storyTree.getTree());
});

app.get('/api/story/timeline/:name', (req, res) => {
  initNPCLife();
  res.json(npcLife.storyTree.getTimeline(req.params.name));
});

app.get('/api/story/day/:day', (req, res) => {
  initNPCLife();
  res.json({ events: npcLife.storyTree.getByDay(parseInt(req.params.day)) });
});

// Add player choice to story tree
app.post('/api/story/choice', (req, res) => {
  initNPCLife();
  const { title, description, options, chosenIndex } = req.body;
  const result = npcLife.storyTree.addChoice({
    title, description,
    day: npcLife.worldDay,
    options: options || [
      { title: 'Option A', description: 'First choice' },
      { title: 'Option B', description: 'Second choice' },
    ],
    chosenIndex: chosenIndex || 0,
    participants: ['player'],
  });
  res.json(result);
});

// ===== ORIGINS & DISABILITIES REFERENCE =====

app.get('/api/reference/origins', (req, res) => {
  res.json({ origins: Object.entries(biogen.ORIGINS).map(([key, o]) => ({ key, name: o.name, atmosphere: o.atmosphere, culturalTraits: o.culturalTraits, physiology: o.physiology })) });
});

app.get('/api/reference/disabilities', (req, res) => {
  res.json({ disabilities: Object.entries(biogen.DISABILITIES).map(([key, d]) => ({ key, name: d.name, description: d.description, behaviorChanges: d.behaviorChanges })) });
});

// ===== SHADOW SYSTEM API =====

// Get all shadows (enemies with grudges)
app.get('/api/shadow/all', (req, res) => {
  res.json({ shadows: shadow.getAllShadows() });
});

// Get specific shadow info
app.get('/api/shadow/:npcId', (req, res) => {
  const info = shadow.getShadowInfo(req.params.npcId);
  if (!info) return res.json({ isShadow: false, encounters: 0 });
  res.json(info);
});

// Record NPC death with kill method (fire, sword, poison, etc.)
app.post('/api/shadow/kill', (req, res) => {
  const { npcId, killMethod, day } = req.body;
  const result = shadow.processNPCDeath(npcId, killMethod || 'sword', day || gameState.day);

  // Story tree
  initNPCLife();
  const npc = npcLife.npcs.get(npcId);
  if (result.cheatedDeath) {
    npcLife.storyTree.addEvent({
      title: `${npc?.name || npcId} "dies"... but will return`,
      description: `Killed by ${killMethod || 'sword'}. ${result.description}. Will return in ${result.returnsIn}.`,
      day: gameState.day,
      participants: [npc?.name || npcId, 'player'],
      category: 'shadow_death_cheat',
    });
  } else {
    npcLife.storyTree.addDeath({
      npcName: npc?.name || npcId,
      killedBy: 'player',
      reason: `Permanently killed by ${killMethod || 'sword'}`,
      day: gameState.day,
    });
  }

  res.json(result);
});

// Record player death to NPC
app.post('/api/shadow/player-death', (req, res) => {
  const { npcId } = req.body;
  const result = shadow.processPlayerDeath(npcId, gameState.day);
  res.json(result);
});

// Check for returning shadows
app.get('/api/shadow/returns', (req, res) => {
  const returning = shadow.checkReturns(gameState.day);
  res.json({ returning, count: returning.length });
});

// Get encounter dialogue for NPC
app.get('/api/shadow/:npcId/dialogue', (req, res) => {
  initNPCLife();
  const npc = npcLife.npcs.get(req.params.npcId);
  const dialogue = shadow.generateEncounterDialogue(req.params.npcId, npc?.name || 'Unknown');
  const info = shadow.getShadowInfo(req.params.npcId);
  res.json({ dialogue, shadowInfo: info });
});

// Trigger power struggle in faction
app.post('/api/shadow/power-struggle', (req, res) => {
  const event = shadow.triggerPowerStruggle();
  initNPCLife();
  npcLife.storyTree.addEvent({
    title: `Power Struggle: ${event.type}`,
    description: event.description,
    day: gameState.day,
    participants: [],
    category: 'faction_event',
  });
  res.json(event);
});

// ===== WORLD SYSTEMS API =====

// --- Vehicles ---
app.get('/api/vehicles', (req, res) => res.json({ vehicles: Array.from(vehicles.vehicles.values()), types: Object.entries(worldSys.VEHICLE_TYPES).map(([k, v]) => ({ key: k, ...v })) }));
app.post('/api/vehicles/create', (req, res) => { const v = vehicles.createVehicle(req.body.type, req.body.ownerId); res.json(v || { error: 'Invalid type' }); });
app.post('/api/vehicles/:id/fuel', (req, res) => res.json(vehicles.fuelVehicle(req.params.id, req.body.coins || 1) || { error: 'Not found' }));
app.post('/api/vehicles/:id/drive', (req, res) => res.json(vehicles.driveCheck(req.params.id, req.body.dexterity || 14, req.body.proficient)));

// --- Deals ---
app.get('/api/deals', (req, res) => res.json({ active: deals.getActiveDeals(), all: deals.getAllDeals() }));
app.post('/api/deals/create', (req, res) => res.json(deals.createDeal(req.body)));
app.post('/api/deals/:id/complete-task', (req, res) => res.json(deals.completeTask(req.params.id, req.body.taskIndex) || { error: 'Not found' }));
app.post('/api/deals/:id/break', (req, res) => res.json(deals.breakDeal(req.params.id) || { error: 'Not found' }));

// --- Party ---
app.get('/api/party', (req, res) => res.json(party.getState()));
app.post('/api/party/add', (req, res) => res.json({ members: party.addMember(req.body) }));
app.post('/api/party/remove', (req, res) => res.json({ members: party.removeMember(req.body.id) }));
app.post('/api/party/role', (req, res) => res.json(party.assignRole(req.body.id, req.body.role)));
app.post('/api/party/travel', (req, res) => res.json(party.travel(req.body.destination, req.body.distance, req.body.hazards)));

// --- Hazards ---
app.get('/api/hazards', (req, res) => res.json({ hazards: Object.entries(worldSys.HAZARDS).map(([k, h]) => ({ key: k, ...h })) }));
app.post('/api/hazards/encounter', (req, res) => {
  const hazard = worldSys.HAZARDS[req.body.hazardKey];
  if (!hazard) return res.json({ error: 'Unknown hazard' });
  const d20 = randomInt(1, 20);
  const ability = hazard.save;
  const abilityScore = req.body.abilityScore || 10;
  const mod = Math.floor((abilityScore - 10) / 2);
  const total = d20 + mod;
  const success = total >= hazard.dc;
  let mutation = null;
  if (!success && hazard.mutationChance && Math.random() < hazard.mutationChance) mutation = worldSys.rollMutation();
  res.json({ hazard: hazard.name, d20, total, dc: hazard.dc, save: ability, success, effect: success ? 'You resist!' : hazard.onFail, damage: success ? 0 : hazard.damage, mutation, breakdown: `${d20} + ${mod} (${ability}) = ${total} vs DC ${hazard.dc}` });
});

// --- Mutations ---
app.get('/api/mutations', (req, res) => res.json({ mutations: worldSys.MUTATIONS }));
app.post('/api/mutations/roll', (req, res) => res.json(worldSys.rollMutation()));

// --- Soul Coins ---
app.get('/api/soul-coins', (req, res) => res.json(worldSys.SOUL_COIN_EFFECTS));

// --- River Styx ---
app.post('/api/river-styx', (req, res) => res.json(worldSys.riverStyxEffect(req.body.intScore || 10, req.body.amount || 'splash')));

function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

// ===== ADVANCED SYSTEMS API =====

// --- Puzzles ---
app.get('/api/puzzles', (req, res) => res.json({ puzzles: advSys.PUZZLES.map(p => ({ id: p.id, title: p.title, type: p.type, dc: p.dc })), solved: puzzles.solvedPuzzles }));
app.get('/api/puzzles/random', (req, res) => { const p = puzzles.getRandomPuzzle(); res.json({ id: p.id, title: p.title, description: p.description, type: p.type }); });
app.post('/api/puzzles/:id/start', (req, res) => res.json(puzzles.startPuzzle(req.params.id) || { error: 'Puzzle not found' }));
app.post('/api/puzzles/:id/solve', (req, res) => res.json(puzzles.attemptSolve(req.params.id, req.body.answer, req.body.skillBonus || 0)));
app.get('/api/puzzles/:id/hint', (req, res) => res.json({ hint: puzzles.getHint(req.params.id) || 'No active puzzle' }));

// --- Artifacts ---
app.get('/api/artifacts', (req, res) => res.json({ artifacts: Object.entries(advSys.ARTIFACTS).map(([k, a]) => ({ key: k, ...a })) }));
app.get('/api/artifacts/:key', (req, res) => { const a = advSys.ARTIFACTS[req.params.key]; res.json(a || { error: 'Not found' }); });

// --- Boss Encounters ---
app.get('/api/bosses', (req, res) => res.json({ bosses: Object.entries(advSys.BOSS_TEMPLATES).map(([k, b]) => ({ key: k, name: b.name, cr: b.cr, hp: b.hp, ac: b.ac, description: b.description })) }));
app.post('/api/boss/start', (req, res) => { activeBoss = new advSys.BossEncounter(req.body.bossKey); res.json(activeBoss ? activeBoss.getState() : { error: 'Invalid boss' }); });
app.get('/api/boss/state', (req, res) => res.json(activeBoss ? activeBoss.getState() : { active: false }));
app.post('/api/boss/damage', (req, res) => { if (!activeBoss) return res.json({ error: 'No active boss' }); res.json(activeBoss.takeDamage(req.body.amount || 0)); });
app.post('/api/boss/legendary', (req, res) => { if (!activeBoss) return res.json({ error: 'No active boss' }); res.json(activeBoss.useLegendaryAction(req.body.actionIndex || 0)); });
app.post('/api/boss/new-round', (req, res) => { if (!activeBoss) return res.json({ error: 'No active boss' }); res.json(activeBoss.newRound()); });

// --- Companions ---
app.get('/api/companions', (req, res) => res.json({ active: companions.getActive(), available: Object.entries(advSys.SUMMONS).map(([k, s]) => ({ key: k, ...s })) }));
app.post('/api/companions/summon', (req, res) => { const c = companions.summon(req.body.creature, req.body.summoner || 'player', req.body.name); res.json(c || { error: 'Unknown creature' }); });
app.post('/api/companions/bag-of-tricks', (req, res) => res.json(companions.bagOfTricks()));
app.post('/api/companions/:id/dismiss', (req, res) => { companions.dismiss(req.params.id); res.json({ dismissed: true }); });

// --- Exploration ---
app.get('/api/exploration/actions', (req, res) => res.json({ actions: Object.entries(advSys.EXPLORATION_ACTIONS).map(([k, a]) => ({ key: k, ...a })) }));
app.post('/api/exploration/action', (req, res) => {
  const action = advSys.EXPLORATION_ACTIONS[req.body.actionKey];
  if (!action) return res.json({ error: 'Unknown action' });
  const d20 = randomInt(1, 20);
  const skillBonus = req.body.skillBonus || 0;
  const total = d20 + skillBonus;
  const success = action.dc === 0 || total >= action.dc;
  res.json({ action: action.name, d20, total, dc: action.dc, success, description: action.description, result: success ? 'You find something!' : 'Nothing stands out.', breakdown: `${d20} + ${skillBonus} = ${total} vs DC ${action.dc}` });
});

// --- Rival Parties ---
app.get('/api/rivals', (req, res) => res.json({ rivals: advSys.RIVAL_PARTIES }));

// ===== EDITOR API =====

// Get all editable data
app.get('/api/editor/world', (req, res) => res.json(world));
app.get('/api/editor/npcs', (req, res) => res.json(npcsData));
app.get('/api/editor/events', (req, res) => res.json(events));
app.get('/api/editor/scenarios', (req, res) => res.json(scenarios));

// Update NPC
app.put('/api/editor/npc/:id', (req, res) => {
  const idx = npcsData.npcs.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'NPC not found' });
  npcsData.npcs[idx] = { ...npcsData.npcs[idx], ...req.body };
  fs.writeFileSync(path.join(worldsDir, 'npcs.json'), JSON.stringify(npcsData, null, 2));
  res.json(npcsData.npcs[idx]);
});

// Create NPC
app.post('/api/editor/npc', (req, res) => {
  const npc = { id: `npc-${Date.now()}`, ...req.body };
  npcsData.npcs.push(npc);
  fs.writeFileSync(path.join(worldsDir, 'npcs.json'), JSON.stringify(npcsData, null, 2));
  res.json(npc);
});

// Delete NPC
app.delete('/api/editor/npc/:id', (req, res) => {
  const idx = npcsData.npcs.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'NPC not found' });
  npcsData.npcs.splice(idx, 1);
  fs.writeFileSync(path.join(worldsDir, 'npcs.json'), JSON.stringify(npcsData, null, 2));
  res.json({ deleted: true });
});

// Update Location
app.put('/api/editor/location/:id', (req, res) => {
  const idx = world.locations.findIndex(l => l.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Location not found' });
  world.locations[idx] = { ...world.locations[idx], ...req.body };
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json(world.locations[idx]);
});

// Create Location
app.post('/api/editor/location', (req, res) => {
  const loc = { id: `loc-${Date.now()}`, ...req.body };
  world.locations.push(loc);
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json(loc);
});

// Delete Location
app.delete('/api/editor/location/:id', (req, res) => {
  const idx = world.locations.findIndex(l => l.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Location not found' });
  world.locations.splice(idx, 1);
  world.connections = world.connections.filter(c => c.from !== req.params.id && c.to !== req.params.id);
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json({ deleted: true });
});

// Update Event
app.put('/api/editor/event/:id', (req, res) => {
  const idx = events.events.findIndex(e => e.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Event not found' });
  events.events[idx] = { ...events.events[idx], ...req.body };
  fs.writeFileSync(path.join(worldsDir, 'events.json'), JSON.stringify(events, null, 2));
  res.json(events.events[idx]);
});

// Create Event
app.post('/api/editor/event', (req, res) => {
  const evt = { id: `evt-${Date.now()}`, ...req.body };
  events.events.push(evt);
  fs.writeFileSync(path.join(worldsDir, 'events.json'), JSON.stringify(events, null, 2));
  res.json(evt);
});

// Delete Event
app.delete('/api/editor/event/:id', (req, res) => {
  const idx = events.events.findIndex(e => e.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Event not found' });
  events.events.splice(idx, 1);
  fs.writeFileSync(path.join(worldsDir, 'events.json'), JSON.stringify(events, null, 2));
  res.json({ deleted: true });
});

// Update Scenario
app.put('/api/editor/scenario/:index', (req, res) => {
  const idx = parseInt(req.params.index);
  if (idx < 0 || idx >= scenarios.length) return res.status(404).json({ error: 'Scenario not found' });
  scenarios[idx] = { ...scenarios[idx], ...req.body };
  fs.writeFileSync(path.join(worldsDir, 'scenarios.json'), JSON.stringify(scenarios, null, 2));
  res.json(scenarios[idx]);
});

// Create Scenario
app.post('/api/editor/scenario', (req, res) => {
  scenarios.push(req.body);
  fs.writeFileSync(path.join(worldsDir, 'scenarios.json'), JSON.stringify(scenarios, null, 2));
  res.json(req.body);
});

// Delete Scenario
app.delete('/api/editor/scenario/:index', (req, res) => {
  const idx = parseInt(req.params.index);
  if (idx < 0 || idx >= scenarios.length) return res.status(404).json({ error: 'Scenario not found' });
  scenarios.splice(idx, 1);
  fs.writeFileSync(path.join(worldsDir, 'scenarios.json'), JSON.stringify(scenarios, null, 2));
  res.json({ deleted: true });
});

// Update World metadata
app.put('/api/editor/world', (req, res) => {
  Object.assign(world, req.body);
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json(world);
});

// Agent Prompts - list all
app.get('/api/editor/prompts', (req, res) => {
  const promptsDir = path.join(__dirname, '..', 'backend', 'app', 'agents', 'prompts');
  const files = fs.readdirSync(promptsDir).filter(f => f.endsWith('.j2'));
  const prompts = files.map(f => ({
    name: f.replace('.j2', ''),
    filename: f,
    content: fs.readFileSync(path.join(promptsDir, f), 'utf-8'),
  }));
  res.json({ prompts });
});

// Agent Prompts - update
app.put('/api/editor/prompt/:name', (req, res) => {
  const promptsDir = path.join(__dirname, '..', 'backend', 'app', 'agents', 'prompts');
  const filePath = path.join(promptsDir, `${req.params.name}.j2`);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'Prompt not found' });
  fs.writeFileSync(filePath, req.body.content, 'utf-8');
  res.json({ saved: true, name: req.params.name });
});

// Connections management
app.get('/api/editor/connections', (req, res) => res.json(world.connections));
app.post('/api/editor/connection', (req, res) => {
  world.connections.push(req.body);
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json(req.body);
});
app.delete('/api/editor/connection', (req, res) => {
  const { from, to } = req.body;
  world.connections = world.connections.filter(c => !(c.from === from && c.to === to) && !(c.from === to && c.to === from));
  fs.writeFileSync(path.join(worldsDir, 'world.json'), JSON.stringify(world, null, 2));
  res.json({ deleted: true });
});

// Start server
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws/game' });
wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      if (msg.type === 'ping') ws.send(JSON.stringify({ type: 'pong' }));
    } catch {}
  });
});

const PORT = 8000;
server.listen(PORT, () => {
  console.log(`Mock DND server running on http://localhost:${PORT}`);
  console.log(`WebSocket on ws://localhost:${PORT}/ws/game`);
  console.log(`World: ${world.name} | ${world.locations.length} locations | ${npcsData.npcs.length} NPCs`);
});
