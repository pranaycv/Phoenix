import os
import sys
from tree_sitter import Language, Parser
import tree_sitter_cpp as tscpp
import ollama
import datetime
import codecs
import json

"""
/**
 * @file generate_docs_ollama.py
 * @brief This script automates the documentation of C++ source files by extracting functions, generating Doxygen-style comments and inline code comments using Ollama AI models, and inserting them back into the files while handling file processing status and logging.
 * @details The script traverses a specified directory for .cpp and .hpp files, uses tree-sitter for parsing C++ code, detects file encodings, generates AI-based documentation, and manages a resumable processing pipeline with status tracking.
 *
 * Classes:
 * - CppParser: Responsible for parsing C++ code using tree-sitter, extracting function definitions, and gathering function metadata like names and line ranges.
 * - OllamaGenerator: Interfaces with Ollama AI models to generate Doxygen comments and inline code comments for functions.
 * - FileProcessor: Handles reading, processing, and writing individual C++ files, including inserting generated comments and handling encoding.
 * - FileListManager: Manages the list of files to process, tracks their status (SUCCESS, FAILURE, or pending), prepares file lists, and provides processing summaries.
 *
 * @author Pranay + AI
 */
"""

class CppParser:
    """
    /**
     * @class CppParser
     * @brief Class for parsing C++ code and extracting function information using tree-sitter.
     * @details Initializes the tree-sitter parser for C++ and provides methods to extract function nodes, names, and other metadata.
     */
    """

    def __init__(self):
        # Initialize the C++ language and parser
        self.cpp_language = Language(tscpp.language())
        self.parser = Parser(self.cpp_language)

    def ParseCode(self, code: bytes):
        """
        /**
         * @brief Parses the given C++ code bytes into a tree-sitter tree.
         * @param code The binary code content to parse.
         * @return The parsed tree root node.
         */
        """
        # Use the parser to create a syntax tree from the code
        tree = self.parser.parse(code)
        return tree

    def ExtractFunctions(self, root_node):
        """
        /**
         * @brief Traverses the parse tree to collect all function_definition nodes.
         * @param root_node The root node of the parsed tree.
         * @return List of function_definition nodes.
         */
        """
        functions = []

        def Traverse(node):
            # Check if the current node is a function definition
            if node.type == 'function_definition':
                functions.append(node)
            # Recurse into children
            for child in node.children:
                Traverse(child)

        # Start traversal from root
        Traverse(root_node)
        return functions

    def GetFunctionName(self, declarator):
        """
        /**
         * @brief Extracts the full name of a function from its declarator node.
         * @param declarator The function_declarator node.
         * @return The function name as a string, or None if not found.
         */
        """
        inner_decl = declarator.child_by_field_name('declarator')
        if not inner_decl:
            return None

        def GetFullName(node):
            # Handle identifier nodes
            if node.type == 'identifier':
                return node.text.decode('utf-8')
            # Handle qualified identifiers (namespaces)
            if node.type == 'qualified_identifier':
                scope = node.child_by_field_name('scope')
                name = node.child_by_field_name('name')
                full = ''
                if scope:
                    full += GetFullName(scope) + '::'
                if name:
                    full += GetFullName(name)
                return full
            # Skip template arguments
            if node.type == 'template_argument_list':
                return ''
            # Recurse through children if no direct match
            for child in node.children:
                result = GetFullName(child)
                if result:
                    return result
            return ''

        # Get the full qualified name
        return GetFullName(inner_decl)

    def GetFunctionInfo(self, functions, original_code):
        """
        /**
         * @brief Gathers metadata for each function, including name and line ranges.
         * @param functions List of function nodes.
         * @param original_code The original code as a string.
         * @return List of dictionaries with function info.
         */
        """
        function_info = []
        for idx, func in enumerate(functions):
            # Find the declarator to get the name
            declarator = next((c for c in func.children if c.type == 'function_declarator'), None)
            name = self.GetFunctionName(declarator) if declarator else f'function_{idx}'

            # Calculate start and end lines based on byte positions
            start_line = original_code[:func.start_byte].count('\n')
            end_line = original_code[:func.end_byte].count('\n')

            # Append info dictionary
            function_info.append({
                'name': name,
                'start_line': start_line,
                'end_line': end_line,
                'func_node': func
            })
        return function_info

    def BreakFunctionIntoSections(self, func_code: str, long_loop_threshold: int = 50) -> list:
        """
        /**
         * @brief Breaks a C++ function into logical sections using tree-sitter.
         * @details Keeps top-level statements as sections; recurses into long loops if they exceed the threshold.
         * @param func_code The full text of the C++ function.
         * @param long_loop_threshold Line count threshold for breaking down loops (default 50).
         * @return List of strings, each a logical section.
         */
        """
        # Parse the function code into a tree
        tree = self.parser.parse(bytes(func_code, 'utf-8'))
        root = tree.root_node

        # Locate the function_definition node
        func_def = next((n for n in root.children if n.type == 'function_definition'), None)
        if not func_def:
            raise ValueError("No function definition found in the provided code.")

        # Locate the function body (compound_statement)
        body = next((c for c in func_def.children if c.type == 'compound_statement'), None)
        if not body:
            raise ValueError("No function body found in the function definition.")

        sections = []

        def CollectSections(node):
            # Handle simple statements as single sections
            if node.type in ('declaration', 'expression_statement', 'return_statement', 'break_statement', 'continue_statement'):
                section_text = node.text.decode('utf-8').strip()
                if section_text:
                    sections.append(section_text)
            # Handle non-loop control structures as single sections
            elif node.type in ('if_statement', 'while_statement', 'do_statement', 'switch_statement'):
                section_text = node.text.decode('utf-8').strip()
                if section_text:
                    sections.append(section_text)
            # Handle for loops, checking if body is long
            elif node.type in ('for_statement'):
                body_node = next((c for c in node.children if c.type == 'compound_statement'), None)
                if body_node:
                    # Approximate line count
                    line_count = body_node.end_point[0] - body_node.start_point[0] + 1
                    if line_count > long_loop_threshold:
                        # Recurse into long loop: add header, recurse body, add closing brace
                        header = node.text.decode('utf-8')[:body_node.start_byte - node.start_byte].strip() + ' {'
                        sections.append(header)
                        for body_child in body_node.children:
                            if body_child.type not in ('{', '}'):
                                CollectSections(body_child)
                        sections.append('}')
                    else:
                        # Short loop as single section
                        section_text = node.text.decode('utf-8').strip()
                        sections.append(section_text)
                else:
                    # Rare case: loop without compound body
                    section_text = node.text.decode('utf-8').strip()
                    sections.append(section_text)
            # Recurse into compound statements
            elif node.type == 'compound_statement':
                for child in node.children:
                    if child.type not in ('{', '}'):
                        CollectSections(child)
            # Fallback for other nodes
            else:
                section_text = node.text.decode('utf-8').strip()
                if section_text:
                    sections.append(section_text)

        # Start collecting from the body
        CollectSections(body)
        return sections


class OllamaGenerator:
    """
    /**
     * @class OllamaGenerator
     * @brief Class for generating documentation and comments using Ollama AI models.
     * @details Provides methods to generate Doxygen-style comments and inline code comments.
     */
    """

    def __init__(self, model_name: str):
        # Store the model name for Ollama calls
        self.model_name = model_name

    def GenerateDoc(self, func_text: str):
        """
        /**
         * @brief Generates a Doxygen-style comment block for the given function text.
         * @param func_text The function code as a string.
         * @return The generated Doxygen comment.
         */
        """
        # Construct the prompt for Doxygen generation
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
        # Call Ollama to generate response
        response = ollama.generate(model=self.model_name, prompt=prompt)
        return response['response']

    def GenerateCodeComment(self, func_text: str, doxygen: str):
        """
        /**
         * @brief Generates inline comments for the function in JSON format.
         * @param func_text The numbered function code as a string.
         * @param doxygen The Doxygen comment (unused in prompt but passed for consistency).
         * @return The JSON string of inline comments.
         */
        """
        # Construct the prompt for inline comments
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
        # Call Ollama with low temperature for determinism
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                'temperature': 0.0  # Ensures deterministic output
            }
        )
        return response['response']


class FileProcessor:
    """
    /**
     * @class FileProcessor
     * @brief Class for processing individual C++ files, inserting comments.
     * @details Handles file reading with encoding detection, function extraction, comment generation, and writing back modified code.
     */
    """

    def __init__(self, cpp_parser: CppParser, ollama_generator: OllamaGenerator):
        # Store references to parser and generator
        self.cpp_parser = cpp_parser
        self.ollama_generator = ollama_generator

    def ReadFileWithEncoding(self, file_path):
        """
        /**
         * @brief Reads a file with automatic encoding detection.
         * @param file_path The path to the file.
         * @return Tuple of (code bytes in UTF-8, detected encoding).
         */
        """
        # Read raw binary content
        with open(file_path, 'rb') as f:
            raw = f.read()

        # Detect BOM for encoding
        if raw.startswith(codecs.BOM_UTF16_LE):
            encoding = 'utf-16-le'
        elif raw.startswith(codecs.BOM_UTF16_BE):
            encoding = 'utf-16-be'
        elif raw.startswith(codecs.BOM_UTF8):
            encoding = 'utf-8-sig'
        else:
            encoding = None

        # Decode if BOM found
        if encoding:
            text = raw.decode(encoding)
            return text.encode('utf-8'), encoding

        # Try common encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'windows-1252', 'ascii']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                return content.encode('utf-8'), enc
            except UnicodeDecodeError:
                continue

        # Fallback with error replacement
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return content.encode('utf-8'), 'utf-8'

    def NumberCodeLinesFromString(self, code_str):
        """
        /**
         * @brief Numbers the lines of code for Ollama input.
         * @param code_str The code as a string.
         * @return Numbered lines as a single string.
         */
        """
        numbered_lines = []
        # Enumerate lines starting from 1
        for i, line in enumerate(code_str.strip().splitlines(), start=1):
            numbered_lines.append(f"{i}: {line.rstrip()}")
        return "\n".join(numbered_lines)

    def ProcessFile(self, file_path):
        """
        /**
         * @brief Processes a C++ file by extracting functions, generating and inserting comments.
         * @param file_path The path to the C++ file.
         */
        """
        # Read file with encoding detection
        code, detected_encoding = self.ReadFileWithEncoding(file_path)
        print(f"File read with encoding: {detected_encoding}")

        # Parse the code
        tree = self.cpp_parser.ParseCode(code)
        root = tree.root_node

        # Extract function nodes
        functions = self.cpp_parser.ExtractFunctions(root)

        # Decode code to string, handling errors
        try:
            original_code = code.decode('utf-8')
        except UnicodeDecodeError:
            original_code = code.decode('utf-8', errors='replace')
            print("Warning: Some characters were replaced during decoding")

        # Split into lines preserving newlines
        lines = original_code.splitlines(keepends=True)

        # Get function info
        function_info = self.cpp_parser.GetFunctionInfo(functions, original_code)

        # Sort functions by start line in reverse to avoid offset issues
        function_info.sort(key=lambda x: x['start_line'], reverse=True)

        # Process each function
        for info in function_info:
            print(f"Processing function: {info['name']}")

            # Extract function lines
            func_lines = lines[info['start_line']:info['end_line'] + 1]
            func_text = ''.join(func_lines)

            # Generate Doxygen comment
            dox_comment = self.ollama_generator.GenerateDoc(func_text)
            start_index = dox_comment.find('/**')
            end_index = dox_comment.find('*/', start_index)
            doxygen = ''
            if start_index != -1 and end_index != -1:
                doxygen = dox_comment[start_index:end_index + 2] + '\n'

            # Number lines for inline comments
            numbered_func = self.NumberCodeLinesFromString(func_text)

            # Generate inline comments JSON
            json_response = self.ollama_generator.GenerateCodeComment(numbered_func, doxygen)

            # Clean and parse JSON
            clean_response = json_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:].strip()
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3].strip()

            try:
                comments = json.loads(clean_response)
            except json.JSONDecodeError:
                comments = []
                print(f"Failed to parse JSON for function {info['name']}")

            # Sort comments by line in reverse to avoid offset issues
            comments.sort(key=lambda x: x['line'], reverse=True)

            # Insert inline comments into function lines
            for comment in comments:
                line_idx = comment['line'] - 1
                if 0 <= line_idx < len(func_lines):
                    stripped_line = func_lines[line_idx].rstrip('\r\n')
                    func_lines[line_idx] = stripped_line + '\t // ' + comment['comment'] + '\n'

            # Prepare replacement lines with Doxygen
            replacement_lines = []
            if doxygen:
                replacement_lines.append(doxygen)
            replacement_lines.extend(func_lines)

            # Replace in main lines
            lines[info['start_line']:info['end_line'] + 1] = replacement_lines

        # Write modified lines back to file
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.writelines(lines)


class FileListManager:
    """
    /**
     * @class FileListManager
     * @brief Manages the list of files to process and their status.
     * @details Prepares file lists, reads/updates status, and provides summaries.
     */
    """

    def __init__(self, source_directory):
        # Set paths for file list and log
        self.source_directory = source_directory
        self.file_list_path = source_directory + "/file_processing_list.txt"
        self.log_file = source_directory + "/processing_log.txt"

    def PrepareFileList(self):
        """
        /**
         * @brief Prepares a text file with all .cpp and .hpp files in the directory.
         */
        """
        print("Preparing file list...")
        with open(self.file_list_path, 'w') as f:
            # Walk the directory tree
            for root, dirs, files in os.walk(self.source_directory):
                for file in files:
                    if file.endswith(('.cpp', '.hpp')):
                        file_path = os.path.join(root, file)
                        f.write(f"{file_path}\n")
        print(f"File list prepared at: {self.file_list_path}")

    def ReadFileStatus(self):
        """
        /**
         * @brief Reads the file list and returns a dictionary of file paths and their status.
         * @return Dict of {file_path: status} where status is 'SUCCESS', 'FAILURE', or None.
         */
        """
        file_status = {}
        if not os.path.exists(self.file_list_path):
            return file_status

        with open(self.file_list_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse status if present
                if line.endswith(' - SUCCESS') or line.endswith(' - FAILURE'):
                    parts = line.rsplit(' - ', 1)
                    file_path = parts[0]
                    status = parts[1]
                    file_status[file_path] = status
                else:
                    file_status[line] = None

        return file_status

    def UpdateFileStatus(self, file_path, status):
        """
        /**
         * @brief Updates the status of a specific file in the file list.
         * @param file_path The file to update.
         * @param status The new status ('SUCCESS' or 'FAILURE').
         */
        """
        # Read current lines
        with open(self.file_list_path, 'r') as f:
            lines = f.readlines()

        # Update the matching line
        updated_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove existing status
            if line.endswith(' - SUCCESS') or line.endswith(' - FAILURE'):
                current_file_path = line.rsplit(' - ', 1)[0]
            else:
                current_file_path = line

            if current_file_path == file_path:
                updated_lines.append(f"{file_path} - {status}\n")
            else:
                updated_lines.append(line + '\n')

        # Write back
        with open(self.file_list_path, 'w') as f:
            f.writelines(updated_lines)

    def GetPendingFiles(self, file_status):
        """
        /**
         * @brief Returns list of files that haven't been processed yet.
         * @param file_status The status dictionary.
         * @return List of pending file paths.
         */
        """
        return [file_path for file_path, status in file_status.items() if status is None]

    def GetProcessingSummary(self, file_status):
        """
        /**
         * @brief Returns a summary of processing status.
         * @param file_status The status dictionary.
         * @return Dict with 'total', 'success', 'failure', 'pending'.
         */
        """
        total = len(file_status)
        success = sum(1 for status in file_status.values() if status == 'SUCCESS')
        failure = sum(1 for status in file_status.values() if status == 'FAILURE')
        pending = sum(1 for status in file_status.values() if status is None)

        return {
            'total': total,
            'success': success,
            'failure': failure,
            'pending': pending
        }

    def LogEntry(self, entry):
        """
        /**
         * @brief Appends an entry to the log file.
         * @param entry The log message.
         */
        """
        with open(self.log_file, 'a') as log:
            log.write(entry)


if __name__ == '__main__':
    # Define source directory
    source_directory = r"/home/administrator/Dev/Pranay/CodeDocumentation/Final_Pending"

    # Initialize manager
    file_list_manager = FileListManager(source_directory)

    # Prepare file list if not exists
    if not os.path.exists(file_list_manager.file_list_path):
        file_list_manager.PrepareFileList()

    # Read current status
    file_status = file_list_manager.ReadFileStatus()

    # Print initial summary
    summary = file_list_manager.GetProcessingSummary(file_status)
    print(f"\nProcessing Summary:")
    print(f"Total files: {summary['total']}")
    print(f"Successfully processed: {summary['success']}")
    print(f"Failed: {summary['failure']}")
    print(f"Pending: {summary['pending']}")

    # Get pending files
    pending_files = file_list_manager.GetPendingFiles(file_status)

    if not pending_files:
        print("\nAll files have been processed!")
    else:
        print(f"\nResuming processing from {len(pending_files)} pending files...")

        # Initialize parser and generator
        cpp_parser = CppParser()
        model_name = "gpt-oss:20b"
        ollama_generator = OllamaGenerator(model_name)
        file_processor = FileProcessor(cpp_parser, ollama_generator)

        # Process each pending file
        for file_path in pending_files:
            print(f"Extracting functions from {file_path}...")
            start_time = datetime.datetime.now()

            try:
                # Process the file
                file_processor.ProcessFile(file_path)
                completion_time = datetime.datetime.now()

                # Update status to SUCCESS
                file_list_manager.UpdateFileStatus(file_path, 'SUCCESS')

                # Log success
                log_entry = f"Success: {file_path} completed at {completion_time}\n"
                file_list_manager.LogEntry(log_entry)

                print(f"  ✓ Completed successfully")

            except Exception as e:
                failure_time = datetime.datetime.now()

                # Update status to FAILURE
                file_list_manager.UpdateFileStatus(file_path, 'FAILURE')

                # Log failure
                log_entry = f"Failure: {file_path} failed at {failure_time} with reason: {str(e)}\n"
                file_list_manager.LogEntry(log_entry)

                print(f"  ✗ Failed: {str(e)}")

        # Print final summary
        final_file_status = file_list_manager.ReadFileStatus()
        final_summary = file_list_manager.GetProcessingSummary(final_file_status)
        print(f"\nFinal Processing Summary:")
        print(f"Total files: {final_summary['total']}")
        print(f"Successfully processed: {final_summary['success']}")
        print(f"Failed: {final_summary['failure']}")
        print(f"Pending: {final_summary['pending']}")