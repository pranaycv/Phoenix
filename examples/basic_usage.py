#!/usr/bin/env python3
"""
Phoenix C++ Documentation Suite - Basic Usage Examples

This file demonstrates various ways to use Phoenix for C++ code documentation.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import phoenix modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from get_git_changes import CppParser, FunctionExtractor, GitRepoHandler, ChangeProcessor
from extract_function_code_2 import FunctionExtractor as SingleFunctionExtractor
from generate_docs_ollama import CppParser as DocCppParser, OllamaGenerator, FileProcessor, FileListManager


def example_1_analyze_git_changes():
    """
    Example 1: Analyze Git changes in a C++ repository
    
    This example shows how to detect function changes between commits.
    """
    print("=" * 60)
    print("Example 1: Analyzing Git Changes")
    print("=" * 60)
    
    # Configuration
    repo_path = "D:/YourProject"  # Change this to your repository path
    extensions = ('.cpp', '.hpp', '.cc', '.h')
    start_date = "2024-01-01"  # Analyze changes since this date
    
    # Initialize components
    cpp_parser = CppParser()
    function_extractor = FunctionExtractor(cpp_parser)
    git_handler = GitRepoHandler(repo_path)
    change_processor = ChangeProcessor(git_handler, function_extractor, extensions)
    
    try:
        # Get the commit from the start date
        old_commit = git_handler.GetLastCommitBeforeDate(start_date)
        if old_commit:
            print(f"Analyzing changes since commit: {old_commit[:8]}...")
            change_processor.ProcessChanges(old_ref=old_commit)
        else:
            print("No commits found before the specified date.")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the repository path exists and is a valid Git repository.")


def example_2_extract_single_function():
    """
    Example 2: Extract and clean a single function
    
    This example shows how to extract a specific function from a file.
    """
    print("\n" + "=" * 60)
    print("Example 2: Extracting Single Function")
    print("=" * 60)
    
    # Configuration
    file_path = "example.cpp"  # Your C++ file
    line_number = 42  # Line where function starts
    
    # Create a sample C++ file for demonstration
    sample_cpp_content = '''
#include <iostream>
#include <vector>

/**
 * @brief Sample function for demonstration
 */
void processData(const std::vector<int>& data) {
    // Process each element
    for (const auto& item : data) {
        std::cout << item << std::endl;
    }
}

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    processData(numbers);
    return 0;
}
'''
    
    # Write sample file
    with open(file_path, 'w') as f:
        f.write(sample_cpp_content)
    
    try:
        # Extract the function at line 7 (processData function)
        extractor = SingleFunctionExtractor(file_path, 7)
        extractor.ExtractAndSave()
        print(f"Function extracted successfully!")
        print(f"Check for generated *_clean.txt files in the current directory.")
        
    except Exception as e:
        print(f"Error extracting function: {e}")
    
    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)


def example_3_batch_documentation():
    """
    Example 3: Batch documentation of C++ files
    
    This example shows how to process multiple files for documentation.
    """
    print("\n" + "=" * 60)
    print("Example 3: Batch Documentation")
    print("=" * 60)
    
    # Create a temporary directory structure
    temp_dir = "temp_cpp_project"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Create sample files
    sample_files = {
        "main.cpp": '''
#include "utils.h"

int main() {
    int result = calculateSum(10, 20);
    return result;
}
''',
        "utils.h": '''
#ifndef UTILS_H
#define UTILS_H

int calculateSum(int a, int b);

#endif
''',
        "utils.cpp": '''
#include "utils.h"

int calculateSum(int a, int b) {
    return a + b;
}
'''
    }
    
    # Write sample files
    for filename, content in sample_files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    try:
        # Initialize components for batch processing
        file_list_manager = FileListManager(temp_dir)
        
        # Prepare file list
        file_list_manager.PrepareFileList()
        
        # Read file status
        file_status = file_list_manager.ReadFileStatus()
        
        # Get processing summary
        summary = file_list_manager.GetProcessingSummary(file_status)
        print(f"Files found: {summary['total']}")
        print(f"Ready for processing: {summary['pending']}")
        
        # Note: Actual documentation would require Ollama server
        print("Note: To complete documentation, ensure Ollama server is running")
        
    except Exception as e:
        print(f"Error in batch processing: {e}")
    
    # Clean up
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def example_4_configuration_management():
    """
    Example 4: Working with configuration files
    
    This example shows how to load and use configuration settings.
    """
    print("\n" + "=" * 60)
    print("Example 4: Configuration Management")
    print("=" * 60)
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'phoenix.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("Configuration loaded successfully!")
        print(f"Project: {config['project']['name']}")
        print(f"Ollama Host: {config['ollama']['host']}")
        print(f"Model: {config['ollama']['model']}")
        print(f"Supported Extensions: {', '.join(config['git']['extensions'])}")
        
        # Example of modifying configuration
        config['ollama']['host'] = 'http://your-server:11434'
        config['git']['default_branch'] = 'develop'
        
        # Save modified configuration (to a different file)
        modified_config_path = 'modified_phoenix.json'
        with open(modified_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Modified configuration saved to: {modified_config_path}")
        
    except Exception as e:
        print(f"Error loading configuration: {e}")


def example_5_error_handling():
    """
    Example 5: Error handling and logging
    
    This example shows how to handle common errors gracefully.
    """
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    # Example of handling Git repository errors
    try:
        invalid_repo = GitRepoHandler("/invalid/path")
        changes = invalid_repo.GetDiffNameStatus()
    except Exception as e:
        print(f"✓ Caught Git error: {type(e).__name__}")
    
    # Example of handling file access errors
    try:
        extractor = SingleFunctionExtractor("/nonexistent/file.cpp", 1)
        extractor.ExtractAndSave()
    except Exception as e:
        print(f"✓ Caught file error: {type(e).__name__}")
    
    # Example of handling Ollama connection errors
    try:
        # This would fail if Ollama is not running
        generator = OllamaGenerator("nonexistent-model")
        result = generator.GenerateDoc("void test() {}")
    except Exception as e:
        print(f"✓ Caught Ollama error: {type(e).__name__}")
    
    print("Error handling examples completed!")


if __name__ == "__main__":
    print("🚀 Phoenix C++ Documentation Suite - Examples")
    print("=" * 60)
    print("This script demonstrates various Phoenix features.")
    print("Modify the paths and settings according to your environment.\n")
    
    # Run examples
    try:
        example_1_analyze_git_changes()
        example_2_extract_single_function()
        example_3_batch_documentation()
        example_4_configuration_management()
        example_5_error_handling()
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed! Check the README.md for more information.")
    print("=" * 60)