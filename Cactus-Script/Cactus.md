# CactUScript - Cactus Protocol Programming Language

## Overview

CactUScript is a custom programming language designed for decentralized applications (dApps) and smart contracts within the Solana ecosystem. The project implements a complete language toolchain including lexer, parser, interpreter, bytecode compiler, and virtual machine.

The language emphasizes:
- **Security**: Minimizing common errors related to memory manipulation and overflow
- **Concurrency**: Built-in async/await support for parallel processing
- **Simplicity**: Python/TypeScript-like syntax for easier adoption

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Language Implementation Pipeline

The project follows a traditional compiler/interpreter architecture:

1. **Lexer** (`src/cactuscript/lexer.py`) - Converts source code into a stream of tokens
2. **Parser** (`src/cactuscript/parser.py`) - Transforms tokens into an Abstract Syntax Tree (AST)
3. **Execution** - Two backends available:
   - **Tree-walking Interpreter** (`src/cactuscript/interpreter.py`) - Directly walks and executes the AST
   - **Bytecode VM** (`src/cactuscript/vm.py`) - Compiles AST to bytecode, then executes on a stack-based virtual machine

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Token Definitions | `tokens.py` | Defines all token types and keywords |
| Lexer | `lexer.py` | Source code → Token stream |
| AST Nodes | `ast_nodes.py` | Data classes representing syntax tree nodes |
| Parser | `parser.py` | Token stream → AST |
| Interpreter | `interpreter.py` | Direct AST execution with environment-based scoping |
| Virtual Machine | `vm.py` | Bytecode compilation and stack-based execution |
| REPL | `repl.py` | Interactive shell with debugging commands |
| CLI | `cli.py` | Command-line interface for running `.cact` files |

### Execution Mode Trade-offs

- **Interpreter Mode**: Better for debugging, clearer error messages, slower execution
- **VM Mode**: Better performance through bytecode compilation, stack-based execution model

### Language Features

- Variable declarations (`let`, `const`)
- Functions (`fn`, `async fn`)
- Control flow (`if/elif/else`, `while`, `for...in`, `break`, `continue`)
- Structs and contracts for Solana smart contract development
- Built-in type system (`int`, `float`, `string`, `bool`, `void`)

### Entry Points

- `main.py` - Primary entry point, routes to REPL or file execution
- File extensions supported: `.cact`, `.cactus`, `.cus`

## External Dependencies

### Runtime Dependencies

- **Python 3.x** - The implementation language
- **asyncio** (standard library) - Used for async/await execution support

### No External Services

This is a self-contained language implementation with no database, external API, or third-party service dependencies. All functionality is implemented in pure Python.