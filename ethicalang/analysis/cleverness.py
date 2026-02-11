"""
Cleverness Detector for EthicaLang

Detects and rejects "clever" code that prioritizes brevity over clarity.
This enforces the principle: "Code is read more often than it is written."

Detection Patterns:
- Excessive method chaining
- Dense bitwise operations
- Overuse of ternary/complex expressions
- Lambda/anonymous function abuse
- Cryptic one-liners
"""

from typing import Dict, List
from ..ast.nodes import *


class ClevernessViolation(Exception):
    """Raised when code is overly clever"""
    pass


class ClevernessDetector(ASTVisitor):
    """
    Detects overly clever code patterns
    
    "Clever" code is code that is technically correct but unnecessarily
    hard to understand. This analyzer identifies such patterns and
    suggests refactoring.
    """
    
    MAX_CHAINING_DEPTH = 3
    MAX_EXPRESSION_DEPTH = 4
    MAX_BINARY_OPS_PER_STATEMENT = 5
    MAX_FUNCTION_ARGS = 5
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the cleverness detector
        
        Args:
            strict_mode: If True, reject any cleverness violations
        """
        self.strict_mode = strict_mode
        self.violations = []
        self.current_function = None
        self.expression_depth = 0
        self.max_expression_depth = 0
        self.chaining_depth = 0
        self.binary_op_count = 0
    
    def analyze(self, ast: Program) -> Dict[str, any]:
        """
        Analyze the entire program for clever code
        
        Returns:
            Dictionary with analysis results
        """
        self.violations = []
        
        try:
            self.visit(ast)
        except ClevernessViolation:
            pass  # Violations are collected
        
        return {
            'passed': len(self.violations) == 0,
            'violations': self.violations,
            'strict_mode': self.strict_mode
        }
    
    def add_violation(self, violation_type: str, message: str, suggestion: str = None, details: Dict = None):
        """Add a cleverness violation"""
        violation = {
            'type': violation_type,
            'message': message,
            'function': self.current_function
        }
        if suggestion:
            violation['suggestion'] = suggestion
        if details:
            violation.update(details)
        
        self.violations.append(violation)
        
        if self.strict_mode:
            raise ClevernessViolation(message)
    
    def visit_Program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: FunctionDef):
        """Visit function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Check parameter count
        if len(node.parameters) > self.MAX_FUNCTION_ARGS:
            self.add_violation(
                'too_many_parameters',
                f'Function "{node.name}" has {len(node.parameters)} parameters (maximum: {self.MAX_FUNCTION_ARGS})',
                suggestion='Consider using a parameter object or breaking into smaller functions',
                details={'parameter_count': len(node.parameters)}
            )
        
        # Check for single-statement functions that might be overly complex
        if len(node.body) == 1 and isinstance(node.body[0], ReturnStatement):
            # Analyze the complexity of the return expression
            if node.body[0].value:
                depth = self._get_expression_depth(node.body[0].value)
                if depth > self.MAX_EXPRESSION_DEPTH:
                    self.add_violation(
                        'complex_one_liner',
                        f'Function "{node.name}" is a complex one-liner (expression depth: {depth})',
                        suggestion='Break down the expression into intermediate variables',
                        details={'expression_depth': depth}
                    )
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        self.current_function = old_function
    
    def visit_Assignment(self, node: Assignment):
        """Visit assignment"""
        # Check expression complexity in assignment
        old_binary_count = self.binary_op_count
        self.binary_op_count = 0
        
        depth = self._get_expression_depth(node.value)
        if depth > self.MAX_EXPRESSION_DEPTH:
            self.add_violation(
                'complex_assignment',
                f'Assignment to "{node.name}" has overly complex expression (depth: {depth})',
                suggestion='Break down into multiple statements with intermediate variables',
                details={'variable': node.name, 'depth': depth}
            )
        
        self.visit(node.value)
        
        if self.binary_op_count > self.MAX_BINARY_OPS_PER_STATEMENT:
            self.add_violation(
                'dense_expression',
                f'Assignment to "{node.name}" has too many operations ({self.binary_op_count} operators)',
                suggestion='Split into multiple statements for clarity',
                details={'operator_count': self.binary_op_count}
            )
        
        self.binary_op_count = old_binary_count
    
    def visit_Variable(self, node: Variable):
        """Visit variable reference"""
        pass
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visit binary operation"""
        self.binary_op_count += 1
        
        # Detect chained comparisons that might be confusing
        if node.operator in ('==', '!=', '<', '<=', '>', '>='):
            if isinstance(node.left, BinaryOp) and node.left.operator in ('==', '!=', '<', '<=', '>', '>='):
                self.add_violation(
                    'chained_comparisons',
                    'Chained comparison operators can be confusing',
                    suggestion='Use logical operators (and/or) to make intent clear',
                    details={'operator': node.operator}
                )
        
        # Detect bitwise operations (often clever)
        if node.operator in ('&', '|', '^', '<<', '>>'):
            self.add_violation(
                'bitwise_operation',
                'Bitwise operations can be hard to understand',
                suggestion='Add comments explaining the bit manipulation or use clearer alternatives',
                details={'operator': node.operator}
            )
        
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visit unary operation"""
        self.visit(node.operand)
    
    def visit_Literal(self, node: Literal):
        """Visit literal value"""
        # Check for magic numbers (except common ones)
        if node.type_name in ('int', 'float'):
            if isinstance(node.value, (int, float)):
                # Flag non-obvious numbers
                if abs(node.value) > 10 and node.value not in (100, 1000, 24, 60, 365):
                    self.add_violation(
                        'magic_number',
                        f'Magic number {node.value} used without explanation',
                        suggestion='Define as a named constant with clear meaning',
                        details={'value': node.value}
                    )
    
    def visit_ListLiteral(self, node: ListLiteral):
        """Visit list literal"""
        # Check for overly complex list comprehension-like patterns
        if len(node.elements) > 0:
            avg_depth = sum(self._get_expression_depth(e) for e in node.elements) / len(node.elements)
            if avg_depth > 3:
                self.add_violation(
                    'complex_list_literal',
                    'List literal contains complex expressions',
                    suggestion='Create elements in separate statements before building the list',
                    details={'element_count': len(node.elements)}
                )
        
        for elem in node.elements:
            self.visit(elem)
    
    def visit_DictLiteral(self, node: DictLiteral):
        """Visit dictionary literal"""
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
    
    def visit_IfStatement(self, node: IfStatement):
        """Visit if statement"""
        # Check condition complexity
        cond_depth = self._get_expression_depth(node.condition)
        if cond_depth > 3:
            self.add_violation(
                'complex_condition',
                f'If statement has overly complex condition (depth: {cond_depth})',
                suggestion='Extract condition into a well-named boolean variable',
                details={'depth': cond_depth}
            )
        
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
    
    def visit_WhileLoop(self, node: WhileLoop):
        """Visit while loop"""
        # Check condition complexity
        cond_depth = self._get_expression_depth(node.condition)
        if cond_depth > 3:
            self.add_violation(
                'complex_loop_condition',
                f'While loop has overly complex condition (depth: {cond_depth})',
                suggestion='Extract condition into a well-named boolean variable or function',
                details={'depth': cond_depth}
            )
        
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ForLoop(self, node: ForLoop):
        """Visit for loop"""
        # Check iterable complexity
        iter_depth = self._get_expression_depth(node.iterable)
        if iter_depth > 2:
            self.add_violation(
                'complex_iterable',
                'For loop iterates over complex expression',
                suggestion='Assign the iterable to a well-named variable first',
                details={'depth': iter_depth}
            )
        
        self.visit(node.iterable)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        """Visit return statement"""
        if node.value:
            # Check return expression complexity
            depth = self._get_expression_depth(node.value)
            if depth > self.MAX_EXPRESSION_DEPTH:
                self.add_violation(
                    'complex_return',
                    f'Return statement has overly complex expression (depth: {depth})',
                    suggestion='Compute the result in a variable before returning',
                    details={'depth': depth}
                )
            self.visit(node.value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        """Visit function call"""
        # Check argument count
        if len(node.arguments) > self.MAX_FUNCTION_ARGS:
            func_name = node.function.name if isinstance(node.function, Variable) else "function"
            self.add_violation(
                'too_many_arguments',
                f'Call to {func_name} has {len(node.arguments)} arguments (maximum: {self.MAX_FUNCTION_ARGS})',
                suggestion='Consider using named parameters or a parameter object',
                details={'argument_count': len(node.arguments)}
            )
        
        # Check for nested function calls (chaining)
        old_chaining = self.chaining_depth
        self.chaining_depth += 1
        
        if self.chaining_depth > self.MAX_CHAINING_DEPTH:
            self.add_violation(
                'excessive_chaining',
                f'Excessive method/function chaining detected (depth: {self.chaining_depth})',
                suggestion='Break the chain into intermediate variables with descriptive names',
                details={'chaining_depth': self.chaining_depth}
            )
        
        self.visit(node.function)
        for arg in node.arguments:
            self.visit(arg)
        
        self.chaining_depth = old_chaining
    
    def visit_MemberAccess(self, node: MemberAccess):
        """Visit member access"""
        old_chaining = self.chaining_depth
        self.chaining_depth += 1
        
        if self.chaining_depth > self.MAX_CHAINING_DEPTH:
            self.add_violation(
                'excessive_member_chaining',
                f'Excessive member access chaining detected (depth: {self.chaining_depth})',
                suggestion='Break the chain using intermediate variables',
                details={'chaining_depth': self.chaining_depth}
            )
        
        self.visit(node.object)
        self.chaining_depth = old_chaining
    
    def visit_IndexAccess(self, node: IndexAccess):
        """Visit index access"""
        self.visit(node.object)
        self.visit(node.index)
    
    def visit_Annotation(self, node: Annotation):
        """Visit annotation"""
        pass
    
    def _get_expression_depth(self, node: ASTNode) -> int:
        """Calculate the depth/complexity of an expression"""
        if isinstance(node, (Literal, Variable)):
            return 1
        elif isinstance(node, BinaryOp):
            return 1 + max(
                self._get_expression_depth(node.left),
                self._get_expression_depth(node.right)
            )
        elif isinstance(node, UnaryOp):
            return 1 + self._get_expression_depth(node.operand)
        elif isinstance(node, FunctionCall):
            arg_depth = max(
                (self._get_expression_depth(arg) for arg in node.arguments),
                default=0
            )
            return 2 + arg_depth
        elif isinstance(node, (MemberAccess, IndexAccess)):
            return 1 + self._get_expression_depth(node.object)
        elif isinstance(node, (ListLiteral, DictLiteral)):
            return 2
        else:
            return 1


def format_cleverness_report(results: Dict) -> str:
    """
    Format cleverness analysis results into a human-readable report
    
    Args:
        results: Results from ClevernessDetector.analyze()
    
    Returns:
        Formatted string report
    """
    if results['passed']:
        return "✓ Cleverness check passed: Code is appropriately clear"
    
    report = ["❌ Cleverness check failed: Code is overly clever\n"]
    for i, violation in enumerate(results['violations'], 1):
        report.append(f"{i}. {violation['type'].upper()}")
        report.append(f"   {violation['message']}")
        if violation.get('suggestion'):
            report.append(f"   💡 Suggestion: {violation['suggestion']}")
        if violation.get('function'):
            report.append(f"   Function: {violation['function']}")
        report.append("")
    
    return "\n".join(report)
