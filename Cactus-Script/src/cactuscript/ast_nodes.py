"""
CactUScript Abstract Syntax Tree (AST) Node Definitions

Defines all AST node types that represent the structure of CactUScript programs.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass


class Expression(ASTNode):
    """Base class for expression nodes."""
    pass


class Statement(ASTNode):
    """Base class for statement nodes."""
    pass


# ============================================================================
# Literal Expressions
# ============================================================================

@dataclass
class IntegerLiteral(Expression):
    value: int


@dataclass
class FloatLiteral(Expression):
    value: float


@dataclass
class StringLiteral(Expression):
    value: str


@dataclass
class BooleanLiteral(Expression):
    value: bool


@dataclass
class NullLiteral(Expression):
    pass


@dataclass
class ListLiteral(Expression):
    elements: List[Expression]


@dataclass
class MapLiteral(Expression):
    pairs: List[tuple]  # List of (key, value) tuples


# ============================================================================
# Identifier and Access Expressions
# ============================================================================

@dataclass
class Identifier(Expression):
    name: str


@dataclass
class MemberAccess(Expression):
    object: Expression
    member: str


@dataclass
class IndexAccess(Expression):
    object: Expression
    index: Expression


# ============================================================================
# Operator Expressions
# ============================================================================

@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression


@dataclass
class ComparisonOp(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class LogicalOp(Expression):
    left: Expression
    operator: str  # 'and', 'or'
    right: Expression


# ============================================================================
# Function and Call Expressions
# ============================================================================

@dataclass
class FunctionCall(Expression):
    function: Expression
    arguments: List[Expression]


@dataclass
class MethodCall(Expression):
    object: Expression
    method: str
    arguments: List[Expression]


@dataclass
class LambdaExpression(Expression):
    parameters: List[str]
    body: Expression


# ============================================================================
# Async Expressions
# ============================================================================

@dataclass
class AwaitExpression(Expression):
    expression: Expression


# ============================================================================
# Statements
# ============================================================================

@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class VariableDeclaration(Statement):
    name: str
    type_annotation: Optional[str]
    value: Optional[Expression]
    is_const: bool = False


@dataclass
class Assignment(Statement):
    target: Expression
    operator: str  # '=', '+=', '-=', etc.
    value: Expression


@dataclass
class Block(Statement):
    statements: List[Statement]


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Block
    elif_branches: List[tuple] = field(default_factory=list)  # List of (condition, block)
    else_branch: Optional[Block] = None


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Block


@dataclass
class ForStatement(Statement):
    variable: str
    iterable: Expression
    body: Block


@dataclass
class BreakStatement(Statement):
    pass


@dataclass
class ContinueStatement(Statement):
    pass


@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]


# ============================================================================
# Function and Type Declarations
# ============================================================================

@dataclass
class Parameter:
    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[Expression] = None


@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: List[Parameter]
    return_type: Optional[str]
    body: Block
    is_async: bool = False


@dataclass
class StructDeclaration(Statement):
    name: str
    fields: List[tuple]  # List of (name, type) tuples
    methods: List[FunctionDeclaration] = field(default_factory=list)


@dataclass
class EnumDeclaration(Statement):
    name: str
    variants: List[str]


# ============================================================================
# Smart Contract Declarations (Solana-specific)
# ============================================================================

@dataclass
class ContractDeclaration(Statement):
    name: str
    body: Block
    events: List['EventDeclaration'] = field(default_factory=list)


@dataclass
class EventDeclaration(Statement):
    name: str
    fields: List[tuple]  # List of (name, type) tuples


@dataclass
class EmitStatement(Statement):
    event_name: str
    arguments: List[Expression]


# ============================================================================
# Implementation Block
# ============================================================================

@dataclass
class ImplBlock(Statement):
    type_name: str
    methods: List[FunctionDeclaration]


# ============================================================================
# Program (Root Node)
# ============================================================================

@dataclass
class Program(ASTNode):
    statements: List[Statement]
