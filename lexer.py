from enum import Enum

tokens = []
errors = []

class TokenType(Enum):
    
    # Literals
    STRING = 1; NUMBER = 2; TYPE_ID = 3; OBJ_ID = 4
    SELF = 4; SELF_TYPE = 5
    
    # Single-character tokens
    LEFT_PAREN = 6; RIGHT_PAREN = 7; LEFT_BRACE = 8
    RIGHT_BRACE = 9; COMMA = 10; DOT = 11; MINUS = 12
    PLUS = 13; SEMICOLON = 14; SLASH = 15; STAR = 16
    
    # keywords, keywords are case insensitive (except for true and false)
    CLASS = 17; ELSE = 18; FALSE = 19; FI = 20
    IF = 21; IN = 22; INHERITS = 23; ISVOID = 24
    LET = 25; LOOP = 26; POOL = 27; THEN = 28
    WHILE = 29; CASE = 30; ESAC = 31; NEW = 32
    OF = 33; NOT = 34; TRUE = 35
    
keywords = {
    "Class"    :  TokenType.CLASS,
    "else"     :  TokenType.ELSE,
    "fi"       :  TokenType.FI,
    "if"       :  TokenType.IF,
    "in"       :  TokenType.IN,
    "inherits" :  TokenType.INHERITS,
    "isvoid"   :  TokenType.ISVOID,
    "let"      :  TokenType.LET,
    "loop"     :  TokenType.LOOP,
    "pool"     :  TokenType.POOL,
    "then"     :  TokenType.THEN,
    "while"    :  TokenType.WHILE,
    "case"     :  TokenType.CASE,
    "esac"     :  TokenType.ESAC,
    "new"      :  TokenType.NEW,
    "of"       :  TokenType.OF,
    "not"      :  TokenType.NOT,
    "true"     :  TokenType.TRUE,
}

class Token:
    tokenType       : TokenType
    lexeme          : str
    contextPosition : int
    line            : int

    def __init__(self, tokenType, lexeme, contextPosition, line):
        self.tokenType = tokenType
        self.lexeme = lexeme
        self.contextPosition = contextPosition
        self.line = line
        
    def __repr__(self) -> str:
        print(f'''
              TokenType        : {self.tokenType.name}
              lexeme           : {self.lexeme}
              contextPosition  : {self.contextPosition}
              line             : {self.line}
              ''')

def tokenize(lexeme: str):
    pass

def scan(sourceFile: str) -> bool:
    with open(sourceFile, "r") as source:
        # scan file
        pass