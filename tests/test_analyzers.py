"""
Tests for static analysis modules
"""

import pytest
from ethicalang.lexer.lexer import Lexer
from ethicalang.parser.parser import Parser
from ethicalang.analysis.energy import EnergyAnalyzer
from ethicalang.analysis.ethics import EthicsChecker
from ethicalang.analysis.readability import ReadabilityScorer
from ethicalang.analysis.cleverness import ClevernessDetector


class TestAnalyzers:
    """Test cases for static analyzers"""
    
    def parse(self, source):
        """Helper to parse source code"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_energy_simple_passes(self):
        """Test that simple code passes energy check"""
        source = """function add(a, b):
    return a + b

result = add(1, 2)
"""
        ast = self.parse(source)
        analyzer = EnergyAnalyzer(budget=1000)
        results = analyzer.analyze(ast)
        
        assert results['within_budget']
        assert results['total_cost'] < 1000
    
    def test_energy_nested_loops_fails(self):
        """Test that nested loops fail energy check"""
        source = """function expensive():
    for i in range(100):
        for j in range(100):
            for k in range(100):
                x = i + j + k
    return x
"""
        ast = self.parse(source)
        analyzer = EnergyAnalyzer(budget=1000)
        results = analyzer.analyze(ast)
        
        assert not results['within_budget']
        assert len(results['violations']) > 0
    
    def test_ethics_missing_consent(self):
        """Test that missing consent annotation fails ethics check"""
        source = """function collect_location():
    return none
"""
        ast = self.parse(source)
        checker = EthicsChecker(strict_mode=False)
        results = checker.analyze(ast)
        
        assert not results['passed']
        assert any(v['type'] == 'missing_consent_annotation' for v in results['violations'])
    
    def test_ethics_with_consent_passes(self):
        """Test that proper consent annotation passes ethics check"""
        source = """@requires_user_consent
function collect_location():
    return none
"""
        ast = self.parse(source)
        checker = EthicsChecker(strict_mode=False)
        results = checker.analyze(ast)
        
        assert results['passed']
    
    def test_readability_good_code(self):
        """Test that readable code passes readability check"""
        source = """function calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    count = len(numbers)
    average = total / count
    return average
"""
        ast = self.parse(source)
        scorer = ReadabilityScorer(min_score=70)
        results = scorer.analyze(ast)
        
        assert results['passed']
        assert results['overall_score'] >= 70
    
    def test_readability_poor_names(self):
        """Test that poor naming fails readability check"""
        source = """function f(x):
    a = x + 1
    b = a * 2
    c = b - 3
    d = c / 4
    e = d + 5
    return e
"""
        ast = self.parse(source)
        scorer = ReadabilityScorer(min_score=70)
        results = scorer.analyze(ast)
        
        assert not results['passed']
        assert results['overall_score'] < 70
    
    def test_cleverness_simple_passes(self):
        """Test that simple code passes cleverness check"""
        source = """function add_numbers(first, second):
    result = first + second
    return result
"""
        ast = self.parse(source)
        detector = ClevernessDetector(strict_mode=False)
        results = detector.analyze(ast)
        
        assert results['passed']
    
    def test_cleverness_complex_expression_fails(self):
        """Test that overly complex expressions fail cleverness check"""
        source = """function calculate(x, y, z):
    return ((x + y) * (z - x) + (y * z)) / ((x + z) - (y - x))
"""
        ast = self.parse(source)
        detector = ClevernessDetector(strict_mode=False)
        results = detector.analyze(ast)
        
        assert not results['passed']
        assert len(results['violations']) > 0
