from enum import Enum

class Lexer:

    tokens : 'list[Token]'
    errors : 'list[Error]'
    
    sourcePosition  : int
    contextPosition : int
    lineNumber      : int
    source          : str
    
    def __init__(self, sourceFile):
        self.tokens = []
        self.errors = []
        with open(sourceFile, "r") as file:
            self.source = file.read()
        self.sourcePosition = 0
        self.contextPosition = 1
        self.lineNumber = 1
        
    def skipWS(self):
        while self.source[self.sourcePosition].strip() == "":
            if self.source[self.sourcePosition] == "\n": 
                self.contextPosition = 1
                self.lineNumber += 1
            self.sourcePosition += 1
            self.contextPosition += 1
    
    def isLiteral(self):
        
        pos = self.sourcePosition
        lexeme = ""
        
        def isString():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos] == '"':
                pos += 1
                while self.source[pos] != '"':
                    lexeme += self.source[pos]; pos += 1; self.contextPosition += 1
                self.tokens.append(Token(TokenType.STRING, lexeme, self.contextPosition-len(lexeme), self.lineNumber))
                self.sourcePosition = pos+1
                return True
            else: return False
            
        def isNumber():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isdigit():
                while self.source[pos].isdigit():
                    lexeme += self.source[pos]; pos += 1; self.contextPosition += 1
                self.tokens.append(Token(TokenType.NUMBER, lexeme, self.contextPosition-len(lexeme), self.lineNumber))
                self.sourcePosition = pos
                return True
            else: return False

        def isTypeID():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isalpha() and self.source[pos].isupper():
                while self.source[pos].isalnum() or self.source[pos] == "_":
                    lexeme += self.source[pos]; pos += 1; self.contextPosition += 1
                if isSelfType(lexeme) : token = Token(TokenType.SELF_TYPE, lexeme, self.contextPosition-len(lexeme), self.lineNumber)
                else                  : token = Token(TokenType.TYPE_ID, lexeme, self.contextPosition-len(lexeme), self.lineNumber)
                self.tokens.append(token)
                self.sourcePosition = pos
                return True
            else: return False 
        
        def isObjID():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isalpha():
                while self.source[pos].isalnum() or self.source[pos] == "_":
                    lexeme += self.source[pos]; pos += 1; self.contextPosition += 1
                if isSelf(lexeme)      : token = Token(TokenType.SELF, lexeme, self.contextPosition-len(lexeme), self.lineNumber) 
                elif isKeyword(lexeme) : token = Token(keywords[lexeme], lexeme, self.contextPosition-len(lexeme), self.lineNumber) 
                else                   : token = Token(TokenType.OBJ_ID, lexeme, self.contextPosition-len(lexeme), self.lineNumber) 
                self.tokens.append(token)
                self.sourcePosition = pos
                return True
            else: return False 
        
        def isSelf(lexeme):
            if lexeme == "self": return True
            
        def isKeyword(lexeme):
            if keywords.get(lexeme) is not None: return True
        
        def isSelfType(lexeme):
            if lexeme == "SELF_TYPE": return True
        
        return (isTypeID() or isObjID() or isNumber() or isString())
    
    def isSingleCharacterToken(self):
        
        char = self.source[self.sourcePosition]  
        
        singleCharacterTokens = {
            "(" : TokenType.LEFT_PAREN,
            ")" : TokenType.RIGHT_PAREN,
            "{" : TokenType.LEFT_BRACE,
            "}" : TokenType.RIGHT_BRACE,
            "," : TokenType.COMMA,
            "." : TokenType.DOT,
            "-" : TokenType.MINUS,
            "+" : TokenType.PLUS,
            ":" : TokenType.COLON,
            ";" : TokenType.SEMICOLON,
            "*" : TokenType.STAR,
            "=" : TokenType.EQ,
            "<" : TokenType.LT,
            ">" : TokenType.GT,
            "<=" : TokenType.LTOE,
            ">=" : TokenType.GTOE
        }
        
        TTYPE = singleCharacterTokens.get(char)
        
        if TTYPE is None: return False
        
        token = Token(TTYPE, char, self.contextPosition-1, self.lineNumber)
        self.tokens.append(token)
        self.sourcePosition += 1; self.contextPosition += 1
        return True
        
    #TODO: add comment support -> (* this is a comment *)
    def scan(self) -> bool:
        while self.sourcePosition < len(self.source):
            self.skipWS()
            if not (self.isLiteral() or self.isSingleCharacterToken()): 
                error = Error(self.sourcePosition, self.lineNumber, f"Syntax error -> {self.lineNumber}:{self.sourcePosition}" )
                self.errors.append(error)
                self.sourcePosition += 1

class TokenType(Enum):
    
    # Literals
    STRING = 1; NUMBER = 2; TYPE_ID = 3; OBJ_ID = 4
    SELF = 5; SELF_TYPE = 6
    
    # Single-character tokens
    LEFT_PAREN = 7; RIGHT_PAREN = 8; LEFT_BRACE = 9
    RIGHT_BRACE = 10; COMMA = 11; DOT = 12; MINUS = 13
    PLUS = 14; COLON = 15; SEMICOLON = 16; SLASH = 17; STAR = 18
    EQ = 19; LT = 20; GT = 21; LTOE = 22; GTOE = 23
    
    # keywords, keywords are case insensitive (except for true and false)
    CLASS = 24; ELSE = 25; FALSE = 26; FI = 27
    IF = 28; IN = 29; INHERITS = 30; ISVOID = 31
    LET = 32; LOOP = 33; POOL = 34; THEN = 35
    WHILE = 36; CASE = 37; ESAC = 38; NEW = 39
    OF = 40; NOT = 41; TRUE = 42
    
keywords = {
    "class"    :  TokenType.CLASS,
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
        return f'''
              TokenType        : {self.tokenType.name}
              lexeme           : {self.lexeme}
              contextPosition  : {self.contextPosition}
              line             : {self.line}
              '''
        
class Error:
    contextPosition : int
    line            : int
    errorMessage    : str
    
    def __init__(self, contextPosition, line, errorMessage):
        self.contextPosition = contextPosition
        self.line = line
        self.errorMessage = errorMessage
        
    def __repr__(self) -> str:
        return f'''
              contextPosition  : {self.contextPosition}
              line             : {self.line}
              errorMessage     : {self.errorMessage}
              '''


lexer = Lexer("example.cl")
lexer.scan()
print("Tokens")
for token in lexer.tokens:
    print(token)
print("ERRORS")
for error in lexer.errors:
    print(error)