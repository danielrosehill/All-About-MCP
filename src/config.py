"""Configuration and environment setup."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Output subdirectories
STYLE_GUIDE_DIR = OUTPUTS_DIR / "style-guide"
CHAPTER_PROMPTS_DIR = OUTPUTS_DIR / "chapter-prompts"
CHAPTERS_DIR = OUTPUTS_DIR / "chapters"
FULL_TEXT_DIR = OUTPUTS_DIR / "full-text"
PDF_DIR = OUTPUTS_DIR / "pdf"
AUDIO_DIR = OUTPUTS_DIR / "audio"

# Input files
CURRICULUM_FILE = INPUTS_DIR / "curriculum-transcript-formatted.md"

# Gemini settings
GEMINI_MODEL = "gemini-3-pro-preview"  # Best quality for deep technical content
GEMINI_MODEL_RESEARCH = "gemini-3-pro-preview"  # With grounding for research

# Chatterbox TTS settings
CHATTERBOX_MODEL = "resemble-ai/chatterbox"
TTS_EXAGGERATION = 0.5  # Neutral
TTS_CFG_WEIGHT = 0.5
TTS_TEMPERATURE = 0.8

def validate_config():
    """Validate required configuration."""
    errors = []

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-gemini-api-key-here":
        errors.append("GOOGLE_API_KEY not set in .env")

    if not REPLICATE_API_TOKEN:
        errors.append("REPLICATE_API_TOKEN not set in .env")

    if not CURRICULUM_FILE.exists():
        errors.append(f"Curriculum file not found: {CURRICULUM_FILE}")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Ensure output directories exist
    for dir_path in [STYLE_GUIDE_DIR, CHAPTER_PROMPTS_DIR, CHAPTERS_DIR,
                     FULL_TEXT_DIR, PDF_DIR, AUDIO_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
