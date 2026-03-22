"""Terminal client for testing the Living World Engine."""

import httpx
import sys

API_URL = "http://localhost:8000/api"


def main():
    client = httpx.Client(base_url=API_URL, timeout=120.0)

    print("=" * 60)
    print("  LIVING WORLD ENGINE — Terminal Client")
    print("=" * 60)
    print()

    # Get initial state
    try:
        resp = client.get("/look")
        resp.raise_for_status()
        data = resp.json()
        print_location(data)
    except httpx.ConnectError:
        print("ERROR: Cannot connect to backend at", API_URL)
        print("Make sure the server is running: docker compose up -d")
        sys.exit(1)

    print("\nCommands:")
    print("  look          — describe current location")
    print("  go <place>    — move to a location")
    print("  talk <npc_id> — start dialogue with NPC")
    print("  say <message> — say something to current NPC (after 'talk')")
    print("  tick          — advance the world by one day")
    print("  log           — show world log")
    print("  map           — show world map")
    print("  observe <id>  — observe NPC (debug mode)")
    print("  reset         — reset the world")
    print("  quit          — exit")
    print()

    current_npc_id = None

    while True:
        try:
            cmd = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFarewell, adventurer!")
            break

        if not cmd:
            continue

        parts = cmd.split(" ", 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if command == "quit" or command == "exit":
                print("Farewell, adventurer!")
                break

            elif command == "look":
                resp = client.get("/look")
                print_location(resp.json())

            elif command in ("go", "move"):
                resp = client.post("/action", json={"action": f"go {arg}"})
                data = resp.json()
                print(f"\n{data['narration']}")

            elif command == "talk":
                current_npc_id = arg
                resp = client.get(f"/npc/{arg}")
                if resp.status_code == 200:
                    npc = resp.json()
                    print(f"\nYou approach {npc['name']} ({npc['occupation']}, mood: {npc['mood']}).")
                    print(f"{npc['description']}")
                    print("Use 'say <message>' to talk.")
                else:
                    print(f"NPC '{arg}' not found.")
                    current_npc_id = None

            elif command == "say":
                if not current_npc_id:
                    print("You're not talking to anyone. Use 'talk <npc_id>' first.")
                else:
                    resp = client.post("/dialogue", json={"npc_id": current_npc_id, "message": arg})
                    data = resp.json()
                    print(f"\n{data['npc_name']}: \"{data['dialogue']}\"")
                    print(f"  (mood: {data['mood']})")

            elif command == "tick":
                print("Advancing the world...")
                resp = client.post("/world/tick")
                data = resp.json()
                print(f"\n--- Day {data['day']} ---")
                if data["events"]:
                    print("\nEvents:")
                    for e in data["events"]:
                        print(f"  [{e['type']}] {e['description']}")
                if data["npc_actions"]:
                    print("\nNPC Actions:")
                    for a in data["npc_actions"][:10]:
                        action_str = f"  {a['npc_name']}: {a['action']}"
                        if a.get("target"):
                            action_str += f" -> {a['target']}"
                        if a.get("dialogue"):
                            action_str += f' ("{a["dialogue"]}")'
                        print(action_str)
                if data["interactions"]:
                    print("\nInteractions:")
                    for i in data["interactions"]:
                        print(f"  {i['summary'][:100]}")

            elif command == "log":
                resp = client.get("/world/log")
                entries = resp.json()["entries"]
                if not entries:
                    print("No world log entries yet. Run 'tick' to advance the world.")
                else:
                    for entry in entries[-5:]:
                        print(f"\n--- Day {entry.get('day', '?')} ---")
                        for e in entry.get("events", []):
                            print(f"  [{e.get('type', '?')}] {e.get('description', '?')}")

            elif command == "map":
                resp = client.get("/world/map")
                data = resp.json()
                print("\n=== WORLD MAP ===")
                for loc in data["locations"]:
                    marker = " <-- YOU" if loc["id"] == data["player_location_id"] else ""
                    npcs_here = [nid for nid, lid in data["npc_locations"].items() if lid == loc["id"]]
                    npc_str = f" [{len(npcs_here)} NPCs]" if npcs_here else ""
                    print(f"  [{loc['type']}] {loc['name']}{npc_str}{marker}")

            elif command == "observe":
                resp = client.get(f"/npc/{arg}/observe")
                if resp.status_code == 200:
                    npc = resp.json()
                    print(f"\n=== {npc['name']} ===")
                    print(f"  Personality: {npc['personality']}")
                    print(f"  Mood: {npc['mood']}")
                    print(f"  Goals: {', '.join(npc['goals'])}")
                    print(f"  Location: {npc['location']['name'] if npc['location'] else 'unknown'}")
                    print(f"  Backstory: {npc['backstory']}")
                    if npc["relationships"]:
                        print("  Relationships:")
                        for r in npc["relationships"]:
                            print(f"    {r['name']}: {r['sentiment']:.1f} ({r['reason']})")
                    if npc["recent_memories"]:
                        print("  Recent memories:")
                        for m in npc["recent_memories"][:5]:
                            print(f"    - {m}")
                else:
                    print(f"NPC '{arg}' not found.")

            elif command == "state":
                resp = client.get("/world/state")
                data = resp.json()
                print(f"\nDay: {data['day']}")
                print(f"Location: {data['player_location'].get('name', 'unknown')}")
                print(f"Gold: {data['player_gold']}")
                if data["player_inventory"]:
                    print("Inventory:")
                    for item in data["player_inventory"]:
                        print(f"  - {item['name']}")

            elif command == "reset":
                resp = client.post("/world/reset")
                print(resp.json()["message"])

            else:
                # Treat as free-form action
                resp = client.post("/action", json={"action": cmd})
                data = resp.json()
                print(f"\n{data['narration']}")

        except httpx.HTTPStatusError as e:
            print(f"Error: {e.response.status_code} — {e.response.text}")
        except httpx.ConnectError:
            print("Lost connection to server.")
        except Exception as e:
            print(f"Error: {e}")


def print_location(data: dict):
    loc = data["location"]
    print(f"\n=== {loc['name']} ===")
    print(f"{loc['description']}")

    if data.get("npcs"):
        print("\nPeople here:")
        for npc in data["npcs"]:
            print(f"  - {npc['name']} ({npc['occupation']}, {npc['mood']})")
            print(f"    ID: {npc['id']}")

    if data.get("exits"):
        print("\nExits:")
        for ex in data["exits"]:
            print(f"  -> {ex['name']} ({ex['type']})")


if __name__ == "__main__":
    main()
