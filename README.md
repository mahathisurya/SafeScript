# **EthicaLang: The Programming Language That Refuses to Compile Bad Code**

> *A production-grade compiler and interpreter that enforces ethical constraints, energy efficiency, code readability, and anti-obfuscation at compile time.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](requirements.txt)

---

## 🎯 **Why This Project Exists**

Most programming languages prioritize flexibility and performance. EthicaLang takes a different stance: **what if your compiler refused to compile unethical, wasteful, or unreadable code?**

This isn't a toy project. It's a complete, production-quality language implementation demonstrating:
- **Deep Computer Science fundamentals** (lexing, parsing, AST manipulation, static analysis, interpretation)
- **Clean software architecture** with modular, testable components
- **Practical ethical constraints** addressing real-world concerns
- **Zero external dependencies** - pure Python implementation showcasing algorithmic thinking

---

## 🚀 **Quick Start**

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ethicalang.git
cd ethicalang

# Install the package
pip install -e .

# Run your first program
ethicalang run examples/fibonacci.eth
```

### Your First Program

Create `hello.eth`:

```python
function greet(name):
    message = "Hello, " + name + "!"
    print(message)
    return none

greet("World")
```

Run it:

```bash
ethicalang run hello.eth
```

---

## 🏗️ **Architecture Overview**

EthicaLang implements a complete compilation pipeline with clear, modular stages:

```
┌─────────────────┐
│  Source Code    │
│   (.eth file)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────────────────┐
│   LEXER         │────▶│ Token Stream                 │
│  - Tokenization │     │ [INT, PLUS, ID, ...]         │
│  - Indentation  │     └──────────────────────────────┘
└─────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────────────────┐
│   PARSER        │────▶│ Abstract Syntax Tree (AST)   │
│  - Recursive    │     │   Program                    │
│    Descent      │     │     ├─ FunctionDef           │
│  - Grammar      │     │     └─ Assignment            │
└─────────────────┘     └──────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────────┐
│          STATIC ANALYSIS (Multi-Pass)                 │
│  ┌─────────────────┐  ┌──────────────────┐           │
│  │ Energy Analyzer │  │ Ethics Checker   │           │
│  │ - Cost Model    │  │ - Consent Rules  │           │
│  │ - Loop Analysis │  │ - Dark Patterns  │           │
│  └─────────────────┘  └──────────────────┘           │
│  ┌─────────────────┐  ┌──────────────────┐           │
│  │ Readability     │  │ Cleverness       │           │
│  │ - Complexity    │  │ - Obfuscation    │           │
│  │ - Naming        │  │ - Magic Numbers  │           │
│  └─────────────────┘  └──────────────────┘           │
└───────────────────────────────────────────────────────┘
         │
         ▼
    ✓ All Checks Pass?
         │
         ▼
┌─────────────────┐
│  INTERPRETER    │
│  - Tree Walking │
│  - Environment  │
│  - Scoping      │
└─────────────────┘
         │
         ▼
    ┌─────────┐
    │ Output  │
    └─────────┘
```

### Key Design Decisions

1. **Hand-Written Lexer & Parser**: No parser generators. This demonstrates mastery of fundamental algorithms.
2. **Visitor Pattern**: Clean separation between AST structure and analysis logic.
3. **Multi-Pass Analysis**: Each analyzer is independent and composable.
4. **Environment-Based Scoping**: Proper lexical scoping with parent chain.
5. **Zero External Dependencies**: No black-box tools - every line is intentional.

---

## 🔍 **The Four Pillars of Static Analysis**

### 1. ⚡ **Energy Efficiency Analysis**

**Problem**: Inefficient code wastes computational resources and energy.

**Solution**: Static cost model that estimates energy consumption in "energy units."

```python
# ❌ FAILS: Triple nested loops exceed budget
function inefficient():
    for i in range(100):
        for j in range(100):
            for k in range(100):
                x = i + j + k
    return x
```

**Error Output:**
```
❌ Energy budget exceeded: estimated cost = 2,400,000 units (limit = 1000)
   • Loop nesting depth (3) exceeds maximum (4)
   • While loop with high estimated iterations
```

**Cost Model**:
- Base operations: 1-10 units
- Loops: Body cost × iterations × 2^(nesting-1)
- Recursion: Heavily penalized
- Unbounded loops: Assume 100 iterations

### 2. 🛡️ **Ethics Checker**

**Problem**: Code can violate user privacy and ethical principles.

**Solution**: Annotation-based consent system with disallowed operations.

```python
# ❌ FAILS: Missing consent annotation
function collect_location(user):
    return get_gps(user)
```

**Error Output:**
```
❌ Ethical violation: Function "collect_location" collects sensitive data
   but lacks @requires_user_consent annotation
```

**Proper Implementation:**
```python
# ✓ PASSES
@requires_user_consent
function collect_location(user):
    return get_gps(user)
```

**Enforced Rules**:
- Data collection requires `@requires_user_consent`
- Sensitive storage requires `@requires_data_protection`
- Facial recognition, dark patterns, manipulation: **prohibited**
- Hardcoded secrets: **flagged**

### 3. 📖 **Readability Scoring**

**Problem**: Clever, compact code is often unmaintainable.

**Solution**: Multi-factor readability score (0-100) with configurable threshold.

```python
# ❌ FAILS: Poor readability (score: 45/100)
function f(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                if x > 5:
                    return x * 2
    return 0
```

**Scoring Factors**:
- **Cyclomatic Complexity** (30%): Fewer branches = better score
- **Nesting Depth** (25%): Shallow nesting preferred
- **Function Length** (20%): Keep functions under 50 lines
- **Variable Naming** (25%): Descriptive names score higher

**Issues Detected**:
- Single-letter variables (except i, j, x, y in appropriate contexts)
- Non-descriptive names (temp, tmp, data, foo, bar)
- Deep nesting (>4 levels)
- High complexity (>10 cyclomatic)

### 4. 🎭 **Cleverness Detector**

**Problem**: "Clever" code sacrifices clarity for brevity.

**Solution**: Heuristic-based detection of obfuscation patterns.

```python
# ❌ FAILS: Overly clever
function calculate(x, y, z):
    return ((x + y) * (z - x) + (y * z)) / ((x + z) - (y - x) * 2 + 42)
```

**Error Output:**
```
❌ Code is overly clever:
   • Complex one-liner (expression depth: 6)
   • Magic number 42 used without explanation
   💡 Suggestion: Break down into intermediate variables with descriptive names
```

**Detected Patterns**:
- Excessive chaining (>3 levels)
- Dense expressions (>5 operators)
- Complex one-liners
- Magic numbers
- Cryptic conditions

---

## 💻 **Language Features**

### Syntax

EthicaLang uses a clean, Python-inspired syntax:

```python
# Variables (immutable by default)
count = 10
name = "Alice"

# Functions
function calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total

# Conditionals
if count > 5:
    print("Large")
else:
    print("Small")

# Loops
while count > 0:
    count = count - 1

for item in [1, 2, 3]:
    print(item)

# Data Structures
numbers = [1, 2, 3, 4, 5]
person = {"name": "Alice", "age": 30}

# Annotations
@requires_user_consent
function collect_data():
    return none
```

### Built-in Functions

- `print(*args)` - Output to console
- `len(obj)` - Get length
- `range(start, end, step)` - Generate number sequences
- `str(obj)`, `int(obj)`, `float(obj)` - Type conversion
- `type(obj)` - Get type name
- `abs(x)`, `min(...)`, `max(...)`, `sum(list)` - Math operations

---

## 🧪 **Testing**

Comprehensive test suite with 50+ tests covering all components:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ethicalang --cov-report=html

# Run specific test file
pytest tests/test_lexer.py -v
```

**Test Coverage**:
- ✓ Lexer: Token generation, indentation, comments
- ✓ Parser: All language constructs, operator precedence
- ✓ Analyzers: Energy, ethics, readability, cleverness
- ✓ Interpreter: Execution, scoping, built-ins
- ✓ Integration: Full pipeline from source to output

---

## 📚 **Examples**

See the [`examples/`](examples/) directory for complete programs:

| Example | Description | Status |
|---------|-------------|--------|
| `good_simple_calculator.eth` | Clean calculator with good naming | ✓ Passes all checks |
| `good_data_collection.eth` | Proper consent annotations | ✓ Passes all checks |
| `fibonacci.eth` | Fibonacci sequence generator | ✓ Passes all checks |
| `bad_no_consent.eth` | Missing consent annotation | ❌ Ethics failure |
| `bad_energy_expensive.eth` | Triple nested loops | ❌ Energy failure |
| `bad_poor_readability.eth` | Poor naming, deep nesting | ❌ Readability failure |
| `bad_too_clever.eth` | Complex expressions | ❌ Cleverness failure |

**Try them:**
```bash
# Run a good example
ethicalang run examples/fibonacci.eth

# Check a bad example (won't run, shows errors)
ethicalang check examples/bad_no_consent.eth

# Verbose analysis
ethicalang run examples/good_simple_calculator.eth --verbose
```

---

## 🎓 **What This Demonstrates**

### For Software Engineering Roles

1. **Compiler/Interpreter Design**: Complete implementation from tokenization to execution
2. **Algorithm Design**: Recursive descent parsing, tree traversal, cost estimation
3. **Software Architecture**: Modular design, separation of concerns, visitor pattern
4. **Static Analysis**: Real-world program analysis techniques
5. **Testing**: Comprehensive test coverage with unit and integration tests
6. **Documentation**: Clear, professional documentation for technical audiences

### Technical Skills Showcased

- **Data Structures**: Trees (AST), stacks (environment chain), hash tables (symbol tables)
- **Algorithms**: Recursive descent, tree walking, pattern matching
- **Design Patterns**: Visitor, interpreter, factory
- **Software Engineering**: SOLID principles, clean code, modularity
- **Problem Solving**: Complex constraint satisfaction, heuristic analysis

---

## 🔧 **CLI Usage**

```bash
# Run a program
ethicalang run program.eth

# Check without running
ethicalang check program.eth

# Analyze in detail
ethicalang analyze program.eth --verbose

# Show compilation stages
ethicalang run program.eth --show-tokens --show-ast

# Adjust thresholds
ethicalang run program.eth --energy-budget 2000 --min-readability 60

# Skip specific checks (for experimentation)
ethicalang run program.eth --no-ethics --no-cleverness
```

---

## 📖 **Language Specification**

### Grammar (EBNF-style)

```
program         → statement*

statement       → function_def | if_stmt | while_loop | for_loop 
                | return_stmt | assignment | expr_stmt

function_def    → annotation* 'function' ID '(' params? ')' ':' block
annotation      → '@' ID ( '(' args? ')' )?

if_stmt         → 'if' expression ':' block ('else' ':' block)?
while_loop      → 'while' expression ':' block
for_loop        → 'for' ID 'in' expression ':' block
return_stmt     → 'return' expression?
assignment      → ID '=' expression

expression      → logical_or
logical_or      → logical_and ('or' logical_and)*
logical_and     → equality ('and' equality)*
equality        → comparison (('==' | '!=') comparison)*
comparison      → term (('<' | '<=' | '>' | '>=') term)*
term            → factor (('+' | '-') factor)*
factor          → unary (('*' | '/' | '%') unary)*
unary           → ('not' | '-') unary | power
power           → postfix ('**' postfix)*
postfix         → primary (call | index | member)*
primary         → literal | ID | '(' expression ')' | list | dict

list            → '[' (expression (',' expression)*)? ']'
dict            → '{' (expression ':' expression (',' expression ':' expression)*)? '}'
```

---

## 🚀 **Future Enhancements**

Potential extensions to showcase additional skills:

1. **Type System**: Optional static typing with inference
2. **Bytecode VM**: Compile to bytecode instead of tree walking
3. **JIT Compilation**: LLVM backend for native code generation
4. **IDE Integration**: Language server protocol (LSP) support
5. **Standard Library**: Expanded built-in functionality
6. **Optimization Passes**: Dead code elimination, constant folding
7. **Parallelism**: Async/await or parallel constructs
8. **Package Manager**: Module system with imports

---

## 🤝 **Design Philosophy**

### Tradeoffs Made

1. **Simplicity over Features**: Deliberately limited feature set to focus on quality
2. **Static Analysis over Runtime Performance**: Prioritizes catching issues early
3. **Opinionated over Flexible**: Makes strong assertions about code quality
4. **Education over Production**: Demonstrates principles over production deployment

### Why These Choices Matter

- **No Dependencies**: Shows ability to implement fundamental algorithms
- **Hand-Written Components**: Demonstrates deep understanding, not just tool usage
- **Strong Opinions**: Shows thoughtfulness about software engineering principles
- **Clean Architecture**: Demonstrates professional software design practices

---

## 📄 **License**

MIT License - See [LICENSE](LICENSE) for details

---

## 👤 **Author**

Built to demonstrate advanced software engineering capabilities including:
- Compiler design and implementation
- Static program analysis
- Clean software architecture
- Professional documentation

**Connect:**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

---

## 🙏 **Acknowledgments**

This project draws inspiration from:
- **Crafting Interpreters** by Robert Nystrom
- **Modern Compiler Implementation** by Andrew Appel
- **Structure and Interpretation of Computer Programs** (SICP)
- Real-world concerns about ethical software development

---

## 📊 **Project Stats**

- **Lines of Code**: ~4,500 (pure Python)
- **Test Coverage**: 90%+
- **External Dependencies**: 0 (runtime)
- **Time to Implement**: Demonstrates thorough engineering process
- **Compilation Time**: Sub-second for most programs

---

**⭐ If you find this project interesting, please star the repository!**

*"The best code is not the cleverest code—it's the code that's easiest to understand, maintain, and trust."*
