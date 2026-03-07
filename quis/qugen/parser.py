"""
Parse LLM output into InsightCard list (tags [INSIGHT] ... [/INSIGHT] and REASON/QUESTION/BREAKDOWN/MEASURE).
"""

from __future__ import annotations

import re
from .models import InsightCard


def parse_insight_cards_from_text(text: str) -> list[InsightCard]:
    """
    Extract Insight Cards from LLM response.
    Looks for [INSIGHT]...[/INSIGHT] blocks and REASON:, QUESTION:, BREAKDOWN:, MEASURE: lines.
    """
    cards: list[InsightCard] = []
    # Split by [INSIGHT] ... [/INSIGHT]
    pattern = re.compile(r"\[INSIGHT\](.*?)\[/INSIGHT\]", re.DOTALL | re.IGNORECASE)
    for block in pattern.findall(text):
        card = _parse_one_card(block.strip())
        if card and card.question and card.measure:
            cards.append(card)

    # If no tags, try to parse consecutive REASON/QUESTION/BREAKDOWN/MEASURE blocks
    if not cards:
        cards = _parse_blocks_without_tags(text)

    return cards


def _parse_one_card(block: str) -> InsightCard | None:
    reason = _extract_field(block, "REASON")
    question = _extract_field(block, "QUESTION")
    breakdown = _extract_field(block, "BREAKDOWN")
    measure = _extract_field(block, "MEASURE")
    if not question:
        return None
    return InsightCard(
        question=question,
        reason=reason or "",
        breakdown=breakdown or "",
        measure=measure or "",
    )


def _extract_field(block: str, key: str) -> str:
    key_upper = key + ":"
    key_lower = key.lower() + ":"
    for line in block.split("\n"):
        line = line.strip()
        if line.upper().startswith(key_upper):
            return line.split(":", 1)[1].strip()
        if line.lower().startswith(key_lower):
            return line.split(":", 1)[1].strip()
    return ""


def _parse_blocks_without_tags(text: str) -> list[InsightCard]:
    """Fallback: look for 'Insight Card N' or consecutive REASON/QUESTION/BREAKDOWN/MEASURE."""
    cards = []
    # Split by "Insight Card" lines
    chunks = re.split(r"\n\s*Insight\s+Card\s+\d+\s*\n", text, flags=re.IGNORECASE)
    for chunk in chunks:
        if not chunk.strip():
            continue
        c = _parse_one_card(chunk)
        if c and c.question:
            cards.append(c)
    if cards:
        return cards
    # Single block
    c = _parse_one_card(text)
    if c and c.question:
        return [c]
    return []
