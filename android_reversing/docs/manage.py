import os
import subprocess
import sys
import argparse
import re

# --- Configuration ---
# The script is now inside the docs directory, so we define paths relative to this new location.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # This is the 'frida' directory
DOCS_DIR_NAME = os.path.basename(SCRIPT_DIR) # This will be 'android'

MAIN_DOC_FILE = "index.md"
PDF_OUTPUT_FILE = os.path.join(PROJECT_ROOT, "Android_Reverse_Engineering_Knowledge_Base.pdf")
MKDOCS_CONFIG_FILE = os.path.join(PROJECT_ROOT, "mkdocs.yml")
PDF_STYLE_FILE = os.path.join(PROJECT_ROOT, "pdf_style.css")
# --- End Configuration ---

def check_dependency(command):
    """Checks if a command-line tool is installed and in the PATH."""
    try:
        subprocess.run([command, '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_mkdocs_config():
    """Dynamically generates the mkdocs.yml configuration file in the project root."""
    # Force delete the old config file to prevent caching issues by mkdocs serve
    if os.path.exists(MKDOCS_CONFIG_FILE):
        try:
            os.remove(MKDOCS_CONFIG_FILE)
            print(f"Removed old config file to prevent caching: '{MKDOCS_CONFIG_FILE}'")
        except OSError as e:
            print(f"Error removing old config file: {e}")
            # We can still proceed, but it's a warning sign
            pass
            
    if not os.path.exists(MAIN_DOC_FILE):
        print(f"Error: Main document '{MAIN_DOC_FILE}' not found in current directory '{os.getcwd()}'.")
        sys.exit(1)

    nav_structure = []
    # Add the main index file first
    nav_structure.append({'Home': MAIN_DOC_FILE})

    # Discover directories inside the current location (which is the docs dir)
    for dirname in sorted(os.listdir('.')):
        dirpath = os.path.join('.', dirname)
        if os.path.isdir(dirpath):
            category_name = dirname.split('-', 1)[-1].replace('_', ' ').title()
            category_items = []
            for filename in sorted(os.listdir(dirpath)):
                if filename.endswith(".md"):
                    # Path is relative to the docs_dir (e.g., '00-Foundations/some.md')
                    filepath = os.path.join(dirname, filename)
                    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
                    category_items.append({title: filepath})
            if category_items:
                nav_structure.append({category_name: category_items})

    # Basic MkDocs configuration
    config = {
        'site_name': 'Android RE Knowledge Base',
        # Crucial change: docs_dir points to the 'android' folder
        'docs_dir': DOCS_DIR_NAME,
        'theme': {
            'name': 'material',
            'custom_dir': os.path.join(DOCS_DIR_NAME, 'custom_theme'),
            'features': [
                'navigation.tabs',
                'navigation.top',
                'search.suggest',
                'search.highlight',
                'navigation.instant'
            ],
            'palette': [
                {
                    "scheme": "default",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode"
                    }
                },
                {
                    "scheme": "slate",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode"
                    }
                }
            ]
        },
        'extra_css': [
            'https://uicdn.toast.com/editor/latest/toastui-editor.min.css',
            'css/chat.css'
        ],
        'extra_javascript': [
            'https://uicdn.toast.com/editor/latest/toastui-editor-all.min.js',
            'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
            'js/editor.js',
            'js/chat.js',
            'js/interview.js'
        ],
        'nav': nav_structure
    }

    # Write the YAML configuration to the project root
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML is required to generate the config. Please run: pip install PyYAML")
        sys.exit(1)

    with open(MKDOCS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Generated '{MKDOCS_CONFIG_FILE}' in project root successfully.")


def serve_docs(port=8000):
    """Serves the documentation using mkdocs."""
    if not check_dependency('mkdocs'):
        print("Error: mkdocs is not installed.")
        print("Please install it first: pip install mkdocs mkdocs-material PyYAML")
        sys.exit(1)
    
    print("Force generating MkDocs configuration to ensure correctness...")
    generate_mkdocs_config()

    # --- Start Gemini Proxy Server ---
    gemini_proxy_script = os.path.join(PROJECT_ROOT, 'gemini_proxy', 'server.py')
    proxy_process = None
    if os.path.exists(gemini_proxy_script):
        print("\nStarting Gemini proxy server in the background...")
        try:
            # Running from the script's directory ensures it can find its own files.
            proxy_process = subprocess.Popen(
                [sys.executable, gemini_proxy_script],
                cwd=os.path.dirname(gemini_proxy_script)
            )
            print(f"Gemini proxy server started with PID: {proxy_process.pid}")
        except Exception as e:
            print(f"Failed to start Gemini proxy server: {e}")
            proxy_process = None
    else:
        print("\nGemini proxy server script not found, skipping.")
    # --- End Gemini Proxy Server ---
    
    print(f"\nStarting the interactive documentation server at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server.")
    
    try:
        # Run from the project root where mkdocs.yml is now located
        subprocess.run(['mkdocs', 'serve', '--dev-addr', f'0.0.0.0:{port}'], check=True, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running mkdocs server: {e}")
        print("Please check the mkdocs installation and the generated config file.")
    finally:
        if proxy_process:
            print("\nStopping Gemini proxy server...")
            proxy_process.terminate()
            proxy_process.wait()
            print("Gemini proxy server stopped.")

def get_pandoc_file_order():
    """Parses the main doc file to get the correct order for PDF generation."""
    if not os.path.exists(MAIN_DOC_FILE):
        print(f"Error: Main document '{MAIN_DOC_FILE}' not found.")
        return []

    # Paths returned will be relative to the project root (e.g., 'android/index.md')
    file_order = [os.path.join(DOCS_DIR_NAME, MAIN_DOC_FILE)]
    link_regex = re.compile(r'\[.*?\]\(\.(.*?)\)')

    with open(MAIN_DOC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    links = link_regex.findall(content)
    unique_links = set()
    for link in links:
        # link is like '/00-Foundations/file.md'
        file_path_in_docs = os.path.normpath(link.strip('/'))
        if os.path.isfile(file_path_in_docs):
            # Prepend the docs directory name to make the path relative to project root
            full_path = os.path.join(DOCS_DIR_NAME, file_path_in_docs)
            unique_links.add(full_path)

    for file_path in sorted(list(unique_links)):
        if file_path not in file_order:
            file_order.append(file_path)
            
    print("PDF generation file order determined (relative to project root):")
    for f in file_order:
        print(f"  - {f}")
    return file_order


def export_to_pdf():
    """Exports all markdown documents into a single PDF file."""
    if not check_dependency('pandoc'):
        print("Error: pandoc is not installed.")
        print("Please install it first.")
        print("  - On macOS: brew install pandoc")
        print("  - On Debian/Ubuntu: sudo apt-get install pandoc")
        sys.exit(1)

    if not check_dependency('weasyprint'):
        print("\nError: weasyprint is not installed. This is needed as the PDF engine.")
        print("It is a lightweight alternative to a full LaTeX installation.")
        print("Please install it first using pip:")
        print("  pip install weasyprint")
        sys.exit(1)

    files_to_convert = get_pandoc_file_order()
    if not files_to_convert:
        print("Could not determine file order for PDF generation. Aborting.")
        sys.exit(1)

    print(f"\nGenerating PDF: '{PDF_OUTPUT_FILE}'...")
    command = [
        'pandoc',
        *files_to_convert,
        '-o', os.path.basename(PDF_OUTPUT_FILE),
        '--pdf-engine=weasyprint',
        '--css', os.path.basename(PDF_STYLE_FILE),
        '--table-of-contents',
        '--toc-depth=2',
        '-V', 'margin-top=1in',
        '-V', 'margin-right=1in',
        '-V', 'margin-bottom=1in',
        '-V', 'margin-left=1in',
        '--resource-path', DOCS_DIR_NAME
    ]

    try:
        # Run pandoc from the project root for correct path resolution
        process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', cwd=PROJECT_ROOT)
        print(f"\nSuccessfully created '{PDF_OUTPUT_FILE}'.")
        if process.stdout:
            print("Pandoc output:", process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\nError during PDF generation with pandoc.")
        print(f"Return Code: {e.returncode}")
        print(f"Pandoc STDOUT:\n{e.stdout}")
        print(f"Pandoc STDERR:\n{e.stderr}")
        print("\nPlease ensure pandoc and weasyprint are correctly installed.")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="A management tool for the Android Reverse Engineering Knowledge Base.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Launch an interactive web server to view the documentation.')
    serve_parser.add_argument(
        '-p', '--port',
        default=8000,
        type=int,
        help='The port to use for the live-reloading server. Default is 8000.'
    )
    serve_parser.set_defaults(func=serve_docs)
    
    # PDF command
    pdf_parser = subparsers.add_parser('pdf', help='Combine all markdown files into a single PDF.')
    pdf_parser.set_defaults(func=export_to_pdf)

    # Config command
    config_parser = subparsers.add_parser('config', help='Generate or update the mkdocs.yml configuration file.')
    config_parser.set_defaults(func=generate_mkdocs_config)

    args = parser.parse_args()
    
    # Call the function with the appropriate arguments
    if args.command == 'serve':
        args.func(port=args.port)
    else:
        args.func()

if __name__ == '__main__':
    main() 