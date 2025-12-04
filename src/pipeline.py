"""Main pipeline orchestration for the MCP crash course generator."""

import json
from pathlib import Path
from crewai import Crew, Process

from src.config import (
    CURRICULUM_FILE,
    STYLE_GUIDE_DIR,
    CHAPTER_PROMPTS_DIR,
    CHAPTERS_DIR,
    FULL_TEXT_DIR,
)
from src.tasks import (
    create_style_guide_task,
    create_curriculum_analysis_task,
    create_chapter_writing_task,
    create_stitching_task,
)
import re
from src.gemini_client import generate_with_grounding, generate_structured_output
from src.schemas import ChapterPromptList, ChapterContent, StyleGuide


def strip_preamble(content: str) -> str:
    """
    Remove conversational preamble from chapter content.

    Strips lines before the first markdown heading that contain
    greetings or meta-commentary.
    """
    lines = content.split('\n')

    # Patterns that indicate preamble (case-insensitive)
    preamble_patterns = [
        r'^(okay|ok|sure|alright|certainly|absolutely)',
        r'^(welcome|hello|hi|hey)\b',
        r'^(in this chapter|let\'s|we\'ll|we will|i will|i\'ll)',
        r'^(here is|here\'s|below is)',
        r'^(this chapter|the following)',
        r'^(great|perfect|excellent)[\s,!]',
        r'^(get ready|ready to|prepared to)',
        r'^(have you ever|did you know)',
        r'^(imagine|picture this)',
        r'^(before we|as we)',
        r'^(now that|so far)',
        r'^(are you|do you)',
        r'^(glad|happy|pleased|excited)',
        r'^\*\*welcome',  # Bold welcome
        r'^_welcome',  # Italic welcome
    ]

    # Find first line that looks like actual content (heading or substantial text)
    start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip().lower()

        # Skip empty lines at the start
        if not stripped:
            continue

        # If it's a markdown heading, start here
        if line.strip().startswith('#'):
            start_idx = i
            break

        # Check if line matches preamble patterns
        is_preamble = any(re.match(p, stripped) for p in preamble_patterns)

        if not is_preamble:
            # This looks like real content
            start_idx = i
            break

        # Otherwise, skip this preamble line
        start_idx = i + 1

    result = '\n'.join(lines[start_idx:])

    # Also strip any leading whitespace/newlines
    return result.lstrip('\n')


def load_curriculum() -> str:
    """Load the curriculum from file."""
    return CURRICULUM_FILE.read_text()


def run_style_guide_generation(curriculum: str) -> str:
    """Generate the style guide."""
    print("\n" + "=" * 60)
    print("PHASE 1: Generating Style Guide")
    print("=" * 60 + "\n")

    task = create_style_guide_task(curriculum)
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    style_guide = str(result)

    # Save style guide
    output_path = STYLE_GUIDE_DIR / "style-guide.md"
    output_path.write_text(style_guide)
    print(f"\nStyle guide saved to: {output_path}")

    return style_guide


def run_curriculum_analysis(curriculum: str) -> list[dict]:
    """Analyze curriculum and generate chapter prompts."""
    print("\n" + "=" * 60)
    print("PHASE 2: Analyzing Curriculum & Generating Chapter Prompts")
    print("=" * 60 + "\n")

    task = create_curriculum_analysis_task(curriculum)
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    result_text = str(result)

    # Parse JSON from result (handle markdown code blocks)
    if "```json" in result_text:
        json_start = result_text.find("```json") + 7
        json_end = result_text.find("```", json_start)
        result_text = result_text[json_start:json_end].strip()
    elif "```" in result_text:
        json_start = result_text.find("```") + 3
        json_end = result_text.find("```", json_start)
        result_text = result_text[json_start:json_end].strip()

    chapter_prompts = json.loads(result_text)

    # Save chapter prompts
    output_path = CHAPTER_PROMPTS_DIR / "chapter-prompts.json"
    output_path.write_text(json.dumps(chapter_prompts, indent=2))
    print(f"\nChapter prompts saved to: {output_path}")

    return chapter_prompts


def run_chapter_writing_with_research(
    chapter_prompts: list[dict],
    style_guide: str,
) -> list[str]:
    """Write all chapters using Gemini with search grounding."""
    print("\n" + "=" * 60)
    print("PHASE 3: Writing Chapters with Live Research")
    print("=" * 60 + "\n")

    chapters = []

    for i, prompt in enumerate(chapter_prompts, 1):
        chapter_num = prompt.get("chapter_number", i)
        chapter_title = prompt.get("title", f"Chapter {i}")

        print(f"\n--- Writing Chapter {chapter_num}: {chapter_title} ---\n")

        # Build the research-enabled prompt
        writing_prompt = f"""You are writing Chapter {chapter_num}: {chapter_title} for
        an MCP (Model Context Protocol) crash course.

        CHAPTER REQUIREMENTS:
        {json.dumps(prompt, indent=2)}

        STYLE GUIDE (follow precisely):
        {style_guide}

        INSTRUCTIONS:
        1. Research current information about the topics using web search
        2. Focus on developments from 2024-2025 as MCP is evolving rapidly
        3. Include specific examples, tools, and real implementations
        4. Address any controversies or debates fairly
        5. Follow the style guide exactly for formatting and tone
        6. Target 1500-2500 words
        7. Include code examples where relevant

        Write the complete chapter in markdown format."""

        # Use Gemini with Google Search grounding
        chapter_content = generate_with_grounding(writing_prompt, use_search=True)
        chapters.append(chapter_content)

        # Save individual chapter
        safe_title = chapter_title.lower().replace(" ", "-").replace("/", "-")
        output_path = CHAPTERS_DIR / f"chapter-{chapter_num:02d}-{safe_title}.md"
        output_path.write_text(chapter_content)
        print(f"Chapter saved to: {output_path}")

    return chapters


def run_chapter_writing_crew(
    chapter_prompts: list[dict],
    style_guide: str,
) -> list[str]:
    """Alternative: Write chapters using CrewAI (sequential, no parallel)."""
    print("\n" + "=" * 60)
    print("PHASE 3: Writing Chapters (CrewAI Sequential)")
    print("=" * 60 + "\n")

    chapters = []

    for i, prompt in enumerate(chapter_prompts, 1):
        chapter_num = prompt.get("chapter_number", i)
        chapter_title = prompt.get("title", f"Chapter {i}")

        print(f"\n--- Writing Chapter {chapter_num}: {chapter_title} ---\n")

        task = create_chapter_writing_task(
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            chapter_prompt=prompt,
            style_guide=style_guide,
        )

        crew = Crew(
            agents=[task.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        chapter_content = str(result)
        chapters.append(chapter_content)

        # Save individual chapter
        safe_title = chapter_title.lower().replace(" ", "-").replace("/", "-")
        output_path = CHAPTERS_DIR / f"chapter-{chapter_num:02d}-{safe_title}.md"
        output_path.write_text(chapter_content)
        print(f"Chapter saved to: {output_path}")

    return chapters


def run_document_stitching(chapters: list[str], style_guide: str) -> str:
    """Stitch chapters into final document."""
    print("\n" + "=" * 60)
    print("PHASE 4: Stitching Document")
    print("=" * 60 + "\n")

    task = create_stitching_task(chapters, style_guide)
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    final_document = str(result)

    # Save final document
    output_path = FULL_TEXT_DIR / "mcp-crash-course.md"
    output_path.write_text(final_document)
    print(f"\nFinal document saved to: {output_path}")

    return final_document


def run_style_guide_structured(curriculum: str) -> str:
    """Generate style guide using Gemini structured output."""
    print("\n" + "=" * 60)
    print("PHASE 1: Generating Style Guide (Structured Output)")
    print("=" * 60 + "\n")

    prompt = f"""Create a style guide for a PRINTED TECHNICAL BOOK about MCP (Model Context Protocol).

    CURRICULUM TO ANALYZE:
    {curriculum}

    This is a FORMAL TECHNICAL BOOK, similar to:
    - "The C Programming Language" by Kernighan & Ritchie
    - "Design Patterns" by the Gang of Four
    - "Clean Code" by Robert Martin

    It is NOT a blog, tutorial, YouTube video transcript, or online course.

    Create a comprehensive style guide covering:

    1. **Voice and Tone**
       - Third person or imperative mood (not "we" or "you")
       - Formal but accessible technical prose
       - No conversational fillers or greetings
       - No exclamation marks in prose

    2. **Terminology Standards**
       - Consistent MCP terminology
       - Acronym handling (define on first use)
       - Technical term glossary

    3. **Formatting Conventions**
       - Header hierarchy (## for chapters, ### for sections)
       - Code block formatting
       - How to present examples

    4. **Chapter Structure**
       - Opening: Start directly with substantive content
       - NO "In this chapter..." or "Welcome back" openers
       - Body: Logical progression of concepts
       - Closing: Brief summary, no "Next chapter" teasers

    5. **Forbidden Patterns**
       - Conversational greetings
       - Second-person address
       - Rhetorical questions as openers
       - Tutorial/video language ("click", "scroll", "let's")

    6. **Research Integration**
       - How to cite sources
       - Currency requirements (2024-2025 focus)

    The full_guide field should contain the complete style guide in markdown."""

    result = generate_structured_output(prompt, StyleGuide)

    # Save style guide
    output_path = STYLE_GUIDE_DIR / "style-guide.md"
    output_path.write_text(result.full_guide)
    print(f"Style guide saved to: {output_path}")

    return result.full_guide


def run_curriculum_analysis_structured(curriculum: str) -> list[dict]:
    """Analyze curriculum using Gemini structured output."""
    print("\n" + "=" * 60)
    print("PHASE 2: Analyzing Curriculum (Structured Output)")
    print("=" * 60 + "\n")

    prompt = f"""Analyze this MCP curriculum and create structured chapter prompts.

    CURRICULUM:
    {curriculum}

    Create 10-12 chapters covering:
    - Part 1: What is MCP (history, origins, basics)
    - Part 2: Technical Deep Dive (transport, remote vs local)
    - Part 3: Security Considerations
    - Part 4: The Ecosystem (registries, fragmentation, tools)
    - Part 5: Use Cases and Limits
    - Part 6: Industry Landscape
    - Part 7: Enterprise and Future
    - Part 8: Development and Implementation
    - Part 9: Global and Public Sector Applications

    For each chapter, provide:
    - Core questions to answer
    - Research topics needing live web search
    - Key concepts to cover
    - Examples needed
    - Connections to other chapters
    - Any controversies to address"""

    result = generate_structured_output(prompt, ChapterPromptList)

    # Convert to list of dicts for compatibility
    chapter_prompts = [ch.model_dump() for ch in result.chapters]

    # Save chapter prompts
    output_path = CHAPTER_PROMPTS_DIR / "chapter-prompts.json"
    output_path.write_text(json.dumps(chapter_prompts, indent=2))
    print(f"Chapter prompts saved to: {output_path}")
    print(f"Generated {len(chapter_prompts)} chapters")

    return chapter_prompts


def run_chapter_writing_structured(
    chapter_prompts: list[dict],
    style_guide: str,
) -> list[str]:
    """Write chapters using Gemini structured output with search grounding."""
    print("\n" + "=" * 60)
    print("PHASE 3: Writing Chapters (Structured Output + Search)")
    print("=" * 60 + "\n")

    chapters = []

    for i, prompt in enumerate(chapter_prompts, 1):
        chapter_num = prompt.get("chapter_number", i)
        chapter_title = prompt.get("title", f"Chapter {i}")

        print(f"\n--- Writing Chapter {chapter_num}: {chapter_title} ---\n")

        writing_prompt = f"""Write Chapter {chapter_num}: {chapter_title} for a PRINTED TECHNICAL BOOK about MCP.

        CHAPTER BRIEF:
        {json.dumps(prompt, indent=2)}

        STYLE GUIDE:
        {style_guide}

        === CRITICAL: BOOK FORMAT RULES ===

        This is a PRINTED TECHNICAL BOOK like "The C Programming Language" or "Design Patterns".
        It is NOT a blog post, YouTube video, tutorial, or online course.

        MANDATORY:
        1. Start content with: ## {chapter_title}
        2. First paragraph after heading must be substantive technical prose
        3. Write in third person or imperative mood, not "we" or "you"
        4. Use formal technical writing style throughout

        ABSOLUTELY FORBIDDEN (will cause rejection):
        - "Welcome" / "Hello" / "Hi there"
        - "In this chapter, we'll..." / "Let's explore..." / "We'll dive into..."
        - "Get started" / "Getting started" / "Let's get started"
        - "Journey" / "Adventure" / "Exciting"
        - "Click" / "Scroll" / "Navigate to"
        - "In the previous chapter" / "As we saw before"
        - Any second-person address ("you will learn", "you'll discover")
        - Rhetorical questions as openers ("Have you ever wondered...?")
        - Exclamation marks in prose

        GOOD OPENING EXAMPLES:
        - "The Model Context Protocol defines a standardized interface..."
        - "Security in MCP deployments requires careful consideration of..."
        - "MCP transport mechanisms fall into two primary categories..."

        BAD OPENING EXAMPLES (DO NOT USE):
        - "Welcome back! In this chapter, we'll explore..."
        - "Let's dive into the exciting world of..."
        - "Have you ever wondered how MCP handles...?"
        - "In this section, you'll learn about..."

        === CONTENT REQUIREMENTS ===
        - Research current MCP information (2024-2025)
        - Include specific tools, implementations, code examples
        - Address controversies objectively
        - Target 1500-2500 words
        - Use markdown formatting appropriately"""

        result = generate_structured_output(
            writing_prompt,
            ChapterContent,
            use_search=True,
            temperature=0.7
        )

        # Post-process to remove any preamble that slipped through
        content = result.content
        content = strip_preamble(content)

        chapters.append(content)

        # Save individual chapter (cleaned)
        safe_title = chapter_title.lower().replace(" ", "-").replace("/", "-")
        output_path = CHAPTERS_DIR / f"chapter-{chapter_num:02d}-{safe_title}.md"
        output_path.write_text(content)
        print(f"Chapter saved to: {output_path}")

        # Save sources if available
        if result.sources:
            sources_path = CHAPTERS_DIR / f"chapter-{chapter_num:02d}-sources.json"
            sources_path.write_text(json.dumps(result.sources, indent=2))

    return chapters


def run_chapter_enhancement(chapters_dir: Path = None) -> list[str]:
    """
    Enhance existing chapters with more depth and technical detail.

    Reads chapters from disk and expands them with:
    - More technical depth and implementation details
    - Additional code examples
    - Deeper analysis of concepts
    - Real-world case studies
    """
    print("\n" + "=" * 60)
    print("PHASE 3.5: Enhancing Chapters (Adding Depth)")
    print("=" * 60 + "\n")

    if chapters_dir is None:
        chapters_dir = CHAPTERS_DIR

    # Find all chapter files
    chapter_files = sorted(chapters_dir.glob("chapter-*.md"))
    if not chapter_files:
        raise ValueError(f"No chapter files found in {chapters_dir}")

    # Filter out any sources files
    chapter_files = [f for f in chapter_files if "sources" not in f.name]

    print(f"Found {len(chapter_files)} chapters to enhance")

    enhanced_chapters = []

    for chapter_path in chapter_files:
        original_content = chapter_path.read_text()
        chapter_name = chapter_path.stem

        # Extract chapter number and title from content
        lines = original_content.strip().split('\n')
        title_line = next((l for l in lines if l.startswith('## ')), "## Unknown")
        chapter_title = title_line.replace('## ', '').strip()

        print(f"\n--- Enhancing: {chapter_title} ---")
        print(f"    Original length: {len(original_content)} chars (~{len(original_content.split())} words)")

        enhancement_prompt = f"""You are enhancing a chapter from a technical book about MCP (Model Context Protocol).

The current chapter is TOO SHALLOW and reads like a superficial blog post. Your task is to
SIGNIFICANTLY EXPAND it with real technical depth.

=== CURRENT CHAPTER (to enhance) ===
{original_content}

=== ENHANCEMENT REQUIREMENTS ===

1. **DOUBLE OR TRIPLE the length** - Target 4000-6000 words minimum

2. **Add Technical Depth**:
   - Detailed explanations of HOW things work, not just WHAT they are
   - Internal architecture and design decisions
   - Edge cases and failure modes
   - Performance considerations
   - Memory and resource implications

3. **Add Implementation Details**:
   - More code examples (complete, runnable where possible)
   - Configuration snippets
   - Command-line examples
   - API request/response examples

4. **Add Real-World Context**:
   - Specific tools and their versions (2024-2025)
   - Actual company implementations if known
   - Common pitfalls practitioners encounter
   - Migration paths and upgrade considerations

5. **Add Analytical Depth**:
   - Trade-off analysis (not just "X is good")
   - Comparison with alternatives
   - When NOT to use certain approaches
   - Security implications in detail

6. **Maintain Book Quality**:
   - Keep formal technical prose (no "we", "you", "let's")
   - No greetings or preamble
   - Logical flow and clear transitions
   - Proper markdown formatting

=== FORMAT ===
Output the COMPLETE enhanced chapter in markdown, starting with the ## heading.
Preserve the original structure but expand each section significantly.
Do NOT summarize or truncate - output the FULL enhanced content."""

        enhanced_content = generate_with_grounding(enhancement_prompt, use_search=True)

        # Clean up any preamble
        enhanced_content = strip_preamble(enhanced_content)

        print(f"    Enhanced length: {len(enhanced_content)} chars (~{len(enhanced_content.split())} words)")

        # Save enhanced chapter (overwrite or create new)
        enhanced_path = chapters_dir / f"{chapter_name}-enhanced.md"
        enhanced_path.write_text(enhanced_content)
        print(f"    Saved to: {enhanced_path}")

        enhanced_chapters.append(enhanced_content)

    return enhanced_chapters


def run_simple_stitch(chapters: list[str] = None, chapters_dir: Path = None, use_enhanced: bool = True) -> str:
    """
    Simple concatenation of chapters - NO LLM processing.

    Just adds a title, TOC, and concatenates chapters with proper spacing.
    This preserves all content without risk of truncation.
    """
    print("\n" + "=" * 60)
    print("PHASE 4: Stitching Document (Direct Concatenation)")
    print("=" * 60 + "\n")

    if chapters is None:
        if chapters_dir is None:
            chapters_dir = CHAPTERS_DIR

        # Decide whether to use enhanced or original chapters
        if use_enhanced:
            chapter_files = sorted(chapters_dir.glob("chapter-*-enhanced.md"))
            if not chapter_files:
                print("No enhanced chapters found, falling back to originals")
                chapter_files = sorted(chapters_dir.glob("chapter-*.md"))
                chapter_files = [f for f in chapter_files if "sources" not in f.name and "enhanced" not in f.name]
        else:
            chapter_files = sorted(chapters_dir.glob("chapter-*.md"))
            chapter_files = [f for f in chapter_files if "sources" not in f.name and "enhanced" not in f.name]

        chapters = [f.read_text() for f in chapter_files]
        print(f"Loaded {len(chapters)} chapters from {chapters_dir}")

    # Extract chapter titles for TOC
    toc_entries = []
    for i, chapter in enumerate(chapters, 1):
        lines = chapter.strip().split('\n')
        title_line = next((l for l in lines if l.startswith('## ')), f"## Chapter {i}")
        title = title_line.replace('## ', '').strip()
        # Create anchor from title
        anchor = title.lower().replace(' ', '-').replace(':', '').replace(',', '')
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)
        toc_entries.append((title, anchor))

    # Build the document
    doc_parts = []

    # Title
    doc_parts.append("# MCP Crash Course: A Comprehensive Guide to the Model Context Protocol\n")

    # Introduction
    doc_parts.append("""
This book provides a thorough examination of the Model Context Protocol (MCP),
the open standard for connecting AI assistants to external data sources and tools.
From foundational concepts to advanced implementation patterns, this guide covers
the technical depth required for practitioners building production MCP systems.

---
""")

    # Table of Contents
    doc_parts.append("## Table of Contents\n")
    for i, (title, anchor) in enumerate(toc_entries, 1):
        doc_parts.append(f"{i}. [{title}](#{anchor})")
    doc_parts.append("\n---\n")

    # Chapters
    for chapter in chapters:
        doc_parts.append(chapter)
        doc_parts.append("\n\n---\n\n")

    # Join everything
    final_document = '\n'.join(doc_parts)

    # Save
    output_path = FULL_TEXT_DIR / "mcp-crash-course.md"
    output_path.write_text(final_document)

    word_count = len(final_document.split())
    print(f"\nFinal document: {len(final_document)} chars (~{word_count} words)")
    print(f"Saved to: {output_path}")

    return final_document


def run_stitching_direct(chapters: list[str], style_guide: str) -> str:
    """Stitch chapters using direct concatenation (not LLM to avoid truncation)."""
    # Use the simple stitch instead of LLM-based stitching
    return run_simple_stitch(chapters=chapters, use_enhanced=False)


def run_full_pipeline(use_direct_gemini: bool = True, use_structured: bool = True) -> str:
    """
    Run the complete pipeline from curriculum to final document.

    Args:
        use_direct_gemini: If True, use direct Gemini calls with search grounding.
                          If False, use CrewAI agents (less search integration).
        use_structured: If True, use Gemini structured outputs (recommended).
                       If False, use free-form text generation.

    Returns:
        Path to the final document.
    """
    # Load curriculum
    curriculum = load_curriculum()
    print(f"Loaded curriculum: {len(curriculum)} characters")

    if use_structured:
        # Use structured outputs (cleaner, no preamble)
        style_guide = run_style_guide_structured(curriculum)
        chapter_prompts = run_curriculum_analysis_structured(curriculum)
        chapters = run_chapter_writing_structured(chapter_prompts, style_guide)
        final_document = run_stitching_direct(chapters, style_guide)
    else:
        # Original CrewAI-based pipeline
        style_guide = run_style_guide_generation(curriculum)
        chapter_prompts = run_curriculum_analysis(curriculum)
        print(f"\nGenerated {len(chapter_prompts)} chapter prompts")

        if use_direct_gemini:
            chapters = run_chapter_writing_with_research(chapter_prompts, style_guide)
        else:
            chapters = run_chapter_writing_crew(chapter_prompts, style_guide)

        final_document = run_document_stitching(chapters, style_guide)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Style Guide: {STYLE_GUIDE_DIR / 'style-guide.md'}")
    print(f"  - Chapter Prompts: {CHAPTER_PROMPTS_DIR / 'chapter-prompts.json'}")
    print(f"  - Individual Chapters: {CHAPTERS_DIR}/")
    print(f"  - Final Document: {FULL_TEXT_DIR / 'mcp-crash-course.md'}")

    return str(FULL_TEXT_DIR / "mcp-crash-course.md")
