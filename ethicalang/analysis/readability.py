"""
Readability Scoring System for EthicaLang

Computes a readability score (0-100) based on:
- Cyclomatic complexity
- Nesting depth
- Function length
- Variable name quality
- Code structure

Rejects programs below a configurable threshold.
"""

import math
import re
from typing import Dict, List
from ..ast.nodes import *


class ReadabilityError(Exception):
    """Raised when code fails readability requirements"""
    pass


class ReadabilityScorer(ASTVisitor):
    """
    Analyzes code readability and assigns a score
    
    Scoring factors:
    - Cyclomatic complexity (lower is better)
    - Nesting depth (lower is better)
    - Function length (shorter is better)
    - Variable naming quality (descriptive names score higher)
    - Comment density (more documentation is better)
    """
    
    MAX_FUNCTION_LENGTH = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MIN_VARIABLE_NAME_LENGTH = 2
    
    def __init__(self, min_score: int = 70):
        """
        Initialize the readability scorer
        
        Args:
            min_score: Minimum required score (0-100, default: 70)
        """
        self.min_score = min_score
        self.scores = {
            'complexity': 100,
            'nesting': 100,
            'function_length': 100,
            'naming': 100,
        }
        self.issues = []
        
        # Tracking state
        self.current_function = None
        self.function_stats = {}
        self.nesting_depth = 0
        self.max_nesting = 0
        self.complexity = 0
        self.variable_names = []
    
    def analyze(self, ast: Program) -> Dict[str, any]:
        """
        Analyze the entire program for readability
        
        Returns:
            Dictionary with score and detailed breakdown
        """
        self.issues = []
        self.function_stats = {}
        
        # Visit the AST
        self.visit(ast)
        
        # Calculate individual scores
        self._calculate_scores()
        
        # Calculate overall score (weighted average)
        weights = {
            'complexity': 0.30,
            'nesting': 0.25,
            'function_length': 0.20,
            'naming': 0.25,
        }
        
        overall_score = sum(
            self.scores[key] * weight 
            for key, weight in weights.items()
        )
        overall_score = round(overall_score, 1)
        
        # Check if score meets threshold
        passed = overall_score >= self.min_score
        
        if not passed:
            self.issues.append({
                'type': 'low_readability',
                'message': f'Readability score too low ({overall_score}/100). Minimum required: {self.min_score}/100',
                'score': overall_score,
                'threshold': self.min_score
            })
        
        return {
            'overall_score': overall_score,
            'min_score': self.min_score,
            'passed': passed,
            'scores': self.scores.copy(),
            'issues': self.issues,
            'function_stats': self.function_stats.copy()
        }
    
    def _calculate_scores(self):
        """Calculate individual component scores"""
        # Complexity score
        if self.complexity > self.MAX_COMPLEXITY:
            penalty = min(50, (self.complexity - self.MAX_COMPLEXITY) * 5)
            self.scores['complexity'] = max(0, 100 - penalty)
            self.issues.append({
                'type': 'high_complexity',
                'message': f'Cyclomatic complexity ({self.complexity}) exceeds recommended maximum ({self.MAX_COMPLEXITY})',
                'complexity': self.complexity
            })
        
        # Nesting score
        if self.max_nesting > self.MAX_NESTING_DEPTH:
            penalty = (self.max_nesting - self.MAX_NESTING_DEPTH) * 15
            self.scores['nesting'] = max(0, 100 - penalty)
            self.issues.append({
                'type': 'deep_nesting',
                'message': f'Maximum nesting depth ({self.max_nesting}) exceeds recommended ({self.MAX_NESTING_DEPTH})',
                'depth': self.max_nesting
            })
        
        # Function length score
        max_func_length = max(
            (stats['length'] for stats in self.function_stats.values()),
            default=0
        )
        if max_func_length > self.MAX_FUNCTION_LENGTH:
            penalty = min(50, (max_func_length - self.MAX_FUNCTION_LENGTH))
            self.scores['function_length'] = max(0, 100 - penalty)
            long_functions = [
                name for name, stats in self.function_stats.items()
                if stats['length'] > self.MAX_FUNCTION_LENGTH
            ]
            self.issues.append({
                'type': 'long_function',
                'message': f'Functions too long: {", ".join(long_functions)}',
                'functions': long_functions
            })
        
        # Naming score
        naming_score = self._calculate_naming_score()
        self.scores['naming'] = naming_score
        if naming_score < 70:
            self.issues.append({
                'type': 'poor_naming',
                'message': 'Variable names could be more descriptive',
                'score': naming_score
            })
    
    def _calculate_naming_score(self) -> float:
        """Calculate score based on variable name quality"""
        if not self.variable_names:
            return 100
        
        total_score = 0
        for name in self.variable_names:
            score = self._score_variable_name(name)
            total_score += score
        
        return (total_score / len(self.variable_names)) * 100
    
    def _score_variable_name(self, name: str) -> float:
        """
        Score an individual variable name (0.0 - 1.0)
        
        Factors:
        - Length (too short or too long is bad)
        - Descriptiveness (words vs abbreviations)
        - Convention (snake_case for Python-like language)
        """
        score = 1.0
        
        # Check length
        if len(name) < self.MIN_VARIABLE_NAME_LENGTH:
            score -= 0.3
            self.issues.append({
                'type': 'short_variable_name',
                'message': f'Variable name "{name}" is too short (< {self.MIN_VARIABLE_NAME_LENGTH} characters)',
                'variable': name
            })
        elif len(name) > 30:
            score -= 0.2
        
        # Check for single letter names (except common ones like i, j, x, y)
        if len(name) == 1 and name not in 'ijxyznkv':
            score -= 0.4
        
        # Check for common bad names
        bad_names = {'temp', 'tmp', 'data', 'var', 'val', 'foo', 'bar', 'baz', 'x1', 'x2'}
        if name.lower() in bad_names:
            score -= 0.5
            self.issues.append({
                'type': 'non_descriptive_name',
                'message': f'Variable name "{name}" is not descriptive',
                'variable': name
            })
        
        # Prefer snake_case
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            score -= 0.1
        
        # Reward longer, meaningful names
        if len(name) >= 5 and '_' in name:
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _count_statements(self, statements: List[ASTNode]) -> int:
        """Count the number of statements in a block"""
        count = 0
        for stmt in statements:
            count += 1
            if isinstance(stmt, IfStatement):
                count += self._count_statements(stmt.then_body)
                if stmt.else_body:
                    count += self._count_statements(stmt.else_body)
            elif isinstance(stmt, (WhileLoop, ForLoop)):
                count += self._count_statements(stmt.body)
        return count
    
    def visit_Program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: FunctionDef):
        """Visit function definition"""
        old_function = self.current_function
        old_complexity = self.complexity
        old_max_nesting = self.max_nesting
        old_nesting = self.nesting_depth
        
        self.current_function = node.name
        self.complexity = 1  # Base complexity
        self.max_nesting = 0
        self.nesting_depth = 0
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        # Calculate function statistics
        function_length = self._count_statements(node.body)
        self.function_stats[node.name] = {
            'length': function_length,
            'complexity': self.complexity,
            'max_nesting': self.max_nesting,
        }
        
        # Restore state
        self.current_function = old_function
        self.complexity = old_complexity + self.complexity
        self.max_nesting = max(old_max_nesting, self.max_nesting)
        self.nesting_depth = old_nesting
    
    def visit_Assignment(self, node: Assignment):
        """Visit assignment"""
        if node.is_declaration:
            self.variable_names.append(node.name)
        self.visit(node.value)
    
    def visit_Variable(self, node: Variable):
        """Visit variable reference"""
        pass
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visit binary operation"""
        # Logical operators increase complexity
        if node.operator in ('and', 'or'):
            self.complexity += 1
        
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visit unary operation"""
        self.visit(node.operand)
    
    def visit_Literal(self, node: Literal):
        """Visit literal value"""
        pass
    
    def visit_ListLiteral(self, node: ListLiteral):
        """Visit list literal"""
        for elem in node.elements:
            self.visit(elem)
    
    def visit_DictLiteral(self, node: DictLiteral):
        """Visit dictionary literal"""
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
    
    def visit_IfStatement(self, node: IfStatement):
        """Visit if statement"""
        self.complexity += 1  # Each branch adds complexity
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        
        if node.else_body:
            self.complexity += 1  # Else branch adds complexity
            for stmt in node.else_body:
                self.visit(stmt)
        
        self.nesting_depth -= 1
    
    def visit_WhileLoop(self, node: WhileLoop):
        """Visit while loop"""
        self.complexity += 1
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)
        
        self.nesting_depth -= 1
    
    def visit_ForLoop(self, node: ForLoop):
        """Visit for loop"""
        self.complexity += 1
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        
        self.variable_names.append(node.variable)
        self.visit(node.iterable)
        for stmt in node.body:
            self.visit(stmt)
        
        self.nesting_depth -= 1
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        """Visit return statement"""
        if node.value:
            self.visit(node.value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        """Visit function call"""
        self.visit(node.function)
        for arg in node.arguments:
            self.visit(arg)
    
    def visit_MemberAccess(self, node: MemberAccess):
        """Visit member access"""
        self.visit(node.object)
    
    def visit_IndexAccess(self, node: IndexAccess):
        """Visit index access"""
        self.visit(node.object)
        self.visit(node.index)
    
    def visit_Annotation(self, node: Annotation):
        """Visit annotation"""
        pass


def format_readability_report(results: Dict) -> str:
    """
    Format readability analysis results into a human-readable report
    
    Args:
        results: Results from ReadabilityScorer.analyze()
    
    Returns:
        Formatted string report
    """
    score = results['overall_score']
    passed = results['passed']
    
    if passed:
        report = [f"✓ Readability check passed: Score = {score}/100"]
    else:
        report = [f"❌ Readability check failed: Score = {score}/100 (minimum: {results['min_score']})"]
    
    report.append("\nScore Breakdown:")
    for component, score_val in results['scores'].items():
        report.append(f"  {component.replace('_', ' ').title()}: {score_val:.1f}/100")
    
    if results['issues']:
        report.append("\nIssues:")
        for i, issue in enumerate(results['issues'], 1):
            if issue['type'] != 'low_readability':  # Skip overall failure message
                report.append(f"  {i}. {issue['message']}")
    
    return "\n".join(report)
