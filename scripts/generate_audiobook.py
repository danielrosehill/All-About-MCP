#!/usr/bin/env python3
"""
Audiobook Generator for MCP Crash Course

Uses Microsoft Edge TTS to convert markdown to audio.
"""

import asyncio
import re
import sys
from pathlib import Path

import edge_tts

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_MD = PROJECT_ROOT / "outputs" / "full-text" / "mcp-crash-course.md"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "audio"
TTS_TEXT_FILE = OUTPUT_DIR / "tts-formatted-text.txt"
OUTPUT_MP3 = OUTPUT_DIR / "mcp-crash-course.mp3"

# Edge TTS settings
VOICE = "en-GB-RyanNeural"  # British male voice


def markdown_to_text(markdown_text: str) -> str:
    """
    Convert markdown to plain text for TTS.
    """
    text = markdown_text

    # Remove YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)

    # Remove LaTeX commands
    text = re.sub(r'\\newpage', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Remove image references
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove figure captions
    text = re.sub(r'\*\*Figure \d+\.\d+:\*\*.*?(?=\n\n|\n#|$)', '', text, flags=re.DOTALL)

    # Convert markdown links to just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Replace code blocks with spoken description
    def replace_code_block(match):
        lang = match.group(1) or "code"
        return f"[{lang} code example omitted for audio]"
    text = re.sub(r'```(\w*)\n.*?```', replace_code_block, text, flags=re.DOTALL)

    # Remove inline code but keep text
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Convert h1 headings
    def format_h1(match):
        title = match.group(1).strip()
        return f'\n\n{title}.\n\n'
    text = re.sub(r'^#\s+(.+)$', format_h1, text, flags=re.MULTILINE)

    # Convert h2 headings
    def format_h2(match):
        title = match.group(1).strip()
        return f'\n\n{title}.\n\n'
    text = re.sub(r'^##\s+(.+)$', format_h2, text, flags=re.MULTILINE)

    # Convert h3+ headings
    def format_subsection(match):
        title = match.group(1).strip()
        return f'\n\n{title}.\n\n'
    text = re.sub(r'^#{3,6}\s+(.+)$', format_subsection, text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Convert bullet points
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Expand abbreviations for better pronunciation
    abbreviations = {
        'e.g.': 'for example',
        'i.e.': 'that is',
        'etc.': 'and so on',
        'vs.': 'versus',
        'API': 'A P I',
        'APIs': 'A P Is',
        'JSON': 'Jason',
        'JSON-RPC': 'Jason R P C',
        'STDIO': 'standard I O',
        'stdio': 'standard I O',
        'SSE': 'S S E',
        'HTTP': 'H T T P',
        'HTTPS': 'H T T P S',
        'URL': 'U R L',
        'URLs': 'U R Ls',
        'URI': 'U R I',
        'LLM': 'L L M',
        'LLMs': 'L L Ms',
        'AI': 'A I',
        'IDE': 'I D E',
        'IDEs': 'I D Es',
        'SDK': 'S D K',
        'SDKs': 'S D Ks',
        'CLI': 'C L I',
        'MCP': 'M C P',
        'REST': 'rest',
        'GraphQL': 'Graph Q L',
        'OAuth': 'O Auth',
        'RAG': 'rag',
        'NPM': 'N P M',
        'npm': 'N P M',
        'UUID': 'U U I D',
    }

    for abbr, expansion in abbreviations.items():
        text = re.sub(rf'\b{re.escape(abbr)}\b', expansion, text)

    # Handle special characters
    text = text.replace('→', ' to ')
    text = text.replace('←', ' from ')
    text = text.replace('×', ' times ')
    text = text.replace('&', ' and ')
    text = text.replace('%', ' percent')

    # Clean up horizontal rules
    text = re.sub(r'^---+$', '\n', text, flags=re.MULTILINE)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))
    text = text.strip()

    return text


async def generate_audio(text: str, output_path: Path) -> bool:
    """
    Generate audio from text using Edge TTS.
    """
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(output_path))
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("MCP Crash Course Audiobook Generator (Edge TTS)")
    print("=" * 60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Read markdown
    print("\n[Step 1] Reading markdown...")
    if not INPUT_MD.exists():
        print(f"Error: Input file not found: {INPUT_MD}")
        sys.exit(1)

    with open(INPUT_MD, 'r') as f:
        markdown_content = f.read()
    print(f"  Read {len(markdown_content):,} characters")

    # Step 2: Convert to plain text
    print("\n[Step 2] Converting to TTS-friendly text...")
    tts_text = markdown_to_text(markdown_content)

    with open(TTS_TEXT_FILE, 'w') as f:
        f.write(tts_text)
    print(f"  Generated {len(tts_text):,} characters")
    print(f"  Saved to: {TTS_TEXT_FILE}")

    # Step 3: Generate audio
    print(f"\n[Step 3] Generating audio with {VOICE}...")
    print("  This may take a few minutes...")

    try:
        asyncio.run(generate_audio(tts_text, OUTPUT_MP3))
        print(f"\n  Output: {OUTPUT_MP3}")
        print(f"  Size: {OUTPUT_MP3.stat().st_size / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"\nError generating audio: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("AUDIOBOOK GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
