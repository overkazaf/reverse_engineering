#!/usr/bin/env python3
import os
import re

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def find_chinese_in_code_blocks(file_path):
    """Find Chinese text in code blocks of markdown files"""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_code_block = False
        code_block_start = 0

        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i
                else:
                    in_code_block = False
            elif in_code_block and has_chinese(line):
                results.append((i, line.rstrip()))

    except Exception as e:
        pass

    return results

# Scan docs directory
docs_dir = 'docs'
files_with_chinese = {}

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(root, file)
            chinese_lines = find_chinese_in_code_blocks(file_path)
            if chinese_lines:
                files_with_chinese[file_path] = chinese_lines

# Print results
if files_with_chinese:
    print(f"Found {len(files_with_chinese)} files with Chinese in code blocks:\n")
    for file_path, lines in sorted(files_with_chinese.items()):
        print(f"=== {file_path} ===")
        for line_num, line in lines[:5]:  # Show first 5 lines
            print(f"  Line {line_num}: {line[:80]}")
        if len(lines) > 5:
            print(f"  ... and {len(lines) - 5} more lines")
        print()
else:
    print("No Chinese text found in code blocks!")
