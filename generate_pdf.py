#!/usr/bin/env python3
"""
SAFT-BOOK PDF Generator
Converts all markdown chapters into a single PDF file using wkhtmltopdf
"""

import markdown
import os
from pathlib import Path
from datetime import datetime

# Configuration
OUTPUT_DIR = Path(__file__).parent
OUTPUT_PDF = OUTPUT_DIR / "SAFT_BOOK.pdf"
FULL_BOOK_MD = OUTPUT_DIR / "FULL_BOOK.md"

# CSS styles for professional book formatting
CSS_STYLE = """
<style>
    @page {
        size: A4;
        margin: 2.5cm;
        @top-center {
            content: string(chapter);
            font-size: 9pt;
            color: #666;
        }
        @bottom-center {
            content: counter(page);
            font-size: 9pt;
        }
    }
    
    * {
        box-sizing: border-box;
    }
    
    body {
        font-family: "DejaVu Serif", "Georgia", serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #1a1a1a;
        text-align: justify;
    }
    
    h1 {
        font-size: 24pt;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 30px;
        page-break-before: always;
    }
    
    h1:first-of-type {
        page-break-before: avoid;
    }
    
    h2 {
        font-size: 18pt;
        color: #34495e;
        margin-top: 35px;
        margin-bottom: 20px;
    }
    
    h3 {
        font-size: 14pt;
        color: #7f8c8d;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    h4, h5, h6 {
        font-size: 12pt;
        color: #95a5a6;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    p {
        margin-bottom: 15px;
        text-indent: 0;
    }
    
    p + p {
        text-indent: 20px;
    }
    
    strong, b {
        color: #2c3e50;
        font-weight: 700;
    }
    
    em, i {
        color: #34495e;
    }
    
    blockquote {
        margin: 20px 40px;
        padding: 15px 20px;
        border-left: 4px solid #3498db;
        background: #f8f9fa;
        font-style: italic;
        color: #555;
    }
    
    code, pre {
        font-family: "DejaVu Sans Mono", "Courier New", monospace;
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 3px;
    }
    
    code {
        padding: 2px 6px;
        color: #e74c3c;
        font-size: 10pt;
    }
    
    pre {
        padding: 15px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
        margin: 20px 0;
    }
    
    pre code {
        padding: 0;
        border: none;
        background: none;
        color: inherit;
    }
    
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    
    li {
        margin-bottom: 8px;
    }
    
    a {
        color: #3498db;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 40px 0;
    }
    
    .title-page {
        text-align: center;
        padding: 100px 0;
    }
    
    .title-page h1 {
        font-size: 36pt;
        border: none;
        margin: 0;
        page-break-before: avoid;
    }
    
    .title-page .subtitle {
        font-size: 18pt;
        color: #7f8c8d;
        margin: 30px 0;
    }
    
    .title-page .author {
        font-size: 14pt;
        color: #34495e;
        margin-top: 50px;
    }
    
    .title-page .date {
        font-size: 11pt;
        color: #95a5a6;
        margin-top: 20px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 10px 15px;
        text-align: left;
    }
    
    th {
        background: #3498db;
        color: white;
        font-weight: 600;
    }
    
    tr:nth-child(even) {
        background: #f8f9fa;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 20px auto;
    }
    
    /* Chapter heading style */
    .chapter-header {
        page-break-before: always;
        margin-top: 60px;
        margin-bottom: 40px;
    }
</style>
"""

def read_chapter(filepath):
    """Read a markdown chapter file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_title_page():
    """Generate HTML for the title page"""
    date_str = datetime.now().strftime("%B %Y")
    return f"""
    <div class="title-page">
        <h1>SAFT-BOOK</h1>
        <div class="subtitle">Ръководство за внедряване на SAF-T в България</div>
        <hr style="width: 200px; margin: 40px auto;">
        <div class="author">От екипа на baraba.org</div>
        <div class="date">Генерирано: {date_str}</div>
    </div>
    """

def generate_toc(chapters):
    """Generate table of contents"""
    toc = '<h2 style="page-break-before: always;">Съдържание</h2>\n<ul>\n'
    for i, (filepath, title) in enumerate(chapters, 1):
        toc += f'<li><a href="#chapter-{i}">{title}</a></li>\n'
    toc += '</ul>\n'
    return toc

def main():
    # Define chapter order
    chapters_order = [
        ('MANIFESTO.md', 'Манифест'),
        ('CHAPTER_0.md', 'Глава 0: Генетични дефекти на БГ софтуера'),
        ('CHAPTER_0A.md', 'Глава 0A'),
        ('CHAPTER_1.md', 'Глава 1'),
        ('CHAPTER_2.md', 'Глава 2'),
        ('CHAPTER_3.md', 'Глава 3'),
        ('CHAPTER_4.md', 'Глава 4'),
        ('CHAPTER_5.md', 'Глава 5'),
        ('CHAPTER_6.md', 'Глава 6'),
        ('CHAPTER_7.md', 'Глава 7'),
        ('CHAPTER_8.md', 'Глава 8'),
        ('CHAPTER_9.md', 'Глава 9'),
        ('CHAPTER_10.md', 'Глава 10'),
        ('CHAPTER_11.md', 'Глава 11'),
        ('APPENDICES.md', 'Приложения'),
    ]
    
    # Filter existing files
    chapters = [(f, t) for f, t in chapters_order if (OUTPUT_DIR / f).exists()]
    
    # Also check if FULL_BOOK.md exists and use it as alternative
    if FULL_BOOK_MD.exists():
        print(f"Using {FULL_BOOK_MD.name} as source...")
        content = read_chapter(FULL_BOOK_MD)
        html_content = markdown.markdown(content, extensions=['extra', 'toc', 'tables'])
        
        full_html = f"""<!DOCTYPE html>
<html lang="bg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAFT-BOOK</title>
    {CSS_STYLE}
</head>
<body>
    {generate_title_page()}
    {html_content}
</body>
</html>"""
    else:
        # Build HTML from individual chapters
        print("Building from individual chapters...")
        full_html = f"""<!DOCTYPE html>
<html lang="bg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAFT-BOOK</title>
    {CSS_STYLE}
</head>
<body>
    {generate_title_page()}
    {generate_toc(chapters)}
"""
        
        for i, (filepath, title) in enumerate(chapters, 1):
            print(f"  Processing: {filepath}")
            content = read_chapter(OUTPUT_DIR / filepath)
            html_content = markdown.markdown(content, extensions=['extra', 'tables'])
            
            # Add chapter markers
            full_html += f'\n<div id="chapter-{i}" class="chapter-header">\n{html_content}\n</div>\n'
        
        full_html += '\n</body>\n</html>'
    
    # Write intermediate HTML (useful for debugging)
    html_file = OUTPUT_DIR / 'book_temp.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Intermediate HTML written to: {html_file}")
    
    # Convert to PDF using wkhtmltopdf
    import subprocess
    
    cmd = [
        'wkhtmltopdf',
        '--page-size', 'A4',
        '--margin-top', '20mm',
        '--margin-bottom', '20mm',
        '--margin-left', '25mm',
        '--margin-right', '25mm',
        '--encoding', 'UTF-8',
        '--enable-local-file-access',
        '--no-stop-slow-scripts',
        '--javascript-delay', '1000',
        '--quiet',
        str(html_file),
        str(OUTPUT_PDF)
    ]
    
    print(f"Generating PDF: {OUTPUT_PDF}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ PDF generated successfully: {OUTPUT_PDF}")
        print(f"  File size: {OUTPUT_PDF.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print(f"✗ Error generating PDF: {result.stderr}")
        return 1
    
    # Clean up temp file (optional)
    # html_file.unlink()
    
    return 0

if __name__ == '__main__':
    exit(main())
