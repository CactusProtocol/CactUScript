"""
CactUScript - A Programming Language for the Cactus Protocol

CactUScript is designed for decentralized applications (dApps) and smart contracts.

Philosophy:
- Security: Minimizing common errors related to memory manipulation and overflow
- Concurrency: Built-in support for asynchronous and parallel processing
- Simplicity: Syntax similar to Python and TypeScript for easier adoption
"""

__version__ = "0.1.0"
__author__ = "Cactus Protocol"

from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .ast_nodes import *
from .interpreter import Interpreter
from .vm import VirtualMachine

__all__ = [
    "Lexer",
    "Token", 
    "TokenType",
    "Parser",
    "Interpreter",
    "VirtualMachine",
]
