# Contributing to EthicaLang

Thank you for your interest in contributing to EthicaLang! This document provides guidelines for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ethicalang.git
   cd ethicalang
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Project Structure

- `ethicalang/` - Main source code
  - `lexer/` - Tokenization
  - `parser/` - Parsing
  - `ast/` - AST definitions
  - `analysis/` - Static analyzers
  - `runtime/` - Interpreter
  - `cli/` - Command-line interface
- `tests/` - Test suite
- `examples/` - Example programs
- `docs/` - Additional documentation

## Code Style

### Python Style Guide

- Follow PEP 8
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes
- Type hints encouraged but not required

### Documentation

- Document complex algorithms
- Explain non-obvious design decisions
- Update README if adding major features

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ethicalang --cov-report=html

# Run specific test file
pytest tests/test_lexer.py -v

# Run specific test
pytest tests/test_lexer.py::TestLexer::test_simple_tokens -v
```

### Writing Tests

- Write tests for all new features
- Include both positive and negative test cases
- Test edge cases
- Use descriptive test names

Example:
```python
def test_feature_with_valid_input(self):
    """Test that feature works with valid input"""
    # Arrange
    input_data = "valid input"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Adding New Features

### Adding a New Analyzer

1. Create new file in `ethicalang/analysis/`
2. Inherit from `ASTVisitor`
3. Implement `analyze()` method returning a dict with `passed` key
4. Add to `analysis/__init__.py`
5. Integrate into CLI (`cli/main.py`)
6. Write tests
7. Update documentation

Example structure:
```python
class NewAnalyzer(ASTVisitor):
    def __init__(self, config):
        self.config = config
        self.violations = []
    
    def analyze(self, ast: Program) -> Dict[str, any]:
        self.visit(ast)
        return {
            'passed': len(self.violations) == 0,
            'violations': self.violations
        }
    
    def visit_FunctionDef(self, node: FunctionDef):
        # Implement analysis logic
        pass
```

### Adding Language Features

1. Update lexer if new tokens needed
2. Update parser grammar
3. Add new AST node type if needed
4. Update all analyzers to handle new node
5. Update interpreter
6. Write comprehensive tests
7. Update language spec in README

## Pull Request Process

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Provide clear description
   - Reference any related issues
   - Ensure CI passes

## Reporting Issues

### Bug Reports

Include:
- EthicaLang version
- Python version
- Operating system
- Minimal reproduction steps
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Clear description of feature
- Use cases
- Proposed implementation (optional)
- Potential impacts on existing features

## Questions?

- Open an issue with the "question" label
- Check existing documentation
- Review closed issues for similar questions

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
