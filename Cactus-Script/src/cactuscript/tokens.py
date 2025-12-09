"""
CactUScript Token Definitions

Defines all token types used by the lexer to tokenize CactUScript source code.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    
    # Keywords - Control Flow
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    
    # Keywords - Declarations
    LET = auto()
    CONST = auto()
    FN = auto()
    ASYNC = auto()
    AWAIT = auto()
    CONTRACT = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPL = auto()
    
    # Keywords - Types
    TYPE_INT = auto()
    TYPE_FLOAT = auto()
    TYPE_STRING = auto()
    TYPE_BOOL = auto()
    TYPE_VOID = auto()
    TYPE_LIST = auto()
    TYPE_MAP = auto()
    
    # Keywords - Special
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    EMIT = auto()
    EVENT = auto()
    
    # Operators - Arithmetic
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **
    
    # Operators - Comparison
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS = auto()           # <
    GREATER = auto()        # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    
    # Operators - Assignment
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    MULTIPLY_ASSIGN = auto() # *=
    DIVIDE_ASSIGN = auto()  # /=
    
    # Operators - Bitwise
    BIT_AND = auto()        # &
    BIT_OR = auto()         # |
    BIT_XOR = auto()        # ^
    BIT_NOT = auto()        # ~
    LEFT_SHIFT = auto()     # <<
    RIGHT_SHIFT = auto()    # >>
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    COMMA = auto()          # ,
    DOT = auto()            # .
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    ARROW = auto()          # ->
    FAT_ARROW = auto()      # =>
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    """Represents a token in CactUScript source code."""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"


KEYWORDS = {
    # Control Flow
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return": TokenType.RETURN,
    
    # Declarations
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "contract": TokenType.CONTRACT,
    "struct": TokenType.STRUCT,
    "enum": TokenType.ENUM,
    "impl": TokenType.IMPL,
    
    # Types
    "int": TokenType.TYPE_INT,
    "float": TokenType.TYPE_FLOAT,
    "string": TokenType.TYPE_STRING,
    "bool": TokenType.TYPE_BOOL,
    "void": TokenType.TYPE_VOID,
    "list": TokenType.TYPE_LIST,
    "map": TokenType.TYPE_MAP,
    
    # Boolean/Null
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "none": TokenType.NONE,
    
    # Logical
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    
    # Events
    "emit": TokenType.EMIT,
    "event": TokenType.EVENT,
}
