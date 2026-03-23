"""Tests for 23 NPC personality archetypes."""

from app.models.archetypes import ARCHETYPES, get_archetype, list_archetypes, ArchetypeID


class TestArchetypeRegistry:
    def test_all_23_archetypes_exist(self):
        assert len(ARCHETYPES) == 23

    def test_all_enum_values_registered(self):
        for aid in ArchetypeID:
            assert aid in ARCHETYPES, f"Archetype {aid} not registered"

    def test_list_archetypes_returns_all(self):
        archs = list_archetypes()
        assert len(archs) == 23


class TestGetArchetype:
    def test_guardian(self):
        a = get_archetype("guardian")
        assert a is not None
        assert a.name == "The Guardian"

    def test_trickster(self):
        a = get_archetype("trickster")
        assert a is not None
        assert "instigator" == a.group_role

    def test_invalid_id(self):
        assert get_archetype("nonexistent") is None

    def test_empty_string(self):
        assert get_archetype("") is None


class TestArchetypeProperties:
    def test_all_have_dialogue_style(self):
        for arch in list_archetypes():
            assert arch.dialogue_style, f"{arch.id} missing dialogue_style"

    def test_all_have_decision_bias(self):
        for arch in list_archetypes():
            assert arch.decision_bias, f"{arch.id} missing decision_bias"

    def test_all_have_group_role(self):
        for arch in list_archetypes():
            assert arch.group_role, f"{arch.id} missing group_role"

    def test_all_have_default_schedule(self):
        for arch in list_archetypes():
            assert arch.default_schedule, f"{arch.id} missing default_schedule"
            for slot in ("morning", "afternoon", "evening"):
                assert slot in arch.default_schedule, f"{arch.id} missing schedule slot: {slot}"

    def test_all_have_action_weights(self):
        for arch in list_archetypes():
            assert arch.action_weights, f"{arch.id} missing action_weights"
