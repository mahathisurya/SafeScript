"""
Tests for the interpreter/runtime
"""

import pytest
from ethicalang.lexer.lexer import Lexer
from ethicalang.parser.parser import Parser
from ethicalang.runtime.interpreter import Interpreter


class TestInterpreter:
    """Test cases for the interpreter"""
    
    def execute(self, source):
        """Helper to execute source code"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        return interpreter.execute(ast)
    
    def test_simple_assignment(self):
        """Test simple variable assignment"""
        source = "x = 42"
        result = self.execute(source)
        # Assignment returns the value
        assert result == 42
    
    def test_arithmetic(self):
        """Test arithmetic operations"""
        source = """a = 10
b = 5
result = a + b * 2
"""
        result = self.execute(source)
        assert result == 20
    
    def test_function_call(self):
        """Test function definition and call"""
        source = """function add(a, b):
    return a + b

result = add(3, 4)
"""
        result = self.execute(source)
        assert result == 7
    
    def test_if_statement(self):
        """Test if statement execution"""
        source = """x = 10
if x > 5:
    result = 1
else:
    result = 2
"""
        result = self.execute(source)
        assert result == 1
    
    def test_while_loop(self):
        """Test while loop execution"""
        source = """counter = 0
while counter < 5:
    counter = counter + 1
result = counter
"""
        result = self.execute(source)
        assert result == 5
    
    def test_for_loop(self):
        """Test for loop execution"""
        source = """total = 0
for i in [1, 2, 3, 4, 5]:
    total = total + i
result = total
"""
        result = self.execute(source)
        assert result == 15
    
    def test_list_operations(self):
        """Test list creation and access"""
        source = """numbers = [10, 20, 30]
first = numbers[0]
second = numbers[1]
result = first + second
"""
        result = self.execute(source)
        assert result == 30
    
    def test_dict_operations(self):
        """Test dictionary creation and access"""
        source = """data = {"a": 1, "b": 2}
result = data["a"] + data["b"]
"""
        result = self.execute(source)
        assert result == 3
    
    def test_builtin_functions(self):
        """Test built-in functions"""
        source = """numbers = [1, 2, 3, 4, 5]
length = len(numbers)
total = sum(numbers)
result = length + total
"""
        result = self.execute(source)
        assert result == 20  # 5 + 15
    
    def test_recursion_fibonacci(self):
        """Test recursive function (Fibonacci)"""
        source = """function fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

result = fib(6)
"""
        result = self.execute(source)
        assert result == 8  # 6th Fibonacci number
    
    def test_logical_operators(self):
        """Test logical operators"""
        source = """a = true
b = false
result1 = a and b
result2 = a or b
result3 = not b
result = result2
"""
        result = self.execute(source)
        assert result == True
    
    def test_comparison_operators(self):
        """Test comparison operators"""
        source = """x = 10
y = 5
result = (x > y) and (y < 10)
"""
        result = self.execute(source)
        assert result == True
