"""
CactUScript Parser

Converts a stream of tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional, Callable
from .tokens import Token, TokenType
from .lexer import Lexer
from .ast_nodes import *


class ParserError(Exception):
    """Exception raised for parser errors."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parser Error at line {token.line}, column {token.column}: {message}")


class Parser:
    """
    Parses CactUScript tokens into an AST.
    
    Example:
        parser = Parser(tokens)
        ast = parser.parse()
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    @property
    def current_token(self) -> Token:
        """Returns the current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead by offset tokens."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Move to the next token and return the current one."""
        token = self.current_token
        self.pos += 1
        return token
    
    def skip_newlines(self):
        """Skip all newline tokens."""
        while self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def expect(self, token_type: TokenType, message: str = None) -> Token:
        """Consume a token of the expected type or raise an error."""
        if self.current_token.type != token_type:
            msg = message or f"Expected {token_type.name}, got {self.current_token.type.name}"
            raise ParserError(msg, self.current_token)
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token.type in token_types
    
    def parse(self) -> Program:
        """Parse the entire program."""
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    # ========================================================================
    # Statement Parsing
    # ========================================================================
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a single statement."""
        self.skip_newlines()
        
        if self.match(TokenType.LET):
            return self.parse_variable_declaration(is_const=False)
        elif self.match(TokenType.CONST):
            return self.parse_variable_declaration(is_const=True)
        elif self.match(TokenType.FN):
            return self.parse_function_declaration(is_async=False)
        elif self.match(TokenType.ASYNC):
            return self.parse_async_function()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        elif self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStatement()
        elif self.match(TokenType.STRUCT):
            return self.parse_struct_declaration()
        elif self.match(TokenType.ENUM):
            return self.parse_enum_declaration()
        elif self.match(TokenType.CONTRACT):
            return self.parse_contract_declaration()
        elif self.match(TokenType.IMPL):
            return self.parse_impl_block()
        elif self.match(TokenType.EMIT):
            return self.parse_emit_statement()
        elif self.match(TokenType.EVENT):
            return self.parse_event_declaration()
        else:
            return self.parse_expression_or_assignment()
    
    def parse_variable_declaration(self, is_const: bool) -> VariableDeclaration:
        """Parse let/const variable declaration."""
        self.advance()  # skip 'let' or 'const'
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.parse_type_annotation()
        
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
        
        return VariableDeclaration(name, type_annotation, value, is_const)
    
    def parse_type_annotation(self) -> str:
        """Parse a type annotation."""
        type_tokens = [
            TokenType.TYPE_INT, TokenType.TYPE_FLOAT, TokenType.TYPE_STRING,
            TokenType.TYPE_BOOL, TokenType.TYPE_VOID, TokenType.TYPE_LIST,
            TokenType.TYPE_MAP, TokenType.IDENTIFIER
        ]
        
        if self.match(*type_tokens):
            return self.advance().value
        
        raise ParserError("Expected type annotation", self.current_token)
    
    def parse_function_declaration(self, is_async: bool) -> FunctionDeclaration:
        """Parse function declaration."""
        self.expect(TokenType.FN)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        parameters = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type_annotation()
        
        body = self.parse_block()
        
        return FunctionDeclaration(name, parameters, return_type, body, is_async)
    
    def parse_async_function(self) -> FunctionDeclaration:
        """Parse async function declaration."""
        self.expect(TokenType.ASYNC)
        return self.parse_function_declaration(is_async=True)
    
    def parse_parameters(self) -> List[Parameter]:
        """Parse function parameters."""
        parameters = []
        
        while not self.match(TokenType.RPAREN):
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value
            
            type_annotation = None
            if self.match(TokenType.COLON):
                self.advance()
                type_annotation = self.parse_type_annotation()
            
            default_value = None
            if self.match(TokenType.ASSIGN):
                self.advance()
                default_value = self.parse_expression()
            
            parameters.append(Parameter(name, type_annotation, default_value))
            
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        return parameters
    
    def parse_block(self) -> Block:
        """Parse a block of statements."""
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if/elif/else statement."""
        self.expect(TokenType.IF)
        
        condition = self.parse_expression()
        then_branch = self.parse_block()
        
        elif_branches = []
        else_branch = None
        
        self.skip_newlines()
        
        while self.match(TokenType.ELIF):
            self.advance()
            elif_cond = self.parse_expression()
            elif_body = self.parse_block()
            elif_branches.append((elif_cond, elif_body))
            self.skip_newlines()
        
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.parse_block()
        
        return IfStatement(condition, then_branch, elif_branches, else_branch)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while loop."""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for loop."""
        self.expect(TokenType.FOR)
        var_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        return ForStatement(var_token.value, iterable, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_struct_declaration(self) -> StructDeclaration:
        """Parse struct declaration."""
        self.expect(TokenType.STRUCT)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        
        fields = []
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            if self.match(TokenType.FN):
                break  # Methods come after fields
            
            field_name = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.COLON)
            field_type = self.parse_type_annotation()
            fields.append((field_name.value, field_type))
            
            self.skip_newlines()
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return StructDeclaration(name_token.value, fields)
    
    def parse_enum_declaration(self) -> EnumDeclaration:
        """Parse enum declaration."""
        self.expect(TokenType.ENUM)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        
        variants = []
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            variant = self.expect(TokenType.IDENTIFIER)
            variants.append(variant.value)
            
            self.skip_newlines()
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return EnumDeclaration(name_token.value, variants)
    
    def parse_contract_declaration(self) -> ContractDeclaration:
        """Parse smart contract declaration."""
        self.expect(TokenType.CONTRACT)
        name_token = self.expect(TokenType.IDENTIFIER)
        body = self.parse_block()
        return ContractDeclaration(name_token.value, body)
    
    def parse_impl_block(self) -> ImplBlock:
        """Parse implementation block."""
        self.expect(TokenType.IMPL)
        type_name = self.expect(TokenType.IDENTIFIER)
        
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        
        methods = []
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            if self.match(TokenType.FN):
                methods.append(self.parse_function_declaration(is_async=False))
            elif self.match(TokenType.ASYNC):
                methods.append(self.parse_async_function())
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return ImplBlock(type_name.value, methods)
    
    def parse_event_declaration(self) -> EventDeclaration:
        """Parse event declaration."""
        self.expect(TokenType.EVENT)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        self.expect(TokenType.LPAREN)
        fields = []
        
        while not self.match(TokenType.RPAREN):
            field_name = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.COLON)
            field_type = self.parse_type_annotation()
            fields.append((field_name.value, field_type))
            
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        self.expect(TokenType.RPAREN)
        return EventDeclaration(name_token.value, fields)
    
    def parse_emit_statement(self) -> EmitStatement:
        """Parse emit statement for events."""
        self.expect(TokenType.EMIT)
        event_name = self.expect(TokenType.IDENTIFIER)
        
        self.expect(TokenType.LPAREN)
        arguments = self.parse_arguments()
        self.expect(TokenType.RPAREN)
        
        return EmitStatement(event_name.value, arguments)
    
    def parse_expression_or_assignment(self) -> Statement:
        """Parse expression or assignment statement."""
        expr = self.parse_expression()
        
        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN):
            op = self.advance().value
            value = self.parse_expression()
            return Assignment(expr, op, value)
        
        return ExpressionStatement(expr)
    
    # ========================================================================
    # Expression Parsing (Precedence Climbing)
    # ========================================================================
    
    def parse_expression(self) -> Expression:
        """Parse an expression."""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> Expression:
        """Parse logical OR expression."""
        left = self.parse_and_expression()
        
        while self.match(TokenType.OR):
            self.advance()
            right = self.parse_and_expression()
            left = LogicalOp(left, "or", right)
        
        return left
    
    def parse_and_expression(self) -> Expression:
        """Parse logical AND expression."""
        left = self.parse_not_expression()
        
        while self.match(TokenType.AND):
            self.advance()
            right = self.parse_not_expression()
            left = LogicalOp(left, "and", right)
        
        return left
    
    def parse_not_expression(self) -> Expression:
        """Parse logical NOT expression."""
        if self.match(TokenType.NOT):
            self.advance()
            operand = self.parse_not_expression()
            return UnaryOp("not", operand)
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        left = self.parse_additive()
        
        comparison_ops = [
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL
        ]
        
        while self.match(*comparison_ops):
            op = self.advance().value
            right = self.parse_additive()
            left = ComparisonOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> Expression:
        """Parse additive expression (+, -)."""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expression (*, /, %)."""
        left = self.parse_power()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_power(self) -> Expression:
        """Parse power expression (**)."""
        left = self.parse_unary()
        
        if self.match(TokenType.POWER):
            op = self.advance().value
            right = self.parse_power()  # Right associative
            return BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expression (-, ~)."""
        if self.match(TokenType.MINUS, TokenType.BIT_NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_await()
    
    def parse_await(self) -> Expression:
        """Parse await expression."""
        if self.match(TokenType.AWAIT):
            self.advance()
            expr = self.parse_postfix()
            return AwaitExpression(expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        """Parse postfix expressions (calls, member access, indexing)."""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                self.advance()
                args = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                expr = FunctionCall(expr, args)
            elif self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER)
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, member.value, args)
                else:
                    expr = MemberAccess(expr, member.value)
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            else:
                break
        
        return expr
    
    def parse_arguments(self) -> List[Expression]:
        """Parse function call arguments."""
        args = []
        
        while not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        return args
    
    def parse_primary(self) -> Expression:
        """Parse primary expression (literals, identifiers, grouped)."""
        token = self.current_token
        
        if self.match(TokenType.INTEGER):
            self.advance()
            return IntegerLiteral(token.value)
        
        elif self.match(TokenType.FLOAT):
            self.advance()
            return FloatLiteral(token.value)
        
        elif self.match(TokenType.STRING):
            self.advance()
            return StringLiteral(token.value)
        
        elif self.match(TokenType.TRUE, TokenType.FALSE):
            self.advance()
            return BooleanLiteral(token.value)
        
        elif self.match(TokenType.NULL):
            self.advance()
            return NullLiteral()
        
        elif self.match(TokenType.IDENTIFIER):
            self.advance()
            return Identifier(token.value)
        
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        elif self.match(TokenType.LBRACKET):
            return self.parse_list_literal()
        
        elif self.match(TokenType.LBRACE):
            return self.parse_map_literal()
        
        raise ParserError(f"Unexpected token: {token.type.name}", token)
    
    def parse_list_literal(self) -> ListLiteral:
        """Parse list literal [a, b, c]."""
        self.expect(TokenType.LBRACKET)
        elements = []
        
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements)
    
    def parse_map_literal(self) -> MapLiteral:
        """Parse map literal {key: value, ...}."""
        self.expect(TokenType.LBRACE)
        pairs = []
        
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACE):
            key = self.parse_expression()
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            
            self.skip_newlines()
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return MapLiteral(pairs)
