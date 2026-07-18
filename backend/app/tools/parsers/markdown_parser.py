import re
from typing import List, Dict, Any

def parse_markdown_file(file_path: str) -> Dict[str, Any]:
    """Parses a Markdown file and extracts headings, code blocks, tables, and links."""
    headings = []
    code_blocks = []
    tables = []
    links = []
    sections = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return {}

    lines = content.splitlines()
    
    # Track current states
    current_heading = "Root"
    current_section_lines = []
    in_code_block = False
    current_code_lang = ""
    current_code_lines = []
    in_table = False
    current_table_lines = []

    # 1. Regex expressions
    heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    def flush_section():
        content = "\n".join(current_section_lines).strip()
        if content:
            sections.append({
                "heading": current_heading,
                "content": content
            })
        current_section_lines.clear()

    for line_num, line in enumerate(lines, 1):
        line_strip = line.strip()
        
        # Extract links globally from line
        for match in link_pattern.finditer(line):
            text, url = match.groups()
            links.append({
                "text": text.strip(),
                "url": url.strip(),
                "line": line_num
            })

        # 2. Code Block processing
        if line_strip.startswith("```"):
            if in_code_block:
                # Ending block
                in_code_block = False
                code_blocks.append({
                    "language": current_code_lang,
                    "code": "\n".join(current_code_lines).strip(),
                    "line_start": line_num - len(current_code_lines),
                    "line_end": line_num
                })
                current_code_lines.clear()
            else:
                # Starting block
                in_code_block = True
                current_code_lang = line_strip[3:].strip()
            continue

        if in_code_block:
            current_code_lines.append(line)
            continue

        # 3. Headings processing
        heading_match = heading_pattern.match(line_strip)
        if heading_match:
            flush_section()
            level_str, text = heading_match.groups()
            level = len(level_str)
            current_heading = text.strip()
            headings.append({
                "level": level,
                "text": current_heading,
                "line": line_num
            })
            continue

        # 4. Tables processing (checking for pipes | and dividing dash lines |---|)
        if line_strip.startswith("|"):
            in_table = True
            current_table_lines.append(line)
            continue
        elif in_table:
            flush_section() # flush whatever we accumulated
            # Table has ended
            in_table = False
            if len(current_table_lines) > 1: # verify it's not a single isolated pipe line
                tables.append({
                    "content": "\n".join(current_table_lines).strip(),
                    "line_start": line_num - len(current_table_lines),
                    "line_end": line_num - 1
                })
            current_table_lines.clear()

        # Add line to current section content
        current_section_lines.append(line)

    flush_section()
    if in_table and len(current_table_lines) > 1:
        tables.append({
            "content": "\n".join(current_table_lines).strip(),
            "line_start": len(lines) - len(current_table_lines) + 1,
            "line_end": len(lines)
        })
    if in_code_block and current_code_lines:
        code_blocks.append({
            "language": current_code_lang,
            "code": "\n".join(current_code_lines).strip(),
            "line_start": len(lines) - len(current_code_lines) + 1,
            "line_end": len(lines)
        })

    return {
        "headings": headings,
        "sections": sections,
        "code_blocks": code_blocks,
        "tables": tables,
        "links": links
    }
