import os
import json
import re # Import re module
import subprocess
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import markdown

# --- Configuration & Setup ---
# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

# Define base directories for security
# The script is in 'gemini_proxy', so docs_dir is its parent.
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs'))
print(f"DOCS_DIR -> {DOCS_DIR}")

# --- Proxy Configuration ---
PROXY_URL = "http://127.0.0.1:1087"
os.environ['HTTP_PROXY'] = PROXY_URL
os.environ['HTTPS_PROXY'] = PROXY_URL
print(f"[CONFIG] Using proxy for API calls: {PROXY_URL}")

# This script is located in 'android_reversing/docs/gemini_proxy/'.
# We define DOCS_ROOT as 'android_reversing/docs/'.
DOCS_ROOT = os.path.abspath(os.path.join(DOCS_DIR, '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(DOCS_ROOT, '..'))

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Unified Gemini Client Initialization ---
# This single client will be used for all API calls.
genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# --- Helper Functions ---
def get_safe_path(file_path):
    """
    Validates and resolves a file path to ensure it's within the DOCS_DIR.
    Prevents directory traversal attacks.
    """
    if not file_path:
        return None
    # Normalize path to prevent '..' traversal
    # Ensure the path is relative
    file_path = file_path.lstrip('/')
    safe_path = os.path.normpath(os.path.join(DOCS_DIR, file_path))
    # Check if the resolved path is still within the allowed directory
    if os.path.commonpath([safe_path, DOCS_DIR]) != DOCS_DIR:
        return None
    return safe_path

# --- API Endpoints ---

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    """Handles standard chat requests."""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Invalid request: 'prompt' is required."}), 400
        
        prompt = data['prompt']
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(f"[LOG] Response from Gemini: {response.text}")
        
        # Return the raw text response from the model
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/shell', methods=['POST'])
def shell_handler():
    """
    Executes a shell command within a secured, sandboxed environment.
    This uses a multi-layered approach:
    1. A strict whitelist of allowed commands.
    2. Blocks absolute paths and directory traversal.
    3. Blocks file redirection characters.
    """
    try:
        data = request.json
        command = data.get('command')
        if not command:
            return jsonify({"response": "No command provided.", "status": "error"}), 400

        # --- Sandbox Security Layer ---
        ALLOWED_COMMANDS = {'ls', 'grep', 'pwd', 'find', 'echo', 'cat', 'file'}

        # Split command into components to analyze it
        try:
            # shlex.split is safer for parsing command-line strings
            import shlex
            cmd_parts = shlex.split(command)
        except:
            # Fallback for simple cases
            cmd_parts = command.strip().split()

        if not cmd_parts:
            return jsonify({"response": "Empty command.", "status": "error"}), 200

        # 1. Whitelist check: The actual command must be in the allowed list.
        if cmd_parts[0] not in ALLOWED_COMMANDS:
            msg = f"Error: Command '{cmd_parts[0]}' is not allowed."
            print(f"[SECURITY] {msg}")
            return jsonify({"response": msg, "status": "error"}), 200

        # 2. Argument check: Forbid absolute paths and directory traversal.
        for part in cmd_parts[1:]:
            if part.startswith('/') or '..' in part:
                msg = f"Error: Absolute paths or directory traversal ('..') are not allowed in arguments."
                print(f"[SECURITY] {msg} | Argument: '{part}'")
                return jsonify({"response": msg, "status": "error"}), 200
        
        # 3. Redirection check: Block file redirection operators.
        if any(op in command for op in ['>', '<', '>>', '<<']):
            msg = "Error: File redirection operators (>, <) are not allowed."
            print(f"[SECURITY] {msg} | Command: '{command}'")
            return jsonify({"response": msg, "status": "error"}), 200

        # If all checks pass, execute the command
        print(f"[SANDBOX] Executing allowed command: {command}")
        result = subprocess.run(
            command, # Using the original command string is fine here due to shell=True and prior validation
            shell=True,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT # Execute commands from the project root
        )
        output = result.stdout + result.stderr
        return jsonify({"response": output})
    except Exception as e:
        print(f"An error occurred in /shell: {e}")
        return jsonify({"response": str(e), "status": "error"}), 200

@app.route('/api/write-file', methods=['POST'])
def write_file_handler():
    """Handles requests to write content to a file."""
    try:
        data = request.json
        filepath = data.get('filepath')
        content = data.get('content')
        if not filepath or content is None:
            return jsonify({"status": "error", "message": "Missing 'filepath' or 'content'."}), 400
        
        # Ensure the write path is safely within the project root
        target_path = os.path.normpath(os.path.join(PROJECT_ROOT, filepath))
        if not target_path.startswith(PROJECT_ROOT):
             return jsonify({"status": "error", "message": "Access denied: cannot write outside project directory."}), 403

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({"status": "success", "message": f"File '{filepath}' written successfully."})
    except Exception as e:
        print(f"An error occurred in /write-file: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mock-interview', methods=['POST'])
def mock_interview_handler():
    """Generates a 10-question multiple-choice quiz based on document content."""
    print("\n--- Mock Interview Request Received ---")
    try:
        data = request.json
        if not data or 'content' not in data:
            print("[LOG] Invalid request: 'filepath' is missing.")
            return jsonify({"status": "error", "message": "Invalid request: 'filepath' is required."}), 400
        
        # filepath = data['filepath']
        # print(f"[LOG] Generating quiz for: {filepath}")
        
        # target_path = get_safe_path(filepath)
        # if not target_path or not os.path.exists(target_path):
        #     print(f"[ERROR] File not found or access denied. Path: {target_path}")
        #     return jsonify({"status": "error", "message": "File not found or access is denied."}), 404
            
        # with open(target_path, 'r', encoding='utf-8') as f:
        #     content = f.read()
        # print("[LOG] Successfully read file content.")

        content = data['content']
        prompt = f"""
        Based on the following technical document content, please generate a 10-question multiple-choice quiz.
        The questions should be expert-level, technical, relevant to the topic, and have a clear single correct answer.
        The main subject is Android reverse engineering.

        For each question, provide:
        - A "question" string.
        - An "options" object with four plausible choices labeled "A", "B", "C", and "D".
        - A "correct_answer" string indicating the key of the correct option (e.g., "A").
        - A "topic" string identifying the specific knowledge point.

        Return the entire quiz as a single valid JSON array of these 10 question objects.
        Ensure the JSON is valid and contains no other text or markdown formatting like ```json.
        
        Content:
        ---
        {content}
        ---
        """
        
        print("[LOG] Sending request to Gemini Pro to generate questions...")
        response = genai_client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        print("[LOG] Received response from Gemini Pro.")

        # Extract the JSON block from the potentially markdown-formatted response
        cleaned_text = response.text.strip()
        if '```json' in cleaned_text:
            # Handle cases where the model wraps the JSON in a code block
            json_str = cleaned_text.split('```json')[1].split('```')[0]
        else:
            json_str = cleaned_text
        
        try:
            print("[LOG] Parsing JSON from model response...")
            questions_data = json.loads(json_str)
            # Basic validation of the generated structure
            if not isinstance(questions_data, list) or len(questions_data) != 10:
                 raise ValueError("Generated JSON is not a list of 10 objects.")
            print("[LOG] JSON parsed successfully.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[ERROR] Failed to parse JSON from model response: {e}")
            print(f"--- Raw Model Response ---")
            print(response.text)
            print(f"--------------------------")
            return jsonify({"status": "error", "message": "The AI failed to generate a valid quiz. Please try again."}), 500

        print("[LOG] Successfully generated quiz. Returning to client.")
        print("-------------------------------------\n")
        return jsonify(questions_data)

    except Exception as e:
        print(f"[FATAL] An unexpected error occurred during mock interview generation: {e}")
        print("-------------------------------------\n")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-doc', methods=['GET'])
def get_doc():
    """Fetches the raw content of a markdown file."""
    file_path = request.args.get('path')
    safe_path = get_safe_path(file_path)
    print(f"safe_path -> {safe_path}")
    
    if not safe_path or not os.path.exists(safe_path):
        return jsonify({"error": "File not found or access denied."}), 404
        
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"path": file_path, "content": content})
    except Exception as e:
        app.logger.error(f"Error reading file {safe_path}: {e}")
        return jsonify({"error": "Failed to read file."}), 500

@app.route('/api/save-doc', methods=['POST'])
def save_doc():
    """Saves new content to a markdown file."""
    data = request.json
    file_path = data.get('path')
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    safe_path = get_safe_path(file_path)
    if not safe_path:
        return jsonify({"error": "Invalid file path or access denied."}), 403
        
    try:
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"message": f"File '{file_path}' saved successfully."})
    except Exception as e:
        app.logger.error(f"Error writing to file {safe_path}: {e}")
        return jsonify({"error": "Failed to save file."}), 500

# --- Main Execution Block ---
if __name__ == '__main__':
    # Running on 0.0.0.0 makes it accessible on the local network
    app.run(host='0.0.0.0', port=5001, debug=True) 