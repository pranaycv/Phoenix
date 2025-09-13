import os
from tree_sitter import Parser, Language
import tree_sitter_cpp as tscpp
import re

"""
/**
 * @file extract_function_code_2.py
 * @brief This script extracts a specific function from a C++ file based on a given line number, cleans it by removing comments, and saves the clean code to a text file. It uses tree-sitter for parsing and handles Doxygen comments if present.
 * @details The script reads the C++ file, parses it to find the function definition starting at the specified line, optionally includes preceding Doxygen comments, removes all comments from the function body while handling strings and preserving structure, keeps blank lines, and outputs the cleaned code to a file named based on the source file and function name.
 *
 * Classes:
 * - FileIoHandler: Manages file input/output operations for reading C++ source and writing cleaned function code.
 * - CommentHandler: Handles detection and removal of comments, including Doxygen checks.
 * - CppParser: Sets up and uses tree-sitter to parse C++ code and extract function nodes and names.
 * - FunctionExtractor: Orchestrates the extraction process, coordinating parsing, comment handling, cleaning, and saving.
 *
 * @author Pranay + AI
 */
"""

class FileIoHandler:
    """
    /**
     * @class FileIoHandler
     * @brief Class for handling file input and output operations.
     * @details Provides methods to read binary content from files and write text to output files.
     */
    """

    def ReadFileContent(self, file_path):
        """
        /**
         * @brief Reads the content of a file in binary mode.
         * @param file_path The path to the file to read.
         * @return Tuple of (content_bytes, content_str), or raises IOError.
         */
        """
        # Open file in binary mode to handle any encoding
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
        # Decode to string with replacement for errors
        content = content_bytes.decode('utf-8', errors='replace')
        return content_bytes, content

    def WriteCleanCode(self, output_file, clean_code):
        """
        /**
         * @brief Writes the cleaned code to the specified output file.
         * @param output_file The path to the output file.
         * @param clean_code The cleaned function code as a string.
         */
        """
        # Write the clean code to file in UTF-8 encoding
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_code)


class CommentHandler:
    """
    /**
     * @class CommentHandler
     * @brief Class for handling comments in C++ code.
     * @details Includes methods to check for Doxygen comments, get preceding comments, and remove comments from code.
     */
    """

    def IsDoxygenComment(self, text):
        """
        /**
         * @brief Checks if the given comment text is a Doxygen-style comment.
         * @param text The comment text to check.
         * @return True if it starts with Doxygen markers, False otherwise.
         */
        """
        # Strip and check starting markers
        text = text.strip()
        return text.startswith(('/**', '/*!', '///', '//!'))

    def GetPrecedingComments(self, node):
        """
        /**
         * @brief Collects all preceding comment nodes before a given node.
         * @param node The tree-sitter node to start from.
         * @return List of comment nodes in order from farthest to closest.
         */
        """
        comments = []
        current = node.prev_sibling
        # Traverse previous siblings if they are comments
        while current and current.type == 'comment':
            comments.append(current)
            current = current.prev_sibling
        # Reverse to get chronological order
        comments.reverse()
        return comments

    def RemoveComments(self, text):
        """
        /**
         * @brief Removes C/C++ comments from the text while preserving structure and blank lines.
         * @param text The code text to clean.
         * @return The text with comments removed but blank lines preserved.
         */
        """
        result = ''
        i = 0
        length = len(text)
        in_string = False
        string_char = ''
        while i < length:
            char = text[i]
            if in_string:
                result += char
                if char == '\\':
                    i += 1
                    if i < length:
                        result += text[i]
                        i += 1
                    continue
                if char == string_char:
                    in_string = False
                i += 1
                continue
            if char == '"' or char == "'":
                in_string = True
                string_char = char
                result += char
                i += 1
                continue
            if char == '/' and i+1 < length:
                next_char = text[i+1]
                if next_char == '/':
                    start_line = text.rfind('\n', 0, i) + 1
                    from_start = text[start_line:i]
                    if from_start.strip() == '':
                        # Keep full-line // comments (commented code or standalone comments)
                        result += '//'
                        i += 2
                        while i < length and text[i] != '\n':
                            result += text[i]
                            i += 1
                        if i < length:
                            result += text[i]
                            i += 1
                    else:
                        # Remove inline // comments
                        i += 2
                        while i < length and text[i] != '\n':
                            i += 1
                        if i < length:
                            result += text[i]
                            i += 1
                    continue
                elif next_char == '*':
                    # Always keep block comments
                    result += '/*'
                    i += 2
                    while i < length:
                        if text[i] == '*' and i+1 < length and text[i+1] == '/':
                            result += '*/'
                            i += 2
                            break
                        result += text[i]
                        i += 1
                    continue
            result += char
            i += 1
        # Clean up any extra spaces that might have been left, but preserve line structure
        lines = result.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        return '\n'.join(cleaned_lines)


class CppParser:
    """
    /**
     * @class CppParser
     * @brief Class for parsing C++ code using tree-sitter.
     * @details Initializes the parser, parses content, finds function nodes, and extracts names.
     */
    """

    def __init__(self):
        # Load C++ language for tree-sitter
        self.cpp_language = Language(tscpp.language())
        # Create parser instance
        self.parser = Parser(self.cpp_language)

    def ParseContent(self, content_bytes):
        """
        /**
         * @brief Parses the binary content into a tree-sitter tree.
         * @param content_bytes The binary file content.
         * @return The parsed tree.
         */
        """
        # Parse the bytes into a syntax tree
        tree = self.parser.parse(content_bytes)
        return tree

    def FindFunctionNode(self, tree, line_number):
        """
        /**
         * @brief Finds the function definition node starting at the given line number.
         * @param tree The parsed tree-sitter tree.
         * @param line_number The 1-based line number to match.
         * @return The function node if found, else None.
         */
        """
        # Query for function definitions
        query = self.cpp_language.query('(function_definition) @func_def')
        captures = query.captures(tree.root_node)
        for capture_name, nodes in captures.items():
            if capture_name != 'func_def':
                continue
            for node in nodes:
                # Check start line (0-based +1)
                node_start_line = node.start_point[0] + 1
                if node_start_line == line_number:
                    return node
        return None

    def GetFullFunctionName(self, function_node):
        """
        /**
         * @brief Extracts the full function name from the declarator.
         * @param function_node The function definition node.
         * @return The function name as string, or None if not found.
         */
        """
        # Get declarator node
        decl_node = function_node.child_by_field_name('declarator')
        if not decl_node or decl_node.type != 'function_declarator':
            return None
        # Get inner declarator for name
        name_part_node = decl_node.child_by_field_name('declarator')
        if not name_part_node:
            return None
        # Decode and strip
        return name_part_node.text.decode('utf-8', errors='replace').strip()


class FunctionExtractor:
    """
    /**
     * @class FunctionExtractor
     * @brief Class that orchestrates the function extraction and cleaning process.
     * @details Coordinates file reading, parsing, comment handling, code cleaning, and output saving.
     */
    """

    def __init__(self, file_path, line_number):
        # Store input parameters
        self.file_path = file_path
        self.line_number = line_number
        # Initialize helpers
        self.file_io_handler = FileIoHandler()
        self.comment_handler = CommentHandler()
        self.cpp_parser = CppParser()

    def ExtractAndSave(self):
        """
        /**
         * @brief Main method to extract, clean, and save the function code.
         */
        """
        try:
            # Read file content
            content_bytes, content = self.file_io_handler.ReadFileContent(self.file_path)
        except IOError as e:
            print(f"Error reading file: {e}")
            return

        # Parse the content
        tree = self.cpp_parser.ParseContent(content_bytes)

        # Find the function node
        function_node = self.cpp_parser.FindFunctionNode(tree, self.line_number)
        if not function_node:
            print(f"Function definition starting at line {self.line_number} not found.")
            return

        # Get preceding comments
        comments = self.comment_handler.GetPrecedingComments(function_node)
        doxygen_start_line = None
        if comments:
            # Filter Doxygen comments
            doxygen_comments = [c for c in comments if self.comment_handler.IsDoxygenComment(c.text.decode('utf-8', errors='replace'))]
            if doxygen_comments:
                # Get the earliest Doxygen line
                doxygen_start_line = min(c.start_point[0] + 1 for c in doxygen_comments)

        # Determine start line
        start_line = doxygen_start_line if doxygen_start_line else function_node.start_point[0] + 1
        # End line is function end
        end_line = function_node.end_point[0] + 1

        print(f"Start line: {start_line}")
        print(f"End line: {end_line}")

        # Extract and clean the function code while preserving blank lines
        func_text = content_bytes[function_node.start_byte:function_node.end_byte].decode('utf-8', errors='replace')
        clean_code = self.comment_handler.RemoveComments(func_text)

        # Get function name
        function_name = self.cpp_parser.GetFullFunctionName(function_node) or f"line_{self.line_number}"
        # Sanitize name for filename
        safe_func_name = function_name.replace('::', '_').replace('~', '_destructor_').replace('operator', '_operator_')
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        output_file = f"{base_name}_{safe_func_name}_clean.txt"

        try:
            # Write the clean code
            self.file_io_handler.WriteCleanCode(output_file, clean_code)
            print(f"Clean function code saved to {output_file}")
        except IOError as e:
            print(f"Error writing file: {e}")


if __name__ == "__main__":
    file_path = "D:/GIT2022/BlisbeatEye/bis_eye_main.cpp"
    line_number = 513
    # Create extractor instance
    extractor = FunctionExtractor(file_path, line_number)
    # Run extraction
    extractor.ExtractAndSave()