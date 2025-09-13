# Contributing to Phoenix 🤝

Thank you for your interest in contributing to Phoenix! We welcome contributions from the community and appreciate your help in making this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)

## 🤝 Code of Conduct

This project follows a simple code of conduct:

- **Be respectful** and inclusive
- **Be constructive** in your feedback
- **Be collaborative** and help others
- **Focus on what's best** for the community

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of C++ and Python
- Ollama server (for AI features)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/phoenix.git
   cd phoenix
   ```

## 🛠️ Development Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .  # Install in development mode
```

### 3. Install Development Tools
```bash
pip install -r requirements.txt --extra-index-url dev
```

### 4. Set Up Pre-commit Hooks (Optional)
```bash
pip install pre-commit
pre-commit install
```

## 📝 How to Contribute

### Types of Contributions

1. **🐛 Bug Reports**
   - Report issues with detailed reproduction steps
   - Include system information and error messages

2. **✨ Feature Requests**
   - Propose new features or enhancements
   - Provide clear use cases and benefits

3. **📚 Documentation**
   - Improve existing documentation
   - Add examples and tutorials
   - Fix typos and formatting

4. **🔧 Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Code refactoring

5. **🧪 Testing**
   - Add test cases
   - Improve test coverage
   - Create integration tests

## 💻 Coding Standards

### Python Style
- Follow **PEP 8** guidelines
- Use **Black** for code formatting
- Use **flake8** for linting
- Use **mypy** for type checking

### Code Quality Tools
```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

### Naming Conventions
- **Classes**: PascalCase (`CppParser`)
- **Functions/Methods**: PascalCase to match existing code (`ExtractFunctions`)
- **Variables**: snake_case (`file_path`)
- **Constants**: UPPER_CASE (`MAX_RETRIES`)

### Documentation
- Add docstrings to all classes and functions
- Use Doxygen-style comments for consistency
- Include type hints where possible

### Example Code Structure
```python
class ExampleClass:
    """
    /**
     * @class ExampleClass
     * @brief Brief description of the class.
     * @details Detailed description of what this class does.
     */
    """

    def __init__(self, param: str):
        """Initialize the class with parameter."""
        self.param = param

    def ProcessData(self, data: str) -> str:
        """
        /**
         * @brief Processes the input data.
         * @param data The input data to process.
         * @return The processed data string.
         */
        """
        # Implementation here
        return processed_data
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=phoenix

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (Ollama API, Git, etc.)

### Test Structure
```python
def test_function_extraction_success():
    """Test successful function extraction."""
    # Arrange
    parser = CppParser()
    sample_code = "void test() { return; }"
    
    # Act
    result = parser.ExtractFunctions(sample_code)
    
    # Assert
    assert len(result) == 1
    assert "test" in result[0]["name"]
```

## 🔄 Submitting Changes

### Branch Naming
- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation
- `refactor/description` - for refactoring

### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(parser): add support for template functions`
- `fix(gui): resolve crash on invalid directory path`
- `docs(readme): update installation instructions`

### Development Workflow
1. Create a new branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Commit your changes
7. Push to your fork
8. Create a pull request

## 📋 Issue Guidelines

### Bug Reports
Include:
- **OS and Python version**
- **Phoenix version**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages and logs**
- **Sample code or files (if applicable)**

### Feature Requests
Include:
- **Clear description** of the feature
- **Use case** and benefits
- **Proposed implementation** (if you have ideas)
- **Examples** of how it would work

## 🔀 Pull Request Process

### Before Submitting
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Added tests for new functionality
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or noted)
```

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Address feedback** promptly
4. **Final approval** and merge

## 🎯 Areas for Contribution

### High Priority
- [ ] **Error handling** improvements
- [ ] **Performance** optimizations
- [ ] **Test coverage** expansion
- [ ] **Documentation** enhancements

### Medium Priority
- [ ] **New AI models** integration
- [ ] **Additional languages** support (Java, Python)
- [ ] **VS Code extension** development
- [ ] **Configuration** management improvements

### Future Ideas
- [ ] **Web interface** for remote usage
- [ ] **Team collaboration** features
- [ ] **CI/CD integration** tools
- [ ] **Cloud deployment** options

## 🆘 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community chat
- **Documentation**: Check the wiki for detailed guides

## 🏆 Recognition

Contributors will be:
- **Listed** in the CONTRIBUTORS.md file
- **Mentioned** in release notes
- **Credited** in documentation
- **Invited** to join the core team (for significant contributions)

---

Thank you for contributing to Phoenix! 🚀

*Together, we're making C++ documentation better for everyone.*