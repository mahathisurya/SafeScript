"""
Tests for the lexer module
"""

import pytest
from ethicalang.lexer.lexer import Lexer, TokenType


class TestLexer:
    """Test cases for the lexer"""
    
    def test_simple_tokens(self):
        """Test basic token recognition"""
        source = "123 + 456"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 123
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.INTEGER
        assert tokens[2].value == 456
    
    def test_string_literals(self):
        """Test string literal tokenization"""
        source = '"hello world"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
    
    def test_keywords(self):
        """Test keyword recognition"""
        source = "function if else while for return"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.FUNCTION
        assert tokens[2].type == TokenType.IF
        assert tokens[4].type == TokenType.ELSE
        assert tokens[6].type == TokenType.WHILE
        assert tokens[8].type == TokenType.FOR
        assert tokens[10].type == TokenType.RETURN
    
    def test_identifiers(self):
        """Test identifier tokenization"""
        source = "variable_name another_var x"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "variable_name"
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "another_var"
    
    def test_operators(self):
        """Test operator tokenization"""
        source = "+ - * / == != < > <= >="
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.PLUS
        assert tokens[2].type == TokenType.MINUS
        assert tokens[4].type == TokenType.MULTIPLY
        assert tokens[6].type == TokenType.DIVIDE
        assert tokens[8].type == TokenType.EQ
        assert tokens[10].type == TokenType.NE
    
    def test_indentation(self):
        """Test indentation handling"""
        source = """function test():
    x = 1
    y = 2
"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should have INDENT and DEDENT tokens
        indent_tokens = [t for t in tokens if t.type == TokenType.INDENT]
        dedent_tokens = [t for t in tokens if t.type == TokenType.DEDENT]
        
        assert len(indent_tokens) == 1
        assert len(dedent_tokens) == 1
    
    def test_comments(self):
        """Test comment handling"""
        source = """# This is a comment
x = 5  # Inline comment
"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Comments should be skipped
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        assert len(identifiers) == 1
        assert identifiers[0].value == "x"
    
    def test_annotation_symbol(self):
        """Test @ symbol for annotations"""
        source = "@decorator"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.AT
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "decorator"
