# Contributing to Oracle-CLI

First off, thank you for considering contributing to Oracle-CLI! It's people like you that make Oracle-CLI such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots if relevant**
* **Include your environment details**: OS, Python version, Oracle version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python styleguide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

### Prerequisites

* Python 3.10+
* Git
* Oracle Database (for testing)

### Setting Up Your Development Environment

1. **Fork the repository**

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/oracle-cli.git
   cd oracle-cli
   ```

3. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 guidelines. You can check your code with:

```bash
# Format code
black oracle_cli/

# Type checking
mypy oracle_cli/
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add SQL query export feature

- Implement CSV export
- Implement JSON export
- Add export button to TUI
- Add CLI command for export

Closes #123
```

## Project Structure

```
oracle-cli/
├── oracle_cli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # CLI commands using Click
│   ├── config.py       # Configuration management
│   ├── db.py           # Database operations
│   └── tui.py          # Textual-based TUI
├── tests/              # Test files
├── pyproject.toml      # Project configuration
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## Styleguides

### Python Styleguide

* Follow PEP 8
* Use type hints where possible
* Maximum line length: 100 characters
* Use docstrings for all public functions and classes
* Use f-strings for string formatting

Example:
```python
def fetch_table_data(
    conn: oracledb.Connection,
    schema: str,
    table_name: str,
    limit: int = 100
) -> List[Tuple]:
    """
    Fetch data from a table.
    
    Args:
        conn: Active Oracle database connection
        schema: Schema name containing the table
        table_name: Name of the table to query
        limit: Maximum number of rows to fetch
        
    Returns:
        List of tuples containing table rows
        
    Raises:
        ValueError: If table name is invalid
    """
    # Implementation here
    pass
```

### Documentation Styleguide

* Use Markdown for documentation
* Keep lines under 80 characters when possible
* Use code blocks with language specification
* Include examples where appropriate

## Testing Guidelines

* Write tests for all new features
* Ensure all tests pass before submitting PR
* Aim for high code coverage
* Use descriptive test names

Example:
```python
def test_describe_table_returns_columns():
    """Test that describe_table returns expected column structure."""
    # Test implementation
    pass
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed

## Questions?

Feel free to open an issue with your question or reach out to [@oguzhankalelioglu](https://github.com/oguzhankalelioglu).

## Recognition

Contributors will be recognized in the README.md file.

---

Thank you for contributing to Oracle-CLI! 🎉

