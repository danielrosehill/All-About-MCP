#!/usr/bin/env python3
"""
Chapter Writer for MCP Crash Course
Uses Gemini 3 Pro Preview for chapter text and Nano Banana for illustrations.
"""

import json
import os
import re
import time
import requests
from pathlib import Path
from google import genai
import replicate

# Configuration
GEMINI_MODEL = "gemini-3-pro-preview"
IMAGE_MODEL = "google/nano-banana"

BASE_DIR = Path(__file__).parent.parent
CHAPTER_PROMPTS_FILE = BASE_DIR / "outputs" / "chapter-prompts" / "chapter-prompts.json"
STYLE_GUIDE_FILE = BASE_DIR / "outputs" / "style-guide" / "style-guide.md"
CHAPTERS_OUTPUT_DIR = BASE_DIR / "outputs" / "chapters"
IMAGES_OUTPUT_DIR = BASE_DIR / "outputs" / "images"

# Ensure output directories exist
CHAPTERS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_style_guide() -> str:
    """Load the style guide content."""
    with open(STYLE_GUIDE_FILE, "r") as f:
        return f.read()


def load_chapter_prompts() -> list[dict]:
    """Load chapter prompts from JSON file."""
    with open(CHAPTER_PROMPTS_FILE, "r") as f:
        return json.load(f)


def slugify(title: str) -> str:
    """Convert title to a filename-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def build_chapter_prompt(chapter: dict, style_guide: str) -> str:
    """Build the full prompt for generating a chapter."""
    return f"""You are writing a chapter for a technical book about the Model Context Protocol (MCP).

## Style Guide

Follow this style guide strictly:

{style_guide}

## Chapter Details

**Chapter {chapter['chapter_number']}: {chapter['title']}**

### Core Questions to Address
{chr(10).join(f"- {q}" for q in chapter['core_questions'])}

### Key Concepts to Cover
{chr(10).join(f"- {c}" for c in chapter['key_concepts'])}

### Research Topics (incorporate current information on these)
{chr(10).join(f"- {t}" for t in chapter['research_topics'])}

### Examples Needed
{chr(10).join(f"- {e}" for e in chapter['examples_needed'])}

### Connections to Other Chapters
{chr(10).join(f"- {c}" for c in chapter['connections'])}

### Potential Controversies to Address
{chr(10).join(f"- {p}" for p in chapter['potential_controversies'])}

## Instructions

Write a comprehensive chapter (approximately 3000-5000 words) that:
1. Addresses all core questions thoroughly
2. Explains all key concepts clearly
3. Includes relevant, realistic examples
4. Maintains the formal tone specified in the style guide
5. Uses proper markdown formatting with ## for the chapter title and ### for sections
6. Does NOT include meta-commentary about the writing process
7. Starts directly with the chapter content (no preamble)
8. Include 2-3 image placeholders where illustrations would enhance understanding, using this exact format:
   ![Image: <brief description for image generation>](images/chapter-XX-figure-Y.jpg)
   Where XX is the chapter number (zero-padded) and Y is the figure number (1, 2, 3...)

Write the chapter now:"""


def build_image_prompt(description: str, chapter_title: str) -> str:
    """Build prompt for Nano Banana image generation."""
    return f"""Create a professional technical illustration for a book about Model Context Protocol (MCP).

Chapter context: {chapter_title}

Image requirement: {description}

Style guidelines:
- Clean, modern technical illustration style
- Professional color palette (blues, grays, whites)
- Suitable for a technical book/PDF
- Clear visual hierarchy
- No text in the image (captions will be added separately)
- Diagram or conceptual illustration style, not photorealistic"""


def extract_image_placeholders(content: str) -> list[dict]:
    """Extract image placeholders from chapter content."""
    pattern = r'!\[Image: ([^\]]+)\]\(images/(chapter-\d+-figure-\d+\.jpg)\)'
    matches = re.findall(pattern, content)
    return [{"description": desc, "filename": fname} for desc, fname in matches]


def generate_image(description: str, chapter_title: str, output_path: Path) -> bool:
    """Generate an image using Nano Banana via Replicate."""
    try:
        prompt = build_image_prompt(description, chapter_title)

        output = replicate.run(
            IMAGE_MODEL,
            input={
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "output_format": "jpg"
            }
        )

        # Download the image
        if output:
            response = requests.get(output)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
        return False
    except Exception as e:
        print(f"    ⚠ Image generation failed: {e}")
        return False


def generate_chapter(client: genai.Client, chapter: dict, style_guide: str) -> str:
    """Generate a single chapter using Gemini."""
    prompt = build_chapter_prompt(chapter, style_guide)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text


def main():
    # Initialize clients
    gemini_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Load inputs
    style_guide = load_style_guide()
    chapters = load_chapter_prompts()

    print(f"Loaded {len(chapters)} chapter prompts")
    print(f"Text model: {GEMINI_MODEL}")
    print(f"Image model: {IMAGE_MODEL}")
    print("-" * 50)

    for chapter in chapters:
        chapter_num = chapter["chapter_number"]
        title = chapter["title"]
        filename = f"chapter-{chapter_num:02d}-{slugify(title)}.md"
        output_path = CHAPTERS_OUTPUT_DIR / filename

        # Skip if already exists
        if output_path.exists():
            print(f"Chapter {chapter_num} already exists, skipping...")
            continue

        print(f"Generating Chapter {chapter_num}: {title}...")
        start_time = time.time()

        try:
            # Generate chapter text
            content = generate_chapter(gemini_client, chapter, style_guide)

            # Extract and generate images
            image_placeholders = extract_image_placeholders(content)
            if image_placeholders:
                print(f"  → Generating {len(image_placeholders)} illustrations...")
                for img in image_placeholders:
                    img_path = IMAGES_OUTPUT_DIR / img["filename"]
                    if not img_path.exists():
                        print(f"    • {img['filename']}: {img['description'][:50]}...")
                        success = generate_image(img["description"], title, img_path)
                        if success:
                            print(f"      ✓ Generated")
                        time.sleep(1)  # Rate limiting

            # Write chapter to file
            with open(output_path, "w") as f:
                f.write(content)

            elapsed = time.time() - start_time
            print(f"  ✓ Saved to {filename} ({elapsed:.1f}s)")

            # Small delay to avoid rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"  ✗ Error generating chapter {chapter_num}: {e}")
            continue

    print("-" * 50)
    print("Chapter generation complete!")

    # Summary
    chapters_created = len(list(CHAPTERS_OUTPUT_DIR.glob("*.md")))
    images_created = len(list(IMAGES_OUTPUT_DIR.glob("*.jpg")))
    print(f"Created {chapters_created} chapters and {images_created} images")


if __name__ == "__main__":
    main()
