import os
import subprocess
import hashlib
from tree_sitter import Parser, Language
import tree_sitter_cpp as tscpp
import re
import argparse

"""
/**
 * @file get_git_changes_2.py
 * @brief This script analyzes Git changes in a C++ repository to identify added, modified, or deleted functions in changed files from a specified start date to current.
 * @details It utilizes Git commands to retrieve changed files since the start date, employs tree-sitter for parsing C++ code to extract function definitions, computes MD5 hashes to detect content modifications, and outputs the changes including function names and their starting line numbers.
 *
 * Classes:
 * - CppParser: Initializes the tree-sitter language and parser for C++ code.
 * - FunctionExtractor: Extracts function information from C++ content and derives function names.
 * - GitRepoHandler: Manages Git repository operations such as directory change, diff retrieval, and content fetching for old and new file versions.
 * - ChangeProcessor: Orchestrates the processing of changes by comparing function sets and printing the results.
 *
 * @author Pranay + AI
 */
"""

class CppParser:
    """
    /**
     * @class CppParser
     * @brief Class for initializing the tree-sitter parser specific to C++.
     * @details Sets up the C++ language module and creates a parser instance for code analysis.
     */
    """

    def __init__(self):
        # Load the C++ language module for tree-sitter
        self.cpp_language = Language(tscpp.language())
        # Create the parser instance with the C++ language
        self.parser = Parser(self.cpp_language)


class FunctionExtractor:
    """
    /**
     * @class FunctionExtractor
     * @brief Class for extracting and processing function information from C++ code.
     * @details Uses the parser to build a syntax tree, queries for function definitions, and computes hashes and names.
     */
    """

    def __init__(self, cpp_parser: CppParser):
        # Store the CppParser instance for access to parser and language
        self.cpp_parser = cpp_parser

    def ExtractFunctions(self, content):
        """
        /**
         * @brief Extracts function definitions from the given C++ content.
         * @param content The C++ source code as a string.
         * @return A dictionary with function keys mapping to (hash, start_line) tuples.
         */
        """
        # Parse the content into a syntax tree
        tree = self.cpp_parser.parser.parse(bytes(content, 'utf-8'))
        # Create a query to capture function definitions
        query = self.cpp_parser.cpp_language.query('(function_definition) @func')
        functions = {}
        # Execute the query to get captures
        captures = query.captures(tree.root_node)
        # Group captures by name (though typically single capture name)
        for capture_name, nodes in captures.items():
            for node in nodes:
                # Get the body node and check if it's a compound statement
                body_node = node.child_by_field_name('body')
                if not (body_node and body_node.type == 'compound_statement'):
                    continue
                # Get the declarator node
                decl_node = node.child_by_field_name('declarator')
                if not decl_node:
                    continue

                # Adjust node for text if it's within a template declaration
                node_for_text = node
                if node.parent and node.parent.type in ('template_declaration'):
                    node_for_text = node.parent

                # Use the declarator text as the key
                key = decl_node.text.decode('utf-8', errors='replace').strip()

                # Get the full function text
                func_text = node_for_text.text.decode('utf-8', errors='replace')
                # Compute MD5 hash of the function text
                func_hash = hashlib.md5(func_text.encode('utf-8')).hexdigest()
                # Calculate 1-based start line
                start_line = node.start_point[0] + 1
                # Store in dictionary
                functions[key] = (func_hash, start_line)

        return functions

    def GetFunctionName(self, key):
        """
        /**
         * @brief Derives the function name from the declarator key.
         * @param key The declarator string used as key.
         * @return The extracted function name.
         */
        """
        # Match the name before parameters
        match = re.match(r'([^\(]+)', key)
        if match:
            name = match.group(1).strip()
            # Remove trailing qualifiers
            name = re.sub(r'\s+(const|override|final|noexcept|volatile)\s*$', '', name).strip()
            return name
        return key.strip()


class GitRepoHandler:
    """
    /**
     * @class GitRepoHandler
     * @brief Class for handling Git repository operations.
     * @details Manages directory navigation, diff retrieval, and content access for file versions.
     */
    """

    def __init__(self, repo_path):
        # Store the repository path
        self.repo_path = repo_path

    def GetCurrentBranch(self):
        """
        /**
         * @brief Gets the current branch name.
         * @return: The current branch name or None if not found.
         */
        """
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path
            ).decode('utf-8').strip()
            return branch if branch else None
        except subprocess.CalledProcessError:
            return None

    def GetLastCommitBeforeDate(self, start_date, branch=None):
        """
        /**
         * @brief Finds the last commit before the given start date.
         * @param start_date The start date in YYYY-MM-DD format.
         * @param branch The branch to check (optional, defaults to current branch).
         * @return The commit hash or None if not found.
         */
        """
        if branch is None:
            branch = self.GetCurrentBranch()
            if branch is None:
                return None
        try:
            commit_hash = subprocess.check_output(
                ["git", "log", branch, "--until", start_date, "-1", "--format=%H"],
                cwd=self.repo_path
            ).decode('utf-8').strip()
            return commit_hash if commit_hash else None
        except subprocess.CalledProcessError:
            return None

    # def GetDiffNameStatus(self, old_ref='HEAD'):
    #     """
    #     /**
    #      * @brief Retrieves the Git diff for name-status changes from the given ref to HEAD.
    #      * @param old_ref The old reference (commit hash or 'HEAD').
    #      * @return A dictionary of file paths to their status (A, M, D, etc.).
    #      */
    #     """
    #     if old_ref is None:
    #         old_ref = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'  # Empty tree hash for all as added
    #     # Execute git diff command
    #     output = subprocess.check_output(["git", "diff", "--name-status", f"{old_ref}..HEAD"], cwd=self.repo_path).decode('utf-8')
    #     lines = output.splitlines()
    #     changed = {}
    #     # Parse each line for status and path
    #     for line in lines:
    #         parts = line.split('\t')
    #         if len(parts) < 2:
    #             continue
    #         status = parts[0]
    #         if len(parts) == 2:
    #             path = parts[1]
    #             changed[path] = status
    #         elif len(parts) == 3:
    #             old_path = parts[1]
    #             new_path = parts[2]
    #             changed[new_path] = status  # Treat rename/copy as modified for simplicity

    #     return changed

    def GetDiffNameStatus(self, old_ref='HEAD', include_uncommitted=True):
        """
        Get diff name-status changes.
        If include_uncommitted=True, also include staged and unstaged changes.
        """
        changed = {}

        if old_ref is None:
            old_ref = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'  # empty tree

        # Committed changes between old_ref and HEAD
        output = subprocess.check_output(
            ["git", "diff", "--name-status", f"{old_ref}..HEAD"], cwd=self.repo_path
        ).decode('utf-8')
        for line in output.splitlines():
            parts = line.split('\t')
            if len(parts) >= 2:
                changed[parts[-1]] = parts[0]

        if include_uncommitted:
            # Staged changes
            output = subprocess.check_output(
                ["git", "diff", "--cached", "--name-status"], cwd=self.repo_path
            ).decode('utf-8')
            for line in output.splitlines():
                parts = line.split('\t')
                if len(parts) >= 2:
                    changed[parts[-1]] = parts[0]

            # Unstaged changes (working directory)
            output = subprocess.check_output(
                ["git", "diff", "--name-status"], cwd=self.repo_path
            ).decode('utf-8')
            for line in output.splitlines():
                parts = line.split('\t')
                if len(parts) >= 2:
                    changed[parts[-1]] = parts[0]

        return changed


    def GetOldContent(self, path, old_ref='HEAD'):
        """
        /**
         * @brief Fetches the content of a file from the given ref.
         * @param path The file path.
         * @param old_ref The reference (commit hash or 'HEAD').
         * @return The file content as string, or None on error or if old_ref is None.
         */
        """
        if old_ref is None:
            return None
        try:
            # Use git show to get old content
            return subprocess.check_output(["git", "show", f"{old_ref}:{path}"], cwd=self.repo_path).decode('utf-8', errors='replace')
        except subprocess.CalledProcessError:
            return None

    def GetNewContent(self, path):
        """
        /**
         * @brief Reads the current (new) content of a file.
         * @param path The file path.
         * @return The file content as string, or None on error.
         */
        """
        try:
            # Open and read the file using full path
            with open(os.path.join(self.repo_path, path), 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except IOError:
            return None


class ChangeProcessor:
    """
    /**
     * @class ChangeProcessor
     * @brief Class for processing Git changes and comparing functions.
     * @details Coordinates the extraction, comparison, and output of function changes in C++ files.
     */
    """

    def __init__(self, git_handler: GitRepoHandler, function_extractor: FunctionExtractor, cxx_extensions):
        # Store the handlers and extensions
        self.git_handler = git_handler
        self.function_extractor = function_extractor
        self.cxx_extensions = cxx_extensions

    def ProcessChanges(self, old_ref='HEAD'):
        """
        /**
         * @brief Processes all changed files to detect and print function changes.
         * @param old_ref The old reference for diff.
         */
        """
        # Get the changed files dictionary
        changed = self.git_handler.GetDiffNameStatus(old_ref)

        total_changed_files = 0

        # Iterate over each changed file
        for path, status in changed.items():
            # Skip non-C++ files
            if not path.lower().endswith(self.cxx_extensions):
                continue
            # Initialize function dictionaries
            old_functions = {}
            new_functions = {}
            # Handle deleted files
            if status == 'D':
                old_content = self.git_handler.GetOldContent(path, old_ref)
                if old_content is not None:
                    old_functions = self.function_extractor.ExtractFunctions(old_content)
            # Handle added files
            elif status == 'A':
                new_content = self.git_handler.GetNewContent(path)
                if new_content is not None:
                    new_functions = self.function_extractor.ExtractFunctions(new_content)
            # Handle modified files (including renames for simplicity)
            elif status in ('M', 'R', 'C'):
                old_content = self.git_handler.GetOldContent(path, old_ref)
                new_content = self.git_handler.GetNewContent(path)
                if old_content is not None:
                    old_functions = self.function_extractor.ExtractFunctions(old_content)
                if new_content is not None:
                    new_functions = self.function_extractor.ExtractFunctions(new_content)
            # Find added, deleted, and modified keys
            added_keys = set(new_functions) - set(old_functions)
            deleted_keys = set(old_functions) - set(new_functions)
            modified_keys = {k for k in set(old_functions) & set(new_functions) if old_functions[k][0] != new_functions[k][0]}

            # Prepare lists with names and lines
            added = [(self.function_extractor.GetFunctionName(k), new_functions[k][1]) for k in added_keys]
            deleted = [(self.function_extractor.GetFunctionName(k), old_functions[k][1]) for k in deleted_keys]
            modified = [(self.function_extractor.GetFunctionName(k), new_functions[k][1]) for k in modified_keys]

            # If there are changes, print them and increment counter
            if added or deleted or modified:
                total_changed_files += 1
                print(f"In file {path}:")
                if added:
                    # Sort and print added functions
                    added_sorted = sorted(added, key=lambda x: x[0])
                    print("  Added: " + ", ".join(f"{name} (line {line})" for name, line in added_sorted))
                if modified:
                    # Sort and print modified functions
                    modified_sorted = sorted(modified, key=lambda x: x[0])
                    print("  Modified: " + ", ".join(f"{name} (line {line})" for name, line in modified_sorted))
                if deleted:
                    # Sort and print deleted functions
                    deleted_sorted = sorted(deleted, key=lambda x: x[0])
                    print("  Deleted: " + ", ".join(f"{name} (line {line})" for name, line in deleted_sorted))
                print("")

        print(f"Total files with changes found: {total_changed_files}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Git changes for C++ functions.")
    parser.add_argument('--start-date', type=str, default='2025-08-26', help='Start date for changes (YYYY-MM-DD)')
    parser.add_argument('--branch', type=str, default=None, help='Branch to check (default current)')
    args = parser.parse_args()

    repo_path = "D:/GIT2022"
    cxx_extensions = ('.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx', '.c++', '.h++', '.h', '.c')

    # Initialize the CppParser
    cpp_parser = CppParser()
    # Initialize the FunctionExtractor with the parser
    function_extractor = FunctionExtractor(cpp_parser)
    # Initialize the GitRepoHandler with the repo path
    git_handler = GitRepoHandler(repo_path)
    # Initialize the ChangeProcessor with handlers and extensions
    change_processor = ChangeProcessor(git_handler, function_extractor, cxx_extensions)

    if args.start_date:
        old_commit = git_handler.GetLastCommitBeforeDate(args.start_date, args.branch)
    else:
        old_commit = 'HEAD'

    # Process the changes
    change_processor.ProcessChanges(old_ref=old_commit)