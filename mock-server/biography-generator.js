// ============================================
// NPC Biography Generator
// Generates childhood, formative events, origin effects, physical state
// ============================================

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function randomFloat(min, max) { return min + Math.random() * (max - min); }

// --- ORIGIN SYSTEM (planet/universe/realm) ---
const ORIGINS = {
  medieval_earth: {
    name: 'Medieval Earth', atmosphere: 'standard',
    psychModifiers: { emotionalStability: 0, empathy: 0, willpower: 0, stressLevel: 0 },
    culturalTraits: ['superstitious', 'community-bound', 'hierarchical', 'religious'],
    physiology: 'standard human',
    fears: ['plague', 'famine', 'dark_forest', 'divine_punishment'],
    values: ['honor', 'family', 'faith', 'land'],
  },
  nitrogen_world: {
    name: 'Nitrogen Dominance World', atmosphere: 'high nitrogen, low oxygen',
    psychModifiers: { emotionalStability: 0.15, empathy: 0.1, willpower: -0.1, stressLevel: -0.1 },
    culturalTraits: ['contemplative', 'slow-paced', 'philosophical', 'patient'],
    physiology: 'slower metabolism, deeper breathing, blue-tinted skin',
    fears: ['haste', 'sudden_change', 'oxygen_toxicity'],
    values: ['patience', 'wisdom', 'stillness', 'deep_bonds'],
  },
  high_gravity: {
    name: 'High Gravity World', atmosphere: '2.5x Earth gravity',
    psychModifiers: { emotionalStability: 0.1, empathy: -0.1, willpower: 0.2, stressLevel: 0.1 },
    culturalTraits: ['stoic', 'physically_dominant', 'pragmatic', 'territorial'],
    physiology: 'stocky build, dense bones, powerful muscles, shorter stature',
    fears: ['falling', 'weakness', 'loss_of_ground'],
    values: ['strength', 'endurance', 'stability', 'conquest'],
  },
  low_gravity: {
    name: 'Low Gravity World', atmosphere: '0.3x Earth gravity',
    psychModifiers: { emotionalStability: -0.1, empathy: 0.1, willpower: -0.1, stressLevel: 0.05 },
    culturalTraits: ['ethereal', 'artistic', 'fragile', 'dreamlike'],
    physiology: 'tall, slender, fragile bones, large eyes',
    fears: ['crushing_weight', 'confinement', 'violence'],
    values: ['beauty', 'flight', 'art', 'freedom'],
  },
  toxic_atmosphere: {
    name: 'Toxic Atmosphere World', atmosphere: 'sulfuric compounds, acid rain',
    psychModifiers: { emotionalStability: -0.15, empathy: -0.15, willpower: 0.2, stressLevel: 0.2 },
    culturalTraits: ['paranoid', 'resourceful', 'isolationist', 'survivalist'],
    physiology: 'scarred skin, enhanced filtration organs, reduced lifespan',
    fears: ['exposure', 'outsiders', 'contamination', 'trust'],
    values: ['survival', 'purity', 'self-reliance', 'suspicion'],
  },
  eternal_night: {
    name: 'Eternal Night World', atmosphere: 'no sunlight, bioluminescent ecosystem',
    psychModifiers: { emotionalStability: -0.1, empathy: 0.05, willpower: 0.05, stressLevel: 0.15 },
    culturalTraits: ['secretive', 'perceptive', 'nocturnal', 'whisper-culture'],
    physiology: 'large pupils, pale skin, enhanced hearing, light sensitivity',
    fears: ['bright_light', 'exposure', 'being_seen', 'loud_sounds'],
    values: ['secrecy', 'listening', 'shadow', 'subtlety'],
  },
  water_world: {
    name: 'Water World', atmosphere: 'underwater civilization, air pockets',
    psychModifiers: { emotionalStability: -0.05, empathy: 0.15, willpower: 0, stressLevel: -0.05 },
    culturalTraits: ['fluid', 'collective', 'empathic', 'migratory'],
    physiology: 'webbed digits, gill-like organs, iridescent skin, fluid movement',
    fears: ['drought', 'stillness', 'isolation', 'surface_world'],
    values: ['flow', 'community', 'adaptation', 'current'],
  },
  fey_realm: {
    name: 'Feywild', atmosphere: 'chaotic magic, time distortion',
    psychModifiers: { emotionalStability: -0.2, empathy: 0.1, willpower: -0.15, stressLevel: -0.05 },
    culturalTraits: ['chaotic', 'playful', 'cruel_kindness', 'time_blind'],
    physiology: 'pointed ears, color-shifting eyes, ageless appearance',
    fears: ['iron', 'oaths_broken', 'boredom', 'mortality'],
    values: ['play', 'beauty', 'trickery', 'nature'],
  },
  underdark: {
    name: 'Underdark', atmosphere: 'underground, fungal ecosystem, no sky',
    psychModifiers: { emotionalStability: 0.05, empathy: -0.2, willpower: 0.15, stressLevel: 0.15 },
    culturalTraits: ['hierarchical', 'ruthless', 'cunning', 'matriarchal'],
    physiology: 'darkvision, pale skin, enhanced tremorsense',
    fears: ['open_sky', 'sunlight', 'surface_diseases', 'powerlessness'],
    values: ['power', 'cunning', 'loyalty_through_fear', 'dominance'],
  },
  astral_plane: {
    name: 'Astral Plane', atmosphere: 'thought-substance, timeless',
    psychModifiers: { emotionalStability: 0.2, empathy: 0, willpower: 0.1, stressLevel: -0.2 },
    culturalTraits: ['detached', 'intellectual', 'abstract', 'immortal_perspective'],
    physiology: 'translucent, no biological needs, thought-based form',
    fears: ['emotion', 'attachment', 'physical_form', 'entropy'],
    values: ['knowledge', 'transcendence', 'order', 'thought'],
  },
};

// --- PHYSICAL DISABILITIES ---
const DISABILITIES = {
  blindness: {
    name: 'Blind', description: 'Cannot see since birth or accident',
    psychEffects: { empathy: 0.1, emotionalStability: -0.05, willpower: 0.1 },
    behaviorChanges: ['heightened hearing', 'trusts touch over words', 'anxious in new spaces', 'memorizes layouts'],
    speechModifier: 'mentions sounds, textures, smells instead of visuals',
    goalModifier: 'seeks guides, avoids unfamiliar terrain, values trusted companions',
    combatModifier: 'disadvantage on attack rolls, advantage on hearing-based perception',
  },
  deafness: {
    name: 'Deaf', description: 'Cannot hear',
    psychEffects: { empathy: -0.05, emotionalStability: -0.1, willpower: 0.05 },
    behaviorChanges: ['reads lips and body language', 'suspicious of whispers', 'prefers written communication'],
    speechModifier: 'speaks loudly or in sign, misinterprets tone',
    goalModifier: 'values visual cues, avoids crowds, seeks quiet allies',
    combatModifier: 'cannot be surprised by sounds, disadvantage on verbal deception',
  },
  lost_arm: {
    name: 'Lost Arm', description: 'Missing one arm',
    psychEffects: { emotionalStability: -0.1, willpower: 0.15 },
    behaviorChanges: ['compensates with remaining arm', 'phantom pain episodes', 'avoids pity'],
    speechModifier: 'defensive about disability, proves capability aggressively',
    goalModifier: 'seeks prosthetic or magical restoration, proves worth through action',
    combatModifier: 'cannot dual-wield, disadvantage on grapple, adapted fighting style',
  },
  lost_leg: {
    name: 'Lost Leg', description: 'Missing one leg, uses crutch or prosthetic',
    psychEffects: { emotionalStability: -0.1, willpower: 0.1, stressLevel: 0.1 },
    behaviorChanges: ['limited mobility', 'strategic thinker', 'avoids running situations'],
    speechModifier: 'resents being underestimated, tactical mind compensates for body',
    goalModifier: 'seeks mount or magical movement, plans carefully',
    combatModifier: 'half movement speed, cannot dodge, advantage on seated/mounted combat',
  },
  chronic_pain: {
    name: 'Chronic Pain', description: 'Constant pain from old wound or condition',
    psychEffects: { emotionalStability: -0.15, empathy: 0.1, willpower: -0.1, stressLevel: 0.2 },
    behaviorChanges: ['irritable in mornings', 'seeks remedies', 'understands suffering', 'short temper'],
    speechModifier: 'winces mid-sentence, bitter about health, empathetic to others in pain',
    goalModifier: 'finding cure is secondary goal, manages pain daily',
    combatModifier: 'disadvantage on concentration, may freeze during pain flares',
  },
  scarring: {
    name: 'Severe Scarring', description: 'Disfiguring scars on face/body',
    psychEffects: { emotionalStability: -0.1, empathy: -0.05 },
    behaviorChanges: ['avoids mirrors', 'wears concealing clothing', 'either withdrawn or intimidating'],
    speechModifier: 'either avoids eye contact or uses scars to intimidate',
    goalModifier: 'seeks acceptance or uses fear, avoids social gatherings',
    combatModifier: 'advantage on intimidation checks',
  },
  mental_illness: {
    name: 'Mental Illness', description: 'Periodic episodes of altered perception',
    psychEffects: { emotionalStability: -0.3, empathy: 0.05, willpower: -0.1, stressLevel: 0.2 },
    behaviorChanges: ['unpredictable episodes', 'talks to unseen things', 'brilliant moments of clarity'],
    speechModifier: 'occasionally incoherent, then suddenly profound, references things others cannot see',
    goalModifier: 'seeks stability, fears own mind, may embrace visions as gift',
    combatModifier: 'random advantage/disadvantage based on episode state',
  },
  none: {
    name: 'No Disability', description: 'Physically healthy',
    psychEffects: {}, behaviorChanges: [], speechModifier: '', goalModifier: '', combatModifier: '',
  },
};

// --- CHILDHOOD EVENT TEMPLATES ---
const CHILDHOOD_TEMPLATES = {
  happy: [
    { event: 'Grew up in a loving family with {parent_count} siblings', impact: 'secure attachment', psychEffect: { emotionalStability: 0.1, empathy: 0.1 } },
    { event: 'Was the favorite child, showered with praise', impact: 'high self-esteem, possible narcissism', psychEffect: { willpower: 0.05, empathy: -0.05 } },
    { event: 'Had a beloved mentor who taught them {skill}', impact: 'strong sense of purpose', psychEffect: { willpower: 0.1 } },
  ],
  traumatic: [
    { event: 'Witnessed parent murdered at age {age}', impact: 'PTSD, trust issues, hypervigilance', psychEffect: { emotionalStability: -0.2, empathy: -0.1, stressLevel: 0.3 } },
    { event: 'Abandoned by parents, raised by {caretaker}', impact: 'attachment disorder, self-reliance', psychEffect: { emotionalStability: -0.15, willpower: 0.1, empathy: -0.1 } },
    { event: 'Severe bullying throughout childhood', impact: 'low self-esteem or compensatory aggression', psychEffect: { emotionalStability: -0.1, stressLevel: 0.15 } },
    { event: 'Lost everything in a fire/flood/raid at age {age}', impact: 'loss anxiety, hoarding tendency', psychEffect: { emotionalStability: -0.1, stressLevel: 0.15 } },
    { event: 'Was enslaved as a child, escaped at age {age}', impact: 'authority issues, fierce independence', psychEffect: { willpower: 0.2, empathy: -0.1, emotionalStability: -0.1 } },
  ],
  formative: [
    { event: 'First killed someone in self-defense at age {age}', impact: 'guilt or desensitization', psychEffect: { emotionalStability: -0.1 } },
    { event: 'Fell deeply in love, was heartbroken', impact: 'romantic idealism or cynicism', psychEffect: { empathy: 0.1, emotionalStability: -0.05 } },
    { event: 'Discovered a hidden talent for {skill}', impact: 'sense of uniqueness', psychEffect: { willpower: 0.05 } },
    { event: 'Betrayed by a close friend', impact: 'trust issues, loyalty obsession', psychEffect: { empathy: -0.1, stressLevel: 0.1 } },
    { event: 'Saved someone\'s life, became a local hero', impact: 'savior complex or humility', psychEffect: { empathy: 0.1, willpower: 0.05 } },
    { event: 'Suffered a near-death experience', impact: 'either fearlessness or chronic anxiety', psychEffect: { emotionalStability: -0.1, willpower: 0.1 } },
    { event: 'Traveled far from home for the first time', impact: 'wanderlust or homesickness', psychEffect: {} },
  ],
};

const PARENT_TYPES = [
  { type: 'loving', description: 'warm, supportive parents', psychEffect: { emotionalStability: 0.1, empathy: 0.1 } },
  { type: 'absent', description: 'parents were never around', psychEffect: { emotionalStability: -0.1, willpower: 0.05 } },
  { type: 'abusive', description: 'physically/emotionally abusive parent', psychEffect: { emotionalStability: -0.2, empathy: -0.1, stressLevel: 0.2 } },
  { type: 'strict', description: 'rigid authoritarian parents', psychEffect: { willpower: 0.1, emotionalStability: -0.05 } },
  { type: 'overprotective', description: 'smothering, controlling parents', psychEffect: { willpower: -0.1, emotionalStability: -0.05 } },
  { type: 'orphan', description: 'no parents, raised on the streets or in an institution', psychEffect: { willpower: 0.15, empathy: -0.1, stressLevel: 0.15 } },
];

const SKILLS = ['swordsmanship', 'herbalism', 'smithing', 'thievery', 'magic', 'healing', 'hunting', 'storytelling', 'diplomacy', 'carpentry', 'cooking', 'music'];
const CARETAKERS = ['a stern uncle', 'the village elder', 'a traveling merchant', 'temple monks', 'a pack of wild dogs', 'a hermit wizard', 'street urchins', 'a kindly innkeeper'];

function fillTemplate(template, data = {}) {
  let text = template;
  text = text.replace('{age}', data.age || randomInt(5, 14));
  text = text.replace('{parent_count}', data.parentCount || randomInt(1, 5));
  text = text.replace('{skill}', data.skill || randomChoice(SKILLS));
  text = text.replace('{caretaker}', data.caretaker || randomChoice(CARETAKERS));
  return text;
}

// --- BIOGRAPHY GENERATION ---
function generateBiography(options = {}) {
  const originKey = options.origin || 'medieval_earth';
  const origin = ORIGINS[originKey] || ORIGINS.medieval_earth;
  const age = options.age || randomInt(18, 65);
  const disabilityKey = options.disability || (Math.random() > 0.8 ? randomChoice(Object.keys(DISABILITIES).filter(k => k !== 'none')) : 'none');
  const disability = DISABILITIES[disabilityKey];

  // Parents
  const parentType = options.parentType ? PARENT_TYPES.find(p => p.type === options.parentType) : randomChoice(PARENT_TYPES);

  // Childhood events (2-4 events)
  const childhoodCount = randomInt(2, 4);
  const childhood = [];
  const usedCategories = new Set();

  for (let i = 0; i < childhoodCount; i++) {
    let category;
    if (i === 0 && parentType.type === 'abusive') category = 'traumatic';
    else if (i === 0 && parentType.type === 'loving') category = 'happy';
    else category = randomChoice(['happy', 'traumatic', 'formative']);

    if (usedCategories.has(category) && i > 0) {
      category = randomChoice(['happy', 'traumatic', 'formative'].filter(c => !usedCategories.has(c))) || category;
    }
    usedCategories.add(category);

    const templates = CHILDHOOD_TEMPLATES[category];
    const template = randomChoice(templates);
    childhood.push({
      age: randomInt(3, 14),
      event: fillTemplate(template.event),
      impact: template.impact,
      psychEffect: template.psychEffect,
      category,
    });
  }
  childhood.sort((a, b) => a.age - b.age);

  // Formative events (adolescence)
  const formativeEvents = [];
  const formativeCount = randomInt(1, 3);
  for (let i = 0; i < formativeCount; i++) {
    const template = randomChoice(CHILDHOOD_TEMPLATES.formative);
    formativeEvents.push({
      age: randomInt(14, age - 2),
      event: fillTemplate(template.event, { age: randomInt(14, 20) }),
      impact: template.impact,
      psychEffect: template.psychEffect,
    });
  }
  formativeEvents.sort((a, b) => a.age - b.age);

  // Disability origin story
  let disabilityStory = null;
  if (disabilityKey !== 'none') {
    const congenital = Math.random() > 0.5;
    if (congenital) {
      disabilityStory = {
        type: 'congenital',
        age: 0,
        description: `Born with ${disability.name.toLowerCase()}. ${disability.description}.`,
        impact: `Shaped entire worldview. ${disability.goalModifier}`,
      };
    } else {
      const injuryAge = randomInt(8, age - 5);
      const causes = ['a battle wound', 'an accident', 'a curse', 'a disease', 'an act of violence', 'a magical experiment gone wrong'];
      disabilityStory = {
        type: 'acquired',
        age: injuryAge,
        cause: randomChoice(causes),
        description: `Lost ${disability.name.toLowerCase()} at age ${injuryAge} due to ${randomChoice(causes)}.`,
        impact: `Life divided into before and after. ${disability.goalModifier}`,
      };
    }
  }

  // Origin-specific childhood modifier
  const originChildhood = [];
  if (originKey !== 'medieval_earth') {
    originChildhood.push({
      event: `Grew up on ${origin.name}. ${origin.physiology}. Culture values: ${origin.culturalTraits.join(', ')}.`,
      impact: `Fundamental worldview shaped by ${origin.name} environment`,
      fears: origin.fears,
    });
    if (originKey === 'nitrogen_world') {
      originChildhood.push({ event: 'Learned patience through the slow rhythms of nitrogen-rich air. Quick actions feel foreign and dangerous.', impact: 'Deep contemplation, slow to anger, slow to trust' });
    } else if (originKey === 'eternal_night') {
      originChildhood.push({ event: 'Never saw sunlight. Learned the world through sound and bioluminescent patterns.', impact: 'Heightened non-visual perception, fear of brightness' });
    } else if (originKey === 'high_gravity') {
      originChildhood.push({ event: 'Every step was effort. Learned that weakness means death. The ground is both enemy and foundation.', impact: 'Physical determination, distrust of the "light" and carefree' });
    }
  }

  // Cumulative psych effects from biography
  const cumulativePsychEffect = { emotionalStability: 0, empathy: 0, willpower: 0, stressLevel: 0 };
  const allEffects = [
    parentType.psychEffect,
    ...childhood.map(c => c.psychEffect),
    ...formativeEvents.map(f => f.psychEffect),
    disability.psychEffects,
    origin.psychModifiers,
  ];
  for (const effect of allEffects) {
    for (const [key, val] of Object.entries(effect || {})) {
      cumulativePsychEffect[key] = (cumulativePsychEffect[key] || 0) + (val || 0);
    }
  }

  return {
    origin: { key: originKey, ...origin },
    age,
    parents: parentType,
    childhood,
    formativeEvents,
    originChildhood,
    disability: { key: disabilityKey, ...disability, story: disabilityStory },
    cumulativePsychEffect,
    // Narrative summary
    summary: generateNarrativeSummary({ parentType, childhood, formativeEvents, origin, disability, disabilityStory, age }),
  };
}

function generateNarrativeSummary({ parentType, childhood, formativeEvents, origin, disability, disabilityStory, age }) {
  let summary = '';

  // Origin
  if (origin.name !== 'Medieval Earth') {
    summary += `Born on ${origin.name}, a world of ${origin.atmosphere}. `;
  }

  // Parents
  summary += `Raised by ${parentType.description}. `;

  // Key childhood event
  if (childhood.length > 0) {
    const key = childhood.find(c => c.category === 'traumatic') || childhood[0];
    summary += `${key.event} (age ${key.age}). `;
  }

  // Disability
  if (disabilityStory) {
    summary += `${disabilityStory.description} `;
  }

  // Formative
  if (formativeEvents.length > 0) {
    summary += `${formativeEvents[0].event} (age ${formativeEvents[0].age}). `;
  }

  summary += `Now ${age} years old.`;
  return summary;
}

// --- INJURY SYSTEM (in-game) ---
function applyGameInjury(biography, injury) {
  const updated = { ...biography };
  const injuryEffects = {
    lost_eye: { disability: 'partial_blindness', psychEffect: { emotionalStability: -0.1, willpower: 0.1 }, narrative: 'lost an eye in combat' },
    broken_bones: { disability: 'chronic_pain', psychEffect: { emotionalStability: -0.05, stressLevel: 0.1 }, narrative: 'suffered broken bones' },
    burn_scars: { disability: 'scarring', psychEffect: { emotionalStability: -0.1, empathy: -0.05 }, narrative: 'was badly burned' },
    severed_hand: { disability: 'lost_arm', psychEffect: { willpower: 0.15, emotionalStability: -0.15 }, narrative: 'lost a hand' },
    poisoned: { disability: 'chronic_pain', psychEffect: { stressLevel: 0.15, emotionalStability: -0.1 }, narrative: 'was poisoned, lasting damage to organs' },
    psychological_trauma: { disability: 'mental_illness', psychEffect: { emotionalStability: -0.25, stressLevel: 0.25 }, narrative: 'suffered severe psychological trauma' },
    cursed: { disability: 'mental_illness', psychEffect: { emotionalStability: -0.2, stressLevel: 0.2, empathy: -0.1 }, narrative: 'was cursed, mind partially fractured' },
  };

  const effect = injuryEffects[injury.type] || injuryEffects.broken_bones;

  // Add to formative events
  updated.formativeEvents = [...(updated.formativeEvents || []), {
    age: updated.age,
    event: `${effect.narrative} during ${injury.context || 'an encounter'}`,
    impact: `Life changed dramatically. ${DISABILITIES[effect.disability]?.goalModifier || ''}`,
    psychEffect: effect.psychEffect,
    gameDay: injury.day,
  }];

  // Update disability if worse
  if (updated.disability.key === 'none' || effect.disability === 'mental_illness') {
    updated.disability = { key: effect.disability, ...DISABILITIES[effect.disability], story: {
      type: 'acquired_in_game',
      age: updated.age,
      cause: injury.context || 'combat',
      description: effect.narrative,
      gameDay: injury.day,
    }};
  }

  // Update cumulative effects
  for (const [key, val] of Object.entries(effect.psychEffect)) {
    updated.cumulativePsychEffect[key] = (updated.cumulativePsychEffect[key] || 0) + val;
  }

  return updated;
}

module.exports = {
  ORIGINS, DISABILITIES, CHILDHOOD_TEMPLATES, PARENT_TYPES,
  generateBiography, applyGameInjury, generateNarrativeSummary,
};
