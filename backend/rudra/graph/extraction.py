"""Entity extraction — rule-based with optional LLM enrichment."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rudra.graph.models import EntityType, GraphRelationType
from rudra.graph.seed import SEED_ENTITIES


@dataclass
class ExtractedEntity:
    name: str
    entity_type: str
    confidence: float
    relation_type: str = GraphRelationType.MENTIONS.value


_KNOWN = {item["name"].lower(): item for item in SEED_ENTITIES}

# Title-case multi-word names (e.g. "FutureForge Engineering")
_PROPER_NOUN = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+|[\s][A-Z][a-z]+)+)\b")


def extract_entities_rule_based(text: str) -> list[ExtractedEntity]:
    """Match known ecosystem entities and simple proper-noun patterns."""
    found: dict[str, ExtractedEntity] = {}
    lower = text.lower()

    for key, item in _KNOWN.items():
        if key in lower:
            found[item["name"]] = ExtractedEntity(
                name=item["name"],
                entity_type=item["entity_type"],
                confidence=0.95,
            )

    for match in _PROPER_NOUN.finditer(text):
        name = match.group(1).strip()
        if len(name) < 4 or name.lower() in _KNOWN:
            continue
        if name in found:
            continue
        found[name] = ExtractedEntity(
            name=name,
            entity_type=EntityType.TOPIC.value,
            confidence=0.55,
        )

    return list(found.values())


async def extract_entities(text: str, *, use_llm: bool = False) -> list[ExtractedEntity]:
    """Rule-based extraction first; optional LLM pass when enabled."""
    results = extract_entities_rule_based(text)
    if not use_llm:
        return results

    try:
        from rudra.brain.orchestrator import Brain

        brain = Brain()
        prompt = (
            "Extract named entities from the text. Return JSON array of objects with "
            "name, entity_type (person|company|project|app|topic|goal|task|decision|event). "
            f"Text:\n{text[:3000]}"
        )
        completion = await brain.think([{"role": "user", "content": prompt}], model_tier="fast")
        import json

        extra = json.loads(completion.content)
        if isinstance(extra, list):
            for item in extra:
                name = str(item.get("name", "")).strip()
                if not name:
                    continue
                et = str(item.get("entity_type", EntityType.TOPIC.value))
                if name not in {r.name for r in results}:
                    results.append(ExtractedEntity(name=name, entity_type=et, confidence=0.7))
    except Exception:
        pass

    return results
