"""Pydantic schemas for structured outputs."""

from pydantic import BaseModel, Field


class ChapterPrompt(BaseModel):
    """Schema for a single chapter prompt."""

    chapter_number: int = Field(description="Chapter number (1-indexed)")
    title: str = Field(description="Chapter title")
    core_questions: list[str] = Field(
        description="Key questions this chapter should answer"
    )
    research_topics: list[str] = Field(
        description="Topics requiring live web research for current info"
    )
    key_concepts: list[str] = Field(
        description="Essential concepts that must be covered"
    )
    examples_needed: list[str] = Field(
        description="Concrete examples to include"
    )
    connections: list[str] = Field(
        description="How this chapter connects to others"
    )
    potential_controversies: list[str] = Field(
        description="Debates or differing opinions to address"
    )


class ChapterPromptList(BaseModel):
    """Schema for the list of all chapter prompts."""

    chapters: list[ChapterPrompt] = Field(
        description="List of structured chapter prompts"
    )


class ChapterContent(BaseModel):
    """Schema for generated chapter content."""

    title: str = Field(description="Chapter title")
    content: str = Field(
        description="Full chapter content in markdown format for a PRINTED BOOK. "
        "MANDATORY FORMAT: Start with '## [Chapter Title]' heading, then substantive prose. "
        "FORBIDDEN - Do NOT include ANY of these: "
        "'Welcome', 'Hello', 'In this chapter', 'Let\\'s', 'We\\'ll explore', "
        "'dive in', 'get started', 'journey', 'adventure', 'excited', "
        "'tutorial', 'video', 'click', 'scroll', 'next section'. "
        "Write like a technical BOOK author (Kernighan, Knuth, Fowler), not a YouTuber or blogger."
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Sources and references used"
    )


class StyleGuide(BaseModel):
    """Schema for the style guide."""

    voice_and_tone: str = Field(
        description="Guidelines for voice and tone"
    )
    terminology_standards: str = Field(
        description="Preferred terms and acronym handling"
    )
    formatting_conventions: str = Field(
        description="Header hierarchy, code blocks, formatting rules"
    )
    content_structure: str = Field(
        description="Standard chapter structure and flow"
    )
    research_integration: str = Field(
        description="How to cite sources and handle research"
    )
    length_guidelines: str = Field(
        description="Target lengths and when to break into subsections"
    )
    full_guide: str = Field(
        description="Complete style guide in markdown format"
    )
