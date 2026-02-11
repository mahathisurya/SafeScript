"""
Lexer for EthicaLang

Converts source code text into a stream of tokens for parsing.
Implements a hand-written scanner with lookahead capabilities.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for EthicaLang"""
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    FUNCTION = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()
    
    # Comparison
    EQ = auto()          # ==
    NE = auto()          # !=
    LT = auto()          # <
    LE = auto()          # <=
    GT = auto()          # >
    GE = auto()          # >=
    
    # Assignment
    ASSIGN = auto()      # =
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COMMA = auto()       # ,
    COLON = auto()       # :
    ARROW = auto()       # ->
    DOT = auto()         # .
    AT = auto()          # @ (for annotations)
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single token in the source code"""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


class Lexer:
    """
    Lexical analyzer for EthicaLang
    
    Features:
    - Python-like indentation handling
    - Lookahead support
    - Detailed error reporting with line/column information
    """
    
    KEYWORDS = {
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'none': TokenType.NONE,
    }
    
    def __init__(self, source: str):
        """Initialize lexer with source code"""
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]  # Track indentation levels
        
    def error(self, message: str):
        """Raise a lexer error with position information"""
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")
    
    def current_char(self) -> Optional[str]:
        """Get the current character without advancing"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead at a character without advancing"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Move to the next character"""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
            
        return char
    
    def skip_whitespace(self, skip_newlines: bool = True):
        """Skip whitespace characters"""
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
        
        if skip_newlines:
            while self.current_char() and self.current_char() in '\r\n':
                self.advance()
                self.skip_whitespace(skip_newlines=False)
    
    def skip_comment(self):
        """Skip single-line comments starting with #"""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self) -> str:
        """Read a string literal"""
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote_char:
                    value += quote_char
                else:
                    value += escape_char
                self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() != quote_char:
            self.error(f"Unterminated string literal")
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> Token:
        """Read a numeric literal (integer or float)"""
        start_line = self.line
        start_col = self.column
        
        num_str = ""
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        if has_dot:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_col)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start_line = self.line
        start_col = self.column
        
        ident = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            ident += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(ident, TokenType.IDENTIFIER)
        
        # Set value based on token type
        if token_type in (TokenType.TRUE, TokenType.FALSE):
            value = (token_type == TokenType.TRUE)
        elif token_type == TokenType.NONE:
            value = None
        else:
            value = ident
        
        return Token(token_type, value, start_line, start_col)
    
    def handle_indentation(self, indent_level: int):
        """Generate INDENT/DEDENT tokens based on indentation changes"""
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, None, self.line, 1))
        elif indent_level < current_indent:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, None, self.line, 1))
            
            if not self.indent_stack or self.indent_stack[-1] != indent_level:
                self.error(f"Inconsistent indentation")
    
    def tokenize(self) -> List[Token]:
        """
        Convert source code into a list of tokens
        
        Returns:
            List of tokens including INDENT/DEDENT tokens for Python-like syntax
        """
        at_line_start = True
        
        while self.pos < len(self.source):
            # Handle indentation at start of line
            if at_line_start:
                indent_level = 0
                while self.current_char() in ' \t':
                    if self.current_char() == ' ':
                        indent_level += 1
                    else:  # tab
                        indent_level += 4
                    self.advance()
                
                # Skip blank lines and comments
                if self.current_char() in '\r\n' or self.current_char() == '#':
                    self.skip_comment()
                    if self.current_char() in '\r\n':
                        self.advance()
                    continue
                
                # Handle indentation changes
                if self.current_char() is not None:
                    self.handle_indentation(indent_level)
                    at_line_start = False
                continue
            
            # Skip whitespace (but not newlines)
            if self.current_char() in ' \t':
                self.skip_whitespace(skip_newlines=False)
                continue
            
            # Skip comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Handle newlines
            if self.current_char() in '\r\n':
                start_line = self.line
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_col))
                at_line_start = True
                continue
            
            start_line = self.line
            start_col = self.column
            char = self.current_char()
            
            # String literals
            if char in '"\'':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
            
            # Numbers
            elif char.isdigit():
                self.tokens.append(self.read_number())
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            
            # Operators and delimiters
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            
            elif char == '-':
                self.advance()
                if self.current_char() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            
            elif char == '*':
                self.advance()
                if self.current_char() == '*':
                    self.advance()
                    self.tokens.append(Token(TokenType.POWER, '**', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
            
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
            
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
            
            elif char == '=':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            
            elif char == '!':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', start_line, start_col))
                else:
                    self.error(f"Unexpected character '!'")
            
            elif char == '<':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            
            elif char == '>':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
            
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
            
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
            
            elif char == '.':
                self.advance()
                # Check if it's part of a number
                if self.current_char() and self.current_char().isdigit():
                    self.error("Numbers must start with a digit")
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
            
            elif char == '@':
                self.advance()
                self.tokens.append(Token(TokenType.AT, '@', start_line, start_col))
            
            else:
                self.error(f"Unexpected character '{char}'")
        
        # Add remaining DEDENT tokens
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.column))
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens
