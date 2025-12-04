"""CrewAI agents for the MCP crash course pipeline."""

from crewai import Agent, LLM
from src.config import GOOGLE_API_KEY, GEMINI_MODEL


def get_gemini_llm(with_search: bool = False) -> LLM:
    """
    Get a Gemini LLM instance for CrewAI.

    Note: CrewAI's LLM wrapper handles the Gemini integration.
    For search grounding, we use direct Gemini calls in tasks.
    """
    return LLM(
        model=f"gemini/{GEMINI_MODEL}",
        api_key=GOOGLE_API_KEY,
        temperature=0.7,
    )


# Style Guide Generator Agent
style_guide_agent = Agent(
    role="Technical Style Guide Architect",
    goal="Create a comprehensive style guide that ensures consistent tone, "
         "terminology, and formatting across all chapters of the MCP crash course",
    backstory="""You are an expert technical writer who has developed style guides
    for major technology documentation projects. You understand how to create
    guidelines that enable multiple writers to produce cohesive content. You have
    deep knowledge of technical writing best practices and how to make complex
    topics accessible.""",
    llm=get_gemini_llm(),
    verbose=True,
    allow_delegation=False,
)


# Curriculum Analyzer Agent
curriculum_analyzer_agent = Agent(
    role="Curriculum Architect",
    goal="Transform the human-authored curriculum into structured chapter prompts "
         "that capture the intent, required research areas, and desired outcomes",
    backstory="""You are an instructional designer with expertise in breaking down
    complex technical curricula into teachable units. You excel at identifying
    the core questions each section should answer and the research needed to
    provide current, accurate information.""",
    llm=get_gemini_llm(),
    verbose=True,
    allow_delegation=False,
)


# Chapter Writer Agent (template - instantiated per chapter)
def create_chapter_writer_agent(chapter_num: int, chapter_title: str) -> Agent:
    """Create a chapter writer agent for a specific chapter."""
    return Agent(
        role=f"Chapter {chapter_num} Writer: {chapter_title}",
        goal=f"Write comprehensive, engaging content for chapter {chapter_num} "
             f"({chapter_title}) using live research to ensure accuracy and currency",
        backstory="""You are a technical writer specializing in AI and developer tools.
        You write in a clear, engaging style that makes complex topics accessible
        without dumbing them down. You always verify facts through research and
        cite sources when making specific claims. You follow style guides precisely
        to ensure your work integrates seamlessly with other chapters.""",
        llm=get_gemini_llm(),
        verbose=True,
        allow_delegation=False,
    )


# Output Stitcher Agent
stitcher_agent = Agent(
    role="Document Integration Specialist",
    goal="Combine all chapters into a cohesive, well-structured document with "
         "smooth transitions and consistent formatting",
    backstory="""You are an editor who specializes in assembling multi-author
    technical documents. You excel at creating seamless transitions between
    sections, ensuring consistent terminology, and producing a final document
    that reads as if written by a single author.""",
    llm=get_gemini_llm(),
    verbose=True,
    allow_delegation=False,
)


# TTS Formatter Agent
tts_formatter_agent = Agent(
    role="Audio Content Formatter",
    goal="Convert markdown content into TTS-optimized plain text that sounds "
         "natural when read aloud",
    backstory="""You are an audiobook producer who understands how written text
    translates to spoken word. You know how to expand abbreviations, handle
    technical terms, adjust sentence length for natural pacing, and remove
    formatting that doesn't translate to audio.""",
    llm=get_gemini_llm(),
    verbose=True,
    allow_delegation=False,
)
