"""PDF conversion for the crash course document."""

from pathlib import Path
import markdown
from weasyprint import HTML, CSS

from src.config import FULL_TEXT_DIR, PDF_DIR


# CSS for the PDF
PDF_STYLES = """
@page {
    size: A4;
    margin: 2.5cm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    color: #1a1a2e;
    border-bottom: 2px solid #4a90d9;
    padding-bottom: 10px;
    margin-top: 40px;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 18pt;
    color: #2d3436;
    margin-top: 30px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}

h3 {
    font-size: 14pt;
    color: #2d3436;
    margin-top: 20px;
}

h4 {
    font-size: 12pt;
    color: #555;
    margin-top: 15px;
}

p {
    margin-bottom: 12px;
    text-align: justify;
}

code {
    font-family: 'Consolas', 'Monaco', monospace;
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10pt;
}

pre {
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.4;
    margin: 15px 0;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

blockquote {
    border-left: 4px solid #4a90d9;
    margin: 15px 0;
    padding: 10px 20px;
    background-color: #f8f9fa;
    font-style: italic;
}

ul, ol {
    margin-bottom: 12px;
    padding-left: 30px;
}

li {
    margin-bottom: 6px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

th {
    background-color: #4a90d9;
    color: white;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

a {
    color: #4a90d9;
    text-decoration: none;
}

/* Title page styling */
.title-page {
    text-align: center;
    padding-top: 200px;
}

.title-page h1 {
    font-size: 36pt;
    border: none;
    page-break-before: avoid;
}

.title-page .subtitle {
    font-size: 18pt;
    color: #666;
    margin-top: 20px;
}

/* Tips and warnings */
.tip, .warning, .note {
    padding: 15px;
    margin: 15px 0;
    border-radius: 5px;
}

.tip {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
}

.warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}

.note {
    background-color: #d1ecf1;
    border-left: 4px solid #17a2b8;
}
"""


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML with extensions."""
    extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'nl2br',
    ]

    html = markdown.markdown(
        markdown_content,
        extensions=extensions,
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'guess_lang': False,
            }
        }
    )

    # Wrap in full HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MCP Crash Course</title>
</head>
<body>
{html}
</body>
</html>"""

    return full_html


def convert_to_pdf(
    markdown_path: Path = None,
    output_path: Path = None,
) -> Path:
    """
    Convert markdown document to PDF.

    Args:
        markdown_path: Path to markdown file (defaults to full-text output)
        output_path: Path for PDF output (defaults to pdf directory)

    Returns:
        Path to generated PDF
    """
    if markdown_path is None:
        markdown_path = FULL_TEXT_DIR / "mcp-crash-course.md"

    if output_path is None:
        output_path = PDF_DIR / "mcp-crash-course.pdf"

    print(f"Converting {markdown_path} to PDF...")

    # Read markdown
    markdown_content = markdown_path.read_text()

    # Convert to HTML
    html_content = markdown_to_html(markdown_content)

    # Generate PDF
    html = HTML(string=html_content)
    css = CSS(string=PDF_STYLES)

    html.write_pdf(output_path, stylesheets=[css])

    print(f"PDF saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    convert_to_pdf()
