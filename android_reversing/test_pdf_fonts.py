#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PDF fonts and Chinese character rendering
"""

import sys
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    from PyPDF2 import PdfReader

def check_pdf_fonts(pdf_path):
    """Check fonts embedded in PDF"""
    try:
        reader = PdfReader(pdf_path)
        print(f"📄 PDF: {pdf_path}")
        print(f"📃 Pages: {len(reader.pages)}")
        print(f"\n🔍 Extracting text from first page...\n")

        # Extract text from first page
        first_page = reader.pages[0]
        text = first_page.extract_text()

        # Check for Chinese characters
        chinese_chars = [c for c in text if '\u4e00' <= c <= '\u9fff']

        print(f"📝 Text preview (first 500 chars):")
        print("=" * 60)
        print(text[:500])
        print("=" * 60)

        print(f"\n🔤 Chinese characters found: {len(chinese_chars)}")
        if chinese_chars:
            print(f"✅ Chinese characters detected: {' '.join(chinese_chars[:20])}")
            print("\n✅ PDF contains Chinese characters!")
            return True
        else:
            print("\n⚠️  No Chinese characters found in the extracted text.")
            print("This might indicate:")
            print("  1. Chinese text is embedded as images")
            print("  2. Font subsetting/encoding issues")
            print("  3. PDF extraction limitations")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "output/test_chinese_font.pdf"
    check_pdf_fonts(pdf_path)
