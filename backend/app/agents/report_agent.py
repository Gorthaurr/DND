"""Report Agent — generates narrative summaries of world events."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("report_agent")


class ReportAgent(BaseAgent):
    """Generates human-readable reports from world analytics data."""

    def __init__(self):
        super().__init__("report_analyze.j2")

    async def analyze(self, report_data: dict) -> str:
        """Generate a narrative summary of what happened in the world."""
        try:
            summary = await self.generate_text(
                temperature=0.5,
                report=report_data,
            )
            return summary or "No significant events to report."
        except Exception as e:
            log.error("report_generation_failed", error=str(e))
            return self._fallback_report(report_data)

    def _fallback_report(self, data: dict) -> str:
        """Generate a basic report without LLM when it's unavailable."""
        lines = [f"World Report — Days {data['period']['from_day']} to {data['period']['to_day']}"]
        lines.append(f"Current day: {data['world_day']}")
        lines.append("")

        if data.get("events"):
            lines.append(f"Events ({len(data['events'])}):")
            for e in data["events"][:10]:
                lines.append(f"  Day {e['day']}: {e['description']}")
            lines.append("")

        if data.get("deaths"):
            lines.append(f"Deaths ({len(data['deaths'])}):")
            for d in data["deaths"]:
                lines.append(f"  {d['name']} ({d['occupation']})")
            lines.append("")

        rels = data.get("relationships", {})
        if rels.get("alliances"):
            lines.append(f"Alliances ({len(rels['alliances'])}):")
            for a in rels["alliances"][:5]:
                lines.append(f"  {a['from']} <-> {a['to']} (sentiment: {a['sentiment']:.1f})")

        if rels.get("rivalries"):
            lines.append(f"Rivalries ({len(rels['rivalries'])}):")
            for r in rels["rivalries"][:5]:
                lines.append(f"  {r['from']} vs {r['to']} (sentiment: {r['sentiment']:.1f})")

        scenarios = data.get("scenarios", {})
        if scenarios.get("active"):
            lines.append(f"\nActive Scenarios: {', '.join(s['title'] for s in scenarios['active'])}")
        if scenarios.get("completed"):
            lines.append(f"Completed: {', '.join(s['title'] for s in scenarios['completed'])}")

        return "\n".join(lines)


report_agent = ReportAgent()
