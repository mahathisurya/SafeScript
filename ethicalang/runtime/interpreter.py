"""
AST-Walking Interpreter for EthicaLang

Executes EthicaLang programs by walking the Abstract Syntax Tree.
Implements a tree-walking interpreter with environment-based scoping.
"""

from typing import Any, Dict, List, Optional
from ..ast.nodes import *


class RuntimeError(Exception):
    """Runtime execution error"""
    pass


class ReturnValue(Exception):
    """Exception used to implement return statements"""
    def __init__(self, value):
        self.value = value


class Environment:
    """
    Environment for variable and function storage
    Implements lexical scoping with parent chain
    """
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.bindings: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        """Define a new variable in this environment"""
        self.bindings[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable's value, checking parent scopes if needed"""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: Any):
        """Set a variable's value, checking parent scopes if needed"""
        if name in self.bindings:
            self.bindings[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise RuntimeError(f"Undefined variable: {name}")
    
    def exists(self, name: str) -> bool:
        """Check if a variable exists"""
        if name in self.bindings:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


class Interpreter(ASTVisitor):
    """
    Tree-walking interpreter for EthicaLang
    
    Executes programs by recursively evaluating AST nodes.
    Maintains environment chain for scoping.
    """
    
    def __init__(self, output_callback=None):
        """
        Initialize interpreter
        
        Args:
            output_callback: Function to call for print output (default: print)
        """
        self.global_env = Environment()
        self.current_env = self.global_env
        self.output_callback = output_callback or print
        
        # Register built-in functions
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in functions"""
        self.global_env.define('print', self._builtin_print)
        self.global_env.define('len', self._builtin_len)
        self.global_env.define('range', self._builtin_range)
        self.global_env.define('str', self._builtin_str)
        self.global_env.define('int', self._builtin_int)
        self.global_env.define('float', self._builtin_float)
        self.global_env.define('type', self._builtin_type)
        self.global_env.define('abs', self._builtin_abs)
        self.global_env.define('min', self._builtin_min)
        self.global_env.define('max', self._builtin_max)
        self.global_env.define('sum', self._builtin_sum)
    
    def _builtin_print(self, *args):
        """Built-in print function"""
        output = ' '.join(str(arg) for arg in args)
        self.output_callback(output)
        return None
    
    def _builtin_len(self, obj):
        """Built-in len function"""
        if isinstance(obj, (list, dict, str)):
            return len(obj)
        raise RuntimeError(f"len() not supported for type {type(obj).__name__}")
    
    def _builtin_range(self, *args):
        """Built-in range function"""
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        raise RuntimeError("range() takes 1 to 3 arguments")
    
    def _builtin_str(self, obj):
        """Built-in str function"""
        return str(obj)
    
    def _builtin_int(self, obj):
        """Built-in int function"""
        try:
            return int(obj)
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Cannot convert to int: {e}")
    
    def _builtin_float(self, obj):
        """Built-in float function"""
        try:
            return float(obj)
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Cannot convert to float: {e}")
    
    def _builtin_type(self, obj):
        """Built-in type function"""
        return type(obj).__name__
    
    def _builtin_abs(self, x):
        """Built-in abs function"""
        return abs(x)
    
    def _builtin_min(self, *args):
        """Built-in min function"""
        if len(args) == 1 and isinstance(args[0], list):
            return min(args[0])
        return min(args)
    
    def _builtin_max(self, *args):
        """Built-in max function"""
        if len(args) == 1 and isinstance(args[0], list):
            return max(args[0])
        return max(args)
    
    def _builtin_sum(self, iterable):
        """Built-in sum function"""
        if not isinstance(iterable, list):
            raise RuntimeError("sum() requires a list")
        return sum(iterable)
    
    def execute(self, ast: Program) -> Any:
        """
        Execute a program
        
        Args:
            ast: Program AST to execute
        
        Returns:
            Result of execution (usually None)
        """
        try:
            return self.visit(ast)
        except ReturnValue as rv:
            # Top-level return (unusual but allowed)
            return rv.value
    
    def visit_Program(self, node: Program):
        """Visit program node"""
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result
    
    def visit_FunctionDef(self, node: FunctionDef):
        """Visit function definition"""
        # Store function in current environment
        self.current_env.define(node.name, node)
        return None
    
    def visit_Assignment(self, node: Assignment):
        """Visit assignment"""
        value = self.visit(node.value)
        
        if node.is_declaration or not self.current_env.exists(node.name):
            self.current_env.define(node.name, value)
        else:
            self.current_env.set(node.name, value)
        
        return value
    
    def visit_Variable(self, node: Variable):
        """Visit variable reference"""
        return self.current_env.get(node.name)
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visit binary operation"""
        left = self.visit(node.left)
        
        # Short-circuit evaluation for logical operators
        if node.operator == 'and':
            if not self._is_truthy(left):
                return False
            right = self.visit(node.right)
            return self._is_truthy(left) and self._is_truthy(right)
        
        if node.operator == 'or':
            if self._is_truthy(left):
                return True
            right = self.visit(node.right)
            return self._is_truthy(left) or self._is_truthy(right)
        
        right = self.visit(node.right)
        
        # Arithmetic operators
        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif node.operator == '%':
            return left % right
        elif node.operator == '**':
            return left ** right
        
        # Comparison operators
        elif node.operator == '==':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '<':
            return left < right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == '>':
            return left > right
        elif node.operator == '>=':
            return left >= right
        
        else:
            raise RuntimeError(f"Unknown operator: {node.operator}")
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visit unary operation"""
        operand = self.visit(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == 'not':
            return not self._is_truthy(operand)
        else:
            raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def visit_Literal(self, node: Literal):
        """Visit literal value"""
        return node.value
    
    def visit_ListLiteral(self, node: ListLiteral):
        """Visit list literal"""
        return [self.visit(elem) for elem in node.elements]
    
    def visit_DictLiteral(self, node: DictLiteral):
        """Visit dictionary literal"""
        result = {}
        for key_node, value_node in node.pairs:
            key = self.visit(key_node)
            # Keys must be hashable
            if not isinstance(key, (int, float, str, bool, type(None))):
                raise RuntimeError(f"Dictionary keys must be hashable, got {type(key).__name__}")
            value = self.visit(value_node)
            result[key] = value
        return result
    
    def visit_IfStatement(self, node: IfStatement):
        """Visit if statement"""
        condition = self.visit(node.condition)
        
        if self._is_truthy(condition):
            for stmt in node.then_body:
                self.visit(stmt)
        elif node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        return None
    
    def visit_WhileLoop(self, node: WhileLoop):
        """Visit while loop"""
        while self._is_truthy(self.visit(node.condition)):
            for stmt in node.body:
                self.visit(stmt)
        
        return None
    
    def visit_ForLoop(self, node: ForLoop):
        """Visit for loop"""
        iterable = self.visit(node.iterable)
        
        if not isinstance(iterable, (list, str)):
            raise RuntimeError(f"Cannot iterate over {type(iterable).__name__}")
        
        # Create new scope for loop variable
        loop_env = Environment(self.current_env)
        old_env = self.current_env
        self.current_env = loop_env
        
        try:
            for item in iterable:
                self.current_env.define(node.variable, item)
                for stmt in node.body:
                    self.visit(stmt)
        finally:
            self.current_env = old_env
        
        return None
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        """Visit return statement"""
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnValue(value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        """Visit function call"""
        function = self.visit(node.function)
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Built-in function (Python callable)
        if callable(function) and not isinstance(function, FunctionDef):
            try:
                return function(*args)
            except Exception as e:
                raise RuntimeError(f"Error calling built-in function: {e}")
        
        # User-defined function
        if isinstance(function, FunctionDef):
            # Check argument count
            if len(args) != len(function.parameters):
                raise RuntimeError(
                    f"Function {function.name} expects {len(function.parameters)} "
                    f"arguments, got {len(args)}"
                )
            
            # Create new environment for function
            func_env = Environment(self.global_env)
            
            # Bind parameters
            for param, arg in zip(function.parameters, args):
                func_env.define(param, arg)
            
            # Execute function body
            old_env = self.current_env
            self.current_env = func_env
            
            try:
                for stmt in function.body:
                    self.visit(stmt)
                # No explicit return
                return None
            except ReturnValue as rv:
                return rv.value
            finally:
                self.current_env = old_env
        
        raise RuntimeError(f"Cannot call {type(function).__name__}")
    
    def visit_MemberAccess(self, node: MemberAccess):
        """Visit member access"""
        obj = self.visit(node.object)
        
        # For dictionaries, treat as key access
        if isinstance(obj, dict):
            if node.member in obj:
                return obj[node.member]
            raise RuntimeError(f"Dictionary has no key '{node.member}'")
        
        # For other objects, could implement attribute access
        raise RuntimeError(f"Member access not supported for {type(obj).__name__}")
    
    def visit_IndexAccess(self, node: IndexAccess):
        """Visit index access"""
        obj = self.visit(node.object)
        index = self.visit(node.index)
        
        try:
            return obj[index]
        except (IndexError, KeyError, TypeError) as e:
            raise RuntimeError(f"Index access error: {e}")
    
    def visit_Annotation(self, node: Annotation):
        """Visit annotation"""
        # Annotations are processed at compile time, not runtime
        return None
    
    def _is_truthy(self, value: Any) -> bool:
        """
        Determine if a value is truthy
        
        Python-like truthiness:
        - False, None, 0, empty collections are falsy
        - Everything else is truthy
        """
        if value is None or value is False:
            return False
        if value == 0 or value == 0.0:
            return False
        if isinstance(value, (str, list, dict)) and len(value) == 0:
            return False
        return True
