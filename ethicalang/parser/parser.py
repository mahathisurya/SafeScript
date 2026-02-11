"""
Recursive Descent Parser for EthicaLang

Converts a stream of tokens into an Abstract Syntax Tree (AST).
Implements a hand-written recursive descent parser without external tools.
"""

from typing import List, Optional
from ..lexer.lexer import Token, TokenType
from ..ast.nodes import *


class ParseError(Exception):
    """Exception raised when parsing fails"""
    pass


class Parser:
    """
    Recursive descent parser for EthicaLang
    
    Grammar Overview:
        program         → statement*
        statement       → function_def | if_stmt | while_loop | for_loop | return_stmt | assignment | expr_stmt
        function_def    → annotation* 'function' ID '(' params? ')' ':' block
        if_stmt         → 'if' expression ':' block ('else' ':' block)?
        while_loop      → 'while' expression ':' block
        for_loop        → 'for' ID 'in' expression ':' block
        return_stmt     → 'return' expression?
        assignment      → ID '=' expression
        expression      → logical_or
        logical_or      → logical_and ('or' logical_and)*
        logical_and     → equality ('and' equality)*
        equality        → comparison (('==' | '!=') comparison)*
        comparison      → term (('<' | '<=' | '>' | '>=') term)*
        term            → factor (('+' | '-') factor)*
        factor          → unary (('*' | '/' | '%') unary)*
        unary           → ('not' | '-') unary | power
        power           → postfix ('**' postfix)*
        postfix         → primary (call | index | member)*
        primary         → literal | ID | '(' expression ')' | list | dict
    """
    
    def __init__(self, tokens: List[Token]):
        """Initialize parser with token stream"""
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
    
    def error(self, message: str):
        """Raise a parse error with context"""
        if self.current_token:
            raise ParseError(
                f"Parse error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        else:
            raise ParseError(f"Parse error: {message}")
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at tokens without consuming them"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Token:
        """Move to the next token"""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        if self.current_token is None:
            return False
        return self.current_token.type in token_types
    
    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consume a token of the expected type or raise error"""
        if not self.match(token_type):
            if message:
                self.error(message)
            else:
                self.error(f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}")
        return self.advance()
    
    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        """Parse the entire program"""
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        self.skip_newlines()
        
        # Annotations (for functions)
        annotations = []
        while self.match(TokenType.AT):
            annotations.append(self.parse_annotation())
            self.skip_newlines()
        
        # Function definition
        if self.match(TokenType.FUNCTION):
            return self.parse_function_def(annotations)
        
        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        
        # While loop
        if self.match(TokenType.WHILE):
            return self.parse_while_loop()
        
        # For loop
        if self.match(TokenType.FOR):
            return self.parse_for_loop()
        
        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        
        # Assignment or expression statement
        if self.match(TokenType.IDENTIFIER):
            # Look ahead to check for assignment
            if self.peek(1) and self.peek(1).type == TokenType.ASSIGN:
                return self.parse_assignment()
        
        # Expression statement (function call, etc.)
        expr = self.parse_expression()
        self.skip_newlines()
        return expr
    
    def parse_annotation(self) -> Annotation:
        """Parse an annotation (@decorator)"""
        self.consume(TokenType.AT)
        name_token = self.consume(TokenType.IDENTIFIER, "Expected annotation name")
        name = name_token.value
        
        arguments = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.parse_expression())
            self.consume(TokenType.RPAREN)
        
        return Annotation(name, arguments)
    
    def parse_function_def(self, annotations: List[Annotation] = None) -> FunctionDef:
        """Parse a function definition"""
        self.consume(TokenType.FUNCTION)
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value
        
        self.consume(TokenType.LPAREN)
        parameters = []
        if not self.match(TokenType.RPAREN):
            param_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
            parameters.append(param_token.value)
            while self.match(TokenType.COMMA):
                self.advance()
                param_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
                parameters.append(param_token.value)
        self.consume(TokenType.RPAREN)
        
        self.consume(TokenType.COLON, "Expected ':' after function signature")
        body = self.parse_block()
        
        return FunctionDef(name, parameters, body, annotations or [])
    
    def parse_block(self) -> List[ASTNode]:
        """Parse a block of statements (indented)"""
        self.skip_newlines()
        self.consume(TokenType.INDENT, "Expected indented block")
        
        statements = []
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.consume(TokenType.DEDENT, "Expected dedent")
        return statements
    
    def parse_if_statement(self) -> IfStatement:
        """Parse an if statement"""
        self.consume(TokenType.IF)
        condition = self.parse_expression()
        self.consume(TokenType.COLON)
        then_body = self.parse_block()
        
        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.consume(TokenType.COLON)
            else_body = self.parse_block()
        
        return IfStatement(condition, then_body, else_body)
    
    def parse_while_loop(self) -> WhileLoop:
        """Parse a while loop"""
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.COLON)
        body = self.parse_block()
        
        return WhileLoop(condition, body)
    
    def parse_for_loop(self) -> ForLoop:
        """Parse a for loop"""
        self.consume(TokenType.FOR)
        var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable")
        variable = var_token.value
        self.consume(TokenType.IN, "Expected 'in' keyword")
        iterable = self.parse_expression()
        self.consume(TokenType.COLON)
        body = self.parse_block()
        
        return ForLoop(variable, iterable, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse a return statement"""
        self.consume(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_assignment(self) -> Assignment:
        """Parse an assignment statement"""
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value
        self.consume(TokenType.ASSIGN)
        value = self.parse_expression()
        
        return Assignment(name, value)
    
    def parse_expression(self) -> ASTNode:
        """Parse an expression"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOp(left, 'or', right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left, 'and', right)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality comparison"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression"""
        left = self.parse_term()
        
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.advance().value
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_term(self) -> ASTNode:
        """Parse addition/subtraction"""
        left = self.parse_factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_factor(self) -> ASTNode:
        """Parse multiplication/division/modulo"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary operations"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_power()
    
    def parse_power(self) -> ASTNode:
        """Parse power operation"""
        left = self.parse_postfix()
        
        if self.match(TokenType.POWER):
            op = self.advance().value
            right = self.parse_power()  # Right associative
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix operations (function call, member access, indexing)"""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                self.advance()
                arguments = []
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.parse_expression())
                self.consume(TokenType.RPAREN)
                expr = FunctionCall(expr, arguments)
            
            elif self.match(TokenType.LBRACKET):
                # Index access
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            
            elif self.match(TokenType.DOT):
                # Member access
                self.advance()
                member_token = self.consume(TokenType.IDENTIFIER, "Expected member name")
                expr = MemberAccess(expr, member_token.value)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (literals, variables, parenthesized expressions)"""
        
        # Literals
        if self.match(TokenType.INTEGER):
            token = self.advance()
            return Literal(token.value, 'int')
        
        if self.match(TokenType.FLOAT):
            token = self.advance()
            return Literal(token.value, 'float')
        
        if self.match(TokenType.STRING):
            token = self.advance()
            return Literal(token.value, 'string')
        
        if self.match(TokenType.TRUE, TokenType.FALSE):
            token = self.advance()
            return Literal(token.value, 'bool')
        
        if self.match(TokenType.NONE):
            self.advance()
            return Literal(None, 'none')
        
        # Variable
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Variable(token.value)
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # List literal
        if self.match(TokenType.LBRACKET):
            return self.parse_list_literal()
        
        # Dict literal
        if self.match(TokenType.LBRACE):
            return self.parse_dict_literal()
        
        self.error(f"Unexpected token: {self.current_token.type.name if self.current_token else 'EOF'}")
    
    def parse_list_literal(self) -> ListLiteral:
        """Parse a list literal"""
        self.consume(TokenType.LBRACKET)
        elements = []
        
        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RBRACKET):  # Trailing comma
                    break
                elements.append(self.parse_expression())
        
        self.consume(TokenType.RBRACKET)
        return ListLiteral(elements)
    
    def parse_dict_literal(self) -> DictLiteral:
        """Parse a dictionary literal"""
        self.consume(TokenType.LBRACE)
        pairs = []
        
        if not self.match(TokenType.RBRACE):
            key = self.parse_expression()
            self.consume(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RBRACE):  # Trailing comma
                    break
                key = self.parse_expression()
                self.consume(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
        
        self.consume(TokenType.RBRACE)
        return DictLiteral(pairs)
