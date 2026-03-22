# Memory Migration Plan: SQLite -> Neo4j

## Current: SQLite (memory.db)
- Fast, simple, works for single instance
- No relationship to graph nodes

## Target: Neo4j :Memory nodes
- Memory node linked to NPC via :REMEMBERS relationship
- Enables graph queries like "all NPCs who remember event X"
- Required for multi-instance deployment

## Steps:
1. Add :Memory node type with id, text, day, importance, npc_id
2. Add REMEMBERS relationship from NPC to Memory
3. Migrate add_memory/get_recent_memories to Neo4j queries
4. Keep SQLite as fallback during transition
5. Add memory search via full-text index in Neo4j

## Priority: Low (current system works, optimize later)
