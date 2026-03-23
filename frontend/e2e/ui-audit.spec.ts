/**
 * UI Audit — comprehensive visual testing with screenshots.
 *
 * Takes screenshots of EVERY page, tab, component state, and interaction.
 * Mocks all API calls so tests run without backend.
 *
 * Run:  npx playwright test e2e/ui-audit.spec.ts
 * View: open e2e/screenshots/
 */

import { test, expect, Page } from "@playwright/test";

const SHOTS = "e2e/screenshots/audit";

/* ── API Mock: intercept all backend calls ─────────────────────── */

async function mockAPI(page: Page) {
  // IMPORTANT: In Playwright, LAST registered route wins.
  // Register catch-all FIRST so specific routes override it.

  // Catch-all for WebSocket (ignore)
  await page.route("**/ws/**", (route) => route.abort());

  // Fallback for any unhandled API routes (registered FIRST = lowest priority)
  await page.route("**/api/**", (route) => {
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
  });

  // World state
  await page.route("**/api/world/state", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        day: 14,
        player_location: { id: "loc-tavern", name: "The Rusty Tankard", type: "tavern", description: "A warm tavern" },
        player_gold: 47,
        player_inventory: [
          { id: "longsword", name: "Longsword", type: "weapon", description: "A sharp blade", value: 15 },
          { id: "leather", name: "Leather Armor", type: "armor", description: "Light protection", value: 10 },
          { id: "hpot", name: "Health Potion x2", type: "consumable", description: "Restores HP", value: 5 },
        ],
        player_hp: 28,
        player_max_hp: 34,
        player_level: 3,
        player_class: "Fighter",
        player_xp: 1250,
      }),
    })
  );

  // Look — current location
  await page.route("**/api/look", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        location: {
          id: "loc-tavern",
          name: "The Rusty Tankard",
          type: "tavern",
          description:
            "A warm tavern with a roaring fireplace. The smell of ale and roasted meat fills the air. Adventurers swap tales at worn wooden tables.",
        },
        npcs: [
          { id: "npc-barkeep", name: "Greta the Barkeep", occupation: "barkeeper", mood: "cheerful", description: "A stout woman with a hearty laugh" },
          { id: "npc-guard", name: "Sir Aldric", occupation: "guard captain", mood: "wary", description: "A tall knight in polished armor" },
          { id: "npc-bard", name: "Lyra Songweaver", occupation: "bard", mood: "happy", description: "An elf playing a silver lute" },
        ],
        items: [
          { id: "notice-board", name: "Notice Board", type: "interactable", description: "A wooden board with postings", value: 0 },
          { id: "fireplace", name: "Fireplace", type: "decoration", description: "A roaring fireplace", value: 0 },
        ],
        exits: [
          { id: "loc-market", name: "Market Square", type: "market", description: "A bustling marketplace" },
          { id: "loc-chapel", name: "Chapel of Light", type: "temple", description: "A peaceful chapel" },
          { id: "loc-forest", name: "Darkwood Forest", type: "wilderness", description: "A dark forest path" },
        ],
      }),
    })
  );

  // NPCs list
  await page.route("**/api/npcs", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: "npc-barkeep", name: "Greta the Barkeep", occupation: "barkeeper", mood: "cheerful", description: "Stout woman" },
        { id: "npc-guard", name: "Sir Aldric", occupation: "guard captain", mood: "wary", description: "Tall knight" },
        { id: "npc-bard", name: "Lyra Songweaver", occupation: "bard", mood: "happy", description: "Elf bard" },
        { id: "npc-smith", name: "Dorn Ironhand", occupation: "blacksmith", mood: "focused", description: "Muscular dwarf" },
      ]),
    })
  );

  // NPC observe
  await page.route("**/api/npc/*/observe", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: "npc-barkeep",
        name: "Greta the Barkeep",
        personality: { openness: 0.6, conscientiousness: 0.8, extraversion: 0.9, agreeableness: 0.7, neuroticism: 0.3 },
        backstory: "Greta inherited the tavern from her father. She knows every secret in the village.",
        goals: ["Keep the tavern profitable", "Protect the village"],
        mood: "cheerful",
        occupation: "barkeeper",
        age: 42,
        alive: true,
        location: { id: "loc-tavern", name: "The Rusty Tankard", type: "tavern", description: "A warm tavern" },
        relationships: [
          { id: "r1", name: "Sir Aldric", sentiment: 0.6, reason: "Trusted friend" },
          { id: "r2", name: "Lyra Songweaver", sentiment: 0.4, reason: "Good customer" },
        ],
        recent_memories: [
          "Served ale to a group of adventurers",
          "Overheard rumors about missing merchant",
          "Sir Aldric warned about bandits on the road",
        ],
      }),
    })
  );

  // World log
  await page.route("**/api/world/log", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        entries: [
          { day: 14, summary: "A tense day in the village", events: ["Storm clouds gathered", "Merchant caravan arrived"], npc_actions: ["Greta prepared extra ale", "Sir Aldric doubled the guard"] },
          { day: 13, summary: "Quiet morning, busy afternoon", events: ["Market day began", "A stranger was spotted"], npc_actions: ["Lyra played at the square", "Dorn finished a new blade"] },
          { day: 12, summary: "News from the capital", events: ["A royal decree was posted", "Wolves seen near the forest"], npc_actions: ["Guard patrol increased"] },
        ],
      }),
    })
  );

  // World map
  await page.route("**/api/world/map", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        locations: [
          { id: "loc-tavern", name: "The Rusty Tankard", type: "tavern" },
          { id: "loc-market", name: "Market Square", type: "market" },
          { id: "loc-chapel", name: "Chapel of Light", type: "temple" },
          { id: "loc-smithy", name: "Ironhand Forge", type: "shop" },
          { id: "loc-forest", name: "Darkwood Forest", type: "wilderness" },
        ],
        connections: [
          { from_id: "loc-tavern", to_id: "loc-market", distance: 1 },
          { from_id: "loc-market", to_id: "loc-chapel", distance: 1 },
          { from_id: "loc-market", to_id: "loc-smithy", distance: 1 },
          { from_id: "loc-tavern", to_id: "loc-forest", distance: 2 },
        ],
        player_location_id: "loc-tavern",
        npc_locations: {
          "npc-barkeep": "loc-tavern",
          "npc-guard": "loc-tavern",
          "npc-bard": "loc-tavern",
          "npc-smith": "loc-smithy",
        },
      }),
    })
  );

  // Quests
  await page.route("**/api/quests", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: "q1",
          title: "The Missing Merchant",
          description: "A merchant has gone missing on the forest road. Find him before it is too late.",
          giver_npc_name: "Sir Aldric",
          objectives: [
            { description: "Talk to witnesses at the market", completed: true },
            { description: "Search the forest road", completed: false },
            { description: "Report back to Sir Aldric", completed: false },
          ],
          reward_gold: 50,
          reward_description: "50 gold and a reputation boost",
          difficulty: "medium",
          status: "active",
        },
        {
          id: "q2",
          title: "Song of the Lost",
          description: "Lyra needs rare strings for her lute, said to be found in old ruins.",
          giver_npc_name: "Lyra Songweaver",
          objectives: [{ description: "Find enchanted strings in the ruins", completed: false }],
          reward_gold: 30,
          difficulty: "hard",
          status: "active",
        },
      ]),
    })
  );

  // Chat history
  await page.route("**/api/chat/history", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    })
  );

  // Character
  await page.route("**/api/character", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        name: "Thorin Oakenshield",
        race: { id: "dwarf", name: "Dwarf" },
        class: { id: "fighter", name: "Fighter", hit_die: 10 },
        level: 3,
        ability_scores: { strength: 16, dexterity: 12, constitution: 14, intelligence: 10, wisdom: 13, charisma: 8 },
        modifiers: { strength: 3, dexterity: 1, constitution: 2, intelligence: 0, wisdom: 1, charisma: -1 },
        hp: 28,
        max_hp: 34,
        proficiencies: ["Athletics", "Intimidation", "Heavy Armor", "Shields"],
        equipment: ["Longsword", "Chain Mail", "Shield"],
        backstory: "A dwarf of ancient lineage seeking glory.",
        xp: 1250,
      }),
    })
  );

  // Action response
  await page.route("**/api/action", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        narration:
          "You look around the tavern. The fire crackles warmly. Greta polishes mugs behind the bar, while Sir Aldric studies a map. Lyra strums a gentle melody.",
        npcs_involved: ["Greta the Barkeep", "Sir Aldric"],
        npcs_killed: [],
        location: { id: "loc-tavern", name: "The Rusty Tankard", type: "tavern", description: "A warm tavern" },
        items_changed: [],
      }),
    })
  );

  // Inventory
  await page.route("**/api/inventory", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          { id: "longsword", name: "Longsword", type: "weapon", description: "Sharp blade", value: 15 },
          { id: "chainmail", name: "Chain Mail", type: "armor", description: "Heavy armor", value: 75 },
          { id: "shield", name: "Shield", type: "armor", description: "Wooden shield", value: 10 },
          { id: "hpot", name: "Health Potion x2", type: "consumable", description: "Heals", value: 5 },
          { id: "torch", name: "Torch", type: "gear", description: "Light source", value: 1 },
          { id: "rope", name: "50ft Rope", type: "gear", description: "Hempen rope", value: 1 },
        ],
        gold: 47,
        silver: 12,
        copper: 5,
      }),
    })
  );

  // D&D reference data
  await page.route("**/api/dnd/races", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: "human", name: "Human", speed: 30, ability_bonus: { all: 1 }, traits: ["Extra feat"] },
        { id: "elf", name: "Elf", speed: 30, ability_bonus: { dex: 2 }, traits: ["Darkvision"] },
        { id: "dwarf", name: "Dwarf", speed: 25, ability_bonus: { con: 2 }, traits: ["Darkvision"] },
      ]),
    })
  );

  await page.route("**/api/dnd/classes", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: "fighter", name: "Fighter", hit_die: 10, primary_ability: "str" },
        { id: "wizard", name: "Wizard", hit_die: 6, primary_ability: "int" },
        { id: "rogue", name: "Rogue", hit_die: 8, primary_ability: "dex" },
      ]),
    })
  );

  // World builder
  await page.route("**/api/worlds", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: "medieval_village", name: "Medieval Village", description: "A quiet village with a dark secret", locations_count: 5, npcs_count: 8, factions_count: 2 },
        { id: "pirate_cove", name: "Pirate Cove", description: "A lawless port for sea-farers", locations_count: 4, npcs_count: 6, factions_count: 3 },
      ]),
    })
  );

  await page.route("**/api/worlds/*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: "medieval_village",
        name: "Medieval Village",
        description: "A quiet village with a dark secret",
        locations: [
          { id: "loc-tavern", name: "The Rusty Tankard", type: "tavern", description: "A warm tavern" },
          { id: "loc-market", name: "Market Square", type: "market", description: "Busy marketplace" },
        ],
        npcs: [
          { id: "npc-barkeep", name: "Greta", occupation: "barkeeper" },
          { id: "npc-guard", name: "Sir Aldric", occupation: "guard" },
        ],
      }),
    })
  );

}

/* ── Screenshot helper ─────────────────────────────────────────── */

async function shot(page: Page, name: string, fullPage = true) {
  await page.screenshot({ path: `${SHOTS}/${name}.png`, fullPage });
}

/* ═══════════════════════════════════════════════════════════════
   1. MAIN PAGE — all tabs
   ═══════════════════════════════════════════════════════════════ */

test.describe("Main Game Page", () => {
  test.beforeEach(async ({ page }) => {
    await mockAPI(page);
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000); // animations
  });

  test("01 — full page overview", async ({ page }) => {
    await shot(page, "01-main-overview");
    // Header should exist
    const body = await page.textContent("body");
    expect(body?.length).toBeGreaterThan(50);
  });

  test("02 — Adventure / Chat tab", async ({ page }) => {
    // Chat tab is default, should be visible
    const chatArea = page.locator("textarea, input[type='text']").first();
    await shot(page, "02-tab-adventure-chat");
  });

  test("03 — Map tab", async ({ page }) => {
    const mapBtn = page.locator("button").filter({ hasText: /map|карта/i }).first();
    if (await mapBtn.isVisible()) {
      await mapBtn.click();
      await page.waitForTimeout(800);
    }
    await shot(page, "03-tab-map");
  });

  test("04 — Observer tab", async ({ page }) => {
    const obsBtn = page.locator("button").filter({ hasText: /observer|наблюдат/i }).first();
    if (await obsBtn.isVisible()) {
      await obsBtn.click();
      await page.waitForTimeout(800);
    }
    await shot(page, "04-tab-observer");
  });

  test("05 — Chronicles tab", async ({ page }) => {
    const logBtn = page.locator("button").filter({ hasText: /chronicles|хроник/i }).first();
    if (await logBtn.isVisible()) {
      await logBtn.click();
      await page.waitForTimeout(800);
    }
    await shot(page, "05-tab-chronicles");
  });

  test("06 — Quests tab", async ({ page }) => {
    const questBtn = page.locator("button").filter({ hasText: /quests|квест/i }).first();
    if (await questBtn.isVisible()) {
      await questBtn.click();
      await page.waitForTimeout(800);
    }
    await shot(page, "06-tab-quests");
  });

  test("07 — Right sidebar: location, NPCs, exits", async ({ page }) => {
    // Crop right side of page
    const vp = page.viewportSize()!;
    await page.screenshot({
      path: `${SHOTS}/07-sidebar-right.png`,
      clip: { x: vp.width - 320, y: 60, width: 320, height: vp.height - 60 },
    });
  });

  test("08 — Header bar: stats, day, connection", async ({ page }) => {
    await page.screenshot({
      path: `${SHOTS}/08-header-bar.png`,
      clip: { x: 0, y: 0, width: page.viewportSize()!.width, height: 70 },
    });
  });

  test("09 — Send action and see response", async ({ page }) => {
    const input = page.locator("textarea, input[type='text']").first();
    if (await input.isVisible()) {
      await input.fill("I look around the tavern");
      await shot(page, "09-action-typed");
      // Press Enter or click send
      await input.press("Enter");
      await page.waitForTimeout(1500);
      await shot(page, "09-action-response");
    }
  });

  test("10 — Mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    await shot(page, "10-mobile-main");
  });

  test("11 — Tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    await shot(page, "11-tablet-main");
  });
});

/* ═══════════════════════════════════════════════════════════════
   2. CHARACTER CREATION PAGE
   ═══════════════════════════════════════════════════════════════ */

test.describe("Character Creation Page", () => {
  test.beforeEach(async ({ page }) => {
    await mockAPI(page);
    await page.goto("/character");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(800);
  });

  test("20 — character page overview", async ({ page }) => {
    await shot(page, "20-character-overview");
    const body = await page.textContent("body");
    expect(body).toMatch(/race|class|character|расу|класс/i);
  });

  test("21 — race selection cards", async ({ page }) => {
    // Click on first race card
    const raceCard = page.locator("[class*='race'], [class*='card']").first();
    if (await raceCard.isVisible()) {
      await raceCard.click();
      await page.waitForTimeout(300);
    }
    await shot(page, "21-race-selection");
  });

  test("22 — class selection cards", async ({ page }) => {
    // First select a race
    const raceCards = page.locator("button, [class*='card']").filter({ hasText: /human|elf|dwarf|halfling/i });
    if ((await raceCards.count()) > 0) {
      await raceCards.first().click();
      await page.waitForTimeout(500);
    }
    await shot(page, "22-class-selection");
  });

  test("23 — stat rolling area", async ({ page }) => {
    // Scroll down to see the full page
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(300);
    await shot(page, "23-stats-area");
  });

  test("24 — mobile character page", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    await shot(page, "24-character-mobile");
  });
});

/* ═══════════════════════════════════════════════════════════════
   3. WORLD BUILDER PAGE
   ═══════════════════════════════════════════════════════════════ */

test.describe("World Builder Page", () => {
  test.beforeEach(async ({ page }) => {
    await mockAPI(page);
    await page.goto("/worldbuilder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(800);
  });

  test("30 — world builder overview / world list", async ({ page }) => {
    await shot(page, "30-worldbuilder-overview");
    const body = await page.textContent("body");
    expect(body?.length).toBeGreaterThan(20);
  });

  test("31 — create world dialog", async ({ page }) => {
    const createBtn = page.locator("button").filter({ hasText: /create|создать|new|\+/i }).first();
    if (await createBtn.isVisible()) {
      await createBtn.click();
      await page.waitForTimeout(500);
      await shot(page, "31-create-world-dialog");
    }
  });

  test("32 — world editor: locations tab", async ({ page }) => {
    // Click on a world card to open editor
    const worldCard = page.locator("[class*='card'], button").filter({ hasText: /medieval|village/i }).first();
    if (await worldCard.isVisible()) {
      await worldCard.click();
      await page.waitForTimeout(800);
      await shot(page, "32-world-editor-locations");
    }
  });

  test("33 — world editor: NPCs tab", async ({ page }) => {
    const worldCard = page.locator("[class*='card'], button").filter({ hasText: /medieval|village/i }).first();
    if (await worldCard.isVisible()) {
      await worldCard.click();
      await page.waitForTimeout(800);
      // Switch to NPCs tab
      const npcTab = page.locator("button").filter({ hasText: /npc/i }).first();
      if (await npcTab.isVisible()) {
        await npcTab.click();
        await page.waitForTimeout(500);
      }
      await shot(page, "33-world-editor-npcs");
    }
  });

  test("34 — mobile world builder", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    await shot(page, "34-worldbuilder-mobile");
  });
});

/* ═══════════════════════════════════════════════════════════════
   4. LANGUAGE SWITCH
   ═══════════════════════════════════════════════════════════════ */

test.describe("Language Switching", () => {
  test("40 — English UI", async ({ page }) => {
    await mockAPI(page);
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    // Make sure we're in EN
    const langBtn = page.locator("button").filter({ hasText: /ru|en/i }).first();
    if (await langBtn.isVisible()) {
      const text = await langBtn.textContent();
      if (text?.match(/ru/i)) {
        await langBtn.click();
        await page.waitForTimeout(800);
      }
    }
    await shot(page, "40-lang-english");
  });

  test("41 — Russian UI", async ({ page }) => {
    await mockAPI(page);
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    const langBtn = page.locator("button").filter({ hasText: /ru|en/i }).first();
    if (await langBtn.isVisible()) {
      const text = await langBtn.textContent();
      if (text?.match(/en/i)) {
        await langBtn.click();
        await page.waitForTimeout(800);
      }
    }
    await shot(page, "41-lang-russian");
  });
});

/* ═══════════════════════════════════════════════════════════════
   5. 404 PAGE
   ═══════════════════════════════════════════════════════════════ */

test.describe("Error Pages", () => {
  test("50 — 404 not found", async ({ page }) => {
    await page.goto("/this-page-does-not-exist");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(500);
    await shot(page, "50-404-page");
  });
});

/* ═══════════════════════════════════════════════════════════════
   6. WIDE VIEWPORT — check that all sidebar & panels fit
   ═══════════════════════════════════════════════════════════════ */

test.describe("Wide Desktop", () => {
  test("60 — ultrawide 2560px", async ({ page }) => {
    await mockAPI(page);
    await page.setViewportSize({ width: 2560, height: 1440 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await shot(page, "60-ultrawide-main");
  });
});
