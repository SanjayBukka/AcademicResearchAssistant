# Contributing to Academic Research Assistant

Thank you for your interest in contributing to the Academic Research Assistant project! This document provides guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- Clear description of the enhancement
- Use case and benefits
- Possible implementation approach (optional)

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Write or update tests if applicable
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add some feature'`)
7. Push to the branch (`git push origin feature/your-feature-name`)
8. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Write clear, descriptive commit messages
- Add comments for complex logic
- Include docstrings for functions and classes
- Keep functions focused and modular

### Testing

- Test your changes locally before submitting
- Ensure existing functionality is not broken
- Add tests for new features when possible

## Development Setup

```bash
# Clone the repository
git clone https://github.com/SanjayBukka/AcademicResearchAssistant.git
cd AcademicResearchAssistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run the application
streamlit run main.py
```

## Project Structure

```
AcademicResearchAssistant/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── features/              # Feature modules
│   ├── references/        # Reference finder
│   ├── writing/           # Writing assistant
│   ├── summarizer/        # Paper summarizer
│   ├── gap_finder/        # Research gap analyzer
│   └── question/          # Q&A assistant
└── utils/                 # Utility functions
```

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Contact the maintainers

Thank you for contributing!
