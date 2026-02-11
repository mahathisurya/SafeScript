# EthicaLang Quick Start Guide

Get up and running with EthicaLang in 5 minutes!

## Installation

```bash
# 1. Navigate to the project directory
cd /path/to/ethicalang

# 2. Install the package
pip install -e .

# 3. Verify installation
python verify_installation.py
```

Expected output:
```
✓ All checks passed! EthicaLang is ready to use.
```

## Your First Program

Create a file called `hello.eth`:

```python
function greet_user(username):
    greeting = "Hello, " + username + "!"
    print(greeting)
    return greeting

result = greet_user("Alice")
```

Run it:

```bash
python -m ethicalang.cli.main run hello.eth
```

Output:
```
Hello, Alice!
```

## Example Programs

Try the included examples:

### Good Example (Passes All Checks)

```bash
python -m ethicalang.cli.main run examples/fibonacci.eth --verbose
```

This will show:
- ✓ Lexical analysis complete
- ✓ Parsing complete  
- ✓ Energy budget satisfied
- ✓ No ethical violations
- ✓ Readability score: 100/100
- ✓ Code is appropriately clear
- Program output: Fibonacci sequence

### Bad Example (Shows Violations)

```bash
python -m ethicalang.cli.main check examples/bad_no_consent.eth
```

This will show:
- ❌ Ethics check failed
- Missing @requires_user_consent annotation

## Common Commands

```bash
# Run a program
ethicalang run program.eth

# Check without running
ethicalang check program.eth

# Verbose output (shows all stages)
ethicalang run program.eth --verbose

# Adjust thresholds
ethicalang run program.eth --energy-budget 2000 --min-readability 60

# Skip specific checks
ethicalang run program.eth --no-ethics
```

## Language Syntax Cheat Sheet

### Variables
```python
name = "Alice"
age = 30
is_active = true
nothing = none
```

### Functions
```python
function calculate(x, y):
    result = x + y
    return result
```

### Control Flow
```python
# If/Else
if x > 10:
    print("Large")
else:
    print("Small")

# While Loop
while count > 0:
    count = count - 1

# For Loop
for item in [1, 2, 3]:
    print(item)
```

### Data Structures
```python
# Lists
numbers = [1, 2, 3, 4, 5]
first = numbers[0]

# Dictionaries
person = {"name": "Alice", "age": 30}
name = person["name"]
```

### Annotations
```python
@requires_user_consent
function collect_location():
    return get_gps()
```

## Built-in Functions

- `print(*args)` - Output to console
- `len(obj)` - Get length
- `range(n)` - Generate 0 to n-1
- `str(x)`, `int(x)`, `float(x)` - Type conversion
- `min(...)`, `max(...)`, `sum(list)` - Math operations

## Understanding Errors

### Energy Budget Exceeded
```
❌ Energy budget exceeded: estimated cost = 2400 units (limit = 1000)
```
**Fix**: Reduce loop nesting or iterations

### Ethics Violation
```
❌ Function "collect_location" lacks @requires_user_consent annotation
```
**Fix**: Add appropriate annotation

### Low Readability
```
❌ Readability score too low (45/100)
```
**Fix**: Use descriptive variable names, reduce nesting

### Too Clever
```
❌ Code is overly clever: Complex one-liner detected
```
**Fix**: Break complex expressions into simpler steps

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=ethicalang

# Specific test
pytest tests/test_lexer.py -v
```

## Next Steps

1. **Read the README** - Comprehensive documentation
2. **Study Examples** - See `examples/` directory
3. **Try Writing Code** - Create your own programs
4. **Explore Analyzers** - Understand what each checks
5. **Read ARCHITECTURE.md** - Deep technical dive

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'ethicalang'
```
**Solution**: Run `pip install -e .` from project root

### Examples Not Found
```
File not found: examples/program.eth
```
**Solution**: Run commands from project root directory

### Permission Denied (run_examples.sh)
```
Permission denied: ./run_examples.sh
```
**Solution**: `chmod +x run_examples.sh`

## Getting Help

- Check `examples/README.md` for more examples
- Read `ARCHITECTURE.md` for technical details
- Review test files for usage patterns
- Open an issue on GitHub

## Demo Script

For a full demonstration:

```bash
./run_examples.sh
```

This will run all examples and show you how the language works!

---

**You're ready to use EthicaLang! Start writing ethical, efficient, readable code.** 🚀
