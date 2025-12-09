# CactUScript - Cactus Protocol Programming Language

## Overview

CactUScript is a custom programming language designed for decentralized applications (dApps) and smart contracts within the Solana ecosystem. The project implements a complete language toolchain including a lexer, parser, AST representation, tree-walking interpreter, bytecode virtual machine, and interactive REPL.

The language philosophy emphasizes:
- **Security**: Minimizing memory manipulation and overflow errors
- **Concurrency**: Built-in async/await support for parallel processing
- **Simplicity**: Python/TypeScript-like syntax for easier adoption

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Language Implementation Pipeline

The project follows a traditional compiler/interpreter architecture with these stages:

1. **Lexer** (`lexer.py`) - Tokenizes source code into a stream of tokens
2. **Parser** (`parser.py`) - Converts tokens into an Abstract Syntax Tree (AST)
3. **Execution** - Two execution modes available:
   - **Tree-walking Interpreter** (`interpreter.py`) - Direct AST interpretation
   - **Bytecode VM** (`vm.py`) - Compiles AST to bytecode then executes

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Token Definitions | `tokens.py` | Defines all token types and keywords |
| Lexer | `lexer.py` | Source code → Token stream |
| AST Nodes | `ast_nodes.py` | Data classes for syntax tree nodes |
| Parser | `parser.py` | Token stream → AST |
| Interpreter | `interpreter.py` | Direct AST execution with environment scoping |
| Virtual Machine | `vm.py` | Bytecode compilation and stack-based execution |
| REPL | `repl.py` | Interactive shell with command support |
| CLI | `cli.py` | Command-line interface for running files |

### Execution Modes

The system supports two execution backends:
- **Interpreter Mode**: Easier to debug, better error messages, slower execution
- **VM Mode**: Better performance through bytecode compilation, stack-based execution

### Language Features

- Variable declarations (`let`, `const`)
- Functions (`fn`, `async fn`)
- Control flow (`if/elif/else`, `while`, `for...in`)
- Data structures (`struct`, `contract`)
- Type annotations (`int`, `float`, `string`, `bool`, `list`, `map`, `void`)
- Async/await patterns for concurrency

### File Extensions

The language recognizes `.cact`, `.cactus`, and `.cus` file extensions.

## External Dependencies

### Runtime Dependencies

- **Python 3.x** - The implementation language
- **asyncio** (stdlib) - Used for async/await execution in the interpreter

### No External Services

This is a self-contained language implementation with no external databases, APIs, or third-party services. All functionality runs locally through the Python runtime.

### Development Pattern

Entry point is `main.py` which adds `src/` to the Python path and delegates to the CLI module. The package is structured under `src/cactuscript/` for clean imports.