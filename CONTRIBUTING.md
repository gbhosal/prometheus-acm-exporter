# Contributing to Prometheus ACM Certificate Exporter

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, Python version, AWS region, etc.)
- Relevant logs or error messages

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use case and motivation
- Proposed implementation approach (if you have one)

### Submitting Pull Requests

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure all tests pass** and code is properly formatted
6. **Submit a pull request** with a clear description of changes

## Development Setup

### Prerequisites

- Python 3.11+
- pip
- Docker (for testing container builds)
- AWS credentials configured (for testing)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/acm-prometheus-exporter.git
cd acm-prometheus-exporter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the exporter locally:
```bash
python -m src.acm_exporter --config examples/config.yaml
```

## Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

## Testing

- Write tests for new features
- Ensure existing tests still pass
- Test with multiple AWS regions if applicable
- Test error handling scenarios

## Commit Messages

Use clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- First line should be a brief summary (50 chars or less)
- Add detailed description if needed (separated by blank line)

Example:
```
Add support for certificate ID label

Extract certificate ID from ARN and include it as a label
in the metrics output for better certificate identification.
```

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation if you've changed functionality
3. Add tests for new features
4. Ensure all tests pass
5. Update CHANGELOG.md if applicable
6. Request review from maintainers

## Questions?

If you have questions, please open an issue with the `question` label or reach out to the maintainers.

Thank you for contributing!
