import os
import sys
import requests  # Import requests for direct API calls
import json
import datetime  # Import datetime for timing
import threading
import dearpygui.dearpygui as dpg

# Assuming the supplied py files are in the same directory or adjust sys.path accordingly
# sys.path.append('/path/to/scripts') if needed

from get_git_changes import CppParser as GitCppParser, FunctionExtractor as GitFunctionExtractor, GitRepoHandler, ChangeProcessor
from extract_function_code_2 import FileIoHandler, CommentHandler, CppParser as ExtractCppParser, FunctionExtractor as ExtractFunctionExtractor
from generate_docs_ollama import CppParser as DocCppParser, OllamaGenerator, FileProcessor as DocFileProcessor, FileListManager

"""
/**
 * @file auto_document_git_changes.py
 * @brief This script orchestrates the automatic documentation of changed functions in a Git repository using imported classes from supplied scripts.
 * @details It detects changes using get_git_changes_2.py components, extracts function details with extract_function_code_2.py, generates documentation via direct Ollama API calls using requests, and updates files accordingly. Only changed functions in changed files are processed.
 *
 * @author Pranay
 */
"""

class CustomOllamaGenerator:
    """
    /**
     * @class CustomOllamaGenerator
     * @brief Custom class for generating documentation using direct HTTP requests to Ollama API.
     * @details Bypasses the ollama library to directly call the REST API for better reliability with remote hosts. Includes connection testing.
     */
    """

    def __init__(self, model_name: str, host: str = 'http://192.168.0.132:11434'):
        # Initialize model and host details
        self.model_name = model_name
        self.host = host
        self.api_endpoint = f"{self.host}/api/generate"
        self.tags_endpoint = f"{self.host}/api/tags"
        self.test_connection()

    def test_connection(self):
        # Test connection to Ollama API
        try:
            response = requests.get(self.tags_endpoint)
            response.raise_for_status()
            log_message("Connected to Ollama API successfully.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.host}. Error: {str(e)}\nPlease ensure Ollama is running, OLLAMA_HOST is set to 0.0.0.0 on the server, port 11434 is open in the firewall, and the IP is correct.") from e

    def _call_api(self, prompt: str, options: dict = None, stream: bool = False, timeout: int = None):  # Changed to None for infinite wait
        # Internal method to call Ollama API with retry logic
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": options or {}
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # print(f"API call attempt {attempt + 1}/{max_retries}...")
                log_message(".", end=" ")
                response = requests.post(self.api_endpoint, json=data, timeout=timeout)
                response.raise_for_status()
                return response.json()['response']
            except requests.exceptions.Timeout as e:
                log_message(f"Timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    raise ConnectionError(f"API call failed after {max_retries} attempts: {str(e)}") from e
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"API call failed: {str(e)}") from e

    def GenerateDoc(self, func_text: str):
        """
        /**
         * @brief Generates a Doxygen-style comment block for the given function text.
         * @param func_text The function code as a string.
         * @return The generated Doxygen comment.
         */
        """
        # Prompt for generating Doxygen comment
        prompt = (
            f"{func_text}\n\n"
            "You are given a C++ function. Your task is to:\n"
            "Generate a Doxygen-style comment block.\n"
            "Use this Doxygen format: \n"
            "/**\n"
            "* @brief \n"
            "* @details \n"
            "* Steps: Make these steps clear and precise, like a mind map.\n"
            "* 1. \n"
            "* 2. \n"
            "* @param \n"
            "* @return \n"
            "*/\n\n"
            "NOTE: The output MUST begin with '/**' and end with */.\n"
        )
        return self._call_api(prompt, stream=False)

    def GenerateCodeComment(self, func_text: str, doxygen: str):
        """
        /**
         * @brief Generates inline comments for the function in JSON format.
         * @param func_text The numbered function code as a string.
         * @param doxygen The Doxygen comment (unused in prompt but passed for consistency).
         * @return The JSON string of inline comments.
         */
        """
        # Prompt for generating inline code comments
        prompt = (
            "You are a coding assistant.\n\n"
            "Below is a C++ function. Each line starts with a line number followed by a colon and a space, like this:\n"
            "<line number>: <actual code>\n\n"
            "Your task is to analyze the code and return a JSON array of inline comments for the important logic blocks only.\n\n"
            "Focus only on:\n"
            "- Loops (for/while)\n"
            "- Conditionals (if/else/switch)\n"
            "- Key algorithm steps\n"
            "- Function calls that drive the core logic\n\n"
            "CRITICAL RULES for multi-line statements:\n"
            "- For multi-line function calls, SQL queries, or string literals that span multiple lines:\n"
            "  * Place the comment ONLY on the FINAL line of the statement (the one ending with ';' or '{').\n"
            "  * Do NOT insert comments on intermediate lines.\n"
            "- For multi-line if/for/while statements:\n"
            "  * Place the comment on the line with the condition or the opening brace.\n"
            "- For variable declarations spanning multiple lines:\n"
            "  * Place the comment on the final line where the declaration ends.\n\n"
            "Avoid:\n"
            "- Comments for simple declarations, braces, or boilerplate code\n"
            "- Commenting every line — only comment meaningful logic\n\n"
            "Return a JSON array where each object contains:\n"
            "- \"line\": the line number where the comment should be inserted\n"
            "- \"comment\": a short explanation of the logic\n\n"
            "⚠️ Do NOT rewrite or reformat the code.\n"
            "⚠️ Only return a valid JSON array, and nothing else.\n\n"
            "Example format:\n"
            "[\n"
            "  { \"line\": 4, \"comment\": \"Sorts the list in ascending order\" },\n"
            "  { \"line\": 6, \"comment\": \"Loops through the list to apply processing\" }\n"
            "]\n\n"
            "Here is the code (preserve it exactly as given, including multi-line statements and backslashes):\n\n"
            + func_text
        )
        options = {'temperature': 0.0}
        return self._call_api(prompt, options=options, stream=False)
    
    def GenerateCodeReviewLog(self, file_name: str, func_name: str, func_text: str):
        """
        /**
         * @brief Reviews the given function for critical glitches.
         * @param file_name The file where the function resides.
         * @param func_name The function name.
         * @param func_text The function code as a string.
         * @return JSON string with file, function, and identified glitches.
         */
        """
        prompt = (
            "You are a strict C++ code reviewer.\n\n"
            f"File: {file_name}\n"
            f"Function: {func_name}\n\n"
            "Review the provided function code and identify any CRITICAL GLITCHES such as:\n"
            "- Memory leaks\n"
            "- Null pointer dereferences\n"
            "- Undefined behavior\n"
            "- Threading issues\n"
            "- Performance bottlenecks\n"
            "- Security risks (buffer overflow, injections, etc.)\n\n"
            "Return ONLY a JSON object in this format:\n"
            "{\n"
            "  \"file\": \"<file_name>\",\n"
            "  \"function\": \"<function_name>\",\n"
            "  \"glitches\": [\"glitch1\", \"glitch2\"]\n"
            "}\n\n"
            "Here is the code:\n\n"
            f"{func_text}\n"
        )
        options = {"temperature": 0.0, "top_p": 1.0, "top_k": 0}
        # options = {'temperature': 0.0}
        return self._call_api(prompt, options=options, stream=False)


def initialize_processors(repo_path, cxx_extensions):
    """
    Initialize all necessary parsers and handlers.
    """
    git_cpp_parser = GitCppParser()
    git_function_extractor = GitFunctionExtractor(git_cpp_parser)
    git_handler = GitRepoHandler(repo_path)
    change_processor = ChangeProcessor(git_handler, git_function_extractor, cxx_extensions)

    extract_cpp_parser = ExtractCppParser()
    comment_handler = CommentHandler()
    file_io_handler = FileIoHandler()

    doc_cpp_parser = DocCppParser()

    return git_handler, git_function_extractor, extract_cpp_parser, comment_handler, file_io_handler, git_cpp_parser

def collect_files_to_process(git_handler, git_function_extractor, start_date_str, branch, cxx_extensions):
    """
    Detect changes and collect files to process.
    """
    old_commit = git_handler.GetLastCommitBeforeDate(start_date_str, branch if branch else None)
    changed = git_handler.GetDiffNameStatus(old_ref=old_commit)

    files_to_process = []
    for path, status in changed.items():
        if not path.lower().endswith(cxx_extensions) or status == 'D':
            continue

        new_content = git_handler.GetNewContent(path)
        if new_content is None:
            continue

        old_functions = {}
        if status in ('M', 'R', 'C'):
            old_content = git_handler.GetOldContent(path, old_ref=old_commit)
            if old_content is not None:
                old_functions = git_function_extractor.ExtractFunctions(old_content)

        new_functions = git_function_extractor.ExtractFunctions(new_content)

        added_keys = set(new_functions) - set(old_functions)
        modified_keys = {k for k in set(old_functions) & set(new_functions) if old_functions[k][0] != new_functions[k][0]}
        changed_keys = added_keys | modified_keys

        changed_lines = [new_functions[k][1] for k in changed_keys]

        if not changed_lines:
            continue

        files_to_process.append((path, new_content, new_functions, changed_lines))
    
    return files_to_process

def process_file(path, reviewed_funcs, new_content, new_functions, changed_lines, repo_path,
                 git_cpp_parser, git_function_extractor, extract_cpp_parser,
                 comment_handler, file_io_handler, ollama_generator, verify_code, document_code):
    """
    Process a single file: parse, generate docs/comments, update file,
    and optionally generate code review logs.
    """
    full_path = os.path.join(repo_path, path)
    log_message(f"📄 Processing file: {path}")

    # Parse file with tree-sitter
    tree = git_cpp_parser.parser.parse(bytes(new_content, 'utf-8'))

    # Find changed functions
    changed_nodes = []
    for line in changed_lines:
        node = extract_cpp_parser.FindFunctionNode(tree, line)
        if node:
            changed_nodes.append(node)

    changed_nodes.sort(key=lambda n: n.start_point[0], reverse=True)

    start_line_to_key = {new_functions[k][1]: k for k in new_functions}
    lines = new_content.splitlines(keepends=True)

    for node in changed_nodes:
        start_line = node.start_point[0] + 1
        key = start_line_to_key.get(start_line)
        func_name = git_function_extractor.GetFunctionName(key) if key else "unknown"
        log_message(f"  🔧 Processing function: {func_name}")

        # Extract function text
        func_lines = lines[node.start_point[0]: node.end_point[0] + 1]
        func_text = ''.join(func_lines)

        # Clean comments
        clean_text = comment_handler.RemoveComments(func_text)
        clean_lines = clean_text.splitlines()
        clean_func_text = '\n'.join(clean_lines)
        clean_func_lines = [line + '\n' for line in clean_lines]

        if document_code:
            # Check for existing comments
            comments = comment_handler.GetPrecedingComments(node)
            doxygen_comments = [
                c for c in comments
                if comment_handler.IsDoxygenComment(c.text.decode('utf-8', errors='replace'))
            ]
            doxygen_start_row = min(c.start_point[0] for c in doxygen_comments) if doxygen_comments else None

            start_row = doxygen_start_row if doxygen_start_row is not None else node.start_point[0]
            end_row = node.end_point[0]

            # Generate doxygen
            dox_comment = ollama_generator.GenerateDoc(clean_func_text)
            start_index = dox_comment.find('/**')
            end_index = dox_comment.find('*/', start_index)
            doxygen = dox_comment[start_index:end_index + 2] + '\n' if start_index != -1 and end_index != -1 else ''

            # if verify_code:
            #     log_message("Generated Doxygen:")
            #     log_message(doxygen)

            # Numbered function text for inline comments
            def number_code_lines(code_str):
                return "\n".join(f"{i}: {line.rstrip()}" for i, line in enumerate(code_str.strip().splitlines(), start=1))

            numbered_func = number_code_lines(clean_func_text)

            # Generate inline comments
            json_response = ollama_generator.GenerateCodeComment(numbered_func, doxygen)
            clean_response = json_response.strip().removeprefix('```json').removesuffix('```').strip()

            try:
                comments = json.loads(clean_response)
            except json.JSONDecodeError:
                comments = []

            # if verify_code:
            #     log_message("Generated Inline Comments JSON:")
            #     log_message(json.dumps(comments, indent=4))

            # Apply inline comments
            comments.sort(key=lambda x: x['line'], reverse=True)
            for comment in comments:
                line_idx = comment['line'] - 1
                if 0 <= line_idx < len(clean_func_lines):
                    stripped_line = clean_func_lines[line_idx].rstrip('\r\n')
                    clean_func_lines[line_idx] = stripped_line + '\t // ' + comment['comment'] + '\n'

            # Replace old function with new version
            replacement_lines = [line + '\n' if not line.endswith('\n') else line for line in doxygen.splitlines()] + clean_func_lines
            lines[start_row: end_row + 1] = replacement_lines

        # === NEW: Code Review Log (if verify_code) ===
        if verify_code and (path, func_name) in reviewed_funcs:
            log_message(f"  ⏩ Skipping {func_name} (already reviewed)")
            continue
        elif verify_code:
            review_json = ollama_generator.GenerateCodeReviewLog(path, func_name, clean_func_text)
            try:
                review_data = json.loads(review_json.strip())
            except json.JSONDecodeError:
                review_data = {
                    "file": path,
                    "function": func_name,
                    "glitches": ["Failed to parse review JSON"]
                }

            # Add date and time to the review data
            review_data["date_time"] = datetime.datetime.now().isoformat()

            master_log_path = os.path.join(os.getcwd(), "code_review_log.json")
            if os.path.exists(master_log_path):
                with open(master_log_path, "r", encoding="utf-8") as f:
                    master_log = json.load(f)
            else:
                master_log = []

            master_log.append(review_data)

            with open(master_log_path, "w", encoding="utf-8") as f:
                json.dump(master_log, f, indent=4)

            log_message(f"🔍 Code review log updated for {func_name} in {path}")

    # Save updated file
    if document_code:
        file_io_handler.WriteCleanCode(full_path, ''.join(lines))
        log_message(f"✅ Updated {path}\n")
    else:
        log_message(f"Skipped documentation for {path}\n")


def run_processing(repo_path, last_date, ollama_host, branch, log_entry, verify_code, cxx_extensions, document_code):
    # Main processing logic run in a thread
    model_name = "gpt-oss:20b"  # Hardcoded
    start_time = datetime.datetime.now()
    log_message(f"Start time: {start_time}")

    # Use custom generator
    try:
        ollama_generator = CustomOllamaGenerator(model_name, ollama_host)
    except ConnectionError as e:
        log_message(str(e))
        return

    # Initialize processors
    git_handler, git_function_extractor, extract_cpp_parser, comment_handler, file_io_handler, git_cpp_parser = initialize_processors(repo_path, cxx_extensions)

    # Collect files
    # start_date_str = last_date.strftime('%Y-%m-%d')
    files_to_process = collect_files_to_process(git_handler, git_function_extractor, last_date, branch, cxx_extensions)

    # Display files info
    log_message(f"\nTotal files to process: {len(files_to_process)}")

    log_message("\nFiles to process:")
    for i, (path, _, _, _) in enumerate(files_to_process, 1):
        log_message(f"  {i}. {path}")

    log_message("\nStarting processing...\n")

    # === Load existing review log once per file ===
    master_log_path = os.path.join(os.getcwd(), "code_review_log.json")
    if os.path.exists(master_log_path):
        with open(master_log_path, "r", encoding="utf-8") as f:
            try:
                master_log = json.load(f)
            except json.JSONDecodeError:
                master_log = []
    else:
        master_log = []

    # Convert to set for quick lookup (file,function)
    reviewed_funcs = {(entry["file"], entry["function"]) for entry in master_log if isinstance(entry, dict) and "file" in entry and "function" in entry}

    print(f"Already reviewed functions: {len(reviewed_funcs)}")

    # Process each file
    for path, new_content, new_functions, changed_lines in files_to_process:
        process_file(path, reviewed_funcs, new_content, new_functions, changed_lines, repo_path, git_cpp_parser, git_function_extractor, extract_cpp_parser, comment_handler, file_io_handler, ollama_generator, verify_code, document_code)

    end_time = datetime.datetime.now()
    log_message(f"End time: {end_time}")

    # Save last documentation date in GIT directory
    last_doc_path = os.path.join(repo_path, "last_doc_date.json")
    with open(last_doc_path, "w", encoding="utf-8") as f:
        json.dump({"last_date": datetime.date.today().strftime("%Y-%m-%d")}, f, indent=4)
    log_message(f"📅 Saved last documentation date to {last_doc_path}")


    # Append log entry if provided
    if log_entry:
        log_message("Log Entry:")
        log_message(log_entry)

def run_processing_wrapper(repo_path, last_date, ollama_host, branch, log_entry, verify_code, cxx_extensions, document_code):
    try:
        run_processing(repo_path, last_date, ollama_host, branch, log_entry, verify_code, cxx_extensions, document_code)
    finally:
        # Re-enable the button when done (success or error)
        dpg.configure_item("generate_button", enabled=True)


def start_processing(sender, app_data, user_data):
    # Disable the button immediately
    dpg.configure_item("generate_button", enabled=False)

    # Clear log before starting a new run
    dpg.set_value("log_text", "")

    repo_path = dpg.get_value("dir_path")
    date_value = dpg.get_value("date")
    ollama_host = dpg.get_value("ollama_host")
    branch = dpg.get_value("branch")
    log_entry = dpg.get_value("log_entry")
    verify_code = dpg.get_value("verify_code")
    document_code = dpg.get_value("document_code")

    cxx_extensions = ('.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx', '.c++', '.h++', '.h', '.c')

    # Run in thread to avoid blocking GUI
    threading.Thread(
        target=run_processing_wrapper,
        args=(repo_path, date_value, ollama_host, branch, log_entry, verify_code, cxx_extensions, document_code)
    ).start()


def get_last_documented_date(sender, app_data, user_data):
    repo_path = dpg.get_value("dir_path")
    last_doc_path = os.path.join(repo_path, "last_doc_date.json")
    if os.path.exists(last_doc_path):
        with open(last_doc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        last_date = data.get("last_date", "YYYY-MM-DD")
        dpg.set_value("date", last_date)
        log_message(f"Loaded last documented date: {last_date}")
    else:
        last_date = "YYYY-MM-DD"
        dpg.set_value("date", last_date)
        log_message("No last documented date file found.")


def update_date(sender, app_data, user_data):
    # Update selected date text when date changes
    date_value = dpg.get_value("date_picker")
    last_date = datetime.date(date_value["year"] + 1900, date_value["month"] + 1, date_value["day"])
    dpg.set_value("selected_date", last_date.strftime('%Y-%m-%d'))

def log_message(message, end="\n"):
    # Append message to logger
    current_log = dpg.get_value("log_text")
    dpg.set_value("log_text", current_log + message + end)
    dpg.set_y_scroll("log_window", dpg.get_y_scroll_max("log_window"))

def setup_gui():
    # Setup Dear PyGui interface
    dpg.create_context()

    # Theme for light gray background and black text
    # with dpg.theme() as global_theme:
    #     with dpg.theme_component(dpg.mvAll):
    #         dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (37, 37, 37, 255))  # Light gray
    #         dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (37, 37, 37, 255))  # Light gray for child
    #         dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  # Black text
    #         dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (37, 37, 37, 255))  # Light gray for inputs
    #         dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 255))  # Black border

    # dpg.bind_theme(global_theme)

    # Custom theme for buttons
    with dpg.theme() as button_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (65, 105, 225, 255))         # Royal Blue (normal)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (72, 118, 255, 255))  # Lighter blue on hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 140, 0, 255))    # Orange on click

    vertical_spacing = 5

    with dpg.window(label="Smart Document - VisionStudio", width=1000, height=800):
        with dpg.group(horizontal=True):
            with dpg.group(width=200):  # Left side for inputs
                # Company logo - keep aspect ratio
                # logo_width, logo_height, channels, data = dpg.load_image("company_logo.png")  # Replace with actual logo path
                logo_width, logo_height, channels, data = dpg.load_image("logo.png")  # Replace with actual logo path
                with dpg.texture_registry(show=False):
                    texture_id = dpg.add_static_texture(width=logo_width, height=logo_height, default_value=data)

                aspect_ratio = logo_height / logo_width
                dpg.add_image(texture_id, width=200, height=200 * aspect_ratio)

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_input_text(label="Directory Path", default_value="D:/GIT2022", tag="dir_path", width=200)

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_input_text(label="Last Document Date", default_value="YYYY-MM-DD", tag="date", width=200)

                dpg.add_spacing(count=vertical_spacing)
                get_last_btn = dpg.add_button(label="Get Last Documented Date", tag="get_last_date_button", callback=get_last_documented_date, width=200)

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_input_text(label="Ollama Host URL", default_value="http://192.168.0.132:11434", tag="ollama_host", width=200)

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_input_text(label="Branch (optional)", tag="branch", width=200)

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_checkbox(label="Code Verification Log", default_value=True, tag="verify_code")

                dpg.add_spacing(count=vertical_spacing)
                dpg.add_checkbox(label="Document Code", default_value=True, tag="document_code")

                dpg.add_spacing(count=vertical_spacing)
                generate_btn = dpg.add_button(label="Generate", tag="generate_button", callback=start_processing, width=200)

                dpg.bind_item_theme(generate_btn, button_theme)
                dpg.bind_item_theme(get_last_btn, button_theme)

            with dpg.child_window(width=630, height=800, tag="log_window"):  # Right side for log
                dpg.add_text(tag="log_text", wrap=0)  # wrap=0 disables word wrap
                # dpg.add_text(tag="log_text")

    # Try to load last documented date
    try:
        repo_path = dpg.get_value("dir_path")
        last_doc_path = os.path.join(repo_path, "last_doc_date.json")
        if os.path.exists(last_doc_path):
            with open(last_doc_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            dpg.set_value("date", data.get("last_date", "YYYY-MM-DD"))
    except Exception as e:
        log_message(f"⚠️ Could not load last documented date: {e}")


    dpg.create_viewport(title='Smart Document - VisionStudio', width=1020, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Initial date update
    # update_date(None, None, None)

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    setup_gui()