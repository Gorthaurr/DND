"""Evaluation metrics for fine-tuned model quality assessment."""

from __future__ import annotations

import json
import math
from collections import Counter

from finetune.schemas import validate_response


def json_validity_rate(responses: list[str]) -> float:
    """Percentage of responses that parse as valid JSON (0.0 - 1.0)."""
    if not responses:
        return 0.0
    valid = 0
    for resp in responses:
        try:
            json.loads(resp)
            valid += 1
        except (json.JSONDecodeError, TypeError):
            pass
    return valid / len(responses)


def schema_compliance_rate(agent_type: str, responses: list[dict]) -> float:
    """Percentage of parsed dicts passing Pydantic schema validation (0.0 - 1.0)."""
    if not responses:
        return 0.0
    valid = 0
    for resp in responses:
        ok, _ = validate_response(agent_type, resp)
        if ok:
            valid += 1
    return valid / len(responses)


def action_entropy(responses: list[dict]) -> float:
    """Shannon entropy of the 'action' field distribution.

    Higher values indicate more diverse action selection.
    Lower values signal potential mode collapse.
    Only meaningful for agent types that produce an 'action' field
    (e.g. npc_decision).
    """
    actions = [r.get("action") for r in responses if "action" in r]
    if not actions:
        return 0.0

    counts = Counter(actions)
    total = sum(counts.values())
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def avg_response_length(responses: list[str]) -> float:
    """Average character length of raw response strings."""
    if not responses:
        return 0.0
    return sum(len(r) for r in responses) / len(responses)
