# Contributing to Spotify High-Quality Downloader

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/selvaa-p/spotify-downloader.git
   cd spotify-downloader
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # When available
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

## 📝 Contribution Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) Python style guidelines
- Use type hints for all functions and methods
- Write comprehensive docstrings for all public functions
- Maximum line length: 88 characters (Black formatter standard)

### Commit Messages

Use conventional commit format:
```
type(scope): description

body (optional)

footer (optional)
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(downloader): add support for album downloads
fix(metadata): resolve encoding issues with special characters
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python -m pytest tests/
   python spotify_downloader.py --test
   ```

4. **Submit a pull request**
   - Use a clear, descriptive title
   - Provide detailed description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, dependency versions
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error output and logs
- **Additional context**: Screenshots, relevant configuration

### Bug Report Template

```markdown
**Environment:**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Package versions: [output of `pip freeze`]

**Describe the bug:**
A clear description of what the bug is.

**To Reproduce:**
1. Run command '...'
2. With URL '...'
3. See error

**Expected behavior:**
What you expected to happen.

**Error output:**
```
[Paste error messages and logs here]
```

**Additional context:**
Any other information that might be helpful.
```

## 💡 Feature Requests

We welcome feature suggestions! Please:

- **Check existing issues** to avoid duplicates
- **Provide detailed description** of the proposed feature
- **Explain the use case** and why it would be valuable
- **Consider implementation complexity** and maintenance burden

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like:**
A clear description of what you want to happen.

**Describe alternatives you've considered:**
Alternative solutions or features you've considered.

**Additional context:**
Any other context, screenshots, or examples.
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=spotify_downloader

# Run specific test file
python -m pytest tests/test_downloader.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_download_single_track_success`
- Include both positive and negative test cases
- Mock external API calls for unit tests
- Use fixtures for common test data

## 📚 Documentation

### Updating Documentation

- Keep README.md up to date with new features
- Update docstrings for any modified functions
- Add examples for new functionality
- Update configuration documentation

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent
- Test all code examples

## 🔧 Development Tools

### Recommended Tools

- **Code Formatter**: [Black](https://black.readthedocs.io/)
- **Linter**: [Flake8](https://flake8.pycqa.org/) or [Pylint](https://pylint.org/)
- **Type Checker**: [mypy](http://mypy-lang.org/)
- **Import Sorter**: [isort](https://pycqa.github.io/isort/)

### Pre-commit Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 🏷️ Release Process

For maintainers:

1. **Update version** in `spotify_downloader.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Create release PR** with all changes
4. **Tag release** after PR merge
5. **Create GitHub release** with release notes

## ❓ Questions?

- **General questions**: Open a [Discussion](https://github.com/selvaa-p/spotify-downloader/discussions)
- **Bug reports**: Open an [Issue](https://github.com/selvaa-p/spotify-downloader/issues)
- **Feature requests**: Open an [Issue](https://github.com/selvaa-p/spotify-downloader/issues) with feature request template

## 📞 Contact

- **GitHub**: [@selvaa-p](https://github.com/selvaa-p)

---

Thank you for contributing to make this project better! 🎵
