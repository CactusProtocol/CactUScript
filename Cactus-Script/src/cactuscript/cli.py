"""
CactUScript Command Line Interface

Provides command-line tools for running CactUScript files.
"""

import argparse
import sys
from pathlib import Path
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .interpreter import Interpreter, RuntimeError as CactRuntimeError
from .vm import Compiler, VirtualMachine
from .repl import REPL


def run_file(filepath: str, use_vm: bool = False, show_tokens: bool = False, 
             show_ast: bool = False, show_bytecode: bool = False):
    """Run a CactUScript file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    if not path.suffix in ['.cact', '.cactus', '.cus']:
        print(f"Warning: File does not have a CactUScript extension (.cact, .cactus, .cus)")
    
    try:
        source = path.read_text()
        
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if show_tokens:
            print("=== Tokens ===")
            for token in tokens:
                print(f"  {token}")
            print()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        if show_ast:
            print("=== AST ===")
            print(ast)
            print()
        
        # Execute
        if use_vm:
            compiler = Compiler()
            bytecode = compiler.compile(ast)
            
            if show_bytecode:
                print("=== Bytecode ===")
                for i, instr in enumerate(bytecode):
                    print(f"  {i:04d}: {instr}")
                print()
            
            vm = VirtualMachine()
            result = vm.run(bytecode, compiler.constants)
        else:
            interpreter = Interpreter()
            result = interpreter.run(ast)
        
        if result is not None:
            print(result)
            
    except LexerError as e:
        print(f"Lexer Error in {filepath}:")
        print(f"  {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"Parser Error in {filepath}:")
        print(f"  {e}")
        sys.exit(1)
    except CactRuntimeError as e:
        print(f"Runtime Error in {filepath}:")
        print(f"  {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog='cactuscript',
        description='CactUScript - A programming language for the Cactus Protocol'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='CactUScript file to run (.cact, .cactus, .cus)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='CactUScript 0.1.0'
    )
    
    parser.add_argument(
        '--vm',
        action='store_true',
        help='Use bytecode VM instead of tree-walking interpreter'
    )
    
    parser.add_argument(
        '--tokens',
        action='store_true',
        help='Display tokenized output'
    )
    
    parser.add_argument(
        '--ast',
        action='store_true',
        help='Display AST'
    )
    
    parser.add_argument(
        '--bytecode',
        action='store_true',
        help='Display compiled bytecode (requires --vm)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive REPL'
    )
    
    args = parser.parse_args()
    
    if args.interactive or args.file is None:
        repl = REPL(use_vm=args.vm)
        repl.run()
    else:
        run_file(
            args.file,
            use_vm=args.vm,
            show_tokens=args.tokens,
            show_ast=args.ast,
            show_bytecode=args.bytecode
        )


if __name__ == "__main__":
    main()
