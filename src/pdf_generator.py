#!/usr/bin/env python3
"""
PDF Generator for MCP Crash Course
Stitches chapters together and converts to PDF with images using WeasyPrint.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CHAPTERS_DIR = BASE_DIR / "outputs" / "chapters"
IMAGES_DIR = BASE_DIR / "outputs" / "images"
FULL_TEXT_DIR = BASE_DIR / "outputs" / "full-text"
PDF_DIR = BASE_DIR / "outputs" / "pdf"

# Ensure output directories exist
FULL_TEXT_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

# CSS for PDF styling
PDF_CSS = """
@page {
    size: letter;
    margin: 1in;
    @top-center {
        content: "MCP Crash Course";
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
    }
}

body {
    font-family: Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    color: #1a1a1a;
    margin-top: 2em;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 18pt;
    color: #2a2a2a;
    margin-top: 1.5em;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.3em;
}

h3 {
    font-size: 14pt;
    color: #3a3a3a;
    margin-top: 1.2em;
}

h4 {
    font-size: 12pt;
    color: #4a4a4a;
    margin-top: 1em;
}

p {
    margin: 0.8em 0;
    text-align: justify;
}

code {
    font-family: "Courier New", monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

pre {
    font-family: "Courier New", monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    border: 1px solid #ddd;
}

pre code {
    background: none;
    padding: 0;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
    border: 1px solid #ddd;
    border-radius: 5px;
}

blockquote {
    border-left: 4px solid #4a90d9;
    margin: 1em 0;
    padding-left: 1em;
    color: #555;
    font-style: italic;
}

ul, ol {
    margin: 0.8em 0;
    padding-left: 1.5em;
}

li {
    margin: 0.3em 0;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
}

.title-page {
    text-align: center;
    padding-top: 3in;
}

.title-page h1 {
    font-size: 32pt;
    border: none;
    page-break-before: avoid;
}

.title-page h2 {
    font-size: 18pt;
    border: none;
    color: #666;
}
"""


def stitch_chapters() -> str:
    """Combine all chapters into a single markdown document."""
    chapters = sorted(CHAPTERS_DIR.glob("chapter-*.md"))

    # Front matter
    content_parts = [
        '<div class="title-page">',
        "",
        "# MCP Crash Course",
        "",
        "## A Comprehensive Guide to the Model Context Protocol",
        "",
        "</div>",
        "",
        "---",
        "",
    ]

    # Add each chapter
    for chapter_file in chapters:
        with open(chapter_file, "r") as f:
            chapter_content = f.read()

        content_parts.append(chapter_content)
        content_parts.append("")
        content_parts.append("---")
        content_parts.append("")

    return "\n".join(content_parts)


def fix_image_paths(content: str) -> str:
    """Update image paths to be absolute for WeasyPrint."""
    # Images are referenced as (images/chapter-XX-figure-Y.jpg)
    content = content.replace("](images/", f"](file://{IMAGES_DIR}/")
    return content


def main():
    print("MCP Crash Course PDF Generator")
    print("-" * 50)

    # Step 1: Stitch chapters
    print("Stitching chapters...")
    full_content = stitch_chapters()

    # Step 2: Fix image paths
    print("Fixing image paths...")
    full_content = fix_image_paths(full_content)

    # Step 3: Save full markdown
    full_md_path = FULL_TEXT_DIR / "mcp-crash-course.md"
    with open(full_md_path, "w") as f:
        f.write(full_content)
    print(f"  ✓ Saved full text to {full_md_path}")

    # Step 4: Convert markdown to HTML
    print("Converting markdown to HTML...")
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc'])
    html_content = md.convert(full_content)

    # Wrap in full HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MCP Crash Course</title>
</head>
<body>
{html_content}
</body>
</html>"""

    # Save HTML for reference
    html_path = FULL_TEXT_DIR / "mcp-crash-course.html"
    with open(html_path, "w") as f:
        f.write(full_html)
    print(f"  ✓ Saved HTML to {html_path}")

    # Step 5: Convert to PDF using WeasyPrint
    print("Converting to PDF...")
    pdf_path = PDF_DIR / "mcp-crash-course.pdf"

    try:
        html = HTML(string=full_html, base_url=str(BASE_DIR))
        css = CSS(string=PDF_CSS)
        html.write_pdf(pdf_path, stylesheets=[css])

        # Get file size
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ PDF generated: {pdf_path}")
        print(f"  ✓ File size: {size_mb:.2f} MB")

    except Exception as e:
        print(f"  ✗ PDF generation failed: {e}")

    print("-" * 50)
    print("PDF generation complete!")


if __name__ == "__main__":
    main()
