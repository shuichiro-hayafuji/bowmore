"""Validated menu selection; no storage, audio, or ability assessment."""

import json
import random
from pathlib import Path

STAGES = ("short_response", "give_reasons", "express_opinion", "handle_questions")
MODES = {"balanced", "listening", "speaking", "expressions", "rephrase"}
STEP_KINDS = ["expressions", "listening", "conversation", "reflection"]
CATALOG = Path(__file__).resolve().parents[1] / "docs" / "learning-patterns.json"


def validate_catalog(catalog):
    """Reject incomplete or inconsistent design data before offering a menu."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(isinstance(catalog, dict), "Catalog must be an object")
    require(type(catalog.get("schema_version")) is int and catalog["schema_version"] == 1,
            "Unsupported catalog version")
    patterns = catalog.get("patterns")
    require(isinstance(patterns, list) and len(patterns) == 100, "Expected 100 menus")
    ids, titles, topics = set(), set(), {}
    for pattern in patterns:
        require(isinstance(pattern, dict), "Menu must be an object")
        for key in ("id", "title", "topic_id", "stage", "mode", "goal"):
            require(isinstance(pattern.get(key), str) and bool(pattern[key].strip()),
                    f"Missing menu field: {key}")
        require(pattern["id"] not in ids, "Duplicate menu ID")
        require(pattern["title"] not in titles, "Duplicate menu title")
        ids.add(pattern["id"])
        titles.add(pattern["title"])
        require(pattern["stage"] in STAGES, "Unknown learning stage")
        require(pattern["mode"] in MODES, "Unknown practice mode")
        topic = topics.setdefault(pattern["topic_id"], {"stage": pattern["stage"], "modes": set()})
        require(topic["stage"] == pattern["stage"], "Topic has inconsistent stages")
        require(pattern["mode"] not in topic["modes"], "Duplicate topic/mode pair")
        topic["modes"].add(pattern["mode"])
        require(type(pattern.get("duration_minutes")) is int and pattern["duration_minutes"] == 10,
                "Menu duration must be 10 minutes")
        steps = pattern.get("steps")
        require(isinstance(steps, list) and len(steps) == 4 and
                all(isinstance(step, dict) for step in steps), "Expected four learning steps")
        require([step.get("kind") for step in steps] == STEP_KINDS, "Incorrect step order")
        for step in steps:
            require(type(step.get("minutes")) is int and step["minutes"] > 0,
                    "Step duration must be a positive integer")
            require(isinstance(step.get("task"), str) and bool(step["task"].strip()),
                    "Missing step task")
        require(sum(step["minutes"] for step in steps) == 10, "Steps must total 10 minutes")
    require(len(topics) == 20 and all(topic["modes"] == MODES for topic in topics.values()),
            "Expected 20 topics with five modes each")
    assignments = catalog.get("initial_stage_assignments")
    require(isinstance(assignments, dict) and set(assignments) == {"owner", "friends"},
            "Missing initial profiles")
    for stages in assignments.values():
        validate_stages(stages)
        require(any(pattern["stage"] in stages for pattern in patterns), "No eligible menus")
    return catalog


def validate_stages(stages):
    if not isinstance(stages, (list, tuple)) or not stages or any(
        not isinstance(stage, str) or stage not in STAGES for stage in stages
    ):
        raise ValueError("Provide one or more known current learning stages")


def read_catalog(path=CATALOG):
    return validate_catalog(json.loads(Path(path).read_text(encoding="utf-8")))


def select_for_stages(catalog, stages, seed=None):
    """Uniform draw from current stages; does not infer or change ability."""
    validate_catalog(catalog)
    validate_stages(stages)
    candidates = [pattern for pattern in catalog["patterns"] if pattern["stage"] in stages]
    if not candidates:
        raise ValueError("No menus for the current learning stages")
    return random.Random(seed).choice(candidates)


def select_pattern(catalog, profile, seed=None):
    validate_catalog(catalog)
    if profile not in catalog["initial_stage_assignments"]:
        raise ValueError("Unknown initial profile")
    return select_for_stages(catalog, catalog["initial_stage_assignments"][profile], seed)
