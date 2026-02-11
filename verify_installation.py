#!/usr/bin/env python3
"""
Verification script for EthicaLang installation
Runs a quick check to ensure everything is working
"""

import sys
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_check(name, passed):
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {name}")

def main():
    print_header("EthicaLang Installation Verification")
    
    all_passed = True
    
    # Check 1: Python version
    print("\nChecking Python version...")
    py_version = sys.version_info
    py_ok = py_version.major == 3 and py_version.minor >= 8
    print_check(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}", py_ok)
    all_passed = all_passed and py_ok
    
    # Check 2: Import modules
    print("\nChecking module imports...")
    try:
        from ethicalang.lexer import Lexer
        print_check("Lexer module", True)
        
        from ethicalang.parser import Parser
        print_check("Parser module", True)
        
        from ethicalang.analysis import EnergyAnalyzer, EthicsChecker, ReadabilityScorer, ClevernessDetector
        print_check("Analysis modules", True)
        
        from ethicalang.runtime import Interpreter
        print_check("Runtime module", True)
        
        from ethicalang.cli import main
        print_check("CLI module", True)
        
    except ImportError as e:
        print_check(f"Module import: {e}", False)
        all_passed = False
        print("\n⚠ Run: pip install -e .")
        return 1
    
    # Check 3: Quick compilation test
    print("\nTesting basic compilation...")
    try:
        source = """
function test():
    x = 1
    return x

result = test()
"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print_check("Lexer", len(tokens) > 0)
        
        parser = Parser(tokens)
        ast = parser.parse()
        print_check("Parser", ast is not None)
        
        energy = EnergyAnalyzer()
        energy_result = energy.analyze(ast)
        print_check("Energy Analyzer", energy_result is not None)
        
        ethics = EthicsChecker(strict_mode=False)
        ethics_result = ethics.analyze(ast)
        print_check("Ethics Checker", ethics_result is not None)
        
        readability = ReadabilityScorer()
        readability_result = readability.analyze(ast)
        print_check("Readability Scorer", readability_result is not None)
        
        cleverness = ClevernessDetector(strict_mode=False)
        cleverness_result = cleverness.analyze(ast)
        print_check("Cleverness Detector", cleverness_result is not None)
        
    except Exception as e:
        print_check(f"Compilation: {e}", False)
        all_passed = False
        return 1
    
    # Check 4: Execution test
    print("\nTesting program execution...")
    try:
        interpreter = Interpreter()
        result = interpreter.execute(ast)
        print_check("Interpreter execution", result == 1)
    except Exception as e:
        print_check(f"Execution: {e}", False)
        all_passed = False
        return 1
    
    # Check 5: Example files exist
    print("\nChecking example files...")
    examples_dir = Path(__file__).parent / "examples"
    if examples_dir.exists():
        example_files = list(examples_dir.glob("*.eth"))
        print_check(f"Found {len(example_files)} example files", len(example_files) > 0)
    else:
        print_check("Examples directory", False)
        all_passed = False
    
    # Final result
    print_header("Verification Results")
    if all_passed:
        print("\n✓ All checks passed! EthicaLang is ready to use.")
        print("\nNext steps:")
        print("  1. Run an example: python -m ethicalang.cli.main run examples/fibonacci.eth")
        print("  2. Try the demo script: ./run_examples.sh")
        print("  3. Run tests: pytest")
        print("  4. Read the docs: README.md")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
