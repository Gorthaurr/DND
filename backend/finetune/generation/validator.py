"""Validates Claude responses against Pydantic schemas."""

from __future__ import annotations

import logging

from finetune.schemas import SCHEMA_MAP, validate_response

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validate and sanitize Claude API responses."""

    def validate(self, agent_type: str, response_data: dict) -> tuple[bool, str | None]:
        """Validate *response_data* against the schema for *agent_type*.

        Returns:
            (True, None) on success.
            (False, error_message) on failure.
        """
        return validate_response(agent_type, response_data)

    def sanitize(self, agent_type: str, response_data: dict) -> dict:
        """Try to fix common issues before validation.

        Applies:
        - Fill missing optional fields with defaults.
        - Coerce numeric strings to int/float where expected.
        - Strip leading/trailing whitespace from string fields.
        """
        schema = SCHEMA_MAP.get(agent_type)
        if schema is None:
            return response_data

        cleaned: dict = dict(response_data)

        for name, field_info in schema.model_fields.items():
            # Fill missing optional fields with their default.
            if name not in cleaned and field_info.default is not None:
                cleaned[name] = field_info.default

            if name not in cleaned:
                continue

            value = cleaned[name]

            # Strip whitespace from strings.
            if isinstance(value, str):
                cleaned[name] = value.strip()

            # Coerce numeric strings.
            annotation = field_info.annotation
            if annotation is int and isinstance(value, str):
                try:
                    cleaned[name] = int(value)
                except (ValueError, TypeError):
                    pass
            elif annotation is float and isinstance(value, str):
                try:
                    cleaned[name] = float(value)
                except (ValueError, TypeError):
                    pass

        return cleaned
