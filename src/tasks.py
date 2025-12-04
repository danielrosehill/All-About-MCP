"""CrewAI tasks for the MCP crash course pipeline."""

from crewai import Task
from src.agents import (
    style_guide_agent,
    curriculum_analyzer_agent,
    create_chapter_writer_agent,
    stitcher_agent,
    tts_formatter_agent,
)


def create_style_guide_task(curriculum: str) -> Task:
    """Create task for generating the style guide."""
    return Task(
        description=f"""Analyze the following curriculum and create a comprehensive
        style guide for writing the MCP crash course.

        CURRICULUM:
        {curriculum}

        The style guide must include:

        1. **Voice and Tone**
           - Define the target audience (developers familiar with AI/APIs but new to MCP)
           - Specify the tone (professional but accessible, not academic)
           - Guidelines for addressing the reader

        2. **Terminology Standards**
           - Preferred terms for MCP concepts (e.g., "MCP server" vs "MCP tool")
           - How to handle acronyms (define on first use, then use freely)
           - Technical terms that need consistent usage

        3. **Formatting Conventions**
           - Header hierarchy (H1 for parts, H2 for chapters, H3 for sections)
           - Code block usage and language annotations
           - How to format examples, tips, and warnings

        4. **Content Structure**
           - Standard chapter opening (hook, context, what you'll learn)
           - Section flow within chapters
           - Standard chapter closing (summary, key takeaways)

        5. **Research Integration**
           - How to cite sources and external references
           - When to use specific examples vs general statements
           - Currency requirements (prioritize 2024-2025 developments)

        6. **Length Guidelines**
           - Target length per chapter section
           - When to break content into subsections

        Output a complete style guide document in markdown format.""",
        expected_output="A comprehensive markdown style guide document",
        agent=style_guide_agent,
    )


def create_curriculum_analysis_task(curriculum: str) -> Task:
    """Create task for analyzing curriculum and generating chapter prompts."""
    return Task(
        description=f"""Analyze the following curriculum and create structured
        chapter prompts that will guide the chapter writers.

        CURRICULUM:
        {curriculum}

        For each major section/chapter in the curriculum, create a detailed prompt
        that includes:

        1. **Chapter Number and Title**
        2. **Core Questions to Answer** - What specific questions should this chapter address?
        3. **Required Research Topics** - What needs live research for current info?
        4. **Key Concepts to Cover** - Essential points that must be included
        5. **Examples Needed** - What concrete examples would help?
        6. **Connections** - How does this chapter connect to others?
        7. **Potential Controversies** - Any debates or differing opinions to address?

        Based on the curriculum, identify approximately 10-12 chapters that cover:
        - Part 1: What is MCP (history, origins, basics)
        - Part 2: Technical Deep Dive (transport, remote vs local)
        - Part 3: Security Considerations
        - Part 4: The Ecosystem (registries, fragmentation, tools)
        - Part 5: Use Cases and Limits
        - Part 6: Industry Landscape
        - Part 7: Enterprise and Future
        - Part 8: Development and Implementation
        - Part 9: Global and Public Sector Applications

        Output as a structured JSON array of chapter prompts.""",
        expected_output="JSON array of structured chapter prompts",
        agent=curriculum_analyzer_agent,
    )


def create_chapter_writing_task(
    chapter_num: int,
    chapter_title: str,
    chapter_prompt: dict,
    style_guide: str,
) -> Task:
    """Create a task for writing a specific chapter."""
    agent = create_chapter_writer_agent(chapter_num, chapter_title)

    return Task(
        description=f"""Write Chapter {chapter_num}: {chapter_title}

        CHAPTER REQUIREMENTS:
        {chapter_prompt}

        STYLE GUIDE (follow precisely):
        {style_guide}

        INSTRUCTIONS:
        1. Use Google Search to research current information about the topics
        2. Focus on developments from 2024-2025 as MCP is evolving rapidly
        3. Include specific examples, tools, and real implementations
        4. Address any controversies or debates fairly
        5. Follow the style guide exactly for formatting and tone
        6. Target 1500-2500 words per chapter
        7. Include code examples where relevant (properly formatted)

        RESEARCH PRIORITIES:
        - Official Anthropic MCP documentation and announcements
        - Recent blog posts and tutorials about MCP
        - GitHub repositories for MCP tools and implementations
        - Community discussions and debates about MCP
        - Enterprise adoption stories if available

        Output the complete chapter in markdown format, ready to be combined
        with other chapters.""",
        expected_output=f"Complete markdown chapter for '{chapter_title}'",
        agent=agent,
    )


def create_stitching_task(chapters: list[str], style_guide: str) -> Task:
    """Create task for combining chapters into final document."""
    chapters_text = "\n\n---CHAPTER BREAK---\n\n".join(chapters)

    return Task(
        description=f"""Combine the following chapters into a cohesive crash course
        document.

        STYLE GUIDE:
        {style_guide}

        CHAPTERS:
        {chapters_text}

        YOUR TASKS:
        1. Add a compelling introduction that sets up the entire course
        2. Create smooth transitions between chapters
        3. Ensure terminology is consistent throughout
        4. Add a conclusion that ties everything together
        5. Create a table of contents
        6. Fix any formatting inconsistencies
        7. Ensure the document flows as if written by a single author

        The final document should be:
        - Well-structured with clear navigation
        - Consistent in voice and terminology
        - Complete with intro and conclusion
        - Properly formatted in markdown

        Output the complete, integrated crash course document.""",
        expected_output="Complete integrated markdown document",
        agent=stitcher_agent,
    )


def create_tts_formatting_task(markdown_content: str) -> Task:
    """Create task for converting markdown to TTS-friendly text."""
    return Task(
        description=f"""Convert the following markdown document into TTS-optimized
        plain text suitable for audiobook generation.

        MARKDOWN CONTENT:
        {markdown_content}

        CONVERSION RULES:
        1. Remove all markdown formatting (headers become spoken transitions)
        2. Expand all abbreviations on first use (MCP -> "M-C-P, the Model Context Protocol")
        3. Convert code blocks to spoken descriptions ("The following code shows...")
        4. Replace URLs with spoken descriptions ("visit the official documentation")
        5. Break long sentences into shorter ones (15-25 words ideal for TTS)
        6. Add natural pauses with commas and periods
        7. Convert bullet points to flowing prose
        8. Handle technical terms phonetically if needed
        9. Add chapter/section announcements ("Chapter One: What is MCP")
        10. Remove or describe images/diagrams

        PACING GUIDANCE:
        - Add "[pause]" markers between major sections
        - Keep paragraphs to 3-4 sentences for natural breathing points
        - Vary sentence length for natural rhythm

        Output clean plain text optimized for text-to-speech.""",
        expected_output="TTS-optimized plain text document",
        agent=tts_formatter_agent,
    )
