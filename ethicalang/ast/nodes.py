"""
Abstract Syntax Tree Node Definitions for EthicaLang

This module defines all AST node types used to represent parsed programs.
Each node type corresponds to a language construct.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def __repr__(self):
        pass


@dataclass
class Program(ASTNode):
    """Root node representing an entire program"""
    statements: List[ASTNode]
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


@dataclass
class Annotation(ASTNode):
    """Decorator/annotation (e.g., @requires_user_consent)"""
    name: str
    arguments: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        args = f"({', '.join(repr(a) for a in self.arguments)})" if self.arguments else ""
        return f"@{self.name}{args}"


@dataclass
class FunctionDef(ASTNode):
    """Function definition"""
    name: str
    parameters: List[str]
    body: List[ASTNode]
    annotations: List[Annotation] = field(default_factory=list)
    return_type: Optional[str] = None
    
    def __repr__(self):
        return f"FunctionDef({self.name}, params={self.parameters})"


@dataclass
class Assignment(ASTNode):
    """Variable assignment"""
    name: str
    value: ASTNode
    is_declaration: bool = True  # First assignment
    
    def __repr__(self):
        return f"Assignment({self.name} = {self.value})"


@dataclass
class Variable(ASTNode):
    """Variable reference"""
    name: str
    
    def __repr__(self):
        return f"Var({self.name})"


@dataclass
class BinaryOp(ASTNode):
    """Binary operation (e.g., a + b, x == y)"""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(ASTNode):
    """Unary operation (e.g., -x, not flag)"""
    operator: str
    operand: ASTNode
    
    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


@dataclass
class Literal(ASTNode):
    """Literal value (number, string, boolean, none)"""
    value: Any
    type_name: str  # 'int', 'float', 'string', 'bool', 'none'
    
    def __repr__(self):
        return f"Literal({self.type_name}:{repr(self.value)})"


@dataclass
class ListLiteral(ASTNode):
    """List literal [1, 2, 3]"""
    elements: List[ASTNode]
    
    def __repr__(self):
        return f"List([{', '.join(repr(e) for e in self.elements)}])"


@dataclass
class DictLiteral(ASTNode):
    """Dictionary literal {key: value}"""
    pairs: List[tuple[ASTNode, ASTNode]]
    
    def __repr__(self):
        items = ', '.join(f"{repr(k)}: {repr(v)}" for k, v in self.pairs)
        return f"Dict({{{items}}})"


@dataclass
class IfStatement(ASTNode):
    """Conditional statement"""
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None
    
    def __repr__(self):
        return f"If({self.condition})"


@dataclass
class WhileLoop(ASTNode):
    """While loop"""
    condition: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"While({self.condition})"


@dataclass
class ForLoop(ASTNode):
    """For loop (iterating over collections)"""
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"For({self.variable} in {self.iterable})"


@dataclass
class ReturnStatement(ASTNode):
    """Return statement"""
    value: Optional[ASTNode] = None
    
    def __repr__(self):
        return f"Return({self.value if self.value else 'void'})"


@dataclass
class FunctionCall(ASTNode):
    """Function call"""
    function: ASTNode  # Usually a Variable, but could be complex expression
    arguments: List[ASTNode]
    
    def __repr__(self):
        args = ', '.join(repr(a) for a in self.arguments)
        return f"Call({self.function}({args}))"


@dataclass
class MemberAccess(ASTNode):
    """Member access (e.g., obj.field)"""
    object: ASTNode
    member: str
    
    def __repr__(self):
        return f"MemberAccess({self.object}.{self.member})"


@dataclass
class IndexAccess(ASTNode):
    """Index access (e.g., list[0])"""
    object: ASTNode
    index: ASTNode
    
    def __repr__(self):
        return f"IndexAccess({self.object}[{self.index}])"


# Visitor pattern for AST traversal
class ASTVisitor(ABC):
    """
    Base class for AST visitors
    Implements the visitor pattern for tree traversal
    """
    
    def visit(self, node: ASTNode):
        """Dispatch to appropriate visit method"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        """Default visit method"""
        raise NotImplementedError(f"No visit method for {node.__class__.__name__}")
    
    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: FunctionDef):
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_Assignment(self, node: Assignment):
        self.visit(node.value)
    
    def visit_Variable(self, node: Variable):
        pass
    
    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        self.visit(node.operand)
    
    def visit_Literal(self, node: Literal):
        pass
    
    def visit_ListLiteral(self, node: ListLiteral):
        for elem in node.elements:
            self.visit(elem)
    
    def visit_DictLiteral(self, node: DictLiteral):
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
    
    def visit_IfStatement(self, node: IfStatement):
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
    
    def visit_WhileLoop(self, node: WhileLoop):
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ForLoop(self, node: ForLoop):
        self.visit(node.iterable)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        if node.value:
            self.visit(node.value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        self.visit(node.function)
        for arg in node.arguments:
            self.visit(arg)
    
    def visit_MemberAccess(self, node: MemberAccess):
        self.visit(node.object)
    
    def visit_IndexAccess(self, node: IndexAccess):
        self.visit(node.object)
        self.visit(node.index)
    
    def visit_Annotation(self, node: Annotation):
        for arg in node.arguments:
            self.visit(arg)
