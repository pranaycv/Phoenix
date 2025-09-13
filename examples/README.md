# Phoenix Examples 📚

This directory contains examples and sample configurations for Phoenix.

## 🚀 Quick Start Examples

### `basic_usage.py`
Comprehensive examples demonstrating Phoenix's core features:
- Git change analysis
- Single function extraction  
- Batch documentation processing
- Configuration management
- Error handling

**Run the examples:**
```bash
cd examples
python basic_usage.py
```

## ⚙️ Configuration Examples

### Basic Configuration
Copy the example configuration and customize:
```bash
cp config/local.example.json config/local.json
# Edit config/local.json with your settings
```

### Environment-Specific Configs

**Development:**
- `config/local.example.json` - Local development settings
- Lower timeouts, debug logging enabled
- Process only committed changes

**Production:**
- `config/phoenix.json` - Full production configuration
- All features enabled, optimized settings
- Comprehensive logging and error handling

## 💡 Usage Patterns

### Pattern 1: Daily Documentation Updates
```python
# Process changes from yesterday
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Run Phoenix with date filter
# This pattern is ideal for CI/CD integration
```

### Pattern 2: Feature Branch Documentation
```python
# Document changes in a feature branch
git_handler = GitRepoHandler("./")
old_commit = git_handler.GetLastCommitBeforeDate("2024-01-01", "main")

# Compare feature branch with main branch
change_processor.ProcessChanges(old_ref=old_commit)
```

### Pattern 3: Legacy Code Documentation
```python
# Process all files in a directory
file_list_manager = FileListManager("/path/to/legacy/code")
file_list_manager.PrepareFileList()

# Batch process with status tracking
# Resume interrupted documentation sessions
```

## 🛠️ Customization Examples

### Custom AI Prompts
```python
# Extend CustomOllamaGenerator with custom prompts
class MyCustomGenerator(CustomOllamaGenerator):
    def GenerateDoc(self, func_text):
        # Custom prompt for your coding style
        prompt = f"Document this C++ function in our company style: {func_text}"
        return self._call_api(prompt)
```

### Custom File Filters
```python
# Filter files by custom criteria
def custom_file_filter(file_path):
    # Only process files with specific naming convention
    return file_path.endswith('_impl.cpp') or file_path.endswith('_api.hpp')

# Apply filter in processing
for file_path in files:
    if custom_file_filter(file_path):
        process_file(file_path)
```

## 🧪 Testing Examples

### Mock AI Responses
```python
# Test documentation generation without AI service
class MockOllamaGenerator:
    def GenerateDoc(self, func_text):
        return "/** Mock documentation */"
    
    def GenerateCodeComment(self, func_text, doxygen):
        return '[{"line": 1, "comment": "Mock comment"}]'
```

### Test Repository Setup
```python
# Create test repository for examples
def setup_test_repo():
    os.makedirs("test_repo")
    with open("test_repo/sample.cpp", "w") as f:
        f.write("void testFunction() { return; }")
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd="test_repo")
    subprocess.run(["git", "add", "."], cwd="test_repo")
    subprocess.run(["git", "commit", "-m", "Initial"], cwd="test_repo")
```

## 🔧 Integration Examples

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Generate Documentation
  run: |
    python -c "
    from phoenix import AutoDocumentationRunner
    runner = AutoDocumentationRunner('./config/ci.json')
    runner.process_recent_changes(days=1)
    "
```

### VS Code Task Integration
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Phoenix Documentation",
      "type": "shell",
      "command": "python",
      "args": ["phoenix/auto_comment_cpp_code.py"],
      "group": "build"
    }
  ]
}
```

## 📝 Best Practices

### 1. Configuration Management
- Keep sensitive data in environment variables
- Use different configs for different environments
- Version control example configurations

### 2. Error Handling
- Always validate paths before processing
- Handle AI service outages gracefully  
- Implement retry logic for network operations

### 3. Performance Optimization
- Process files in batches
- Use caching for repeated operations
- Monitor memory usage for large repositories

### 4. Code Quality
- Test documentation generation with sample code
- Review generated documentation for accuracy
- Maintain consistent documentation style

## 🆘 Troubleshooting

### Common Issues

**Ollama Connection Errors:**
```python
# Check if Ollama is running
try:
    response = requests.get("http://localhost:11434/api/tags")
    print("Ollama is running")
except:
    print("Ollama is not accessible")
```

**Git Repository Issues:**
```python
# Validate Git repository
def is_git_repo(path):
    return os.path.exists(os.path.join(path, '.git'))

if not is_git_repo('./'):
    print("Not a Git repository")
```

**File Encoding Problems:**
```python
# Handle encoding issues
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except UnicodeDecodeError:
    # Fallback to different encoding
    with open(file_path, 'r', encoding='latin1') as f:
        content = f.read()
```

## 🤝 Contributing Examples

Have a useful example or pattern? Please contribute!

1. Add your example to this directory
2. Update this README with description
3. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.