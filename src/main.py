#!/usr/bin/env python3
"""
MCP Crash Course Generator

A multi-agent pipeline that transforms a curriculum into a complete crash course
with PDF and audiobook outputs.

Usage:
    # Generate everything (book + PDF + audiobook)
    python -m src.main --all

    # Generate just the book
    python -m src.main --book

    # Generate PDF from existing markdown
    python -m src.main --pdf

    # Generate audiobook from existing markdown
    python -m src.main --audio

    # Run specific phases
    python -m src.main --style-guide
    python -m src.main --chapters

    # Enhance existing chapters and re-stitch
    python -m src.main --enhance          # Enhance + stitch
    python -m src.main --stitch           # Just stitch (use existing enhanced if available)
    python -m src.main --stitch-original  # Stitch original chapters (no enhancement)
"""

import argparse
import sys
from pathlib import Path

from src.config import validate_config, FULL_TEXT_DIR, PDF_DIR, AUDIO_DIR, CHAPTERS_DIR
from src.pipeline import (
    load_curriculum,
    run_style_guide_generation,
    run_curriculum_analysis,
    run_chapter_writing_with_research,
    run_document_stitching,
    run_full_pipeline,
    run_chapter_enhancement,
    run_simple_stitch,
)
from src.pdf_converter import convert_to_pdf
from src.audiobook import generate_audiobook


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP crash course from curriculum",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m src.main --all          Generate everything
    python -m src.main --book         Generate book only
    python -m src.main --pdf          Generate PDF from existing markdown
    python -m src.main --audio        Generate audiobook from existing markdown
    python -m src.main --enhance      Enhance existing chapters with more depth
    python -m src.main --stitch       Stitch chapters into final document
        """
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate everything: book, PDF, and audiobook"
    )
    parser.add_argument(
        "--book",
        action="store_true",
        help="Generate the book (style guide + chapters + stitch)"
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate PDF from existing markdown"
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Generate audiobook from existing markdown"
    )
    parser.add_argument(
        "--style-guide",
        action="store_true",
        help="Generate only the style guide"
    )
    parser.add_argument(
        "--chapters",
        action="store_true",
        help="Generate chapters (requires existing style guide)"
    )
    parser.add_argument(
        "--use-crewai",
        action="store_true",
        help="Use CrewAI for chapter writing instead of direct Gemini calls"
    )
    parser.add_argument(
        "--no-structured",
        action="store_true",
        help="Disable structured outputs (use free-form text generation)"
    )
    parser.add_argument(
        "--voice-reference",
        type=str,
        help="URL to reference audio for voice cloning in audiobook"
    )

    args = parser.parse_args()

    # Default to --all if no arguments provided
    if not any([args.all, args.book, args.pdf, args.audio,
                args.style_guide, args.chapters]):
        args.all = True

    try:
        # Validate configuration
        validate_config()

        if args.all or args.book:
            print("\n" + "=" * 70)
            print("  MCP CRASH COURSE GENERATOR")
            print("  Multi-agent pipeline with Gemini + Google Search grounding")
            print("=" * 70)

            # Run full book pipeline
            markdown_path = run_full_pipeline(
                use_direct_gemini=not args.use_crewai,
                use_structured=not args.no_structured
            )

            if args.all:
                # Generate PDF
                print("\n" + "=" * 70)
                print("  GENERATING PDF")
                print("=" * 70)
                convert_to_pdf()

                # Generate audiobook
                print("\n" + "=" * 70)
                print("  GENERATING AUDIOBOOK")
                print("=" * 70)
                generate_audiobook(audio_prompt=args.voice_reference)

        elif args.pdf:
            markdown_path = FULL_TEXT_DIR / "mcp-crash-course.md"
            if not markdown_path.exists():
                print(f"Error: Markdown file not found: {markdown_path}")
                print("Run --book first to generate the content.")
                sys.exit(1)
            convert_to_pdf(markdown_path)

        elif args.audio:
            markdown_path = FULL_TEXT_DIR / "mcp-crash-course.md"
            if not markdown_path.exists():
                print(f"Error: Markdown file not found: {markdown_path}")
                print("Run --book first to generate the content.")
                sys.exit(1)
            generate_audiobook(
                markdown_path=markdown_path,
                audio_prompt=args.voice_reference
            )

        elif args.style_guide:
            curriculum = load_curriculum()
            run_style_guide_generation(curriculum)

        elif args.chapters:
            from src.config import STYLE_GUIDE_DIR, CHAPTER_PROMPTS_DIR
            import json

            style_guide_path = STYLE_GUIDE_DIR / "style-guide.md"
            prompts_path = CHAPTER_PROMPTS_DIR / "chapter-prompts.json"

            if not style_guide_path.exists():
                print("Error: Style guide not found. Run --style-guide first.")
                sys.exit(1)

            if not prompts_path.exists():
                print("Error: Chapter prompts not found.")
                print("Run the full --book pipeline or generate them separately.")
                sys.exit(1)

            style_guide = style_guide_path.read_text()
            chapter_prompts = json.loads(prompts_path.read_text())

            if args.use_crewai:
                from src.pipeline import run_chapter_writing_crew
                run_chapter_writing_crew(chapter_prompts, style_guide)
            else:
                run_chapter_writing_with_research(chapter_prompts, style_guide)

        print("\n" + "=" * 70)
        print("  COMPLETE!")
        print("=" * 70)
        print("\nOutputs:")
        print(f"  Book:      {FULL_TEXT_DIR / 'mcp-crash-course.md'}")
        if args.all or args.pdf:
            print(f"  PDF:       {PDF_DIR / 'mcp-crash-course.pdf'}")
        if args.all or args.audio:
            print(f"  Audiobook: {AUDIO_DIR / 'mcp-crash-course.mp3'}")

    except ValueError as e:
        print(f"\nConfiguration Error:\n{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
