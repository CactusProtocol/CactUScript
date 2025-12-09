"""
CactUScript Lexer (Tokenizer)

Converts source code into a stream of tokens for parsing.
"""

from typing import List, Optional
from .tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Exception raised for lexer errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at line {line}, column {column}: {message}")


class Lexer:
    """
    Tokenizes CactUScript source code.
    
    Example:
        lexer = Lexer("let x = 42")
        tokens = lexer.tokenize()
    """
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    @property
    def current_char(self) -> Optional[str]:
        """Returns the current character or None if at end."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead by offset characters."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Move to the next character and return the current one."""
        char = self.current_char
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters (except newlines)."""
        while self.current_char and self.current_char in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line and multi-line comments."""
        if self.current_char == '/' and self.peek() == '/':
            # Single-line comment
            while self.current_char and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            # Multi-line comment
            self.advance()  # skip /
            self.advance()  # skip *
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # skip *
                    self.advance()  # skip /
                    break
                self.advance()
    
    def read_string(self) -> Token:
        """Read a string literal."""
        quote_char = self.current_char
        start_line = self.line
        start_col = self.column
        self.advance()  # skip opening quote
        
        result = []
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\':
                self.advance()
                escape_chars = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                }
                if self.current_char in escape_chars:
                    result.append(escape_chars[self.current_char])
                else:
                    result.append(self.current_char)
            else:
                result.append(self.current_char)
            self.advance()
        
        if not self.current_char:
            raise LexerError("Unterminated string literal", start_line, start_col)
        
        self.advance()  # skip closing quote
        return Token(TokenType.STRING, ''.join(result), start_line, start_col)
    
    def read_number(self) -> Token:
        """Read a numeric literal (integer or float)."""
        start_line = self.line
        start_col = self.column
        result = []
        is_float = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break  # Second dot, stop reading
                if self.peek() and self.peek().isdigit():
                    is_float = True
                else:
                    break  # Dot not followed by digit
            result.append(self.current_char)
            self.advance()
        
        value_str = ''.join(result)
        if is_float:
            return Token(TokenType.FLOAT, float(value_str), start_line, start_col)
        return Token(TokenType.INTEGER, int(value_str), start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_col = self.column
        result = []
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result.append(self.current_char)
            self.advance()
        
        value = ''.join(result)
        
        # Check if it's a keyword
        if value in KEYWORDS:
            token_type = KEYWORDS[value]
            if token_type == TokenType.TRUE:
                return Token(token_type, True, start_line, start_col)
            elif token_type == TokenType.FALSE:
                return Token(token_type, False, start_line, start_col)
            elif token_type == TokenType.NONE:
                return Token(TokenType.NULL, None, start_line, start_col)
            return Token(token_type, value, start_line, start_col)
        
        return Token(TokenType.IDENTIFIER, value, start_line, start_col)
    
    def make_token(self, token_type: TokenType, value: any = None) -> Token:
        """Create a token at current position."""
        return Token(token_type, value, self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.current_char:
            # Skip whitespace
            if self.current_char in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current_char == '\n':
                self.tokens.append(self.make_token(TokenType.NEWLINE, '\n'))
                self.advance()
                continue
            
            # Handle comments
            if self.current_char == '/' and self.peek() in ['/', '*']:
                self.skip_comment()
                continue
            
            # Handle strings
            if self.current_char in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Handle numbers
            if self.current_char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Handle identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Handle operators and delimiters
            token = self._read_operator_or_delimiter()
            if token:
                self.tokens.append(token)
                continue
            
            raise LexerError(f"Unexpected character: {self.current_char}", self.line, self.column)
        
        self.tokens.append(self.make_token(TokenType.EOF, None))
        return self.tokens
    
    def _read_operator_or_delimiter(self) -> Optional[Token]:
        """Read operators and delimiters."""
        start_line = self.line
        start_col = self.column
        char = self.current_char
        next_char = self.peek()
        
        # Two-character operators
        two_char_ops = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.MULTIPLY_ASSIGN,
            '/=': TokenType.DIVIDE_ASSIGN,
            '**': TokenType.POWER,
            '->': TokenType.ARROW,
            '=>': TokenType.FAT_ARROW,
            '<<': TokenType.LEFT_SHIFT,
            '>>': TokenType.RIGHT_SHIFT,
        }
        
        if next_char and char + next_char in two_char_ops:
            self.advance()
            self.advance()
            return Token(two_char_ops[char + next_char], char + next_char, start_line, start_col)
        
        # Single-character operators and delimiters
        single_char_ops = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '=': TokenType.ASSIGN,
            '&': TokenType.BIT_AND,
            '|': TokenType.BIT_OR,
            '^': TokenType.BIT_XOR,
            '~': TokenType.BIT_NOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
        }
        
        if char in single_char_ops:
            self.advance()
            return Token(single_char_ops[char], char, start_line, start_col)
        
        return None
