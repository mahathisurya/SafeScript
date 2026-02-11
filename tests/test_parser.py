"""
Tests for the parser module
"""

import pytest
from ethicalang.lexer.lexer import Lexer
from ethicalang.parser.parser import Parser
from ethicalang.ast.nodes import *


class TestParser:
    """Test cases for the parser"""
    
    def parse(self, source):
        """Helper to parse source code"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_simple_assignment(self):
        """Test simple variable assignment"""
        source = "x = 5"
        ast = self.parse(source)
        
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert ast.statements[0].name == "x"
    
    def test_function_definition(self):
        """Test function definition parsing"""
        source = """function add(a, b):
    return a + b
"""
        ast = self.parse(source)
        
        assert isinstance(ast, Program)
        func = ast.statements[0]
        assert isinstance(func, FunctionDef)
        assert func.name == "add"
        assert func.parameters == ["a", "b"]
        assert len(func.body) == 1
    
    def test_if_statement(self):
        """Test if statement parsing"""
        source = """if x > 5:
    y = 1
else:
    y = 2
"""
        ast = self.parse(source)
        
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStatement)
        assert isinstance(stmt.condition, BinaryOp)
        assert len(stmt.then_body) == 1
        assert len(stmt.else_body) == 1
    
    def test_while_loop(self):
        """Test while loop parsing"""
        source = """while x < 10:
    x = x + 1
"""
        ast = self.parse(source)
        
        stmt = ast.statements[0]
        assert isinstance(stmt, WhileLoop)
        assert isinstance(stmt.condition, BinaryOp)
        assert len(stmt.body) == 1
    
    def test_for_loop(self):
        """Test for loop parsing"""
        source = """for i in range(10):
    print(i)
"""
        ast = self.parse(source)
        
        stmt = ast.statements[0]
        assert isinstance(stmt, ForLoop)
        assert stmt.variable == "i"
        assert isinstance(stmt.iterable, FunctionCall)
    
    def test_function_call(self):
        """Test function call parsing"""
        source = "result = calculate(1, 2, 3)"
        ast = self.parse(source)
        
        assignment = ast.statements[0]
        assert isinstance(assignment.value, FunctionCall)
        assert len(assignment.value.arguments) == 3
    
    def test_list_literal(self):
        """Test list literal parsing"""
        source = "numbers = [1, 2, 3, 4, 5]"
        ast = self.parse(source)
        
        assignment = ast.statements[0]
        assert isinstance(assignment.value, ListLiteral)
        assert len(assignment.value.elements) == 5
    
    def test_dict_literal(self):
        """Test dictionary literal parsing"""
        source = 'data = {"key": "value", "num": 42}'
        ast = self.parse(source)
        
        assignment = ast.statements[0]
        assert isinstance(assignment.value, DictLiteral)
        assert len(assignment.value.pairs) == 2
    
    def test_annotation(self):
        """Test annotation parsing"""
        source = """@requires_user_consent
function collect_data():
    return none
"""
        ast = self.parse(source)
        
        func = ast.statements[0]
        assert isinstance(func, FunctionDef)
        assert len(func.annotations) == 1
        assert func.annotations[0].name == "requires_user_consent"
    
    def test_binary_operations(self):
        """Test binary operation parsing"""
        source = "result = a + b * c"
        ast = self.parse(source)
        
        assignment = ast.statements[0]
        # Should respect operator precedence
        assert isinstance(assignment.value, BinaryOp)
        assert assignment.value.operator == "+"
        assert isinstance(assignment.value.right, BinaryOp)
        assert assignment.value.right.operator == "*"
