"""
CactUScript Virtual Machine

A bytecode-based virtual machine for executing CactUScript programs.
This provides better performance than the tree-walking interpreter.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Dict, Optional
from .ast_nodes import *


class OpCode(Enum):
    """Virtual machine opcodes."""
    # Stack operations
    PUSH = auto()
    POP = auto()
    DUP = auto()
    
    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    NEG = auto()
    
    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Bitwise
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    SHL = auto()
    SHR = auto()
    
    # Variables
    LOAD = auto()
    STORE = auto()
    LOAD_CONST = auto()
    DEFINE = auto()
    
    # Control flow
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    JUMP_IF_TRUE = auto()
    LOOP = auto()
    
    # Functions
    CALL = auto()
    RETURN = auto()
    
    # Collections
    BUILD_LIST = auto()
    BUILD_MAP = auto()
    INDEX = auto()
    STORE_INDEX = auto()
    
    # Objects
    GET_ATTR = auto()
    SET_ATTR = auto()
    
    # Special
    PRINT = auto()
    HALT = auto()
    NOP = auto()


@dataclass
class Instruction:
    """Represents a VM instruction."""
    opcode: OpCode
    operand: Any = None
    
    def __repr__(self):
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name


@dataclass
class CompiledFunction:
    """Represents a compiled function."""
    name: str
    params: List[str]
    code: List[Instruction]
    num_locals: int


class Compiler:
    """
    Compiles CactUScript AST to bytecode.
    """
    
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.constants: List[Any] = []
        self.functions: Dict[str, CompiledFunction] = {}
        self.locals: Dict[str, int] = {}
        self.local_count = 0
        self.loop_starts: List[int] = []
        self.loop_ends: List[List[int]] = []
    
    def compile(self, program: Program) -> List[Instruction]:
        """Compile a program to bytecode."""
        for stmt in program.statements:
            self.compile_statement(stmt)
        self.emit(OpCode.HALT)
        return self.instructions
    
    def emit(self, opcode: OpCode, operand: Any = None) -> int:
        """Emit an instruction."""
        self.instructions.append(Instruction(opcode, operand))
        return len(self.instructions) - 1
    
    def patch_jump(self, address: int, target: int):
        """Patch a jump instruction with the correct target."""
        self.instructions[address].operand = target
    
    def add_constant(self, value: Any) -> int:
        """Add a constant and return its index."""
        self.constants.append(value)
        return len(self.constants) - 1
    
    def get_local(self, name: str) -> int:
        """Get or create a local variable slot."""
        if name not in self.locals:
            self.locals[name] = self.local_count
            self.local_count += 1
        return self.locals[name]
    
    # ========================================================================
    # Statement Compilation
    # ========================================================================
    
    def compile_statement(self, stmt: Statement):
        """Compile a statement."""
        method_name = f"compile_{type(stmt).__name__}"
        method = getattr(self, method_name, self.compile_default)
        method(stmt)
    
    def compile_default(self, node):
        raise RuntimeError(f"Cannot compile: {type(node).__name__}")
    
    def compile_ExpressionStatement(self, stmt: ExpressionStatement):
        self.compile_expression(stmt.expression)
        self.emit(OpCode.POP)
    
    def compile_VariableDeclaration(self, stmt: VariableDeclaration):
        if stmt.value:
            self.compile_expression(stmt.value)
        else:
            self.emit(OpCode.PUSH, None)
        
        slot = self.get_local(stmt.name)
        self.emit(OpCode.DEFINE, (stmt.name, slot))
    
    def compile_Assignment(self, stmt: Assignment):
        if isinstance(stmt.target, Identifier):
            if stmt.operator == "=":
                self.compile_expression(stmt.value)
            else:
                self.emit(OpCode.LOAD, stmt.target.name)
                self.compile_expression(stmt.value)
                self._emit_compound_op(stmt.operator)
            self.emit(OpCode.STORE, stmt.target.name)
        
        elif isinstance(stmt.target, IndexAccess):
            self.compile_expression(stmt.target.object)
            self.compile_expression(stmt.target.index)
            if stmt.operator == "=":
                self.compile_expression(stmt.value)
            else:
                self.emit(OpCode.DUP)
                self.emit(OpCode.DUP)
                self.emit(OpCode.INDEX)
                self.compile_expression(stmt.value)
                self._emit_compound_op(stmt.operator)
            self.emit(OpCode.STORE_INDEX)
    
    def _emit_compound_op(self, op: str):
        ops = {
            "+=": OpCode.ADD,
            "-=": OpCode.SUB,
            "*=": OpCode.MUL,
            "/=": OpCode.DIV,
        }
        if op in ops:
            self.emit(ops[op])
    
    def compile_Block(self, block: Block):
        for stmt in block.statements:
            self.compile_statement(stmt)
    
    def compile_IfStatement(self, stmt: IfStatement):
        self.compile_expression(stmt.condition)
        
        jump_if_false = self.emit(OpCode.JUMP_IF_FALSE, 0)
        self.compile_Block(stmt.then_branch)
        
        jump_to_end = self.emit(OpCode.JUMP, 0)
        self.patch_jump(jump_if_false, len(self.instructions))
        
        for condition, block in stmt.elif_branches:
            self.compile_expression(condition)
            elif_jump = self.emit(OpCode.JUMP_IF_FALSE, 0)
            self.compile_Block(block)
            jump_to_end_elif = self.emit(OpCode.JUMP, 0)
            self.patch_jump(elif_jump, len(self.instructions))
        
        if stmt.else_branch:
            self.compile_Block(stmt.else_branch)
        
        self.patch_jump(jump_to_end, len(self.instructions))
    
    def compile_WhileStatement(self, stmt: WhileStatement):
        loop_start = len(self.instructions)
        self.loop_starts.append(loop_start)
        self.loop_ends.append([])
        
        self.compile_expression(stmt.condition)
        exit_jump = self.emit(OpCode.JUMP_IF_FALSE, 0)
        
        self.compile_Block(stmt.body)
        
        self.emit(OpCode.JUMP, loop_start)
        
        loop_end = len(self.instructions)
        self.patch_jump(exit_jump, loop_end)
        
        for break_jump in self.loop_ends.pop():
            self.patch_jump(break_jump, loop_end)
        self.loop_starts.pop()
    
    def compile_ForStatement(self, stmt: ForStatement):
        self.compile_expression(stmt.iterable)
        iter_slot = self.get_local("__iter__")
        self.emit(OpCode.DEFINE, ("__iter__", iter_slot))
        
        idx_slot = self.get_local("__idx__")
        self.emit(OpCode.PUSH, 0)
        self.emit(OpCode.DEFINE, ("__idx__", idx_slot))
        
        loop_start = len(self.instructions)
        self.loop_starts.append(loop_start)
        self.loop_ends.append([])
        
        self.emit(OpCode.LOAD, "__idx__")
        self.emit(OpCode.LOAD, "__iter__")
        const_idx = self.add_constant("__len__")
        self.emit(OpCode.GET_ATTR, const_idx)
        self.emit(OpCode.LT)
        
        exit_jump = self.emit(OpCode.JUMP_IF_FALSE, 0)
        
        self.emit(OpCode.LOAD, "__iter__")
        self.emit(OpCode.LOAD, "__idx__")
        self.emit(OpCode.INDEX)
        var_slot = self.get_local(stmt.variable)
        self.emit(OpCode.DEFINE, (stmt.variable, var_slot))
        
        self.compile_Block(stmt.body)
        
        self.emit(OpCode.LOAD, "__idx__")
        self.emit(OpCode.PUSH, 1)
        self.emit(OpCode.ADD)
        self.emit(OpCode.STORE, "__idx__")
        
        self.emit(OpCode.JUMP, loop_start)
        
        loop_end = len(self.instructions)
        self.patch_jump(exit_jump, loop_end)
        
        for break_jump in self.loop_ends.pop():
            self.patch_jump(break_jump, loop_end)
        self.loop_starts.pop()
    
    def compile_BreakStatement(self, stmt: BreakStatement):
        if self.loop_ends:
            jump = self.emit(OpCode.JUMP, 0)
            self.loop_ends[-1].append(jump)
    
    def compile_ContinueStatement(self, stmt: ContinueStatement):
        if self.loop_starts:
            self.emit(OpCode.JUMP, self.loop_starts[-1])
    
    def compile_ReturnStatement(self, stmt: ReturnStatement):
        if stmt.value:
            self.compile_expression(stmt.value)
        else:
            self.emit(OpCode.PUSH, None)
        self.emit(OpCode.RETURN)
    
    def compile_FunctionDeclaration(self, stmt: FunctionDeclaration):
        func_compiler = Compiler()
        func_compiler.locals = {}
        func_compiler.local_count = 0
        
        for param in stmt.parameters:
            func_compiler.get_local(param.name)
        
        for s in stmt.body.statements:
            func_compiler.compile_statement(s)
        
        func_compiler.emit(OpCode.PUSH, None)
        func_compiler.emit(OpCode.RETURN)
        
        compiled_func = CompiledFunction(
            name=stmt.name,
            params=[p.name for p in stmt.parameters],
            code=func_compiler.instructions,
            num_locals=func_compiler.local_count
        )
        
        self.functions[stmt.name] = compiled_func
        const_idx = self.add_constant(compiled_func)
        self.emit(OpCode.LOAD_CONST, const_idx)
        self.emit(OpCode.DEFINE, (stmt.name, self.get_local(stmt.name)))
    
    # ========================================================================
    # Expression Compilation
    # ========================================================================
    
    def compile_expression(self, expr: Expression):
        """Compile an expression."""
        method_name = f"compile_{type(expr).__name__}"
        method = getattr(self, method_name, self.compile_expr_default)
        method(expr)
    
    def compile_expr_default(self, node):
        raise RuntimeError(f"Cannot compile expression: {type(node).__name__}")
    
    def compile_IntegerLiteral(self, expr: IntegerLiteral):
        self.emit(OpCode.PUSH, expr.value)
    
    def compile_FloatLiteral(self, expr: FloatLiteral):
        self.emit(OpCode.PUSH, expr.value)
    
    def compile_StringLiteral(self, expr: StringLiteral):
        self.emit(OpCode.PUSH, expr.value)
    
    def compile_BooleanLiteral(self, expr: BooleanLiteral):
        self.emit(OpCode.PUSH, expr.value)
    
    def compile_NullLiteral(self, expr: NullLiteral):
        self.emit(OpCode.PUSH, None)
    
    def compile_Identifier(self, expr: Identifier):
        self.emit(OpCode.LOAD, expr.name)
    
    def compile_ListLiteral(self, expr: ListLiteral):
        for elem in expr.elements:
            self.compile_expression(elem)
        self.emit(OpCode.BUILD_LIST, len(expr.elements))
    
    def compile_MapLiteral(self, expr: MapLiteral):
        for key, value in expr.pairs:
            self.compile_expression(key)
            self.compile_expression(value)
        self.emit(OpCode.BUILD_MAP, len(expr.pairs))
    
    def compile_BinaryOp(self, expr: BinaryOp):
        self.compile_expression(expr.left)
        self.compile_expression(expr.right)
        
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '**': OpCode.POW,
            '&': OpCode.BIT_AND,
            '|': OpCode.BIT_OR,
            '^': OpCode.BIT_XOR,
            '<<': OpCode.SHL,
            '>>': OpCode.SHR,
        }
        
        if expr.operator in op_map:
            self.emit(op_map[expr.operator])
    
    def compile_UnaryOp(self, expr: UnaryOp):
        self.compile_expression(expr.operand)
        
        if expr.operator == '-':
            self.emit(OpCode.NEG)
        elif expr.operator == '~':
            self.emit(OpCode.BIT_NOT)
        elif expr.operator == 'not':
            self.emit(OpCode.NOT)
    
    def compile_ComparisonOp(self, expr: ComparisonOp):
        self.compile_expression(expr.left)
        self.compile_expression(expr.right)
        
        op_map = {
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '>': OpCode.GT,
            '<=': OpCode.LE,
            '>=': OpCode.GE,
        }
        
        if expr.operator in op_map:
            self.emit(op_map[expr.operator])
    
    def compile_LogicalOp(self, expr: LogicalOp):
        self.compile_expression(expr.left)
        
        if expr.operator == 'and':
            jump = self.emit(OpCode.JUMP_IF_FALSE, 0)
            self.emit(OpCode.POP)
            self.compile_expression(expr.right)
            self.patch_jump(jump, len(self.instructions))
        elif expr.operator == 'or':
            jump = self.emit(OpCode.JUMP_IF_TRUE, 0)
            self.emit(OpCode.POP)
            self.compile_expression(expr.right)
            self.patch_jump(jump, len(self.instructions))
    
    def compile_FunctionCall(self, expr: FunctionCall):
        for arg in expr.arguments:
            self.compile_expression(arg)
        self.compile_expression(expr.function)
        self.emit(OpCode.CALL, len(expr.arguments))
    
    def compile_IndexAccess(self, expr: IndexAccess):
        self.compile_expression(expr.object)
        self.compile_expression(expr.index)
        self.emit(OpCode.INDEX)
    
    def compile_MemberAccess(self, expr: MemberAccess):
        self.compile_expression(expr.object)
        const_idx = self.add_constant(expr.member)
        self.emit(OpCode.GET_ATTR, const_idx)


class VirtualMachine:
    """
    Executes CactUScript bytecode.
    
    Example:
        vm = VirtualMachine()
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        result = vm.run(bytecode, compiler.constants)
    """
    
    def __init__(self):
        self.stack: List[Any] = []
        self.frames: List[Dict] = []
        self.globals: Dict[str, Any] = {}
        self.constants: List[Any] = []
        self.pc = 0
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Set up built-in functions."""
        self.globals["print"] = lambda *args: print(*args, end="")
        self.globals["println"] = lambda *args: print(*args)
        self.globals["len"] = len
        self.globals["range"] = lambda *args: list(range(*args))
        self.globals["str"] = str
        self.globals["int"] = int
        self.globals["float"] = float
        self.globals["abs"] = abs
        self.globals["min"] = min
        self.globals["max"] = max
        self.globals["sum"] = sum
    
    def push(self, value: Any):
        """Push a value onto the stack."""
        self.stack.append(value)
    
    def pop(self) -> Any:
        """Pop a value from the stack."""
        return self.stack.pop()
    
    def peek(self) -> Any:
        """Peek at the top of the stack."""
        return self.stack[-1] if self.stack else None
    
    def current_frame(self) -> Dict:
        """Get the current call frame."""
        return self.frames[-1] if self.frames else self.globals
    
    def run(self, instructions: List[Instruction], constants: List[Any]) -> Any:
        """Execute bytecode instructions."""
        self.constants = constants
        self.pc = 0
        self.frames = [{}]
        
        while self.pc < len(instructions):
            instr = instructions[self.pc]
            self.pc += 1
            
            result = self._execute_instruction(instr)
            if result == "HALT":
                break
        
        return self.peek()
    
    def _execute_instruction(self, instr: Instruction) -> Optional[str]:
        """Execute a single instruction."""
        op = instr.opcode
        arg = instr.operand
        
        # Stack operations
        if op == OpCode.PUSH:
            self.push(arg)
        
        elif op == OpCode.POP:
            self.pop()
        
        elif op == OpCode.DUP:
            self.push(self.peek())
        
        # Arithmetic
        elif op == OpCode.ADD:
            b, a = self.pop(), self.pop()
            self.push(a + b)
        
        elif op == OpCode.SUB:
            b, a = self.pop(), self.pop()
            self.push(a - b)
        
        elif op == OpCode.MUL:
            b, a = self.pop(), self.pop()
            self.push(a * b)
        
        elif op == OpCode.DIV:
            b, a = self.pop(), self.pop()
            self.push(a / b)
        
        elif op == OpCode.MOD:
            b, a = self.pop(), self.pop()
            self.push(a % b)
        
        elif op == OpCode.POW:
            b, a = self.pop(), self.pop()
            self.push(a ** b)
        
        elif op == OpCode.NEG:
            self.push(-self.pop())
        
        # Comparison
        elif op == OpCode.EQ:
            b, a = self.pop(), self.pop()
            self.push(a == b)
        
        elif op == OpCode.NE:
            b, a = self.pop(), self.pop()
            self.push(a != b)
        
        elif op == OpCode.LT:
            b, a = self.pop(), self.pop()
            self.push(a < b)
        
        elif op == OpCode.GT:
            b, a = self.pop(), self.pop()
            self.push(a > b)
        
        elif op == OpCode.LE:
            b, a = self.pop(), self.pop()
            self.push(a <= b)
        
        elif op == OpCode.GE:
            b, a = self.pop(), self.pop()
            self.push(a >= b)
        
        # Logical
        elif op == OpCode.NOT:
            self.push(not self.pop())
        
        # Bitwise
        elif op == OpCode.BIT_AND:
            b, a = self.pop(), self.pop()
            self.push(a & b)
        
        elif op == OpCode.BIT_OR:
            b, a = self.pop(), self.pop()
            self.push(a | b)
        
        elif op == OpCode.BIT_XOR:
            b, a = self.pop(), self.pop()
            self.push(a ^ b)
        
        elif op == OpCode.BIT_NOT:
            self.push(~self.pop())
        
        elif op == OpCode.SHL:
            b, a = self.pop(), self.pop()
            self.push(a << b)
        
        elif op == OpCode.SHR:
            b, a = self.pop(), self.pop()
            self.push(a >> b)
        
        # Variables
        elif op == OpCode.LOAD:
            frame = self.current_frame()
            if arg in frame:
                self.push(frame[arg])
            elif arg in self.globals:
                self.push(self.globals[arg])
            else:
                raise RuntimeError(f"Undefined variable: {arg}")
        
        elif op == OpCode.STORE:
            frame = self.current_frame()
            frame[arg] = self.pop()
        
        elif op == OpCode.DEFINE:
            name, slot = arg
            frame = self.current_frame()
            frame[name] = self.pop()
        
        elif op == OpCode.LOAD_CONST:
            self.push(self.constants[arg])
        
        # Control flow
        elif op == OpCode.JUMP:
            self.pc = arg
        
        elif op == OpCode.JUMP_IF_FALSE:
            if not self.pop():
                self.pc = arg
        
        elif op == OpCode.JUMP_IF_TRUE:
            if self.pop():
                self.pc = arg
        
        # Functions
        elif op == OpCode.CALL:
            num_args = arg
            func = self.pop()
            args = [self.pop() for _ in range(num_args)][::-1]
            
            if callable(func) and not isinstance(func, CompiledFunction):
                result = func(*args)
                self.push(result)
            elif isinstance(func, CompiledFunction):
                new_frame = {}
                for i, param in enumerate(func.params):
                    new_frame[param] = args[i] if i < len(args) else None
                self.frames.append(new_frame)
        
        elif op == OpCode.RETURN:
            return_value = self.pop()
            self.frames.pop()
            self.push(return_value)
        
        # Collections
        elif op == OpCode.BUILD_LIST:
            elements = [self.pop() for _ in range(arg)][::-1]
            self.push(elements)
        
        elif op == OpCode.BUILD_MAP:
            pairs = []
            for _ in range(arg):
                value = self.pop()
                key = self.pop()
                pairs.append((key, value))
            self.push(dict(reversed(pairs)))
        
        elif op == OpCode.INDEX:
            index = self.pop()
            obj = self.pop()
            self.push(obj[index])
        
        elif op == OpCode.STORE_INDEX:
            value = self.pop()
            index = self.pop()
            obj = self.pop()
            obj[index] = value
        
        # Objects
        elif op == OpCode.GET_ATTR:
            member = self.constants[arg]
            obj = self.pop()
            if isinstance(obj, dict):
                self.push(obj.get(member))
            elif hasattr(obj, member):
                self.push(getattr(obj, member))
            else:
                self.push(None)
        
        elif op == OpCode.SET_ATTR:
            member = self.constants[arg]
            value = self.pop()
            obj = self.pop()
            if isinstance(obj, dict):
                obj[member] = value
            else:
                setattr(obj, member, value)
        
        # Special
        elif op == OpCode.PRINT:
            print(self.pop(), end="")
        
        elif op == OpCode.HALT:
            return "HALT"
        
        elif op == OpCode.NOP:
            pass
        
        return None
