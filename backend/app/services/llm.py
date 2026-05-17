from __future__ import annotations

"""
LLM Service Abstraction Layer.

This module provides a thin wrapper around an LLM provider.
In Stage 1, this returns mock/default responses.
Stage 3 (post-MVP) will integrate with DeepSeek / LiteLLM gateway.

See: development-log Stage 3 — AI 题库流水线 for the full roadmap.
"""

from typing import Optional


class ChatService:
    """Minimal LLM interaction service. Placeholder for Stage 3."""

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    async def classify_question(self, raw_text: str) -> dict:
        """Given raw exam text, return proposed classification.
        Returns dict with keys: curriculum, subject, topic_path, type, difficulty, stem, etc."""
        # TODO(Stage 3): Replace with actual LLM call via LiteLLM gateway
        return {
            "curriculum": "FAKAO",
            "subject": "unknown",
            "topic_path": [],
            "type": "single_choice",
            "difficulty": 3,
            "stem": raw_text,
            "options": None,
            "answer": None,
            "rubric": None,
            "solution": None,
        }

    async def generate_analysis(self, stem: str, answer: Optional[str] = None) -> dict:
        """Generate AI breakdown for a question.
        Returns dict with summary, key_concepts, common_mistakes."""
        # TODO(Stage 3): Replace with actual LLM call
        return {
            "summary": "AI analysis not yet available (Stage 3).",
            "key_concepts": [],
            "common_mistakes": [],
        }

    async def is_available(self) -> bool:
        """Check if LLM provider is configured and reachable."""
        return self.provider != "mock"