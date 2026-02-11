"""
Integration tests for the complete pipeline
"""

import pytest
from ethicalang.lexer.lexer import Lexer
from ethicalang.parser.parser import Parser
from ethicalang.analysis.energy import EnergyAnalyzer
from ethicalang.analysis.ethics import EthicsChecker
from ethicalang.analysis.readability import ReadabilityScorer
from ethicalang.analysis.cleverness import ClevernessDetector
from ethicalang.runtime.interpreter import Interpreter


class TestIntegration:
    """Integration tests for the complete compilation pipeline"""
    
    def compile_and_run(self, source):
        """Full compilation and execution pipeline"""
        # Lexing
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Static Analysis
        energy = EnergyAnalyzer(budget=1000)
        energy_results = energy.analyze(ast)
        
        ethics = EthicsChecker(strict_mode=False)
        ethics_results = ethics.analyze(ast)
        
        readability = ReadabilityScorer(min_score=70)
        readability_results = readability.analyze(ast)
        
        cleverness = ClevernessDetector(strict_mode=False)
        cleverness_results = cleverness.analyze(ast)
        
        # Check if all passed
        all_passed = (
            energy_results['within_budget'] and
            ethics_results['passed'] and
            readability_results['passed'] and
            cleverness_results['passed']
        )
        
        # Execute if all checks passed
        if all_passed:
            interpreter = Interpreter()
            result = interpreter.execute(ast)
            return result, None
        else:
            errors = []
            if not energy_results['within_budget']:
                errors.append("Energy budget exceeded")
            if not ethics_results['passed']:
                errors.append("Ethics check failed")
            if not readability_results['passed']:
                errors.append("Readability check failed")
            if not cleverness_results['passed']:
                errors.append("Cleverness check failed")
            return None, errors
    
    def test_good_program_passes_all(self):
        """Test that a good program passes all checks and runs"""
        source = """function calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total

numbers_list = [1, 2, 3, 4, 5]
result = calculate_sum(numbers_list)
"""
        result, errors = self.compile_and_run(source)
        
        assert errors is None
        assert result == 15
    
    def test_bad_energy_fails(self):
        """Test that energy-expensive code fails"""
        source = """function expensive():
    for i in range(50):
        for j in range(50):
            for k in range(50):
                x = i + j + k
    return x

result = expensive()
"""
        result, errors = self.compile_and_run(source)
        
        assert result is None
        assert "Energy budget exceeded" in errors
    
    def test_bad_ethics_fails(self):
        """Test that unethical code fails"""
        source = """function collect_location():
    return none

result = collect_location()
"""
        result, errors = self.compile_and_run(source)
        
        assert result is None
        assert "Ethics check failed" in errors
    
    def test_with_annotations_passes(self):
        """Test that properly annotated code passes"""
        source = """@requires_user_consent
function collect_location():
    return none

result = collect_location()
"""
        result, errors = self.compile_and_run(source)
        
        assert errors is None
        assert result is None
