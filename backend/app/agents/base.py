"""Base agent with Jinja2 prompt rendering and LLM integration."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.utils.llm import generate, generate_json
from app.utils.logger import get_logger

log = get_logger("agent")

PROMPTS_DIR = Path(__file__).parent / "prompts"

_jinja_env: Environment | None = None


def _get_jinja() -> Environment:
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(str(PROMPTS_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _jinja_env


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, template_name: str, system_template: str | None = None):
        self._template_name = template_name
        self._system_template = system_template

    def _render(self, template_name: str, **kwargs) -> str:
        env = _get_jinja()
        template = env.get_template(template_name)
        return template.render(**kwargs)

    def render_prompt(self, **kwargs) -> str:
        return self._render(self._template_name, **kwargs)

    def render_system(self, **kwargs) -> str:
        if self._system_template:
            return self._render(self._system_template, **kwargs)
        return ""

    async def generate_text(self, temperature: float | None = None, **kwargs) -> str:
        prompt = self.render_prompt(**kwargs)
        system = self.render_system(**kwargs)
        return await generate(prompt, system=system, temperature=temperature)

    async def generate_json(self, temperature: float | None = None, **kwargs) -> dict:
        prompt = self.render_prompt(**kwargs)
        system = self.render_system(**kwargs)
        return await generate_json(prompt, system=system, temperature=temperature)
