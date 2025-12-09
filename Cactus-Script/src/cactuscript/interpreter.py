"""
CactUScript Interpreter

Executes CactUScript AST directly through tree-walking interpretation.
"""

from typing import Any, Dict, List, Optional, Callable
from .ast_nodes import *
from .tokens import TokenType
import asyncio


class RuntimeError(Exception):
    """Exception raised for runtime errors."""
    pass


class ReturnValue(Exception):
    """Used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Used to implement break statements."""
    pass


class ContinueException(Exception):
    """Used to implement continue statements."""
    pass


class Environment:
    """Variable scope environment."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, Any] = {}
        self.constants: set = set()
        self.parent = parent
    
    def define(self, name: str, value: Any, is_const: bool = False):
        """Define a new variable in the current scope."""
        self.variables[name] = value
        if is_const:
            self.constants.add(name)
    
    def assign(self, name: str, value: Any):
        """Assign a value to an existing variable."""
        if name in self.variables:
            if name in self.constants:
                raise RuntimeError(f"Cannot reassign constant '{name}'")
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")
    
    def get(self, name: str) -> Any:
        """Get a variable's value."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def exists(self, name: str) -> bool:
        """Check if a variable exists."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


class CactUScriptFunction:
    """Represents a CactUScript function."""
    
    def __init__(self, declaration: FunctionDeclaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure
        self.is_async = declaration.is_async
    
    def __repr__(self):
        return f"<function {self.declaration.name}>"


class CactUScriptStruct:
    """Represents a CactUScript struct type."""
    
    def __init__(self, name: str, fields: List[tuple]):
        self.name = name
        self.fields = {name: type_name for name, type_name in fields}
    
    def __repr__(self):
        return f"<struct {self.name}>"


class CactUScriptInstance:
    """Represents an instance of a struct."""
    
    def __init__(self, struct: CactUScriptStruct, values: Dict[str, Any]):
        self.struct = struct
        self.values = values
    
    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        raise RuntimeError(f"Unknown field '{name}' on {self.struct.name}")
    
    def set(self, name: str, value: Any):
        if name in self.struct.fields:
            self.values[name] = value
        else:
            raise RuntimeError(f"Unknown field '{name}' on {self.struct.name}")
    
    def __repr__(self):
        return f"{self.struct.name}({self.values})"


class Interpreter:
    """
    Executes CactUScript programs.
    
    Example:
        interpreter = Interpreter()
        result = interpreter.run(ast)
    """
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.events: Dict[str, List[Any]] = {}
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Set up built-in functions."""
        self.global_env.define("print", self._builtin_print)
        self.global_env.define("println", self._builtin_println)
        self.global_env.define("len", self._builtin_len)
        self.global_env.define("range", self._builtin_range)
        self.global_env.define("str", self._builtin_str)
        self.global_env.define("int", self._builtin_int)
        self.global_env.define("float", self._builtin_float)
        self.global_env.define("type", self._builtin_type)
        self.global_env.define("input", self._builtin_input)
        self.global_env.define("append", self._builtin_append)
        self.global_env.define("pop", self._builtin_pop)
        self.global_env.define("keys", self._builtin_keys)
        self.global_env.define("values", self._builtin_values)
        self.global_env.define("abs", self._builtin_abs)
        self.global_env.define("min", self._builtin_min)
        self.global_env.define("max", self._builtin_max)
        self.global_env.define("sum", self._builtin_sum)
    
    def _builtin_print(self, *args):
        print(*args, end="")
        return None
    
    def _builtin_println(self, *args):
        print(*args)
        return None
    
    def _builtin_len(self, obj):
        if isinstance(obj, (list, str, dict)):
            return len(obj)
        raise RuntimeError(f"len() not supported for {type(obj).__name__}")
    
    def _builtin_range(self, *args):
        return list(range(*args))
    
    def _builtin_str(self, value):
        return str(value)
    
    def _builtin_int(self, value):
        return int(value)
    
    def _builtin_float(self, value):
        return float(value)
    
    def _builtin_type(self, value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "map"
        elif value is None:
            return "none"
        elif isinstance(value, CactUScriptInstance):
            return value.struct.name
        elif callable(value):
            return "function"
        return type(value).__name__
    
    def _builtin_input(self, prompt=""):
        return input(prompt)
    
    def _builtin_append(self, lst, item):
        if not isinstance(lst, list):
            raise RuntimeError("append() requires a list")
        lst.append(item)
        return lst
    
    def _builtin_pop(self, lst, index=-1):
        if not isinstance(lst, list):
            raise RuntimeError("pop() requires a list")
        return lst.pop(index)
    
    def _builtin_keys(self, obj):
        if isinstance(obj, dict):
            return list(obj.keys())
        raise RuntimeError("keys() requires a map")
    
    def _builtin_values(self, obj):
        if isinstance(obj, dict):
            return list(obj.values())
        raise RuntimeError("values() requires a map")
    
    def _builtin_abs(self, value):
        return abs(value)
    
    def _builtin_min(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            return min(args[0])
        return min(args)
    
    def _builtin_max(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            return max(args[0])
        return max(args)
    
    def _builtin_sum(self, iterable):
        return sum(iterable)
    
    def run(self, program: Program) -> Any:
        """Execute a program."""
        result = None
        for stmt in program.statements:
            result = self.execute(stmt)
        return result
    
    def execute(self, node: ASTNode) -> Any:
        """Execute an AST node."""
        method_name = f"execute_{type(node).__name__}"
        method = getattr(self, method_name, self.execute_default)
        return method(node)
    
    def execute_default(self, node: ASTNode):
        raise RuntimeError(f"No execution method for {type(node).__name__}")
    
    # ========================================================================
    # Statement Execution
    # ========================================================================
    
    def execute_ExpressionStatement(self, node: ExpressionStatement) -> Any:
        return self.evaluate(node.expression)
    
    def execute_VariableDeclaration(self, node: VariableDeclaration) -> None:
        value = None
        if node.value:
            value = self.evaluate(node.value)
        self.current_env.define(node.name, value, node.is_const)
    
    def execute_Assignment(self, node: Assignment) -> Any:
        value = self.evaluate(node.value)
        
        if isinstance(node.target, Identifier):
            if node.operator == "=":
                self.current_env.assign(node.target.name, value)
            else:
                current = self.current_env.get(node.target.name)
                new_value = self._apply_compound_assignment(current, node.operator, value)
                self.current_env.assign(node.target.name, new_value)
            return value
        
        elif isinstance(node.target, IndexAccess):
            obj = self.evaluate(node.target.object)
            index = self.evaluate(node.target.index)
            if node.operator == "=":
                obj[index] = value
            else:
                current = obj[index]
                obj[index] = self._apply_compound_assignment(current, node.operator, value)
            return value
        
        elif isinstance(node.target, MemberAccess):
            obj = self.evaluate(node.target.object)
            if isinstance(obj, CactUScriptInstance):
                if node.operator == "=":
                    obj.set(node.target.member, value)
                else:
                    current = obj.get(node.target.member)
                    obj.set(node.target.member, 
                           self._apply_compound_assignment(current, node.operator, value))
                return value
            elif isinstance(obj, dict):
                if node.operator == "=":
                    obj[node.target.member] = value
                else:
                    current = obj.get(node.target.member)
                    obj[node.target.member] = self._apply_compound_assignment(
                        current, node.operator, value)
                return value
        
        raise RuntimeError(f"Invalid assignment target: {type(node.target).__name__}")
    
    def _apply_compound_assignment(self, left: Any, op: str, right: Any) -> Any:
        if op == "+=":
            return left + right
        elif op == "-=":
            return left - right
        elif op == "*=":
            return left * right
        elif op == "/=":
            return left / right
        raise RuntimeError(f"Unknown compound assignment operator: {op}")
    
    def execute_Block(self, node: Block) -> Any:
        result = None
        for stmt in node.statements:
            result = self.execute(stmt)
        return result
    
    def execute_IfStatement(self, node: IfStatement) -> Any:
        if self._is_truthy(self.evaluate(node.condition)):
            return self.execute(node.then_branch)
        
        for condition, block in node.elif_branches:
            if self._is_truthy(self.evaluate(condition)):
                return self.execute(block)
        
        if node.else_branch:
            return self.execute(node.else_branch)
        
        return None
    
    def execute_WhileStatement(self, node: WhileStatement) -> Any:
        result = None
        while self._is_truthy(self.evaluate(node.condition)):
            try:
                result = self.execute(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
        return result
    
    def execute_ForStatement(self, node: ForStatement) -> Any:
        iterable = self.evaluate(node.iterable)
        result = None
        
        previous_env = self.current_env
        self.current_env = Environment(previous_env)
        
        try:
            for item in iterable:
                self.current_env.define(node.variable, item)
                try:
                    result = self.execute(node.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.current_env = previous_env
        
        return result
    
    def execute_BreakStatement(self, node: BreakStatement):
        raise BreakException()
    
    def execute_ContinueStatement(self, node: ContinueStatement):
        raise ContinueException()
    
    def execute_ReturnStatement(self, node: ReturnStatement):
        value = None
        if node.value:
            value = self.evaluate(node.value)
        raise ReturnValue(value)
    
    def execute_FunctionDeclaration(self, node: FunctionDeclaration) -> None:
        func = CactUScriptFunction(node, self.current_env)
        self.current_env.define(node.name, func)
    
    def execute_StructDeclaration(self, node: StructDeclaration) -> None:
        struct = CactUScriptStruct(node.name, node.fields)
        self.current_env.define(node.name, struct)
    
    def execute_EnumDeclaration(self, node: EnumDeclaration) -> None:
        enum_dict = {variant: variant for variant in node.variants}
        self.current_env.define(node.name, enum_dict)
    
    def execute_ContractDeclaration(self, node: ContractDeclaration) -> None:
        contract_env = Environment(self.current_env)
        previous_env = self.current_env
        self.current_env = contract_env
        
        try:
            self.execute(node.body)
        finally:
            self.current_env = previous_env
        
        self.current_env.define(node.name, {
            "__type__": "contract",
            "__name__": node.name,
            "__env__": contract_env,
        })
    
    def execute_EventDeclaration(self, node: EventDeclaration) -> None:
        self.events[node.name] = []
        self.current_env.define(node.name, {
            "__type__": "event",
            "__name__": node.name,
            "__fields__": node.fields,
        })
    
    def execute_EmitStatement(self, node: EmitStatement) -> None:
        args = [self.evaluate(arg) for arg in node.arguments]
        if node.event_name not in self.events:
            self.events[node.event_name] = []
        self.events[node.event_name].append(args)
        print(f"[EVENT] {node.event_name}: {args}")
    
    def execute_ImplBlock(self, node: ImplBlock) -> None:
        struct = self.current_env.get(node.type_name)
        if not isinstance(struct, CactUScriptStruct):
            raise RuntimeError(f"Cannot implement methods for non-struct type: {node.type_name}")
        
        for method in node.methods:
            func = CactUScriptFunction(method, self.current_env)
            self.current_env.define(f"{node.type_name}.{method.name}", func)
    
    # ========================================================================
    # Expression Evaluation
    # ========================================================================
    
    def evaluate(self, node: Expression) -> Any:
        """Evaluate an expression."""
        method_name = f"evaluate_{type(node).__name__}"
        method = getattr(self, method_name, self.evaluate_default)
        return method(node)
    
    def evaluate_default(self, node: Expression):
        raise RuntimeError(f"No evaluation method for {type(node).__name__}")
    
    def evaluate_IntegerLiteral(self, node: IntegerLiteral) -> int:
        return node.value
    
    def evaluate_FloatLiteral(self, node: FloatLiteral) -> float:
        return node.value
    
    def evaluate_StringLiteral(self, node: StringLiteral) -> str:
        return node.value
    
    def evaluate_BooleanLiteral(self, node: BooleanLiteral) -> bool:
        return node.value
    
    def evaluate_NullLiteral(self, node: NullLiteral) -> None:
        return None
    
    def evaluate_ListLiteral(self, node: ListLiteral) -> list:
        return [self.evaluate(elem) for elem in node.elements]
    
    def evaluate_MapLiteral(self, node: MapLiteral) -> dict:
        result = {}
        for key, value in node.pairs:
            k = self.evaluate(key)
            v = self.evaluate(value)
            if isinstance(k, Identifier):
                k = k.name
            result[k] = v
        return result
    
    def evaluate_Identifier(self, node: Identifier) -> Any:
        return self.current_env.get(node.name)
    
    def evaluate_BinaryOp(self, node: BinaryOp) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '%': lambda a, b: a % b,
            '**': lambda a, b: a ** b,
            '&': lambda a, b: a & b,
            '|': lambda a, b: a | b,
            '^': lambda a, b: a ^ b,
            '<<': lambda a, b: a << b,
            '>>': lambda a, b: a >> b,
        }
        
        if node.operator in ops:
            return ops[node.operator](left, right)
        
        raise RuntimeError(f"Unknown binary operator: {node.operator}")
    
    def evaluate_UnaryOp(self, node: UnaryOp) -> Any:
        operand = self.evaluate(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == '~':
            return ~operand
        elif node.operator == 'not':
            return not self._is_truthy(operand)
        
        raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def evaluate_ComparisonOp(self, node: ComparisonOp) -> bool:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        
        ops = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
        }
        
        if node.operator in ops:
            return ops[node.operator](left, right)
        
        raise RuntimeError(f"Unknown comparison operator: {node.operator}")
    
    def evaluate_LogicalOp(self, node: LogicalOp) -> Any:
        left = self.evaluate(node.left)
        
        if node.operator == 'and':
            if not self._is_truthy(left):
                return left
            return self.evaluate(node.right)
        elif node.operator == 'or':
            if self._is_truthy(left):
                return left
            return self.evaluate(node.right)
        
        raise RuntimeError(f"Unknown logical operator: {node.operator}")
    
    def evaluate_FunctionCall(self, node: FunctionCall) -> Any:
        func = self.evaluate(node.function)
        args = [self.evaluate(arg) for arg in node.arguments]
        
        if callable(func) and not isinstance(func, CactUScriptFunction):
            return func(*args)
        
        if isinstance(func, CactUScriptStruct):
            values = {}
            for i, (field_name, _) in enumerate(func.fields.items()):
                if i < len(args):
                    values[field_name] = args[i]
                else:
                    values[field_name] = None
            return CactUScriptInstance(func, values)
        
        if isinstance(func, CactUScriptFunction):
            return self._call_function(func, args)
        
        raise RuntimeError(f"Cannot call non-function: {type(func).__name__}")
    
    def _call_function(self, func: CactUScriptFunction, args: List[Any]) -> Any:
        func_env = Environment(func.closure)
        
        for i, param in enumerate(func.declaration.parameters):
            if i < len(args):
                func_env.define(param.name, args[i])
            elif param.default_value:
                func_env.define(param.name, self.evaluate(param.default_value))
            else:
                func_env.define(param.name, None)
        
        previous_env = self.current_env
        self.current_env = func_env
        
        try:
            self.execute(func.declaration.body)
            return None
        except ReturnValue as rv:
            return rv.value
        finally:
            self.current_env = previous_env
    
    def evaluate_MethodCall(self, node: MethodCall) -> Any:
        obj = self.evaluate(node.object)
        args = [self.evaluate(arg) for arg in node.arguments]
        
        if isinstance(obj, CactUScriptInstance):
            method_name = f"{obj.struct.name}.{node.method}"
            if self.current_env.exists(method_name):
                method = self.current_env.get(method_name)
                return self._call_function(method, [obj] + args)
        
        if isinstance(obj, list):
            list_methods = {
                'append': lambda x: (obj.append(x), obj)[-1],
                'pop': lambda i=-1: obj.pop(i),
                'length': lambda: len(obj),
                'reverse': lambda: list(reversed(obj)),
                'sort': lambda: sorted(obj),
            }
            if node.method in list_methods:
                return list_methods[node.method](*args)
        
        if isinstance(obj, str):
            string_methods = {
                'upper': lambda: obj.upper(),
                'lower': lambda: obj.lower(),
                'split': lambda sep=" ": obj.split(sep),
                'strip': lambda: obj.strip(),
                'replace': lambda old, new: obj.replace(old, new),
                'contains': lambda sub: sub in obj,
                'length': lambda: len(obj),
            }
            if node.method in string_methods:
                return string_methods[node.method](*args)
        
        if isinstance(obj, dict):
            dict_methods = {
                'get': lambda k, default=None: obj.get(k, default),
                'keys': lambda: list(obj.keys()),
                'values': lambda: list(obj.values()),
                'contains': lambda k: k in obj,
            }
            if node.method in dict_methods:
                return dict_methods[node.method](*args)
        
        raise RuntimeError(f"Unknown method '{node.method}' on {type(obj).__name__}")
    
    def evaluate_MemberAccess(self, node: MemberAccess) -> Any:
        obj = self.evaluate(node.object)
        
        if isinstance(obj, CactUScriptInstance):
            return obj.get(node.member)
        
        if isinstance(obj, dict):
            if node.member in obj:
                return obj[node.member]
            raise RuntimeError(f"Key '{node.member}' not found in map")
        
        raise RuntimeError(f"Cannot access member '{node.member}' on {type(obj).__name__}")
    
    def evaluate_IndexAccess(self, node: IndexAccess) -> Any:
        obj = self.evaluate(node.object)
        index = self.evaluate(node.index)
        
        if isinstance(obj, (list, str)):
            return obj[index]
        
        if isinstance(obj, dict):
            return obj[index]
        
        raise RuntimeError(f"Cannot index {type(obj).__name__}")
    
    def evaluate_AwaitExpression(self, node: AwaitExpression) -> Any:
        expr = self.evaluate(node.expression)
        
        if asyncio.iscoroutine(expr):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(expr)
        
        return expr
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
