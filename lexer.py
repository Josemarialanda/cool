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
            else: self.contextPosition += 1
            self.sourcePosition += 1
            if self.sourcePosition+1 > len(self.source): return True
            
    def isLiteral(self):
        
        pos = self.sourcePosition
        lexeme = ""
        
        def advancePosition():
            nonlocal pos
            nonlocal lexeme
            lexeme += self.source[pos]; pos += 1; self.contextPosition += 1
            
        def appendToken(tokenType):
            self.tokens.append(Token(tokenType, 
                                     lexeme, 
                                     self.contextPosition-len(lexeme), 
                                     self.lineNumber))
        
        def isString():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos] == '"':
                pos += 1
                while self.source[pos] != '"':
                    advancePosition()
                    if pos+1 > len(self.source): break
                appendToken(TokenType.STRING)
                self.sourcePosition = pos+1
                return True
            else: return False
            
        def isNumber():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isdigit():
                while self.source[pos].isdigit():
                    advancePosition()
                    if pos+1 > len(self.source): break
                appendToken(TokenType.NUMBER)
                self.sourcePosition = pos
                return True
            else: return False

        def isTypeID():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isalpha() and self.source[pos].isupper():
                while self.source[pos].isalnum() or self.source[pos] == "_":
                    advancePosition()
                    if pos+1 > len(self.source): break
                if isSelfType(lexeme) : appendToken(TokenType.SELF_TYPE)
                else                  : appendToken(TokenType.TYPE_ID)
                self.sourcePosition = pos
                return True
            else: return False 
        
        def isObjID():
            nonlocal pos
            nonlocal lexeme
            if self.source[pos].isalpha():
                while self.source[pos].isalnum() or self.source[pos] == "_":
                    advancePosition()
                    if pos+1 > len(self.source): break
                if isSelf(lexeme)      : appendToken(TokenType.SELF)
                elif isKeyword(lexeme) : appendToken(keywords[lexeme])
                else                   : appendToken(TokenType.OBJ_ID)
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
            ">=" : TokenType.GTOE,
            "<-" : TokenType.ASSIGN,
            "~" : TokenType.TILDE,
            "@" : TokenType.AT
        }
        
        TTYPE = singleCharacterTokens.get(char)

        if TTYPE is None: return False
        elif TTYPE == TokenType.LT or TTYPE == TokenType.GT and self.sourcePosition < len(self.source):
            nextChar = self.source[self.sourcePosition+1]
            if nextChar == "=" or nextChar == "-": 
                self.sourcePosition += 1; self.contextPosition += 1
                if TTYPE == TokenType.GT and nextChar == "=": TTYPE = TokenType.GTOE; char += nextChar
                if TTYPE == TokenType.LT:
                    if nextChar == "=": TTYPE = TokenType.LTOE; char += nextChar
                    if nextChar == "-": TTYPE = TokenType.ASSIGN; char += nextChar
        
        token = Token(TTYPE, 
                      char, 
                      (self.contextPosition-1 if 
                       TTYPE == TokenType.LTOE or 
                       TTYPE == TokenType.GTOE or 
                       TTYPE == TokenType.ASSIGN 
                       else self.contextPosition), 
                      self.lineNumber)
        
        self.tokens.append(token)
        self.sourcePosition += 1; self.contextPosition += 1
        return True
        
    #TODO: add comment support -> (* this is a comment *)
    def scan(self) -> bool:
        while self.sourcePosition < len(self.source):
            if self.skipWS(): break
            if not (self.isLiteral() or self.isSingleCharacterToken()): 
                error = Error(self.contextPosition, self.lineNumber, f"Syntax error -> {self.lineNumber}:{self.contextPosition} | unkown symbol: {self.source[self.sourcePosition]}" )
                self.errors.append(error)
                self.sourcePosition += 1
                self.contextPosition += 1

class TokenType(Enum):
    
    # Literals
    STRING = 1; NUMBER = 2; TYPE_ID = 3; OBJ_ID = 4
    SELF = 5; SELF_TYPE = 6
    
    # Single-or-2-character tokens
    LEFT_PAREN = 7; RIGHT_PAREN = 8; LEFT_BRACE = 9
    RIGHT_BRACE = 10; COMMA = 11; DOT = 12; MINUS = 13
    PLUS = 14; COLON = 15; SEMICOLON = 16; SLASH = 17; STAR = 18
    EQ = 19; LT = 20; GT = 21; LTOE = 22; GTOE = 23; ASSIGN = 24
    TILDE = 25; AT = 26
    
    # keywords, keywords are case insensitive (except for true and false)
    CLASS = 27; ELSE = 28; FALSE = 29; FI = 30
    IF = 31; IN = 32; INHERITS = 33; ISVOID = 34
    LET = 35; LOOP = 36; POOL = 37; THEN = 38
    WHILE = 39; CASE = 40; ESAC = 41; NEW = 42
    OF = 43; NOT = 44; TRUE = 45
    
keywords = {
    "class"    :  TokenType.CLASS,
    "else"     :  TokenType.ELSE,
    "false"    :  TokenType.FALSE,
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
    "true"     :  TokenType.TRUE
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