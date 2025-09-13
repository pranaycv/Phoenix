# 🚀 Phoenix - AI-Powered C++ Documentation Suite

![Phoenix Logo](https://img.shields.io/badge/Phoenix-AI%20Documentation-orange?style=for-the-badge&logo=fire&logoColor=white)

[![GitHub release](https://img.shields.io/github/release/your-username/phoenix.svg)](https://github.com/your-username/phoenix/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Phoenix** is a comprehensive AI-powered toolkit for automated C++ code documentation, analysis, and maintenance. It combines the power of tree-sitter parsing, Ollama AI models, and modern GUI interfaces to revolutionize how developers document and maintain their C++ codebases.

## 🌟 Key Features

### 🤖 **AI-Powered Documentation Generation**
- **Doxygen-style Comments**: Automatically generates comprehensive function documentation
- **Inline Code Comments**: Smart contextual comments for complex logic blocks
- **Multi-line Statement Handling**: Correctly handles complex C++ constructs

### 🔍 **Git Integration & Change Tracking**
- **Smart Change Detection**: Identifies modified, added, and deleted functions
- **Historical Analysis**: Compare functions across commits and time ranges
- **Automated Processing**: Process only changed functions for efficiency

### 🖥️ **Modern GUI Interface**
- **Intuitive Design**: Clean, modern interface built with DearPyGUI
- **Real-time Progress**: Live logging and status updates
- **Customizable Settings**: Flexible configuration options

### 📊 **Code Quality Analysis**
- **Critical Glitch Detection**: Identifies memory leaks, null pointer dereferences
- **Performance Analysis**: Spots potential bottlenecks and issues
- **Security Assessment**: Detects buffer overflows and injection vulnerabilities

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Git (for repository analysis)
- [Ollama](https://ollama.ai/) server (local or remote)

### Quick Install
```bash
# Clone the repository
git clone https://github.com/your-username/phoenix.git
cd phoenix

# Install dependencies
pip install -r requirements.txt

# For development setup
pip install -e .
```

### Ollama Setup
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull gpt-oss:20b  # or your preferred model
ollama serve
```

## 🚀 Quick Start

### 1. GUI Mode (Recommended)
```bash
python auto_comment_cpp_code.py
```

**Configuration Options:**
- **Directory Path**: Your C++ project directory
- **Last Document Date**: Process changes since this date
- **Ollama Host**: AI model server URL
- **Branch**: Git branch to analyze (optional)

### 2. Command Line Usage

**Extract Single Function:**
```bash
python extract_function_code_2.py
# Edit the file_path and line_number variables
```

**Analyze Git Changes:**
```bash
python get_git_changes.py --start-date 2024-01-01 --branch main
```

**Batch Process Files:**
```bash
python generate_docs_ollama.py
# Configure source_directory in the script
```

## 📁 Project Structure

```
phoenix/
├── 🎯 auto_comment_cpp_code.py     # Main GUI application
├── 🔍 extract_function_code_2.py   # Function extraction utility
├── 📝 generate_docs_ollama.py      # Batch documentation generator
├── 🔄 get_git_changes.py          # Git change analyzer
├── 📋 requirements.txt            # Dependencies
├── 🏗️ setup.py                   # Package setup
├── 📚 docs/                       # Documentation
├── 🧪 examples/                   # Usage examples
└── ⚙️ config/                    # Configuration files
```

## 🎮 Usage Examples

### Example 1: Document Recent Changes
```python
# Set your project path
repo_path = "D:/YourProject"

# Process changes from last week
last_date = "2024-01-15"

# Run with GUI
python auto_comment_cpp_code.py
```

### Example 2: Extract Specific Function
```python
from extract_function_code_2 import FunctionExtractor

extractor = FunctionExtractor("src/main.cpp", 42)
extractor.ExtractAndSave()
```

### Example 3: Analyze Git Changes
```python
from get_git_changes import ChangeProcessor, GitRepoHandler, CppParser, FunctionExtractor

parser = CppParser()
extractor = FunctionExtractor(parser)
git_handler = GitRepoHandler("./")
processor = ChangeProcessor(git_handler, extractor, ('.cpp', '.hpp'))
processor.ProcessChanges('HEAD~10')
```

## ⚙️ Configuration

### Environment Variables
```bash
export OLLAMA_HOST="http://localhost:11434"
export PHOENIX_MODEL="gpt-oss:20b"
export PHOENIX_TEMP_DIR="/tmp/phoenix"
```

### Config File (config/phoenix.json)
```json
{
  "ollama": {
    "host": "http://192.168.1.100:11434",
    "model": "gpt-oss:20b",
    "temperature": 0.0
  },
  "git": {
    "extensions": [".cpp", ".hpp", ".cc", ".h"],
    "ignore_patterns": ["**/build/**", "**/test/**"]
  },
  "documentation": {
    "include_doxygen": true,
    "inline_comments": true,
    "code_review": true
  }
}
```

## 🏗️ Architecture

### Core Components

#### 🧠 **AI Engine (CustomOllamaGenerator)**
- Direct HTTP API integration with Ollama
- Robust error handling and retry logic
- Optimized prompts for C++ documentation

#### 🌳 **Parsing Engine (CppParser)**
- Tree-sitter based C++ parsing
- Accurate function extraction
- Multi-file support with encoding detection

#### 📁 **File Management (FileProcessor)**
- Smart encoding detection
- Batch processing capabilities
- Status tracking and resumable operations

#### 🔄 **Version Control (GitRepoHandler)**
- Git integration for change detection
- Support for branches and commit ranges
- Staged and unstaged change handling

### Data Flow
```
C++ Source Files → Tree-sitter Parser → Function Extraction 
                                             ↓
Git Change Analysis → AI Documentation → Code Integration
                                             ↓
Quality Review → Updated Source Files → Status Tracking
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/phoenix.git
cd phoenix

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/
```

### Code Standards
- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tree-sitter** team for the excellent parsing library
- **Ollama** team for making AI models accessible
- **DearPyGUI** for the modern GUI framework
- **Open Source Community** for continuous inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/phoenix/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/phoenix/discussions)
- **Wiki**: [Project Wiki](https://github.com/your-username/phoenix/wiki)

## 🗺️ Roadmap

- [ ] **VS Code Extension** integration
- [ ] **Multiple AI Model** support (OpenAI, Claude, etc.)
- [ ] **Java/Python** language support
- [ ] **Team Collaboration** features
- [ ] **CI/CD Pipeline** integration
- [ ] **Cloud-based** processing options

---

<div align="center">

**Made with ❤️ by developers, for developers**

[⭐ Star this repo](https://github.com/your-username/phoenix) | [🐛 Report Bug](https://github.com/your-username/phoenix/issues) | [💡 Request Feature](https://github.com/your-username/phoenix/issues)

</div>