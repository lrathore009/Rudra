"""Agent profiles — data sources, voice personas, and inter-agent links."""

from dataclasses import dataclass, field

from rudra.agents.types import AgentType


@dataclass(frozen=True)
class VoiceProfile:
    """Hints for browser TTS — mapped client-side to available voices."""
    pitch: float = 1.0
    rate: float = 0.92
    voice_hints: tuple[str, ...] = ("en-US",)


@dataclass(frozen=True)
class AgentProfile:
    data_sources: tuple[str, ...]
    memory_tags: tuple[str, ...] = ()
    use_web_research: bool = False
    use_wikipedia: bool = False
    use_luxury_intel: bool = False
    related_agents: tuple[AgentType, ...] = ()
    voice: VoiceProfile = field(default_factory=VoiceProfile)
    peer_note: str = ""


AGENT_PROFILES: dict[AgentType, AgentProfile] = {
    AgentType.EXECUTIVE_ASSISTANT: AgentProfile(
        data_sources=(
            "user_memories",
            "semantic_search",
            "skills",
            "interaction_history",
            "calendar",
            "email",
            "tasks",
            "contacts",
            "slack",
            "documents",
            "weather",
            "news",
            "finance",
            "travel",
            "health",
            "transcripts",
            "commitments",
        ),
        memory_tags=("briefing", "calendar", "priority", "task"),
        use_web_research=True,
        related_agents=(AgentType.RESEARCH_ANALYST, AgentType.OPERATIONS),
        voice=VoiceProfile(pitch=0.88, rate=0.95, voice_hints=("Daniel", "Alex", "Male", "en-GB")),
        peer_note="Coordinates priorities across research and operations.",
    ),
    AgentType.RESEARCH_ANALYST: AgentProfile(
        data_sources=("web_search", "wikipedia", "user_memories", "semantic_search", "skills", "free_intel"),
        memory_tags=("research", "analysis", "fact"),
        use_web_research=True,
        use_wikipedia=True,
        related_agents=(AgentType.KNOWLEDGE_LIBRARIAN, AgentType.LUXURY_ANALYST),
        voice=VoiceProfile(pitch=1.0, rate=0.88, voice_hints=("Samantha", "Karen", "Female", "en-AU")),
        peer_note="Feeds verified findings to the knowledge librarian and luxury analyst.",
    ),
    AgentType.CONCIERGE: AgentProfile(
        data_sources=("web_search", "luxury_intel", "user_memories", "semantic_search", "free_intel"),
        memory_tags=("concierge", "reservation", "experience", "dining"),
        use_web_research=True,
        use_luxury_intel=True,
        related_agents=(AgentType.LUXURY_ANALYST, AgentType.TRAVEL),
        voice=VoiceProfile(pitch=1.05, rate=0.9, voice_hints=("Victoria", "Moira", "Female", "en-GB")),
        peer_note="Pairs with luxury and travel specialists for end-to-end experiences.",
    ),
    AgentType.LUXURY_ANALYST: AgentProfile(
        data_sources=("luxury_intel", "web_search", "user_memories", "semantic_search", "free_intel"),
        memory_tags=("luxury", "uhni", "investment", "collectible"),
        use_web_research=True,
        use_luxury_intel=True,
        related_agents=(AgentType.CONCIERGE, AgentType.RESEARCH_ANALYST),
        voice=VoiceProfile(pitch=0.95, rate=0.85, voice_hints=("Fred", "Tom", "Male", "en-US")),
        peer_note="Supplies market intelligence to concierge and research teams.",
    ),
    AgentType.TRAVEL: AgentProfile(
        data_sources=("web_search", "wikipedia", "user_memories", "semantic_search", "luxury_intel", "free_intel"),
        memory_tags=("travel", "itinerary", "flight", "hotel", "visa"),
        use_web_research=True,
        use_wikipedia=True,
        use_luxury_intel=True,
        related_agents=(AgentType.CONCIERGE, AgentType.OPERATIONS),
        voice=VoiceProfile(pitch=1.02, rate=0.93, voice_hints=("Tessa", "Allison", "Female", "en-US")),
        peer_note="Aligns itineraries with concierge bookings and operational logistics.",
    ),
    AgentType.KNOWLEDGE_LIBRARIAN: AgentProfile(
        data_sources=("semantic_search", "user_memories", "wikipedia", "interaction_history", "free_intel"),
        memory_tags=("knowledge", "note", "reference", "document"),
        use_wikipedia=True,
        related_agents=(AgentType.RESEARCH_ANALYST, AgentType.WRITING),
        voice=VoiceProfile(pitch=0.92, rate=0.87, voice_hints=("Serena", "Kate", "Female", "en-GB")),
        peer_note="Organizes knowledge consumed by research and writing agents.",
    ),
    AgentType.WRITING: AgentProfile(
        data_sources=("user_memories", "semantic_search", "interaction_history", "free_intel"),
        memory_tags=("writing", "tone", "draft", "email", "letter"),
        related_agents=(AgentType.PRESENTATION, AgentType.EXECUTIVE_ASSISTANT),
        voice=VoiceProfile(pitch=1.08, rate=0.9, voice_hints=("Zira", "Susan", "Female", "en-US")),
        peer_note="Shapes prose that feeds presentations and executive comms.",
    ),
    AgentType.PRESENTATION: AgentProfile(
        data_sources=("user_memories", "semantic_search", "web_search", "free_intel"),
        memory_tags=("presentation", "slide", "deck", "briefing"),
        use_web_research=True,
        related_agents=(AgentType.WRITING, AgentType.RESEARCH_ANALYST),
        voice=VoiceProfile(pitch=0.9, rate=0.86, voice_hints=("Rishi", "Oliver", "Male", "en-IN")),
        peer_note="Structures narratives sourced from writing and research.",
    ),
    AgentType.OPERATIONS: AgentProfile(
        data_sources=("user_memories", "semantic_search", "web_search", "interaction_history", "free_intel"),
        memory_tags=("operations", "vendor", "household", "maintenance"),
        use_web_research=True,
        related_agents=(AgentType.EXECUTIVE_ASSISTANT, AgentType.TRAVEL),
        voice=VoiceProfile(pitch=0.85, rate=0.94, voice_hints=("Aaron", "Nathan", "Male", "en-US")),
        peer_note="Handles logistics alongside executive and travel planning.",
    ),
}
