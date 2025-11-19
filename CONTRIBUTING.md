# Contributing to Stock Trading Decision Support System

First off, thank you for considering contributing to this project! It's people like you that make this a great tool for everyone.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Commit Guidelines](#commit-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Documentation](#documentation)
10. [Community](#community)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge to:

- Be friendly and patient
- Be welcoming and inclusive
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Ways to Contribute

- **Report bugs**: Submit detailed bug reports
- **Suggest features**: Propose new features or improvements
- **Write code**: Fix bugs, add features, improve performance
- **Improve documentation**: Fix typos, add examples, clarify explanations
- **Write tests**: Increase test coverage
- **Review pull requests**: Help review code from other contributors

### Before You Start

1. Check existing [issues](https://github.com/your-repo/issues) to avoid duplicates
2. For major changes, open an issue first to discuss
3. Make sure you agree with the project's goals and direction

---

## How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check the documentation
- Search existing issues
- Try the latest version

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Code samples, error messages, logs
- Environment details (OS, Python version, dependencies)

**Bug Report Template:**

```markdown
### Description
[Clear description of the bug]

### Steps to Reproduce
1. Step 1
2. Step 2
3. ...

### Expected Behavior
[What you expected to happen]

### Actual Behavior
[What actually happened]

### Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Package versions: [paste output of `pip list`]

### Additional Context
[Logs, screenshots, etc.]
```

### Suggesting Features

**Before submitting a feature request:**
- Check if it aligns with project goals
- Search existing feature requests
- Consider if it benefits most users

**When suggesting a feature, include:**
- Clear, descriptive title
- Detailed description of the feature
- Why this feature would be useful
- Possible implementation approach
- Examples or mockups if applicable

**Feature Request Template:**

```markdown
### Feature Description
[Clear description of the feature]

### Problem It Solves
[What problem does this address?]

### Proposed Solution
[How should this work?]

### Alternatives Considered
[Other approaches you've thought about]

### Additional Context
[Examples, mockups, references]
```

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip or conda

### Setting Up Development Environment

1. **Fork the repository**

```bash
# Click "Fork" on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/stock-trading-decision-support.git
cd stock-trading-decision-support
```

2. **Add upstream remote**

```bash
git remote add upstream https://github.com/original/stock-trading-decision-support.git
```

3. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**

```bash
# Install all dependencies including dev dependencies
pip install -r requirements.txt
pip install -e .

# Install development tools
pip install black flake8 isort mypy pytest pytest-cov
```

5. **Install pre-commit hooks** (optional but recommended)

```bash
pip install pre-commit
pre-commit install
```

6. **Verify setup**

```bash
pytest tests/
```

### Development Workflow

1. **Sync with upstream**

```bash
git checkout main
git fetch upstream
git merge upstream/main
```

2. **Create feature branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

3. **Make changes**

```bash
# Edit files
# Run tests frequently
pytest tests/
```

4. **Commit changes**

```bash
git add .
git commit -m "feat: add new feature"
```

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Open Pull Request**

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings, single quotes for dict keys
- **Imports**: Organized with isort

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all Python files
black src/ tests/

# Check without modifying
black --check src/ tests/
```

### Import Organization

We use **isort** for import sorting:

```bash
# Sort imports
isort src/ tests/

# Check without modifying
isort --check-only src/ tests/
```

Import order:
1. Standard library imports
2. Related third party imports
3. Local application imports

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third party
import numpy as np
import pandas as pd
from fastapi import FastAPI

# Local
from src.models.lstm_model import LSTMModel
from src.config.settings import get_settings
```

### Type Hints

Use type hints for all function signatures:

```python
def predict_price(
    symbol: str,
    data: pd.DataFrame,
    model: str = "ensemble"
) -> Dict[str, float]:
    """Predict stock price."""
    # Implementation
    return {"predicted_price": 100.0, "confidence": 0.8}
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_position_size(
    capital: float,
    price: float,
    risk_percentage: float = 0.1
) -> int:
    """Calculate the number of shares to buy.

    Args:
        capital: Total available capital
        price: Current stock price
        risk_percentage: Percentage of capital to risk (default: 0.1)

    Returns:
        Number of shares to purchase

    Raises:
        ValueError: If capital or price is negative

    Example:
        >>> calculate_position_size(10000, 100, 0.1)
        10
    """
    if capital < 0 or price < 0:
        raise ValueError("Capital and price must be positive")

    return int((capital * risk_percentage) / price)
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

```python
# Good
class DataProcessor:
    MAX_RETRIES = 3

    def __init__(self):
        self._cache = {}

    def process_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        return self._normalize_data(raw_data)

    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        # Private method
        pass
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately

```python
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol: str) -> pd.DataFrame:
    try:
        data = download_data(symbol)
    except ConnectionError as e:
        logger.error(f"Connection failed for {symbol}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise ValueError(f"Invalid stock symbol: {symbol}") from e

    return data
```

---

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Update tests when modifying existing code
- Aim for >80% code coverage
- Use descriptive test names

### Test Structure

```python
import pytest
from src.models.lstm_model import LSTMModel

class TestLSTMModel:
    """Test cases for LSTM model."""

    @pytest.fixture
    def model(self):
        """Create a test model instance."""
        return LSTMModel(units=64)

    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        # Create test data
        return X_train, y_train

    def test_model_initialization(self, model):
        """Test model is initialized correctly."""
        assert model.units == 64
        assert model.model is not None

    def test_model_training(self, model, sample_data):
        """Test model can be trained."""
        X_train, y_train = sample_data
        history = model.train(X_train, y_train, epochs=1)
        assert 'loss' in history.history

    def test_model_prediction(self, model, sample_data):
        """Test model can make predictions."""
        X_train, y_train = sample_data
        model.train(X_train, y_train, epochs=1)
        predictions = model.predict(X_train[:10])
        assert len(predictions) == 10

    def test_invalid_input_raises_error(self, model):
        """Test invalid input raises appropriate error."""
        with pytest.raises(ValueError):
            model.train(None, None)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestLSTMModel::test_model_initialization

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Test Coverage

Maintain >80% test coverage:

```bash
# Generate coverage report
pytest --cov=src --cov-report=html tests/

# View report
open htmlcov/index.html
```

---

## Commit Guidelines

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes (dependencies, etc.)

**Examples:**

```bash
# Feature
feat(models): add transformer model for stock prediction

# Bug fix
fix(api): correct prediction endpoint response format

# Documentation
docs(readme): update installation instructions

# Refactoring
refactor(data): simplify data preprocessing pipeline

# Multiple changes
feat(trading): add stop-loss and take-profit logic

- Implement stop-loss at 5% below entry
- Add take-profit at 10% above entry
- Update position manager to track both
```

### Commit Best Practices

- One logical change per commit
- Write clear, descriptive messages
- Reference issues when applicable (`fixes #123`)
- Keep commits focused and atomic

---

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**

```bash
pytest tests/
```

2. **Format code**

```bash
black src/ tests/
isort src/ tests/
```

3. **Lint code**

```bash
flake8 src/ tests/
mypy src/
```

4. **Update documentation** if needed

5. **Update CHANGES_SUMMARY.md** with your changes

### Submitting Pull Request

1. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request on GitHub**

3. **Fill out PR template**

```markdown
## Description
[Describe what this PR does]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Code coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

4. **Wait for review**

### During Review

- Be responsive to feedback
- Make requested changes promptly
- Keep discussions professional and constructive
- Update PR based on feedback

### After Approval

- Maintainers will merge your PR
- Delete your feature branch
- Sync your fork with upstream

---

## Documentation

### What to Document

- All public APIs
- Complex algorithms
- Configuration options
- Installation procedures
- Usage examples
- Breaking changes

### Documentation Style

- Clear and concise
- Use examples
- Keep up-to-date with code
- Include both simple and advanced usage

### Updating Documentation

Documentation files to update:
- `README.md` - High-level overview
- `USER_GUIDE.md` - User instructions
- `DEVELOPER_GUIDE.md` - Developer instructions
- `API_DOCUMENTATION.md` - API reference
- Inline code comments and docstrings

---

## Community

### Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our community chat (if available)

### Staying Updated

- Watch the repository for updates
- Subscribe to release notifications
- Follow project announcements

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation (where applicable)

---

## Development Tips

### Debugging

```python
# Use logging instead of print
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Your code here
train_model()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Memory Profiling

```bash
pip install memory_profiler

# Add @profile decorator to functions
python -m memory_profiler script.py
```

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Questions?

If you have questions about contributing:
- Open an issue with the `question` label
- Check existing discussions
- Contact maintainers

Thank you for contributing! 🎉
