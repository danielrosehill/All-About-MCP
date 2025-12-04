"""Audiobook generation using Chatterbox TTS via Replicate."""

import re
import time
from pathlib import Path
from typing import Optional
import requests
import replicate

from src.config import (
    FULL_TEXT_DIR,
    AUDIO_DIR,
    REPLICATE_API_TOKEN,
    CHATTERBOX_MODEL,
    TTS_EXAGGERATION,
    TTS_CFG_WEIGHT,
    TTS_TEMPERATURE,
)
from src.tasks import create_tts_formatting_task
from crewai import Crew, Process


# Maximum text length per Chatterbox request (conservative estimate)
MAX_CHUNK_LENGTH = 2000


def format_for_tts(markdown_content: str) -> str:
    """
    Convert markdown to TTS-friendly plain text using CrewAI agent.

    Args:
        markdown_content: The markdown document to convert

    Returns:
        TTS-optimized plain text
    """
    print("Formatting content for TTS...")

    task = create_tts_formatting_task(markdown_content)
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def format_for_tts_simple(markdown_content: str) -> str:
    """
    Simple markdown to TTS conversion without using an agent.

    Args:
        markdown_content: The markdown document to convert

    Returns:
        TTS-friendly plain text
    """
    text = markdown_content

    # Remove code blocks (describe them instead)
    text = re.sub(
        r'```[\w]*\n(.*?)\n```',
        r'[Code example omitted for audio version]',
        text,
        flags=re.DOTALL
    )

    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Convert headers to spoken transitions
    text = re.sub(r'^# (.+)$', r'\n[pause]\nPart: \1\n[pause]\n', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'\n[pause]\nChapter: \1\n[pause]\n', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'\nSection: \1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'\n\1\n', text, flags=re.MULTILINE)

    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'__(.+?)__', r'\1', text)  # Bold
    text = re.sub(r'_(.+?)_', r'\1', text)  # Italic

    # Convert links to spoken form
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'[Image: \1]', text)

    # Convert bullet points to prose
    text = re.sub(r'^[\-\*] (.+)$', r'\1.', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\. (.+)$', r'\1.', text, flags=re.MULTILINE)

    # Expand common abbreviations
    abbreviations = {
        'MCP': 'M-C-P',
        'API': 'A-P-I',
        'APIs': 'A-P-Is',
        'SSE': 'S-S-E',
        'STDIO': 'standard I-O',
        'CLI': 'command line interface',
        'JSON': 'J-SON',
        'HTTP': 'H-T-T-P',
        'HTTPS': 'H-T-T-P-S',
        'URL': 'U-R-L',
        'URLs': 'U-R-Ls',
        'SDK': 'S-D-K',
        'SDKs': 'S-D-Ks',
        'LLM': 'L-L-M',
        'LLMs': 'L-L-Ms',
        'AI': 'A-I',
        'vs': 'versus',
        'e.g.': 'for example',
        'i.e.': 'that is',
        'etc.': 'and so on',
    }

    for abbr, expansion in abbreviations.items():
        # Only expand if it's a standalone word
        text = re.sub(rf'\b{abbr}\b', expansion, text)

    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove [pause] markers for actual TTS (they were for structure)
    # Chatterbox handles pacing naturally
    text = text.replace('[pause]', '')

    return text.strip()


def chunk_text(text: str, max_length: int = MAX_CHUNK_LENGTH) -> list[str]:
    """
    Split text into chunks suitable for TTS processing.

    Args:
        text: The text to chunk
        max_length: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    chunks = []
    paragraphs = text.split('\n\n')

    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If paragraph itself is too long, split by sentences
        if len(para) > max_length:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 <= max_length:
                    current_chunk += " " + sentence if current_chunk else sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        elif len(current_chunk) + len(para) + 2 <= max_length:
            current_chunk += "\n\n" + para if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate_audio_chunk(
    text: str,
    audio_prompt: Optional[str] = None,
    exaggeration: float = TTS_EXAGGERATION,
    cfg_weight: float = TTS_CFG_WEIGHT,
    temperature: float = TTS_TEMPERATURE,
) -> str:
    """
    Generate audio for a single text chunk using Chatterbox.

    Args:
        text: Text to synthesize
        audio_prompt: Optional reference audio URL for voice cloning
        exaggeration: Emotion control (0.5 = neutral)
        cfg_weight: Pace control
        temperature: Randomness

    Returns:
        URL to generated audio file
    """
    input_params = {
        "prompt": text,
        "exaggeration": exaggeration,
        "cfg_weight": cfg_weight,
        "temperature": temperature,
        "seed": 0,  # Random seed for variety
    }

    if audio_prompt:
        input_params["audio_prompt"] = audio_prompt

    output = replicate.run(CHATTERBOX_MODEL, input=input_params)

    return output


def download_audio(url: str, output_path: Path) -> Path:
    """Download audio file from URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path


def concatenate_audio_files(audio_files: list[Path], output_path: Path) -> Path:
    """
    Concatenate multiple audio files into one.

    Uses pydub for audio manipulation.
    """
    from pydub import AudioSegment

    combined = AudioSegment.empty()

    for audio_file in audio_files:
        segment = AudioSegment.from_file(audio_file)
        # Add a small pause between segments
        combined += segment + AudioSegment.silent(duration=500)

    # Export as MP3
    combined.export(output_path, format="mp3", bitrate="192k")

    return output_path


def generate_audiobook(
    markdown_path: Path = None,
    output_path: Path = None,
    use_agent_formatting: bool = False,
    audio_prompt: Optional[str] = None,
) -> Path:
    """
    Generate audiobook from markdown document.

    Args:
        markdown_path: Path to markdown file (defaults to full-text output)
        output_path: Path for audio output (defaults to audio directory)
        use_agent_formatting: If True, use CrewAI agent for TTS formatting
        audio_prompt: Optional reference audio for voice cloning

    Returns:
        Path to generated audiobook
    """
    if markdown_path is None:
        markdown_path = FULL_TEXT_DIR / "mcp-crash-course.md"

    if output_path is None:
        output_path = AUDIO_DIR / "mcp-crash-course.mp3"

    print(f"Generating audiobook from {markdown_path}...")

    # Read markdown
    markdown_content = markdown_path.read_text()

    # Format for TTS
    if use_agent_formatting:
        tts_text = format_for_tts(markdown_content)
    else:
        tts_text = format_for_tts_simple(markdown_content)

    # Save TTS-formatted text
    tts_text_path = AUDIO_DIR / "tts-formatted.txt"
    tts_text_path.write_text(tts_text)
    print(f"TTS-formatted text saved to: {tts_text_path}")

    # Chunk text for processing
    chunks = chunk_text(tts_text)
    print(f"Split into {len(chunks)} chunks for TTS processing")

    # Generate audio for each chunk
    audio_files = []
    temp_dir = AUDIO_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)

    for i, chunk in enumerate(chunks):
        print(f"Generating audio for chunk {i + 1}/{len(chunks)}...")

        try:
            audio_url = generate_audio_chunk(chunk, audio_prompt=audio_prompt)

            # Download audio
            temp_file = temp_dir / f"chunk_{i:04d}.wav"
            download_audio(audio_url, temp_file)
            audio_files.append(temp_file)

            # Rate limiting - be nice to the API
            if i < len(chunks) - 1:
                time.sleep(1)

        except Exception as e:
            print(f"Error generating chunk {i + 1}: {e}")
            continue

    if not audio_files:
        raise RuntimeError("No audio chunks were generated successfully")

    # Concatenate all audio files
    print("Concatenating audio files...")
    final_path = concatenate_audio_files(audio_files, output_path)

    # Clean up temp files
    for f in audio_files:
        f.unlink()
    temp_dir.rmdir()

    print(f"Audiobook saved to: {final_path}")
    return final_path


if __name__ == "__main__":
    generate_audiobook()
