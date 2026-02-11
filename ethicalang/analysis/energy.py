"""
Energy Efficiency Analyzer for EthicaLang

Implements a static cost model to estimate computational energy usage.
Rejects programs that exceed a configurable energy budget.

Cost Model:
- Each operation has an energy cost in abstract "energy units"
- Loops multiply costs by estimated iterations
- Recursion is heavily penalized
- Nested structures increase costs exponentially
"""

from typing import Dict, Set
from ..ast.nodes import *


class EnergyBudgetExceeded(Exception):
    """Raised when a program exceeds the energy budget"""
    pass


class EnergyAnalyzer(ASTVisitor):
    """
    Analyzes and estimates the energy cost of a program
    
    This analyzer performs static analysis to estimate computational cost
    and enforces energy efficiency constraints.
    """
    
    # Base costs for operations (in energy units)
    BASE_COSTS = {
        'literal': 1,
        'variable': 1,
        'assignment': 2,
        'binary_op': 3,
        'unary_op': 2,
        'function_call': 10,
        'return': 1,
        'list_access': 5,
        'dict_access': 7,
        'member_access': 3,
    }
    
    # Loop iteration estimates for unbounded loops
    ASSUMED_LOOP_ITERATIONS = 100
    MAX_NESTING_DEPTH = 4
    MAX_RECURSION_DEPTH = 10
    
    def __init__(self, budget: int = 1000):
        """
        Initialize the energy analyzer
        
        Args:
            budget: Maximum allowed energy units (default: 1000)
        """
        self.budget = budget
        self.total_cost = 0
        self.nesting_depth = 0
        self.function_costs: Dict[str, int] = {}
        self.recursive_functions: Set[str] = set()
        self.current_function = None
        self.violations = []
    
    def analyze(self, ast: Program) -> Dict[str, any]:
        """
        Analyze the entire program for energy efficiency
        
        Returns:
            Dictionary with analysis results including cost and violations
        """
        self.total_cost = 0
        self.violations = []
        
        try:
            self.visit(ast)
        except EnergyBudgetExceeded:
            pass  # We'll report it in the results
        
        # Check if budget was exceeded
        if self.total_cost > self.budget:
            self.violations.append({
                'type': 'budget_exceeded',
                'message': f'Energy budget exceeded: estimated cost = {self.total_cost} units (limit = {self.budget})',
                'cost': self.total_cost,
                'budget': self.budget
            })
        
        return {
            'total_cost': self.total_cost,
            'budget': self.budget,
            'within_budget': self.total_cost <= self.budget,
            'violations': self.violations,
            'function_costs': self.function_costs.copy()
        }
    
    def add_cost(self, cost: int, description: str = ""):
        """Add cost and check budget"""
        self.total_cost += cost
        if self.total_cost > self.budget:
            raise EnergyBudgetExceeded(f"Energy budget exceeded (>{self.budget} units)")
    
    def visit_Program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: FunctionDef):
        """Visit function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Check for recursion by analyzing function calls in body
        function_start_cost = self.total_cost
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        # Calculate function cost
        function_cost = self.total_cost - function_start_cost
        self.function_costs[node.name] = function_cost
        
        # Check for recursion
        if self._contains_recursive_call(node.body, node.name):
            self.recursive_functions.add(node.name)
            # Penalize recursion heavily
            recursion_penalty = function_cost * self.MAX_RECURSION_DEPTH
            self.add_cost(recursion_penalty, f"Recursion penalty for {node.name}")
            self.violations.append({
                'type': 'recursion_detected',
                'function': node.name,
                'message': f'Recursive function "{node.name}" detected. Recursion adds significant energy cost.',
                'penalty': recursion_penalty
            })
        
        self.current_function = old_function
    
    def _contains_recursive_call(self, statements: List[ASTNode], function_name: str) -> bool:
        """Check if statements contain a recursive call"""
        for stmt in statements:
            if isinstance(stmt, FunctionCall):
                if isinstance(stmt.function, Variable) and stmt.function.name == function_name:
                    return True
            elif isinstance(stmt, (IfStatement, WhileLoop, ForLoop)):
                if hasattr(stmt, 'body') and self._contains_recursive_call(stmt.body, function_name):
                    return True
                if isinstance(stmt, IfStatement) and stmt.else_body:
                    if self._contains_recursive_call(stmt.else_body, function_name):
                        return True
        return False
    
    def visit_Assignment(self, node: Assignment):
        """Visit assignment"""
        self.add_cost(self.BASE_COSTS['assignment'])
        self.visit(node.value)
    
    def visit_Variable(self, node: Variable):
        """Visit variable reference"""
        self.add_cost(self.BASE_COSTS['variable'])
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visit binary operation"""
        self.add_cost(self.BASE_COSTS['binary_op'])
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visit unary operation"""
        self.add_cost(self.BASE_COSTS['unary_op'])
        self.visit(node.operand)
    
    def visit_Literal(self, node: Literal):
        """Visit literal value"""
        self.add_cost(self.BASE_COSTS['literal'])
    
    def visit_ListLiteral(self, node: ListLiteral):
        """Visit list literal"""
        # Cost proportional to number of elements
        self.add_cost(len(node.elements) * 2)
        for elem in node.elements:
            self.visit(elem)
    
    def visit_DictLiteral(self, node: DictLiteral):
        """Visit dictionary literal"""
        # Dicts are more expensive than lists
        self.add_cost(len(node.pairs) * 3)
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
    
    def visit_IfStatement(self, node: IfStatement):
        """Visit if statement"""
        self.add_cost(5)  # Cost of condition check
        self.visit(node.condition)
        
        # Assume both branches might execute (conservative estimate)
        then_cost = self._estimate_block_cost(node.then_body)
        else_cost = self._estimate_block_cost(node.else_body) if node.else_body else 0
        
        # Add the maximum of both branches
        max_branch_cost = max(then_cost, else_cost)
        self.add_cost(max_branch_cost)
    
    def visit_WhileLoop(self, node: WhileLoop):
        """Visit while loop"""
        self.nesting_depth += 1
        
        # Check nesting depth
        if self.nesting_depth > self.MAX_NESTING_DEPTH:
            self.violations.append({
                'type': 'excessive_nesting',
                'message': f'Loop nesting depth ({self.nesting_depth}) exceeds maximum ({self.MAX_NESTING_DEPTH})',
                'depth': self.nesting_depth
            })
        
        # Unbounded loop - assume worst case iterations
        self.visit(node.condition)
        body_cost = self._estimate_block_cost(node.body)
        
        # Multiply by assumed iterations with exponential penalty for nesting
        multiplier = self.ASSUMED_LOOP_ITERATIONS * (2 ** (self.nesting_depth - 1))
        loop_cost = body_cost * multiplier
        
        self.add_cost(loop_cost)
        
        if multiplier > 200:
            self.violations.append({
                'type': 'unbounded_loop',
                'message': f'While loop with nesting depth {self.nesting_depth} has high estimated cost',
                'estimated_iterations': multiplier
            })
        
        self.nesting_depth -= 1
    
    def visit_ForLoop(self, node: ForLoop):
        """Visit for loop"""
        self.nesting_depth += 1
        
        # Check nesting depth
        if self.nesting_depth > self.MAX_NESTING_DEPTH:
            self.violations.append({
                'type': 'excessive_nesting',
                'message': f'Loop nesting depth ({self.nesting_depth}) exceeds maximum ({self.MAX_NESTING_DEPTH})',
                'depth': self.nesting_depth
            })
        
        self.visit(node.iterable)
        
        # Try to estimate iterations from iterable
        iterations = self.ASSUMED_LOOP_ITERATIONS
        if isinstance(node.iterable, ListLiteral):
            iterations = len(node.iterable.elements)
        
        body_cost = self._estimate_block_cost(node.body)
        
        # Multiply by iterations with exponential penalty for nesting
        multiplier = iterations * (2 ** (self.nesting_depth - 1))
        loop_cost = body_cost * multiplier
        
        self.add_cost(loop_cost)
        
        if multiplier > 200:
            self.violations.append({
                'type': 'high_iteration_loop',
                'message': f'For loop with nesting depth {self.nesting_depth} has high estimated cost',
                'estimated_iterations': multiplier
            })
        
        self.nesting_depth -= 1
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        """Visit return statement"""
        self.add_cost(self.BASE_COSTS['return'])
        if node.value:
            self.visit(node.value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        """Visit function call"""
        base_call_cost = self.BASE_COSTS['function_call']
        self.add_cost(base_call_cost)
        
        # Visit function expression and arguments
        self.visit(node.function)
        for arg in node.arguments:
            self.visit(arg)
        
        # If we know the function's cost, add it
        if isinstance(node.function, Variable):
            func_name = node.function.name
            if func_name in self.function_costs:
                self.add_cost(self.function_costs[func_name])
    
    def visit_MemberAccess(self, node: MemberAccess):
        """Visit member access"""
        self.add_cost(self.BASE_COSTS['member_access'])
        self.visit(node.object)
    
    def visit_IndexAccess(self, node: IndexAccess):
        """Visit index access"""
        self.add_cost(self.BASE_COSTS['list_access'])
        self.visit(node.object)
        self.visit(node.index)
    
    def visit_Annotation(self, node: Annotation):
        """Visit annotation"""
        # Annotations don't have runtime cost
        pass
    
    def _estimate_block_cost(self, statements: List[ASTNode]) -> int:
        """Estimate the cost of a block of statements"""
        if not statements:
            return 0
        
        start_cost = self.total_cost
        for stmt in statements:
            self.visit(stmt)
        end_cost = self.total_cost
        
        return end_cost - start_cost
