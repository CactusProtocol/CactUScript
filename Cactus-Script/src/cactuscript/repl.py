"""
CactUScript REPL (Read-Eval-Print Loop)

Interactive shell for CactUScript.
"""

import sys
from typing import Optional
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .interpreter import Interpreter, RuntimeError as CactRuntimeError
from .vm import Compiler, VirtualMachine


BANNER = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██████╗ █████╗  ██████╗████████╗██╗   ██╗███████╗ ██████╗██████╗║
║  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔════╝██╔════╝██╔══██║
║  ██║     ███████║██║        ██║   ██║   ██║███████╗██║     ██████╔║
║  ██║     ██╔══██║██║        ██║   ██║   ██║╚════██║██║     ██╔══██║
║  ╚██████╗██║  ██║╚██████╗   ██║   ╚██████╔╝███████║╚██████╗██║  ██║
║   ╚═════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝
║                                                                   ║
║         CactUScript v0.1.0 - Cactus Protocol Language             ║
║    Designed for Decentralized Apps and Smart Contracts            ║
║                                                                   ║
║    Type 'help' for commands, 'exit' or Ctrl+C to quit             ║
╚═══════════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
CactUScript REPL Commands:
  help        - Show this help message
  exit/quit   - Exit the REPL
  clear       - Clear the screen
  reset       - Reset the interpreter state
  tokens      - Toggle token display mode
  ast         - Toggle AST display mode
  vm          - Switch to VM execution mode
  interp      - Switch to interpreter execution mode

Language Features:
  - Variables: let x = 10, const PI = 3.14
  - Functions: fn add(a, b) { return a + b }
  - Async: async fn fetch() { ... }
  - Structs: struct Point { x: int, y: int }
  - Contracts: contract Token { ... }
  - Control: if/elif/else, while, for...in
  - Operators: +, -, *, /, %, **, and, or, not

Built-in Functions:
  print, println, len, range, str, int, float,
  type, input, append, pop, keys, values,
  abs, min, max, sum
"""


class REPL:
    """Interactive CactUScript shell."""
    
    def __init__(self, use_vm: bool = False):
        self.interpreter = Interpreter()
        self.vm = VirtualMachine()
        self.use_vm = use_vm
        self.show_tokens = False
        self.show_ast = False
        self.multiline_buffer = []
        self.brace_count = 0
    
    def run(self):
        """Start the REPL."""
        print(BANNER)
        
        while True:
            try:
                line = self.get_input()
                if line is None:
                    continue
                
                result = self.execute(line)
                if result is not None:
                    print(f"=> {result}")
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except EOFError:
                print("\nGoodbye!")
                break
    
    def get_input(self) -> Optional[str]:
        """Get input from user, handling multi-line input."""
        try:
            if self.multiline_buffer:
                prompt = "... "
            else:
                prompt = ">>> "
            
            line = input(prompt)
            
            # Handle commands
            stripped = line.strip().lower()
            if not self.multiline_buffer:
                if stripped in ('exit', 'quit'):
                    raise EOFError()
                if stripped == 'help':
                    print(HELP_TEXT)
                    return None
                if stripped == 'clear':
                    print("\033[2J\033[H")  # ANSI clear screen
                    return None
                if stripped == 'reset':
                    self.interpreter = Interpreter()
                    print("Interpreter state reset.")
                    return None
                if stripped == 'tokens':
                    self.show_tokens = not self.show_tokens
                    print(f"Token display: {'ON' if self.show_tokens else 'OFF'}")
                    return None
                if stripped == 'ast':
                    self.show_ast = not self.show_ast
                    print(f"AST display: {'ON' if self.show_ast else 'OFF'}")
                    return None
                if stripped == 'vm':
                    self.use_vm = True
                    print("Switched to VM execution mode.")
                    return None
                if stripped == 'interp':
                    self.use_vm = False
                    print("Switched to interpreter execution mode.")
                    return None
            
            # Count braces for multi-line input
            self.brace_count += line.count('{') - line.count('}')
            self.multiline_buffer.append(line)
            
            if self.brace_count <= 0:
                complete_input = '\n'.join(self.multiline_buffer)
                self.multiline_buffer = []
                self.brace_count = 0
                return complete_input
            
            return None
            
        except EOFError:
            raise
    
    def execute(self, source: str) -> Optional[any]:
        """Execute CactUScript source code."""
        if not source.strip():
            return None
        
        try:
            # Tokenize
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            if self.show_tokens:
                print("Tokens:")
                for token in tokens:
                    print(f"  {token}")
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            if self.show_ast:
                print("AST:")
                self._print_ast(ast, indent=2)
            
            # Execute
            if self.use_vm:
                compiler = Compiler()
                bytecode = compiler.compile(ast)
                return self.vm.run(bytecode, compiler.constants)
            else:
                return self.interpreter.run(ast)
                
        except LexerError as e:
            print(f"Lexer Error: {e}")
        except ParserError as e:
            print(f"Parser Error: {e}")
        except CactRuntimeError as e:
            print(f"Runtime Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        
        return None
    
    def _print_ast(self, node, indent=0):
        """Pretty print an AST node."""
        prefix = " " * indent
        node_type = type(node).__name__
        
        if hasattr(node, '__dataclass_fields__'):
            print(f"{prefix}{node_type}:")
            for field_name, field_value in node.__dict__.items():
                if isinstance(field_value, list):
                    print(f"{prefix}  {field_name}: [")
                    for item in field_value:
                        if hasattr(item, '__dataclass_fields__'):
                            self._print_ast(item, indent + 4)
                        else:
                            print(f"{prefix}    {item}")
                    print(f"{prefix}  ]")
                elif hasattr(field_value, '__dataclass_fields__'):
                    print(f"{prefix}  {field_name}:")
                    self._print_ast(field_value, indent + 4)
                else:
                    print(f"{prefix}  {field_name}: {field_value}")
        else:
            print(f"{prefix}{node}")


def main():
    """Entry point for the REPL."""
    use_vm = '--vm' in sys.argv
    repl = REPL(use_vm=use_vm)
    repl.run()


if __name__ == "__main__":
    main()
