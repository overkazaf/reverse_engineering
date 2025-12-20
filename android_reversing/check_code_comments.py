#!/usr/bin/env python3
"""
Check code comments in markdown files for mixed Chinese-English patterns.
Focus only on comments within code blocks.
"""

import re
from pathlib import Path

def extract_code_blocks(content):
    """Extract all code blocks from markdown."""
    pattern = r'```[\w]*\n(.*?)\n```'
    return re.findall(pattern, content, re.DOTALL)

def has_mixed_comment(line):
    """Check if a comment line has mixed Chinese-English."""
    # Only check lines that start with # (comments)
    if not re.match(r'^\s*#', line):
        return False

    # Check if line has both Chinese and English letters
    has_chinese = bool(re.search(r'[\u4e00-\u9fa5]', line))
    has_english = bool(re.search(r'[A-Za-z]{2,}', line))  # At least 2 consecutive letters

    # Exclude common acceptable patterns
    if 'HTTP' in line or 'API' in line or 'URL' in line or 'ID' in line:
        return False
    if 'APK' in line or 'DEX' in line or 'SDK' in line or 'ADB' in line:
        return False
    if 'JSON' in line or 'XML' in line or 'SQL' in line:
        return False

    return has_chinese and has_english

def main():
    """Main function."""
    docs_dir = Path('docs')
    issues = []

    for md_file in docs_dir.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            code_blocks = extract_code_blocks(content)
            for block in code_blocks:
                lines = block.split('\n')
                for i, line in enumerate(lines, 1):
                    if has_mixed_comment(line):
                        issues.append({
                            'file': md_file.relative_to(docs_dir),
                            'line': line.strip(),
                            'block_start': i
                        })
        except Exception as e:
            pass

    if issues:
        print(f"Found {len(issues)} potentially problematic code comments:")
        print("=" * 80)
        for issue in issues[:50]:  # Show first 50
            print(f"{issue['file']}")
            print(f"  → {issue['line']}")
            print()
    else:
        print("✓ No mixed Chinese-English comments found in code blocks!")

if __name__ == '__main__':
    main()
