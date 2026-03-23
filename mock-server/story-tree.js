// ============================================
// Story Tree — Detroit: Become Human style branching narrative
// Tracks all key decisions, events, consequences
// ============================================

class StoryTree {
  constructor() {
    this.nodes = [];
    this.edges = [];
    this.branches = [];
    this.nextId = 1;

    // Add root node
    this.addEvent({
      title: 'The Adventure Begins',
      description: 'A new story unfolds in Oakhollow Village.',
      day: 1,
      type: 'event',
      participants: ['player'],
      category: 'story_start',
    });
  }

  _genId() { return `node_${this.nextId++}`; }

  // --- Add an event node ---
  addEvent({ title, description, day, type = 'event', participants = [], category = 'world', parentId = null, metadata = {} }) {
    const id = this._genId();
    const node = {
      id, type, title, description, day,
      participants, category, metadata,
      timestamp: new Date().toISOString(),
      consequences: [],
    };
    this.nodes.push(node);

    // Auto-connect to parent or last node in same category
    if (parentId) {
      this.edges.push({ from: parentId, to: id, label: 'leads to' });
    } else if (this.nodes.length > 1) {
      // Connect to most recent node
      const prev = this.nodes[this.nodes.length - 2];
      this.edges.push({ from: prev.id, to: id, label: 'then' });
    }

    return id;
  }

  // --- Add a player choice (branching point) ---
  addChoice({ title, description, day, options, chosenIndex, participants = [], parentId = null }) {
    // Create the choice node
    const choiceId = this.addEvent({
      title, description, day,
      type: 'choice',
      participants,
      category: 'player_choice',
      parentId,
      metadata: { options, chosenIndex },
    });

    // Create consequence nodes for each option
    const consequenceIds = [];
    options.forEach((option, idx) => {
      const isChosen = idx === chosenIndex;
      const consequenceId = this._genId();
      const node = {
        id: consequenceId,
        type: 'consequence',
        title: option.title,
        description: option.description,
        day,
        participants,
        category: isChosen ? 'chosen_path' : 'locked_path',
        metadata: { isChosen, optionIndex: idx },
        timestamp: new Date().toISOString(),
        consequences: [],
      };
      this.nodes.push(node);
      this.edges.push({
        from: choiceId,
        to: consequenceId,
        label: isChosen ? 'CHOSEN' : 'not taken',
      });
      consequenceIds.push(consequenceId);

      // Track branch
      this.branches.push({
        id: `branch_${this.branches.length + 1}`,
        name: option.title,
        status: isChosen ? 'active' : 'locked',
        choiceNodeId: choiceId,
        consequenceNodeId: consequenceId,
        condition: option.condition || null,
      });
    });

    return { choiceId, consequenceIds, chosenPath: consequenceIds[chosenIndex] };
  }

  // --- Add NPC relationship change ---
  addRelationshipEvent({ npcA, npcB, change, reason, day, parentId = null }) {
    const direction = change > 0 ? 'improved' : 'worsened';
    return this.addEvent({
      title: `${npcA} ↔ ${npcB}: Relationship ${direction}`,
      description: `${reason}. Sentiment changed by ${change > 0 ? '+' : ''}${change.toFixed(1)}.`,
      day,
      type: 'event',
      participants: [npcA, npcB],
      category: 'relationship',
      parentId,
      metadata: { npcA, npcB, sentimentChange: change, reason },
    });
  }

  // --- Add NPC death ---
  addDeath({ npcName, killedBy, reason, day, parentId = null }) {
    return this.addEvent({
      title: `Death of ${npcName}`,
      description: `${npcName} was killed by ${killedBy}. ${reason}`,
      day,
      type: 'event',
      participants: [npcName, killedBy],
      category: 'death',
      parentId,
      metadata: { victim: npcName, killer: killedBy, reason },
    });
  }

  // --- Add combat event ---
  addCombat({ participants, winner, day, description, parentId = null }) {
    return this.addEvent({
      title: `Combat: ${participants.join(' vs ')}`,
      description,
      day,
      type: 'event',
      participants,
      category: 'combat',
      parentId,
      metadata: { winner },
    });
  }

  // --- Add NPC psychological change ---
  addPsychChange({ npcName, changeType, from, to, cause, day, parentId = null }) {
    return this.addEvent({
      title: `${npcName}: ${changeType}`,
      description: `${npcName}'s ${changeType} changed from "${from}" to "${to}" because: ${cause}`,
      day,
      type: 'event',
      participants: [npcName],
      category: 'psych_change',
      parentId,
      metadata: { npcName, changeType, from, to, cause },
    });
  }

  // --- Get full tree for visualization ---
  getTree() {
    return {
      nodes: this.nodes,
      edges: this.edges,
      branches: this.branches,
      stats: {
        totalEvents: this.nodes.length,
        choices: this.nodes.filter(n => n.type === 'choice').length,
        deaths: this.nodes.filter(n => n.category === 'death').length,
        activeBranches: this.branches.filter(b => b.status === 'active').length,
        lockedBranches: this.branches.filter(b => b.status === 'locked').length,
      },
    };
  }

  // --- Get timeline for specific NPC ---
  getTimeline(participantName) {
    const relevantNodes = this.nodes.filter(n =>
      n.participants.some(p => p.toLowerCase().includes(participantName.toLowerCase()))
    );
    const relevantNodeIds = new Set(relevantNodes.map(n => n.id));
    const relevantEdges = this.edges.filter(e =>
      relevantNodeIds.has(e.from) || relevantNodeIds.has(e.to)
    );

    return {
      participant: participantName,
      nodes: relevantNodes,
      edges: relevantEdges,
      eventCount: relevantNodes.length,
    };
  }

  // --- Get events by day ---
  getByDay(day) {
    return this.nodes.filter(n => n.day === day);
  }

  // --- Get events by category ---
  getByCategory(category) {
    return this.nodes.filter(n => n.category === category);
  }

  // --- Serialize for saving ---
  toJSON() {
    return { nodes: this.nodes, edges: this.edges, branches: this.branches, nextId: this.nextId };
  }

  // --- Load from saved state ---
  static fromJSON(data) {
    const tree = new StoryTree();
    tree.nodes = data.nodes || [];
    tree.edges = data.edges || [];
    tree.branches = data.branches || [];
    tree.nextId = data.nextId || tree.nodes.length + 1;
    return tree;
  }
}

module.exports = { StoryTree };
