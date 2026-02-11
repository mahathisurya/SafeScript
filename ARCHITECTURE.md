# EthicaLang Architecture

This document provides an in-depth look at EthicaLang's architecture and implementation details.

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Compilation Pipeline](#compilation-pipeline)
4. [Static Analysis Deep Dive](#static-analysis-deep-dive)
5. [Runtime Execution](#runtime-execution)
6. [Design Patterns](#design-patterns)

---

## Overview

EthicaLang is implemented as a multi-stage compiler and interpreter with clear separation between:
- **Frontend**: Lexical and syntactic analysis
- **Middle-end**: Static analysis and semantic checking
- **Backend**: AST-based interpretation

### Core Philosophy

1. **Modularity**: Each component is independently testable
2. **Extensibility**: New analyzers can be added without modifying existing code
3. **Clarity**: Code readability over clever optimizations
4. **Zero Dependencies**: All algorithms implemented from scratch

---

## Module Structure

```
ethicalang/
├── lexer/
│   └── lexer.py           # Tokenization and indentation handling
├── parser/
│   └── parser.py          # Recursive descent parser
├── ast/
│   └── nodes.py           # AST node definitions and visitor pattern
├── analysis/
│   ├── energy.py          # Energy efficiency analyzer
│   ├── ethics.py          # Ethics constraint checker
│   ├── readability.py     # Readability scoring system
│   └── cleverness.py      # Anti-obfuscation detector
├── runtime/
│   └── interpreter.py     # AST-walking interpreter
└── cli/
    └── main.py            # Command-line interface
```

### Dependency Graph

```
┌──────────┐
│   CLI    │
└────┬─────┘
     │
     ├────────┬─────────┬──────────┬───────────┐
     │        │         │          │           │
┌────▼───┐ ┌─▼──────┐ ┌▼────────┐ ┌▼─────────┐ ┌▼──────────┐
│ Lexer  │ │ Parser │ │ Analysis│ │ Runtime  │ │   AST     │
└────────┘ └────────┘ └─────────┘ └──────────┘ └───────────┘
                          │ │ │ │
                Energy ───┘ │ │ └─── Cleverness
                Ethics ─────┘ │
                Readability ──┘
```

---

## Compilation Pipeline

### Stage 1: Lexical Analysis

**File**: `ethicalang/lexer/lexer.py`

**Input**: Raw source code string
**Output**: Token stream

**Key Features**:
- Hand-written scanner with lookahead
- Python-like indentation handling (INDENT/DEDENT tokens)
- Comment stripping
- String escape sequence processing
- Precise line/column tracking for error reporting

**Algorithm**:
```python
1. Initialize position, line, column counters
2. Initialize indentation stack [0]
3. While not at end:
   a. If at line start, handle indentation:
      - Count spaces/tabs
      - Compare with stack top
      - Generate INDENT/DEDENT tokens
   b. Skip whitespace and comments
   c. Match token patterns:
      - Keywords (function, if, while, etc.)
      - Identifiers (variable names)
      - Literals (numbers, strings, booleans)
      - Operators (+, -, *, ==, etc.)
      - Delimiters (parentheses, brackets, etc.)
   d. Advance position
4. Generate remaining DEDENT tokens
5. Add EOF token
```

**Complexity**: O(n) where n is source code length

### Stage 2: Parsing

**File**: `ethicalang/parser/parser.py`

**Input**: Token stream
**Output**: Abstract Syntax Tree (AST)

**Algorithm**: Recursive Descent

**Key Functions**:
- `parse()` - Entry point, returns Program node
- `parse_statement()` - Dispatches to specific statement parsers
- `parse_expression()` - Handles expressions with proper precedence
- `parse_primary()` - Handles literals and parenthesized expressions

**Operator Precedence** (lowest to highest):
1. Logical OR (`or`)
2. Logical AND (`and`)
3. Equality (`==`, `!=`)
4. Comparison (`<`, `<=`, `>`, `>=`)
5. Addition/Subtraction (`+`, `-`)
6. Multiplication/Division/Modulo (`*`, `/`, `%`)
7. Unary (`not`, `-`)
8. Power (`**`) - right associative
9. Postfix (function call, indexing, member access)

**Error Recovery**: Fails fast with descriptive error messages including line/column

**Complexity**: O(n) where n is number of tokens (single-pass)

### Stage 3: Static Analysis

Each analyzer is independent and can be toggled:

#### 3.1 Energy Analysis

**File**: `ethicalang/analysis/energy.py`

**Cost Model**:
```
Operation               Cost
---------------------------------
Literal                 1 unit
Variable access         1 unit
Assignment              2 units
Binary operation        3 units
Function call           10 units + function body cost
Loop iteration          body_cost × iterations × 2^(nesting-1)
Recursion              function_cost × max_depth (heavily penalized)
```

**Algorithm**:
```python
1. Visit AST with depth-first traversal
2. Accumulate costs for each operation
3. For loops:
   - Estimate iterations (known or assumed)
   - Multiply body cost by iterations
   - Apply exponential penalty for nesting
4. For recursion:
   - Detect by checking for self-calls
   - Apply maximum depth penalty
5. Compare total cost with budget
```

**Complexity**: O(n) where n is AST node count

#### 3.2 Ethics Checking

**File**: `ethicalang/analysis/ethics.py`

**Rule Database**:
- Requires consent: location, biometrics, contacts, messages, etc.
- Requires protection: passwords, payment info, sensitive data
- Disallowed: facial recognition, dark patterns, manipulation

**Algorithm**:
```python
1. Visit each function definition
2. Check function name against rule database
3. Check for required annotations
4. Visit function calls
5. Ensure caller has appropriate annotations
6. Scan for hardcoded secrets in string literals
7. Flag suspicious variable names
8. Collect violations
```

**Complexity**: O(n) where n is AST node count

#### 3.3 Readability Scoring

**File**: `ethicalang/analysis/readability.py`

**Metrics**:
- **Cyclomatic Complexity**: Count decision points (if, while, for, and, or)
- **Nesting Depth**: Maximum indent level
- **Function Length**: Statement count per function
- **Variable Naming**: Entropy, length, descriptiveness

**Scoring Formula**:
```
Overall = 0.30 × complexity_score
        + 0.25 × nesting_score
        + 0.20 × length_score
        + 0.25 × naming_score
```

**Algorithm**:
```python
1. Visit AST tracking:
   - Nesting depth (incremented at if/while/for)
   - Complexity (incremented at branches)
   - Variable names
   - Statement counts
2. Calculate per-component scores
3. Apply penalties for violations
4. Compute weighted average
```

**Complexity**: O(n) where n is AST node count

#### 3.4 Cleverness Detection

**File**: `ethicalang/analysis/cleverness.py`

**Heuristics**:
- Expression depth > 4
- Chaining depth > 3
- Binary operations > 5 per statement
- Magic numbers (except common: 0, 1, 10, 100)
- Single-letter variables (except i, j, k in loops)

**Algorithm**:
```python
1. Visit each expression
2. Calculate depth recursively
3. Count chaining levels (obj.prop.method().prop)
4. Count operators per statement
5. Flag violations with suggestions
```

**Complexity**: O(n) where n is AST node count

### Stage 4: Execution

**File**: `ethicalang/runtime/interpreter.py`

**Execution Model**: Tree-walking interpreter

**Environment**: Lexical scoping with parent chain

**Algorithm**:
```python
1. Create global environment
2. Register built-in functions
3. Visit Program node
4. For each statement:
   a. Function definitions: store in environment
   b. Assignments: evaluate and store
   c. Control flow: evaluate conditionally
   d. Function calls: create new scope, execute, return
5. Return final result
```

**Scoping Rules**:
- Variables defined in current scope or inherited from parent
- Function parameters create new scope
- Loop variables scoped to loop body
- Assignments create new bindings if not found in parent chain

**Complexity**: O(n × d) where n is node count, d is average environment depth

---

## Design Patterns

### 1. Visitor Pattern

**Used in**: All analyzers and interpreter

**Benefits**:
- Separates algorithm from data structure
- Easy to add new operations without modifying AST
- Clean separation of concerns

**Implementation**:
```python
class ASTVisitor:
    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
```

### 2. Interpreter Pattern

**Used in**: Runtime execution

**Benefits**:
- Direct AST evaluation
- Simple to understand and debug
- Sufficient for language demonstration

### 3. Strategy Pattern

**Used in**: Pluggable analyzers

**Benefits**:
- Each analyzer is interchangeable
- Can enable/disable checks independently
- Easy to add new analyzers

---

## Performance Characteristics

| Component | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Lexer | O(n) | O(n) |
| Parser | O(n) | O(d) depth |
| Energy Analysis | O(n) | O(d) depth |
| Ethics Check | O(n) | O(n) |
| Readability | O(n) | O(n) |
| Cleverness | O(n) | O(d) depth |
| Interpreter | O(n × d) | O(d) environment |

Where:
- n = size of input (characters/tokens/nodes)
- d = depth (AST depth or environment chain depth)

---

## Testing Strategy

### Unit Tests
- Each component tested independently
- Mock dependencies
- Cover edge cases

### Integration Tests
- Full pipeline testing
- Good and bad programs
- Error message validation

### Golden Tests
- Known good programs must pass
- Known bad programs must fail with expected errors

---

## Future Optimization Opportunities

1. **Bytecode Compilation**: Replace tree-walking with bytecode VM
2. **Constant Folding**: Evaluate constant expressions at compile time
3. **Dead Code Elimination**: Remove unreachable code
4. **Tail Call Optimization**: Convert tail recursion to iteration
5. **Caching**: Memoize analysis results for unchanged code

---

## References

- Nystrom, Robert. *Crafting Interpreters*. 2021.
- Appel, Andrew. *Modern Compiler Implementation in ML*. 1998.
- Aho et al. *Compilers: Principles, Techniques, and Tools* (Dragon Book). 2006.
