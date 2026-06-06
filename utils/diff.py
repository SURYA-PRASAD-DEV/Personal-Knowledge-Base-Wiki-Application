"""
Utility for comparing versions and generating diffs.
"""
import difflib
from html import escape


def generate_diff(old_text, new_text):
    """
    Generate a side-by-side diff between two text blocks.
    Returns a list of diff lines with indicators.
    """
    old_lines = old_text.split('\n')
    new_lines = new_text.split('\n')
    
    differ = difflib.Differ()
    diff_lines = list(differ.compare(old_lines, new_lines))
    
    return diff_lines


def generate_html_diff(old_text, new_text):
    """
    Generate HTML representation of diff with styling.
    """
    diff_lines = generate_diff(old_text, new_text)
    html_parts = []
    
    for line in diff_lines:
        if line.startswith('- '):
            # Removed line
            html_parts.append(f'<div class="diff-removed"><span class="diff-marker">−</span> {escape(line[2:])}</div>')
        elif line.startswith('+ '):
            # Added line
            html_parts.append(f'<div class="diff-added"><span class="diff-marker">+</span> {escape(line[2:])}</div>')
        elif line.startswith('? '):
            # Hint line (skip for simplicity)
            pass
        else:
            # Unchanged line
            html_parts.append(f'<div class="diff-unchanged"><span class="diff-marker"></span> {escape(line[2:] if line.startswith("  ") else line)}</div>')
    
    return '\n'.join(html_parts)
