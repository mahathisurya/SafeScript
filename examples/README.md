# EthicaLang Examples

This directory contains example programs that demonstrate EthicaLang's features and static analysis capabilities.

## Good Examples (Pass All Checks)

### `good_simple_calculator.eth`
A simple calculator demonstrating:
- Clear function names
- Good variable naming
- Reasonable complexity
- Efficient algorithms

**Run it:**
```bash
ethicalang run examples/good_simple_calculator.eth
```

### `good_data_collection.eth`
Ethical data collection example demonstrating:
- Proper use of `@requires_user_consent` annotation
- Proper use of `@requires_data_protection` annotation
- Transparent data handling

**Run it:**
```bash
ethicalang run examples/good_data_collection.eth
```

### `fibonacci.eth`
Fibonacci sequence generator demonstrating:
- Clear logic flow
- Descriptive variable names
- Iterative (not recursive) approach for efficiency

**Run it:**
```bash
ethicalang run examples/fibonacci.eth
```

## Bad Examples (Fail Various Checks)

### `bad_no_consent.eth`
**Fails:** Ethics Check

Missing required `@requires_user_consent` annotation for location collection.

**Try it:**
```bash
ethicalang check examples/bad_no_consent.eth
```

**Error Output:**
```
❌ Error: Ethical violation: Function "collect_location" collects sensitive data
but lacks @requires_user_consent annotation
```

### `bad_energy_expensive.eth`
**Fails:** Energy Budget Check

Triple-nested loops exceed the energy budget.

**Try it:**
```bash
ethicalang check examples/bad_energy_expensive.eth
```

**Error Output:**
```
❌ Error: Energy budget exceeded: estimated cost = 2,400,000 units (limit = 1000)
```

### `bad_poor_readability.eth`
**Fails:** Readability Check

Poor variable naming, excessive nesting, and unclear logic.

**Try it:**
```bash
ethicalang check examples/bad_poor_readability.eth
```

**Error Output:**
```
❌ Error: Readability score too low (45/100). Minimum required: 70/100
```

### `bad_too_clever.eth`
**Fails:** Cleverness Detection

Overly complex expressions and magic numbers without explanation.

**Try it:**
```bash
ethicalang check examples/bad_too_clever.eth
```

**Error Output:**
```
❌ Error: Code is overly clever. Complex expressions should be broken down
for clarity.
```

## Running Examples

Check a program without running:
```bash
ethicalang check examples/program.eth
```

Run a program:
```bash
ethicalang run examples/program.eth
```

Run with verbose output:
```bash
ethicalang run examples/program.eth --verbose
```

Skip specific checks (for experimentation):
```bash
ethicalang run examples/program.eth --no-ethics
ethicalang run examples/program.eth --no-energy
```
