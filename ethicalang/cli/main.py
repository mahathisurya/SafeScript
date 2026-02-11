"""
Command-line interface for EthicaLang

Provides a user-friendly CLI for compiling and running EthicaLang programs.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from ..lexer.lexer import Lexer
from ..parser.parser import Parser
from ..analysis.energy import EnergyAnalyzer
from ..analysis.ethics import EthicsChecker, format_ethics_report
from ..analysis.readability import ReadabilityScorer, format_readability_report
from ..analysis.cleverness import ClevernessDetector, format_cleverness_report
from ..runtime.interpreter import Interpreter


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}❌ Error:{Colors.RESET} {message}", file=sys.stderr)


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ{Colors.RESET} {message}")


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def compile_program(source_code: str, config: dict) -> tuple[Optional[any], list]:
    """
    Compile a program through all analysis stages
    
    Args:
        source_code: Source code to compile
        config: Configuration dictionary with analyzer settings
    
    Returns:
        Tuple of (AST, errors list)
    """
    errors = []
    
    try:
        # Stage 1: Lexical Analysis
        if config.get('verbose'):
            print_section("Stage 1: Lexical Analysis")
        
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if config.get('show_tokens'):
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
        
        if config.get('verbose'):
            print_success(f"Lexical analysis complete: {len(tokens)} tokens")
        
    except Exception as e:
        print_error(f"Lexical analysis failed: {e}")
        return None, [str(e)]
    
    try:
        # Stage 2: Parsing
        if config.get('verbose'):
            print_section("Stage 2: Parsing")
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if config.get('show_ast'):
            print("Abstract Syntax Tree:")
            print(f"  {ast}")
        
        if config.get('verbose'):
            print_success("Parsing complete")
        
    except Exception as e:
        print_error(f"Parsing failed: {e}")
        return None, [str(e)]
    
    # Stage 3: Static Analysis
    if config.get('verbose'):
        print_section("Stage 3: Static Analysis")
    
    # Energy Analysis
    if config.get('check_energy', True):
        try:
            energy_budget = config.get('energy_budget', 1000)
            energy_analyzer = EnergyAnalyzer(budget=energy_budget)
            energy_results = energy_analyzer.analyze(ast)
            
            if config.get('verbose') or not energy_results['within_budget']:
                print(f"\n{Colors.BOLD}Energy Efficiency Analysis:{Colors.RESET}")
                print(f"  Total Cost: {energy_results['total_cost']} units")
                print(f"  Budget: {energy_results['budget']} units")
                if energy_results['within_budget']:
                    print_success("Energy budget satisfied")
                else:
                    print_error(f"Energy budget exceeded by {energy_results['total_cost'] - energy_results['budget']} units")
                    for violation in energy_results['violations']:
                        print(f"    • {violation['message']}")
                    errors.append("Energy budget exceeded")
        
        except Exception as e:
            print_error(f"Energy analysis failed: {e}")
            errors.append(str(e))
    
    # Ethics Check
    if config.get('check_ethics', True):
        try:
            ethics_checker = EthicsChecker(strict_mode=config.get('strict_ethics', True))
            ethics_results = ethics_checker.analyze(ast)
            
            if config.get('verbose') or not ethics_results['passed']:
                print(f"\n{Colors.BOLD}Ethics Check:{Colors.RESET}")
                if ethics_results['passed']:
                    print_success("No ethical violations detected")
                else:
                    print_error("Ethical violations detected:")
                    for violation in ethics_results['violations']:
                        print(f"    • {violation['message']}")
                    errors.append("Ethics check failed")
        
        except Exception as e:
            print_error(f"Ethics check failed: {e}")
            errors.append(str(e))
    
    # Readability Scoring
    if config.get('check_readability', True):
        try:
            min_score = config.get('min_readability', 70)
            readability_scorer = ReadabilityScorer(min_score=min_score)
            readability_results = readability_scorer.analyze(ast)
            
            if config.get('verbose') or not readability_results['passed']:
                print(f"\n{Colors.BOLD}Readability Analysis:{Colors.RESET}")
                score = readability_results['overall_score']
                print(f"  Overall Score: {score}/100")
                
                if readability_results['passed']:
                    print_success(f"Readability score meets threshold ({min_score})")
                else:
                    print_error(f"Readability score below threshold (minimum: {min_score})")
                    for issue in readability_results['issues']:
                        if issue['type'] != 'low_readability':
                            print(f"    • {issue['message']}")
                    errors.append("Readability check failed")
        
        except Exception as e:
            print_error(f"Readability analysis failed: {e}")
            errors.append(str(e))
    
    # Cleverness Detection
    if config.get('check_cleverness', True):
        try:
            cleverness_detector = ClevernessDetector(strict_mode=config.get('strict_cleverness', True))
            cleverness_results = cleverness_detector.analyze(ast)
            
            if config.get('verbose') or not cleverness_results['passed']:
                print(f"\n{Colors.BOLD}Cleverness Detection:{Colors.RESET}")
                if cleverness_results['passed']:
                    print_success("Code is appropriately clear")
                else:
                    print_error("Overly clever code detected:")
                    for violation in cleverness_results['violations']:
                        print(f"    • {violation['message']}")
                        if violation.get('suggestion'):
                            print(f"      💡 {violation['suggestion']}")
                    errors.append("Cleverness check failed")
        
        except Exception as e:
            print_error(f"Cleverness detection failed: {e}")
            errors.append(str(e))
    
    if errors:
        if config.get('verbose'):
            print_section("Compilation Result")
        print_error(f"Compilation failed with {len(errors)} error(s)")
        return None, errors
    
    if config.get('verbose'):
        print_section("Compilation Result")
        print_success("All static analysis checks passed!")
    
    return ast, []


def run_program(ast, config: dict):
    """
    Execute a compiled program
    
    Args:
        ast: Compiled AST
        config: Configuration dictionary
    """
    try:
        if config.get('verbose'):
            print_section("Stage 4: Execution")
        
        interpreter = Interpreter()
        result = interpreter.execute(ast)
        
        if config.get('verbose'):
            print_section("Execution Complete")
            if result is not None:
                print(f"Program returned: {result}")
        
        return 0
    
    except Exception as e:
        print_error(f"Runtime error: {e}")
        return 1


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description='EthicaLang - An Ethically-Aware Programming Language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ethicalang run program.eth                 # Run a program
  ethicalang run program.eth --verbose       # Run with detailed output
  ethicalang check program.eth               # Check without running
  ethicalang run program.eth --no-ethics     # Skip ethics check
  
For more information, visit: https://github.com/yourusername/ethicalang
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'check', 'analyze'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'file',
        type=str,
        help='EthicaLang source file to process'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--show-tokens',
        action='store_true',
        help='Display token stream'
    )
    
    parser.add_argument(
        '--show-ast',
        action='store_true',
        help='Display abstract syntax tree'
    )
    
    parser.add_argument(
        '--no-energy',
        action='store_true',
        help='Skip energy efficiency check'
    )
    
    parser.add_argument(
        '--no-ethics',
        action='store_true',
        help='Skip ethics check'
    )
    
    parser.add_argument(
        '--no-readability',
        action='store_true',
        help='Skip readability check'
    )
    
    parser.add_argument(
        '--no-cleverness',
        action='store_true',
        help='Skip cleverness detection'
    )
    
    parser.add_argument(
        '--energy-budget',
        type=int,
        default=1000,
        help='Energy budget in units (default: 1000)'
    )
    
    parser.add_argument(
        '--min-readability',
        type=int,
        default=70,
        help='Minimum readability score (default: 70)'
    )
    
    args = parser.parse_args()
    
    # Read source file
    source_path = Path(args.file)
    if not source_path.exists():
        print_error(f"File not found: {args.file}")
        return 1
    
    try:
        source_code = source_path.read_text()
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        return 1
    
    # Build configuration
    config = {
        'verbose': args.verbose,
        'show_tokens': args.show_tokens,
        'show_ast': args.show_ast,
        'check_energy': not args.no_energy,
        'check_ethics': not args.no_ethics,
        'check_readability': not args.no_readability,
        'check_cleverness': not args.no_cleverness,
        'energy_budget': args.energy_budget,
        'min_readability': args.min_readability,
        'strict_ethics': True,
        'strict_cleverness': True,
    }
    
    # Compile
    print_info(f"Compiling {args.file}...")
    ast, errors = compile_program(source_code, config)
    
    if errors:
        return 1
    
    # Execute if requested
    if args.command == 'run':
        return run_program(ast, config)
    else:
        print_success("Program is valid and ready to run")
        return 0


if __name__ == '__main__':
    sys.exit(main())
