"""Agent type identifiers."""

from enum import Enum


class AgentType(str, Enum):
    EXECUTIVE_ASSISTANT = "executive_assistant"
    RESEARCH_ANALYST = "research_analyst"
    CONCIERGE = "concierge"
    LUXURY_ANALYST = "luxury_analyst"
    TRAVEL = "travel"
    KNOWLEDGE_LIBRARIAN = "knowledge_librarian"
    WRITING = "writing"
    PRESENTATION = "presentation"
    OPERATIONS = "operations"
