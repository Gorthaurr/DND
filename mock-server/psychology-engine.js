// ============================================
// D&D NPC Psychology Engine
// Based on: Leonhard, Lichko, Ganushkin, Jung, Maslow, Freud, Berne
// ============================================

// --- LEONHARD ACCENTUATIONS (10 types) ---
const LEONHARD_TYPES = {
  demonstrative: {
    name: 'Demonstrative (Hysteric)',
    traits: ['attention-seeking', 'theatrical', 'emotional', 'manipulative', 'vain'],
    emotionalStyle: 'dramatic swings, exaggerated reactions, public displays',
    socialBehavior: 'center of attention, charming but superficial, lies easily',
    drives: ['recognition', 'admiration', 'being special'],
    vulnerabilities: ['being ignored', 'criticism of appearance', 'anonymity'],
    speechStyle: 'dramatic, expressive, uses superlatives, interrupts to redirect attention',
    underStress: 'creates scenes, faints, threatens self-harm for attention',
    dndRole: 'bard, noble, merchant, entertainer',
  },
  stuck: {
    name: 'Stuck (Paranoid)',
    traits: ['suspicious', 'grudge-holding', 'rigid', 'ambitious', 'jealous'],
    emotionalStyle: 'slow to anger but never forgets, simmering resentment',
    socialBehavior: 'formal, distrustful, counts perceived slights, seeks justice',
    drives: ['justice', 'recognition of merit', 'control'],
    vulnerabilities: ['perceived betrayal', 'disrespect', 'being cheated'],
    speechStyle: 'formal, mentions past grievances, accusatory undertones',
    underStress: 'becomes paranoid, litigious, vengeful conspiracies',
    dndRole: 'judge, guard captain, tax collector, inquisitor',
  },
  pedantic: {
    name: 'Pedantic',
    traits: ['meticulous', 'indecisive', 'perfectionist', 'anxious', 'thorough'],
    emotionalStyle: 'chronic worry, guilt over imperfection, anxiety',
    socialBehavior: 'reliable but boring, follows rules rigidly, criticizes sloppiness',
    drives: ['order', 'correctness', 'avoiding mistakes'],
    vulnerabilities: ['chaos', 'time pressure', 'ambiguity'],
    speechStyle: 'precise, corrects others, lists details, hedges statements',
    underStress: 'paralyzed by indecision, obsessive checking, health anxiety',
    dndRole: 'scribe, librarian, clerk, healer',
  },
  excitable: {
    name: 'Excitable (Explosive)',
    traits: ['impulsive', 'irritable', 'aggressive', 'physical', 'instinctual'],
    emotionalStyle: 'explosive anger, quick to rage, physical expression',
    socialBehavior: 'domineering, settles disputes with fists, respects strength',
    drives: ['immediate gratification', 'dominance', 'physical pleasure'],
    vulnerabilities: ['provocation', 'authority', 'boredom'],
    speechStyle: 'blunt, crude, short sentences, curses, threatens',
    underStress: 'violence, destruction, substance abuse',
    dndRole: 'barbarian, thug, bouncer, warrior, blacksmith',
  },
  hyperthymic: {
    name: 'Hyperthymic',
    traits: ['optimistic', 'energetic', 'talkative', 'risk-taking', 'superficial'],
    emotionalStyle: 'perpetually cheerful, infectious enthusiasm, rarely sad',
    socialBehavior: 'life of the party, makes friends easily, unreliable with commitments',
    drives: ['fun', 'novelty', 'adventure', 'social connection'],
    vulnerabilities: ['boredom', 'routine', 'isolation', 'serious consequences'],
    speechStyle: 'fast, jumping between topics, jokes, plans grand adventures',
    underStress: 'reckless decisions, ignores danger, drinks more',
    dndRole: 'bard, tavern keeper, merchant, adventurer',
  },
  dysthymic: {
    name: 'Dysthymic',
    traits: ['pessimistic', 'serious', 'ethical', 'quiet', 'reliable'],
    emotionalStyle: 'chronic low mood, deep empathy for suffering, melancholic',
    socialBehavior: 'withdrawn, loyal to few, avoids gatherings, deeply thoughtful',
    drives: ['meaning', 'duty', 'preventing suffering'],
    vulnerabilities: ['loss', 'injustice', 'helplessness'],
    speechStyle: 'slow, thoughtful, talks about suffering, philosophical, sighs',
    underStress: 'withdrawal, despair, self-neglect, existential crisis',
    dndRole: 'priest, hermit, gravedigger, philosopher, healer',
  },
  anxious: {
    name: 'Anxious (Fearful)',
    traits: ['timid', 'self-doubting', 'avoidant', 'compliant', 'sensitive'],
    emotionalStyle: 'chronic fear, startles easily, imagines worst outcomes',
    socialBehavior: 'submissive, apologetic, avoids confrontation, needs reassurance',
    drives: ['safety', 'approval', 'avoiding conflict'],
    vulnerabilities: ['aggression', 'public humiliation', 'new situations'],
    speechStyle: 'quiet, hesitant, apologetic, seeks permission, stammers when scared',
    underStress: 'freezes, hides, develops physical symptoms (trembling, nausea)',
    dndRole: 'servant, apprentice, farmer, child',
  },
  emotive: {
    name: 'Emotive',
    traits: ['deeply feeling', 'compassionate', 'gentle', 'tearful', 'altruistic'],
    emotionalStyle: 'feels everything deeply, cries easily, both joy and sorrow intense',
    socialBehavior: 'devoted friend, takes on others pain, easily hurt, forgives quickly',
    drives: ['love', 'harmony', 'helping others', 'beauty'],
    vulnerabilities: ['cruelty', 'conflict', 'witnessing suffering'],
    speechStyle: 'warm, emotional, voice cracks, talks about feelings and others',
    underStress: 'weeps, takes blame, physical illness from emotional overload',
    dndRole: 'healer, nun, orphan caretaker, herbalist',
  },
  cyclothymic: {
    name: 'Cyclothymic',
    traits: ['mood-swinging', 'unpredictable', 'creative when high', 'paralyzed when low'],
    emotionalStyle: 'alternates between euphoria and depression in cycles',
    socialBehavior: 'inconsistent - charming and warm, then cold and withdrawn',
    drives: ['depends on phase - ambition when high, rest when low'],
    vulnerabilities: ['rejection during low phase', 'overwhelming demands'],
    speechStyle: 'varies dramatically - eloquent and fast vs monotone and slow',
    underStress: 'deeper swings, either reckless mania or complete shutdown',
    dndRole: 'artist, fortune teller, ranger, wizard',
  },
  exalted: {
    name: 'Exalted (Affective)',
    traits: ['ecstatic', 'passionate', 'dramatic emotions', 'inspired', 'volatile'],
    emotionalStyle: 'extreme emotional reactions to everything, from rapture to despair',
    socialBehavior: 'inspiring but exhausting, falls in love instantly, passionate about causes',
    drives: ['passion', 'beauty', 'inspiration', 'transcendence'],
    vulnerabilities: ['disappointment', 'ugliness', 'mediocrity'],
    speechStyle: 'exclamatory, poetic, uses metaphors, voice trembles with feeling',
    underStress: 'emotional collapse, dramatic declarations, impulsive actions',
    dndRole: 'paladin, prophet, romantic knight, poet',
  },
};

// --- LICHKO ACCENTUATIONS (11 types, adolescent focus but applicable) ---
const LICHKO_TYPES = {
  hyperthymic: { name: 'Hyperthymic', coreTraits: ['energetic', 'optimistic', 'scattered'], weakness: 'monotony and control' },
  cycloid: { name: 'Cycloid', coreTraits: ['alternating moods', 'productive then apathetic'], weakness: 'unpredictable emotions' },
  labile: { name: 'Labile', coreTraits: ['extremely mood-sensitive', 'reactive to small events'], weakness: 'emotional instability' },
  asthenic: { name: 'Asthenic-Neurotic', coreTraits: ['fatigable', 'irritable', 'hypochondriac'], weakness: 'exhaustion and illness anxiety' },
  sensitive: { name: 'Sensitive', coreTraits: ['shy', 'deeply moral', 'self-conscious'], weakness: 'unfair accusations' },
  psychasthenic: { name: 'Psychasthenic', coreTraits: ['anxious', 'indecisive', 'superstitious'], weakness: 'responsibility for others' },
  schizoid: { name: 'Schizoid', coreTraits: ['detached', 'inner fantasy world', 'emotionally cold'], weakness: 'forced intimacy' },
  epileptoid: { name: 'Epileptoid', coreTraits: ['explosive', 'controlling', 'jealous', 'meticulous'], weakness: 'loss of control' },
  hysteroid: { name: 'Hysteroid', coreTraits: ['theatrical', 'attention-seeking', 'egocentric'], weakness: 'being ignored' },
  unstable: { name: 'Unstable', coreTraits: ['hedonistic', 'easily led', 'lazy'], weakness: 'discipline' },
  conformist: { name: 'Conformist', coreTraits: ['follows crowd', 'conservative', 'adapts to environment'], weakness: 'isolation from group' },
};

// --- GANUSHKIN PSYCHOPATHIES (pathological extremes) ---
const GANUSHKIN_PSYCHOPATHIES = {
  cycloid: { name: 'Cycloid', description: 'Pathological mood swings between mania and depression', dangerLevel: 'medium' },
  asthenic: { name: 'Asthenic', description: 'Chronic weakness, hypersensitivity, exhaustion', dangerLevel: 'low' },
  schizoid: { name: 'Schizoid', description: 'Complete emotional detachment, bizarre thinking', dangerLevel: 'medium' },
  paranoid: { name: 'Paranoid', description: 'Pathological suspicion, persecution delusions, vengeful', dangerLevel: 'high' },
  epileptoid: { name: 'Epileptoid', description: 'Explosive rage episodes, cruelty, sadistic tendencies', dangerLevel: 'high' },
  hysterical: { name: 'Hysterical', description: 'Pathological lying, pseudo-seizures, extreme manipulation', dangerLevel: 'medium' },
  unstable: { name: 'Unstable', description: 'Total lack of will, criminal susceptibility, suggestible', dangerLevel: 'high' },
  antisocial: { name: 'Antisocial', description: 'No empathy, predatory, manipulative, zero remorse', dangerLevel: 'critical' },
};

// --- JUNG PSYCHOLOGICAL TYPES ---
const JUNG_TYPES = {
  attitudes: ['extravert', 'introvert'],
  functions: ['thinking', 'feeling', 'sensing', 'intuiting'],
  // 8 combinations
};

// --- MASLOW HIERARCHY (determines primary drive) ---
const MASLOW_LEVELS = {
  survival: { name: 'Survival', needs: ['food', 'water', 'shelter', 'sleep'], dndContext: 'beggar, refugee, prisoner, starving peasant' },
  safety: { name: 'Safety', needs: ['security', 'stability', 'health', 'property'], dndContext: 'farmer, guard, merchant, cautious villager' },
  belonging: { name: 'Belonging', needs: ['love', 'friendship', 'family', 'community'], dndContext: 'tavern regular, guild member, family person' },
  esteem: { name: 'Esteem', needs: ['respect', 'status', 'recognition', 'power'], dndContext: 'noble, captain, master craftsman, elder' },
  selfActualization: { name: 'Self-Actualization', needs: ['purpose', 'creativity', 'morality', 'meaning'], dndContext: 'sage, artist, paladin, philosopher' },
};

// --- FREUD STRUCTURE (Id/Ego/Superego balance) ---
// Represented as weights: { id: 0-1, ego: 0-1, superego: 0-1 }
// High Id = impulsive, pleasure-seeking
// High Ego = rational, pragmatic, adaptive
// High Superego = moralistic, guilt-ridden, perfectionistic

// --- BERNE TRANSACTIONAL ANALYSIS ---
const BERNE_STATES = {
  parent: { nurturing: 'caring, protective, supportive', critical: 'judging, controlling, punishing' },
  adult: 'rational, objective, problem-solving',
  child: { free: 'spontaneous, creative, playful', adapted: 'compliant, anxious, rebellious' },
};

// --- DEFENSE MECHANISMS ---
const DEFENSE_MECHANISMS = [
  'denial', 'repression', 'projection', 'displacement', 'sublimation',
  'rationalization', 'regression', 'reaction_formation', 'intellectualization',
  'compensation', 'splitting', 'dissociation', 'humor', 'passive_aggression',
];

// ============================================
// CHARACTER PSYCHOLOGY GENERATOR
// ============================================

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomFloat(min, max) { return min + Math.random() * (max - min); }
function clamp(val, min, max) { return Math.min(max, Math.max(min, val)); }

function generatePsychProfile(options = {}) {
  // Pick accentuation type
  const accentKeys = Object.keys(LEONHARD_TYPES);
  const accentKey = options.accentuation || randomChoice(accentKeys);
  const accentuation = LEONHARD_TYPES[accentKey];

  // Jung type
  const attitude = options.attitude || randomChoice(JUNG_TYPES.attitudes);
  const dominantFunction = options.function || randomChoice(JUNG_TYPES.functions);
  const auxiliaryFunction = randomChoice(JUNG_TYPES.functions.filter(f => f !== dominantFunction));

  // Maslow level
  const maslowKeys = Object.keys(MASLOW_LEVELS);
  const maslowKey = options.maslowLevel || randomChoice(maslowKeys);
  const maslowLevel = MASLOW_LEVELS[maslowKey];

  // Freud balance (Id/Ego/Superego)
  let idWeight, egoWeight, superegoWeight;
  switch (accentKey) {
    case 'excitable': idWeight = 0.7; egoWeight = 0.2; superegoWeight = 0.1; break;
    case 'pedantic': idWeight = 0.1; egoWeight = 0.3; superegoWeight = 0.6; break;
    case 'demonstrative': idWeight = 0.5; egoWeight = 0.4; superegoWeight = 0.1; break;
    case 'dysthymic': idWeight = 0.1; egoWeight = 0.3; superegoWeight = 0.6; break;
    case 'hyperthymic': idWeight = 0.5; egoWeight = 0.4; superegoWeight = 0.1; break;
    case 'anxious': idWeight = 0.2; egoWeight = 0.2; superegoWeight = 0.6; break;
    case 'stuck': idWeight = 0.3; egoWeight = 0.2; superegoWeight = 0.5; break;
    default: idWeight = 0.33; egoWeight = 0.34; superegoWeight = 0.33; break;
  }

  // Add some randomness
  idWeight = clamp(idWeight + randomFloat(-0.1, 0.1), 0.05, 0.9);
  egoWeight = clamp(egoWeight + randomFloat(-0.1, 0.1), 0.05, 0.9);
  superegoWeight = clamp(superegoWeight + randomFloat(-0.1, 0.1), 0.05, 0.9);

  // Normalize
  const total = idWeight + egoWeight + superegoWeight;
  idWeight /= total; egoWeight /= total; superegoWeight /= total;

  // Berne dominant state
  let dominantBerne;
  if (superegoWeight > 0.4) dominantBerne = 'critical_parent';
  else if (idWeight > 0.4) dominantBerne = 'free_child';
  else if (egoWeight > 0.4) dominantBerne = 'adult';
  else if (accentKey === 'emotive') dominantBerne = 'nurturing_parent';
  else if (accentKey === 'anxious') dominantBerne = 'adapted_child';
  else dominantBerne = 'adult';

  // Defense mechanisms (pick 2-3 based on accentuation)
  const defenseMap = {
    demonstrative: ['denial', 'repression', 'regression'],
    stuck: ['projection', 'rationalization', 'displacement'],
    pedantic: ['intellectualization', 'reaction_formation', 'repression'],
    excitable: ['displacement', 'denial', 'splitting'],
    hyperthymic: ['denial', 'humor', 'sublimation'],
    dysthymic: ['repression', 'intellectualization', 'sublimation'],
    anxious: ['repression', 'regression', 'passive_aggression'],
    emotive: ['repression', 'compensation', 'sublimation'],
    cyclothymic: ['splitting', 'denial', 'dissociation'],
    exalted: ['sublimation', 'denial', 'reaction_formation'],
  };
  const defenses = defenseMap[accentKey] || ['denial', 'rationalization'];

  // Psychopathy potential (0-1, most characters should be low)
  const psychopathyPotential = options.psychopathic ? randomFloat(0.6, 0.95) : randomFloat(0, 0.15);

  // Emotional stability (0-1)
  const stabilityMap = {
    demonstrative: 0.3, stuck: 0.4, pedantic: 0.5, excitable: 0.2,
    hyperthymic: 0.6, dysthymic: 0.4, anxious: 0.2, emotive: 0.3,
    cyclothymic: 0.15, exalted: 0.25,
  };
  const emotionalStability = clamp((stabilityMap[accentKey] || 0.5) + randomFloat(-0.1, 0.1), 0, 1);

  // Empathy level
  const empathyMap = {
    demonstrative: 0.3, stuck: 0.2, pedantic: 0.4, excitable: 0.15,
    hyperthymic: 0.5, dysthymic: 0.7, anxious: 0.6, emotive: 0.95,
    cyclothymic: 0.5, exalted: 0.8,
  };
  const empathy = clamp((empathyMap[accentKey] || 0.5) + randomFloat(-0.1, 0.1), 0, 1);

  // Willpower
  const willMap = {
    demonstrative: 0.4, stuck: 0.8, pedantic: 0.6, excitable: 0.3,
    hyperthymic: 0.5, dysthymic: 0.4, anxious: 0.2, emotive: 0.3,
    cyclothymic: 0.35, exalted: 0.4,
  };
  const willpower = clamp((willMap[accentKey] || 0.5) + randomFloat(-0.1, 0.1), 0, 1);

  // Current emotional state
  const moodStates = ['content', 'anxious', 'angry', 'sad', 'excited', 'fearful', 'scheming', 'hopeful'];
  const moodBias = {
    demonstrative: ['excited', 'scheming'], stuck: ['angry', 'scheming'], pedantic: ['anxious', 'content'],
    excitable: ['angry', 'excited'], hyperthymic: ['excited', 'hopeful'], dysthymic: ['sad', 'content'],
    anxious: ['fearful', 'anxious'], emotive: ['sad', 'hopeful'], cyclothymic: ['excited', 'sad'],
    exalted: ['excited', 'hopeful'],
  };
  const currentMood = randomChoice(moodBias[accentKey] || moodStates);

  // Inner conflicts
  const conflicts = [];
  if (idWeight > 0.4 && superegoWeight > 0.3) conflicts.push('desires vs morality');
  if (maslowKey === 'survival' && accentKey === 'dysthymic') conflicts.push('will to live vs despair');
  if (accentKey === 'stuck' && maslowKey === 'esteem') conflicts.push('ambition vs paranoia');
  if (accentKey === 'emotive' && maslowKey === 'safety') conflicts.push('compassion vs self-preservation');
  if (conflicts.length === 0) conflicts.push('searching for purpose');

  return {
    // Core psychology
    accentuation: { key: accentKey, ...accentuation },
    jungType: { attitude, dominantFunction, auxiliaryFunction, label: `${attitude}-${dominantFunction}` },
    maslowLevel: { key: maslowKey, ...maslowLevel },
    freudBalance: { id: Math.round(idWeight * 100) / 100, ego: Math.round(egoWeight * 100) / 100, superego: Math.round(superegoWeight * 100) / 100 },
    berneState: dominantBerne,
    defenses,
    // Metrics
    emotionalStability: Math.round(emotionalStability * 100) / 100,
    empathy: Math.round(empathy * 100) / 100,
    willpower: Math.round(willpower * 100) / 100,
    psychopathyPotential: Math.round(psychopathyPotential * 100) / 100,
    // State
    currentMood,
    stressLevel: randomFloat(0.1, 0.5),
    innerConflicts: conflicts,
    // Behavior
    speechStyle: accentuation.speechStyle,
    underStress: accentuation.underStress,
    socialBehavior: accentuation.socialBehavior,
  };
}

// ============================================
// BEHAVIOR DECISION ENGINE
// ============================================

function decideBehavior(psychProfile, context) {
  const { accentuation, maslowLevel, freudBalance, emotionalStability, stressLevel } = psychProfile;

  // Maslow drives current primary motivation
  const primaryNeed = randomChoice(maslowLevel.needs);

  // Stress increases Id influence temporarily
  const effectiveId = freudBalance.id + stressLevel * 0.3;
  const effectiveEgo = freudBalance.ego;
  const effectiveSuperego = freudBalance.superego - stressLevel * 0.1;

  // Decision tendency
  let actionType;
  if (effectiveId > effectiveEgo && effectiveId > effectiveSuperego) {
    // Id-driven: impulsive, pleasure-seeking, aggressive
    const idActions = ['fight', 'rob', 'threaten', 'gossip', 'rest', 'trade'];
    actionType = randomChoice(idActions);
  } else if (effectiveSuperego > effectiveEgo) {
    // Superego-driven: moral, guilt-based
    const superegoActions = ['help', 'pray', 'patrol', 'work', 'investigate'];
    actionType = randomChoice(superegoActions);
  } else {
    // Ego-driven: rational, adaptive
    const egoActions = ['trade', 'work', 'talk', 'move', 'investigate', 'craft'];
    actionType = randomChoice(egoActions);
  }

  // Accentuation-specific overrides
  if (accentuation.key === 'excitable' && stressLevel > 0.6) actionType = 'fight';
  if (accentuation.key === 'anxious' && stressLevel > 0.5) actionType = 'rest';
  if (accentuation.key === 'demonstrative' && context?.nearby?.length > 2) actionType = 'talk';
  if (accentuation.key === 'stuck' && context?.enemy) actionType = 'threaten';
  if (accentuation.key === 'emotive' && context?.someoneHurt) actionType = 'help';

  return {
    action: actionType,
    motivation: primaryNeed,
    reasoning: `${accentuation.name}: driven by ${primaryNeed} (Id:${Math.round(effectiveId*100)}% Ego:${Math.round(effectiveEgo*100)}% Superego:${Math.round(effectiveSuperego*100)}%)`,
    emotionalState: psychProfile.currentMood,
  };
}

// ============================================
// DIALOGUE GENERATOR (based on psychology)
// ============================================

function generateDialogue(psychProfile, situation) {
  const { accentuation, jungType, currentMood, empathy, stressLevel } = psychProfile;
  const style = accentuation.speechStyle;

  // Introvert vs extravert affects talkativeness
  const isIntrovert = jungType.attitude === 'introvert';

  // Mood-based response templates
  const templates = {
    demonstrative: {
      greeting: ['*strikes a pose* "Finally, someone worth talking to!"', '"You won\'t BELIEVE what happened to me!"'],
      angry: ['"How DARE you! Do you have ANY idea who I am?!"', '*dramatic gasp* "I have never been so insulted!"'],
      scared: ['"I can\'t... I simply can\'t bear it..." *fans self dramatically*'],
      happy: ['"Oh, how WONDERFUL! This is the best day of my life!"'],
    },
    stuck: {
      greeting: ['"I remember you. Last time we met, you..." *narrows eyes*', '"What do you want? And don\'t try to deceive me."'],
      angry: ['"I will not forget this slight. Mark my words."', '"Justice will be served. I\'ll make sure of it."'],
      scared: ['"They\'re all plotting against me. I can feel it."'],
      happy: ['"Finally. Someone recognizes my worth." *slight nod*'],
    },
    excitable: {
      greeting: ['"Huh? What d\'you want?"', '*grunts* "Make it quick."'],
      angry: ['"Say that again. I DARE you." *clenches fists*', '"I\'ll break every bone in your—" *steps forward menacingly*'],
      scared: ['"Back off! I\'ll kill anyone who comes closer!"'],
      happy: ['"Hah! Not bad!" *slaps you on the back hard enough to hurt*'],
    },
    anxious: {
      greeting: ['"Oh... h-hello. Is everything alright? You look... is something wrong?"', '"Please don\'t... I mean... welcome, I suppose."'],
      angry: ['"I-I wish you wouldn\'t... please..."', '"..." *trembles but says nothing*'],
      scared: ['"No no no no no... please, I can\'t..." *backs against wall*'],
      happy: ['"Oh! That\'s... that\'s actually nice. Thank you." *small smile*'],
    },
    emotive: {
      greeting: ['"Welcome, dear friend. How is your heart today?"', '*warm smile, eyes glistening* "It\'s so good to see a kind face."'],
      angry: ['"It breaks my heart that you would do this..." *tears forming*'],
      scared: ['"I\'m frightened for everyone... what will happen to the children?"'],
      happy: ['"Oh..." *tears of joy* "This world can still be beautiful."'],
    },
    dysthymic: {
      greeting: ['"Another day passes. What brings you to this troubled place?"', '*sighs deeply* "I suppose we should talk."'],
      angry: ['"The world is unjust. But what else is new?"'],
      scared: ['"I always knew darkness would come. We were fools to hope."'],
      happy: ['"A rare moment of light... let us not waste it." *faint smile*'],
    },
    hyperthymic: {
      greeting: ['"Hey! Great to see you! Come, sit down, I have SO much to tell you!"', '"Oh man, perfect timing! I just had the BEST idea!"'],
      angry: ['"That\'s annoying but whatever — hey, wanna go do something fun instead?"'],
      scared: ['"Psh, scared? Nah! Well... maybe a little. But we\'ll figure it out!"'],
      happy: ['"THIS IS AMAZING! Let\'s celebrate! Drinks on me! Actually wait, I\'m broke. Drinks on YOU!"'],
    },
    pedantic: {
      greeting: ['"Good day. I trust you\'ve followed proper protocol in entering this area?"', '"Ah yes, you. I have you listed in my records as..."'],
      angry: ['"This is a clear violation of established procedure, section 4, paragraph 3..."'],
      scared: ['"I need to recheck all the locks. And the records. And the locks again."'],
      happy: ['"Satisfactory. Everything is in order. That is... pleasing."'],
    },
    cyclothymic: {
      greeting_high: ['"Life is INCREDIBLE today! Everything feels possible!"'],
      greeting_low: ['"... leave me alone. I can\'t do this today."'],
      angry: ['"I don\'t know whether to laugh or scream!"'],
    },
    exalted: {
      greeting: ['"Oh! The very heavens sing at our meeting!"', '"Your presence here — it must be DESTINY!"'],
      angry: ['"My soul BURNS with righteous fury! How could they?!"'],
      scared: ['"I feel the darkness closing in... the very air grows cold with evil..."'],
      happy: ['"RAPTURE! Pure, unbridled rapture! Can you feel it?!" *grabs your hands*'],
    },
  };

  const accentTemplates = templates[accentuation.key] || templates.dysthymic;

  // Select based on mood
  let moodCategory = 'greeting';
  if (currentMood === 'angry') moodCategory = 'angry';
  else if (['fearful', 'anxious'].includes(currentMood)) moodCategory = 'scared';
  else if (['excited', 'hopeful', 'content'].includes(currentMood)) moodCategory = 'happy';

  const options = accentTemplates[moodCategory] || accentTemplates.greeting;
  let dialogue = randomChoice(options);

  // Introvert modification
  if (isIntrovert && dialogue.length > 80) {
    dialogue = dialogue.substring(0, dialogue.lastIndexOf('.') + 1) || dialogue.substring(0, 60) + '..."';
  }

  return dialogue;
}

// ============================================
// PSYCHOLOGY EVOLUTION (changes over time)
// ============================================

function evolvePsychology(psychProfile, event) {
  const profile = { ...psychProfile };

  switch (event.type) {
    case 'betrayal':
      profile.stressLevel = clamp(profile.stressLevel + 0.3, 0, 1);
      profile.empathy = clamp(profile.empathy - 0.1, 0, 1);
      if (profile.accentuation.key === 'stuck') profile.currentMood = 'angry';
      if (profile.accentuation.key === 'anxious') profile.currentMood = 'fearful';
      if (!profile.defenses.includes('projection')) profile.defenses.push('projection');
      break;

    case 'kindness':
      profile.stressLevel = clamp(profile.stressLevel - 0.2, 0, 1);
      profile.empathy = clamp(profile.empathy + 0.05, 0, 1);
      if (profile.accentuation.key === 'emotive') profile.currentMood = 'hopeful';
      break;

    case 'violence':
      profile.stressLevel = clamp(profile.stressLevel + 0.4, 0, 1);
      profile.emotionalStability = clamp(profile.emotionalStability - 0.1, 0, 1);
      if (profile.accentuation.key === 'excitable') profile.currentMood = 'angry';
      if (profile.accentuation.key === 'anxious') profile.currentMood = 'fearful';
      break;

    case 'loss':
      profile.stressLevel = clamp(profile.stressLevel + 0.3, 0, 1);
      if (profile.accentuation.key === 'dysthymic') profile.currentMood = 'sad';
      if (profile.accentuation.key === 'exalted') profile.currentMood = 'sad';
      break;

    case 'success':
      profile.stressLevel = clamp(profile.stressLevel - 0.2, 0, 1);
      profile.willpower = clamp(profile.willpower + 0.05, 0, 1);
      profile.currentMood = 'excited';
      break;

    case 'humiliation':
      profile.stressLevel = clamp(profile.stressLevel + 0.3, 0, 1);
      if (profile.accentuation.key === 'demonstrative') profile.currentMood = 'angry';
      if (profile.accentuation.key === 'anxious') profile.currentMood = 'fearful';
      if (profile.accentuation.key === 'stuck') {
        profile.currentMood = 'scheming';
        profile.psychopathyPotential = clamp(profile.psychopathyPotential + 0.1, 0, 1);
      }
      break;

    case 'time_passes':
      // Natural stress decay
      profile.stressLevel = clamp(profile.stressLevel - 0.05, 0, 1);
      // Mood can shift based on accentuation
      if (profile.accentuation.key === 'cyclothymic') {
        profile.currentMood = Math.random() > 0.5 ? 'excited' : 'sad';
      }
      break;
  }

  return profile;
}

module.exports = {
  LEONHARD_TYPES, LICHKO_TYPES, GANUSHKIN_PSYCHOPATHIES,
  JUNG_TYPES, MASLOW_LEVELS, BERNE_STATES, DEFENSE_MECHANISMS,
  generatePsychProfile, decideBehavior, generateDialogue, evolvePsychology,
};
