"""Tests for BaseAgent — Jinja2 template rendering + LLM delegation."""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.base import BaseAgent, _get_jinja, PROMPTS_DIR


class TestJinjaEnvironment:
    def test_prompts_dir_exists(self):
        assert PROMPTS_DIR.exists()

    def test_get_jinja_singleton(self):
        env1 = _get_jinja()
        env2 = _get_jinja()
        assert env1 is env2

    def test_jinja_loads_templates(self):
        env = _get_jinja()
        # Should be able to list templates
        templates = env.loader.list_templates()
        assert len(templates) > 0


class TestBaseAgent:
    def test_render_prompt(self):
        agent = BaseAgent("npc_dialogue.j2")
        rendered = agent.render_prompt(
            name="Test", age=30, occupation="guard",
            personality="O:5", mood="neutral", backstory="born",
            other_name="Player", relationship=None, relevant_memories=[],
            message="Hello", is_player=True, reputation=0,
            archetype_dialogue_style=None, speech_instructions=None,
            biography=None, trust_baseline=0, mood_baseline=0,
            aggression_baseline=0, confidence_baseline=0,
        )
        assert "Test" in rendered
        assert "guard" in rendered

    def test_render_system_none(self):
        agent = BaseAgent("npc_dialogue.j2")
        rendered = agent.render_system()
        assert rendered == ""

    def test_render_system_with_template(self):
        # Create agent with system template
        agent = BaseAgent("npc_dialogue.j2", system_template="npc_dialogue.j2")
        rendered = agent.render_system(
            name="X", age=1, occupation="x", personality="x",
            mood="x", backstory="x", other_name="x",
            relationship=None, relevant_memories=[], message="x",
            is_player=True, reputation=0, archetype_dialogue_style=None,
            speech_instructions=None, biography=None,
            trust_baseline=0, mood_baseline=0,
            aggression_baseline=0, confidence_baseline=0,
        )
        assert len(rendered) > 0

    @pytest.mark.asyncio
    async def test_generate_text(self):
        agent = BaseAgent("npc_dialogue.j2")
        with patch("app.agents.base.generate", new_callable=AsyncMock, return_value="response"):
            result = await agent.generate_text(
                name="Test", age=30, occupation="guard",
                personality="O:5", mood="neutral", backstory="born",
                other_name="Player", relationship=None, relevant_memories=[],
                message="Hello", is_player=True, reputation=0,
                archetype_dialogue_style=None, speech_instructions=None,
                biography=None, trust_baseline=0, mood_baseline=0,
                aggression_baseline=0, confidence_baseline=0,
            )
            assert result == "response"

    @pytest.mark.asyncio
    async def test_generate_json(self):
        agent = BaseAgent("npc_dialogue.j2")
        with patch("app.agents.base.generate_json", new_callable=AsyncMock, return_value={"dialogue": "Hi"}):
            result = await agent.generate_json(
                name="Test", age=30, occupation="guard",
                personality="O:5", mood="neutral", backstory="born",
                other_name="Player", relationship=None, relevant_memories=[],
                message="Hello", is_player=True, reputation=0,
                archetype_dialogue_style=None, speech_instructions=None,
                biography=None, trust_baseline=0, mood_baseline=0,
                aggression_baseline=0, confidence_baseline=0,
            )
            assert result["dialogue"] == "Hi"
