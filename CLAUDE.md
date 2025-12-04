# MCP Crash Course Generator

Generate a comprehensive crash course document on the Model Context Protocol (MCP).

## Project Purpose

Create an educational document about MCP using a multi-agent pipeline. The workflow transforms a human-authored curriculum outline into a complete crash course with PDF and audiobook outputs.

## Recommended Framework

This project is designed for implementation with **GPT-Researcher + LangGraph** or **CrewAI**:

- **GPT-Researcher**: For web research to gather current MCP information (the field moves fast)
- **LangGraph/CrewAI**: For orchestrating parallel chapter generation with style consistency

### Style Consistency Mechanism

The **style guide** is critical for coherent output across parallel chapter generation:
1. Style guide is generated first from curriculum analysis
2. Each chapter-writer agent receives: curriculum section + style guide + research context
3. This ensures the stitched document reads as unified prose, not disjointed chunks

### Up-to-Date Information

Since MCP evolves rapidly, the pipeline should include a research phase using:
- Tavily or Perplexity for web search
- Context7 MCP for official documentation lookup

## Repository Structure

```
All-About-MCP/
  CLAUDE.md
  README.md
  .env                                   # API keys (REPLICATE_API_TOKEN for Chatterbox)
  api-ref/
    chatterbox.txt                       # Resemble AI Chatterbox TTS API reference
  inputs/
    curriculum-transcript-formatted.md   # Main curriculum input (human-authored)
    curriculum-transcript-raw.md         # Raw transcript (reference)
  outputs/
    style-guide.md
    chapter-prompts/
    chapters/
    full-text/
    pdf/
    audio/                               # Audiobook output
  agents/
    style-guide-generator.md
    curriculum-prompt-generator.md
    chapter-writer.md
    output-stitcher.md
    markdown-pdf-converter.md
    tts-formatter.md
    audiobook-generator.md
```

## Core Pipeline (Book Generation)

### 1. style-guide-generator
Creates style guide for consistent tone and formatting across all chapters.

### 2. curriculum-prompt-generator
Transforms curriculum into structured chapter prompts (curriculum is human-authored, not generated).

### 3. chapter-writer
Generates chapter content. Supports parallel execution - each writer receives style guide for consistency.

### 4. output-stitcher
Concatenates chapters into unified document.

### 5. markdown-pdf-converter
Converts markdown to PDF.

## Audiobook Generation

After the book is complete, generate audio using Resemble AI's Chatterbox model:

### TTS Service: Chatterbox via Replicate

- **Model**: `resemble-ai/chatterbox`
- **API**: Replicate (key in `.env` as `REPLICATE_API_TOKEN`)
- **Features**:
  - Emotion exaggeration control (0.5 = neutral)
  - Instant voice cloning from short audio reference
  - Built-in watermarking
  - MIT licensed, production-grade quality

### Audio Pipeline

1. **tts-formatter** - Converts markdown to TTS-friendly plain text:
   - Removes markup, expands abbreviations
   - Optimizes sentence length for Chatterbox (15-25 words)
   - Handles technical content appropriately

2. **audiobook-generator** - Orchestrates Chatterbox via Replicate:
   - Chunks text to respect API limits
   - Calls `resemble-ai/chatterbox` for each segment
   - Concatenates audio segments
   - Outputs MP3/WAV to `outputs/audio/`

### Chatterbox Parameters

```json
{
  "prompt": "Text to synthesize",
  "audio_prompt": "Optional voice reference audio URL",
  "exaggeration": 0.5,    // 0.5 = neutral, higher = more expressive
  "cfg_weight": 0.5,      // Pace control
  "temperature": 0.8,
  "seed": 0               // 0 = random
}
```

See `api-ref/chatterbox.txt` for full API documentation.

## Input

Primary input: `inputs/curriculum-transcript-formatted.md`

## Output

- `outputs/full-text/mcp-crash-course.md` - Complete document
- `outputs/pdf/mcp-crash-course.pdf` - PDF version
- `outputs/audio/mcp-crash-course.mp3` - Audiobook (optional)
