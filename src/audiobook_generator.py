#!/usr/bin/env python3
"""
Audiobook Generator for MCP Crash Course
Uses Gemini 3 for text preprocessing and Chatterbox via Replicate for TTS with voice cloning.
"""

import os
import re
import time
import requests
from pathlib import Path
import replicate

# Configuration
TTS_MODEL = "resemble-ai/chatterbox"

BASE_DIR = Path(__file__).parent.parent
CHAPTERS_DIR = BASE_DIR / "outputs" / "chapters"
AUDIO_OUTPUT_DIR = BASE_DIR / "outputs" / "audio"
VOICE_REFERENCE = BASE_DIR / "inputs" / "voices" / "corn-1min.mp3"

# TTS Settings
TTS_SETTINGS = {
    "exaggeration": 0.5,  # Neutral
    "cfg_weight": 0.5,    # Default pace
    "temperature": 0.8,
    "seed": 0             # Random
}

# Ensure output directory exists
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_chapters() -> list[tuple[str, str]]:
    """Load all chapter markdown files in order."""
    chapters = []
    for chapter_file in sorted(CHAPTERS_DIR.glob("chapter-*.md")):
        with open(chapter_file, "r") as f:
            content = f.read()
        chapters.append((chapter_file.stem, content))
    return chapters


def clean_markdown_for_tts(content: str) -> str:
    """Remove markdown formatting and prepare text for TTS."""
    # Remove image references
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

    # Remove code blocks
    content = re.sub(r'```[\s\S]*?```', '[code example omitted]', content)
    content = re.sub(r'`[^`]+`', '', content)

    # Convert headers to spoken form
    content = re.sub(r'^#{1,6}\s+(.+)$', r'\1.', content, flags=re.MULTILINE)

    # Remove bold/italic markers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    content = re.sub(r'__([^_]+)__', r'\1', content)
    content = re.sub(r'_([^_]+)_', r'\1', content)

    # Remove links but keep text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

    # Remove bullet points
    content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)

    # Remove horizontal rules
    content = re.sub(r'^---+$', '', content, flags=re.MULTILINE)

    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()

    return content


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """Split text into chunks suitable for TTS API."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def upload_voice_reference() -> str:
    """Convert voice reference to data URL for Replicate."""
    import base64
    import mimetypes

    mime_type = mimetypes.guess_type(str(VOICE_REFERENCE))[0] or "audio/mpeg"

    with open(VOICE_REFERENCE, "rb") as f:
        audio_data = f.read()

    base64_data = base64.b64encode(audio_data).decode("utf-8")
    return f"data:{mime_type};base64,{base64_data}"


def generate_audio_chunk(text: str, voice_url: str, output_path: Path) -> bool:
    """Generate audio for a text chunk using Chatterbox."""
    try:
        output = replicate.run(
            TTS_MODEL,
            input={
                "prompt": text,
                "audio_prompt": voice_url,
                **TTS_SETTINGS
            }
        )

        if output:
            response = requests.get(output)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
        return False
    except Exception as e:
        print(f"    ⚠ TTS generation failed: {e}")
        return False


def concatenate_audio_files(audio_files: list[Path], output_path: Path):
    """Concatenate multiple audio files into one using ffmpeg."""
    if not audio_files:
        return

    # Create file list for ffmpeg
    list_file = output_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for audio_file in audio_files:
            f.write(f"file '{audio_file.absolute()}'\n")

    # Run ffmpeg
    import subprocess
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True)

    # Cleanup
    list_file.unlink()
    for f in audio_files:
        f.unlink()


def simple_tts_optimize(text: str) -> str:
    """Simple text optimization for TTS without LLM."""
    # Expand common abbreviations
    replacements = {
        "MCP": "M C P",
        "API": "A P I",
        "APIs": "A P Is",
        "JSON": "Jason",
        "HTTP": "H T T P",
        "HTTPS": "H T T P S",
        "URL": "U R L",
        "URLs": "U R Ls",
        "CLI": "C L I",
        "SDK": "S D K",
        "SSE": "S S E",
        "STDIO": "standard I O",
        "AI": "A I",
        "LLM": "L L M",
        "LLMs": "L L Ms",
        "e.g.": "for example",
        "i.e.": "that is",
        "etc.": "et cetera",
    }

    for abbr, expansion in replacements.items():
        text = text.replace(abbr, expansion)

    return text


def main():
    # Load chapters
    chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapters")
    print(f"TTS model: {TTS_MODEL}")
    print(f"Voice reference: {VOICE_REFERENCE}")
    print("-" * 50)

    # Upload voice reference once
    print("Preparing voice reference...")
    voice_url = upload_voice_reference()
    print(f"  ✓ Voice ready")

    all_chapter_audios = []

    for chapter_name, content in chapters:
        chapter_audio_path = AUDIO_OUTPUT_DIR / f"{chapter_name}.wav"

        # Skip if already exists
        if chapter_audio_path.exists():
            print(f"{chapter_name} already exists, skipping...")
            all_chapter_audios.append(chapter_audio_path)
            continue

        print(f"Processing {chapter_name}...")
        start_time = time.time()

        # Step 1: Clean markdown
        print("  → Cleaning markdown...")
        clean_text = clean_markdown_for_tts(content)

        # Step 2: Simple TTS optimization
        print("  → Optimizing for speech...")
        optimized_text = simple_tts_optimize(clean_text)

        # Step 3: Chunk text
        chunks = chunk_text(optimized_text)
        print(f"  → Split into {len(chunks)} chunks")

        # Step 4: Generate audio for each chunk
        chunk_audio_files = []
        for i, chunk in enumerate(chunks):
            chunk_path = AUDIO_OUTPUT_DIR / f"{chapter_name}_chunk_{i:03d}.wav"
            print(f"    • Generating chunk {i+1}/{len(chunks)}...")

            success = generate_audio_chunk(chunk, voice_url, chunk_path)
            if success:
                chunk_audio_files.append(chunk_path)
            else:
                print(f"      ⚠ Failed to generate chunk {i+1}")

            time.sleep(1)  # Rate limiting

        # Step 5: Concatenate chunks
        if chunk_audio_files:
            print(f"  → Concatenating {len(chunk_audio_files)} audio files...")
            concatenate_audio_files(chunk_audio_files, chapter_audio_path)
            all_chapter_audios.append(chapter_audio_path)

        elapsed = time.time() - start_time
        print(f"  ✓ Completed {chapter_name} ({elapsed:.1f}s)")
        print()

    # Final concatenation of all chapters
    if all_chapter_audios:
        print("-" * 50)
        print("Creating final audiobook...")
        final_output = AUDIO_OUTPUT_DIR / "mcp-crash-course-audiobook.wav"

        # For final, we don't delete the chapter files
        list_file = AUDIO_OUTPUT_DIR / "final_concat_list.txt"
        with open(list_file, "w") as f:
            for audio_file in all_chapter_audios:
                f.write(f"file '{audio_file.absolute()}'\n")

        import subprocess
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(final_output)
        ]
        subprocess.run(cmd, capture_output=True)
        list_file.unlink()

        print(f"  ✓ Final audiobook saved to {final_output}")

    print("-" * 50)
    print("Audiobook generation complete!")


if __name__ == "__main__":
    main()
