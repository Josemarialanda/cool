from lexer import Token, TokenType
import sys

class Node:
    def __init__(self, lexeme):
        self.left   = None
        self.right  = None
        self.lexeme = lexeme
    
'''
Cool grammar (syntax)

program ::= [[ class; ]]+
class   ::= class TYPE_ID [inherits TYPE_ID] { [[feature; ]]∗ }
feature ::= OBJ_ID( [ formal [[, formal]]∗ ] ) : TYPE_ID { expr }
          | OBJ_ID : TYPE_ID [ <- expr ]
formal  ::= OBJ_ID : TYPE_ID
expr    ::= OBJ_ID <- expr
          | expr[@TYPE_ID].ID( [ expr [[, expr]]∗ ] )
          | OBJ_ID( [ expr [[, expr]]∗ ] )
          | if expr then expr else expr fi
          | while expr loop expr pool
          | { [[expr; ]]+ }
          | let OBJ_ID : TYPE_ID [ <- expr ] [[, OBJ_ID : TYPE_ID [ <- expr ]]]∗ in expr
          | case expr of [[OBJ_ID : TYPE_ID => expr; ]]+ esac
          | new TYPE_ID
          | isvoid expr
          | expr + expr
          | expr − expr
          | expr ∗ expr
          | expr / expr
          | ˜expr
          | expr < expr
          | expr <= expr
          | expr = expr
          | not expr
          | (expr)
          | OBJ_ID
          | number
          | string
          | true
          | false
'''

precedence = [TokenType.DOT,
              TokenType.AT,
              TokenType.TILDE,
              TokenType.ISVOID,
              [TokenType.STAR,TokenType.DOT],
              [TokenType.PLUS,TokenType.MINUS],
              [TokenType.LTOE,TokenType.LT,TokenType.EQ],
              TokenType.NOT,
              TokenType.ASSIGN]

class Parser:
    
    tokens : 'list[Token]'
    parseTree : Node # will store parse tree here
    
    def __init__(self, tokens):
        self.parseStatus = True
        self.tokens = tokens
        self.position = -1
        self.currentToken = self.tokens[self.position]
        
    def parse(self):
        self.PROGRAM()
        print("Success!")
        
    def next(self, step = 1):
        self.position += step
        self.currentToken = self.tokens[self.position]
        return self.tokens[self.position].tokenType
    
    def hasNext(self):
        return self.peek() != TokenType.EOF
    
    def peek(self, lookahead = 1):
        return self.tokens[self.position+lookahead].tokenType
    
    def FAIL(self, errorMessage = "Syntax error"):
        sys.exit(f"{errorMessage} : {self.currentToken.line}:{self.currentToken.contextPosition}")
    
    def PROGRAM(self):
        self.CLASS_()
        self.SEMICOLON()
        while self.hasNext():
            self.CLASS_()
            self.SEMICOLON()
        
    def CLASS_(self):
        self.CLASS()
        self.TYPE_ID()
        if self.peek() == TokenType.INHERITS:
            self.next()
            self.TYPE_ID()
        self.LEFT_BRACE()
        while self.peek() != TokenType.RIGHT_BRACE:
            self.FEATURE()
            self.SEMICOLON()
        self.RIGHT_BRACE()
        
    def FEATURE(self):
        
        def FEATURE1():
            if self.peek() != TokenType.RIGHT_PAREN:            
                self.formal()
                while self.peek() != TokenType.RIGHT_PAREN:
                    self.COMMA()
                    self.formal()
            self.RIGHT_PAREN()
            self.COLON()
            self.TYPE_ID()
            self.LEFT_BRACE()
            self.EXPR()
            self.RIGHT_BRACE()
        
        def FEATURE2():
            self.TYPE_ID()
            if self.peek() == TokenType.ASSIGN:
                self.ASSIGN()
                self.EXPR()
        
        self.OBJ_ID()
        if self.peek() == TokenType.LEFT_PAREN:
            self.next() 
            FEATURE1()
        if self.peek() == TokenType.COLON: 
            self.next() 
            FEATURE2()
    
    def formal(self):
        self.OBJ_ID()
        self.COLON()
        self.TYPE_ID()
    
    def EXPR(self):
        
        position = self.position
        token = self.tokens[position].tokenType
            
        def EXPR1():
            self.OBJ_ID()
            self.ASSIGN()
            self.EXPR()
        
        def EXPR2():
            self.EXPR()
            if self.peek() == TokenType.AT:
                self.AT()
                self.TYPE_ID()
            self.DOT()
            self.OBJ_ID()
            self.LEFT_PAREN()
            if self.peek() != TokenType.RIGHT_PAREN:
                self.EXPR()
                if self.peek() == TokenType.COMMA:
                    while self.peek() != TokenType.RIGHT_PAREN:
                        self.COMMA()
                        self.EXPR()
            self.RIGHT_PAREN()
        
        def EXPR3():
            self.OBJ_ID()
            self.LEFT_PAREN()
            if self.peek() != TokenType.RIGHT_PAREN:
                self.EXPR()
                if self.peek() == TokenType.COMMA:
                    while self.peek() != TokenType.RIGHT_PAREN:
                        self.COMMA()
                        self.EXPR()
            self.RIGHT_PAREN()
        
        def EXPR4():
            self.IF()
            self.EXPR()
            self.THEN()
            self.EXPR()
            self.ELSE()
            self.EXPR()
            self.FI()
        
        def EXPR5():
            self.WHILE()
            self.EXPR()
            self.LOOP()
            self.EXPR()
            self.POOL()
        
        def EXPR6():
            self.LEFT_BRACE()
            if self.peek() != TokenType.RIGHT_BRACE:
                self.EXPR()
                self.SEMICOLON()
                while self.peek() != TokenType.RIGHT_BRACE:
                    self.EXPR()
                    self.SEMICOLON()
            self.RIGHT_BRACE()
        
        def EXPR7():
            self.LET()
            self.OBJ_ID()
            self.COLON()
            self.TYPE_ID()
            if self.peek() == TokenType.ASSIGN:
                self.ASSIGN()
                self.EXPR()
            if self.peek() == TokenType.COMMA:
                while self.peek() != TokenType.IN:
                    self.COMMA()
                    self.OBJ_ID()
                    self.COLON()
                    self.TYPE_ID()
                    if self.peek() == TokenType.ASSIGN:
                        self.ASSIGN()
                        self.EXPR()
            self.IN()
            self.EXPR()
                
        def EXPR8():
            self.CASE()
            self.EXPR()
            self.OF()
            self.OBJ_ID()
            self.COLON()
            self.TYPE_ID()
            self.GTOE() # temporary... should be =>
            self.EXPR()
            self.SEMICOLON()
            if self.peek() == self.OBJ_ID:
                while self.peek() != TokenType.ESAC:
                    self.OBJ_ID()
                    self.COLON()
                    self.TYPE_ID()
                    self.GTOE() # temporary... should be =>
                    self.EXPR()
                    self.SEMICOLON()
            self.ESAC()
        
        def EXPR9():
            self.NEW()
            self.TYPE_ID()
        
        def EXPR10():
            self.ISVOID()
            self.EXPR()
        
        def EXPR11():
            self.PLUS()
            self.EXPR()
        
        def EXPR12():
            self.MINUS()
            self.EXPR()
        
        def EXPR13():
            self.STAR()
            self.EXPR()
        
        def EXPR14():
            self.SLASH()
            self.EXPR()
        
        def EXPR15():
            self.TILDE()
            self.EXPR()
        
        def EXPR16():
            self.LT()
            self.EXPR()
        
        def EXPR17():
            self.LTOE()
            self.EXPR()
        
        def EXPR18():
            self.EQ()
            self.EXPR()
        
        def EXPR19():
            self.NOT()
            self.EXPR()
        
        def EXPR20():
            self.LEFT_PAREN()
            self.EXPR()
            self.RIGHT_PAREN()
        
        def EXPR21():
            self.OBJ_ID()
        
        def EXPR22():
            self.NUMBER()
        
        def EXPR23():
            self.STRING()
        
        def EXPR24():
            self.TRUE()
        
        def EXPR25():
            self.FALSE()
            
        if self.peek() == TokenType.OBJ_ID:
            if self.peek(2) == TokenType.ASSIGN: EXPR1()
            elif self.peek(2) == TokenType.LEFT_PAREN: EXPR3()
            else: EXPR21()
        elif self.peek() == TokenType.IF: EXPR4()
        elif self.peek() == TokenType.WHILE: EXPR5()
        elif self.peek() == TokenType.LEFT_BRACE: EXPR6()
        elif self.peek() == TokenType.LET: EXPR7()
        elif self.peek() == TokenType.CASE: EXPR8()
        elif self.peek() == TokenType.NEW: EXPR9()
        elif self.peek() == TokenType.ISVOID: EXPR10()
        elif self.peek() == TokenType.TILDE: EXPR15()
        elif self.peek() == TokenType.NOT: EXPR19()
        elif self.peek() == TokenType.LEFT_PAREN: EXPR20()
        elif self.peek() == TokenType.NUMBER: EXPR22()
        elif self.peek() == TokenType.STRING: EXPR23()
        elif self.peek() == TokenType.TRUE: EXPR24()
        elif self.peek() == TokenType.FALSE: EXPR25()
        else: # expr case
            self.EXPR()
            if self.peek() == TokenType.PLUS: EXPR11()
            elif self.peek() == TokenType.MINUS: EXPR12()
            elif self.peek() == TokenType.STAR: EXPR13()
            elif self.peek() == TokenType.SLASH: EXPR14()
            elif self.peek() == TokenType.LT: EXPR16()
            elif self.peek() == TokenType.LTOE: EXPR17()
            elif self.peek() == TokenType.EQ: EXPR18()
            else: EXPR2()

    # terminals
    
    STRING      = lambda self: self.next() == TokenType.STRING      or self.FAIL()
    NUMBER      = lambda self: self.next() == TokenType.NUMBER      or self.FAIL()
    TYPE_ID     = lambda self: self.next() == TokenType.TYPE_ID     or self.FAIL()
    OBJ_ID      = lambda self: self.next() == TokenType.OBJ_ID      or self.FAIL()
    SELF        = lambda self: self.next() == TokenType.SELF        or self.FAIL()
    SELF_TYPE   = lambda self: self.next() == TokenType.SELF_TYPE   or self.FAIL()
    LEFT_PAREN  = lambda self: self.next() == TokenType.LEFT_PAREN  or self.FAIL()
    RIGHT_PAREN = lambda self: self.next() == TokenType.RIGHT_PAREN or self.FAIL()
    LEFT_BRACE  = lambda self: self.next() == TokenType.LEFT_BRACE  or self.FAIL()
    RIGHT_BRACE = lambda self: self.next() == TokenType.RIGHT_BRACE or self.FAIL()
    COMMA       = lambda self: self.next() == TokenType.COMMA       or self.FAIL()
    DOT         = lambda self: self.next() == TokenType.DOT         or self.FAIL()
    MINUS       = lambda self: self.next() == TokenType.MINUS       or self.FAIL()
    PLUS        = lambda self: self.next() == TokenType.PLUS        or self.FAIL()
    COLON       = lambda self: self.next() == TokenType.COLON       or self.FAIL()
    SEMICOLON   = lambda self: self.next() == TokenType.SEMICOLON   or self.FAIL()
    SLASH       = lambda self: self.next() == TokenType.SLASH       or self.FAIL()
    STAR        = lambda self: self.next() == TokenType.STAR        or self.FAIL()
    EQ          = lambda self: self.next() == TokenType.EQ          or self.FAIL()
    LT          = lambda self: self.next() == TokenType.LT          or self.FAIL()
    GT          = lambda self: self.next() == TokenType.GT          or self.FAIL()
    LTOE        = lambda self: self.next() == TokenType.LTOE        or self.FAIL()
    GTOE        = lambda self: self.next() == TokenType.GTOE        or self.FAIL()
    ASSIGN      = lambda self: self.next() == TokenType.ASSIGN      or self.FAIL()
    TILDE       = lambda self: self.next() == TokenType.TILDE       or self.FAIL()
    AT          = lambda self: self.next() == TokenType.AT          or self.FAIL()
    CLASS       = lambda self: self.next() == TokenType.CLASS       or self.FAIL()
    ELSE        = lambda self: self.next() == TokenType.ELSE        or self.FAIL()
    FALSE       = lambda self: self.next() == TokenType.FALSE       or self.FAIL()
    FI          = lambda self: self.next() == TokenType.FI          or self.FAIL()
    IF          = lambda self: self.next() == TokenType.IF          or self.FAIL()
    IN          = lambda self: self.next() == TokenType.IN          or self.FAIL()
    INHERITS    = lambda self: self.next() == TokenType.INHERITS    or self.FAIL()
    ISVOID      = lambda self: self.next() == TokenType.ISVOID      or self.FAIL()
    LET         = lambda self: self.next() == TokenType.LET         or self.FAIL()
    LOOP        = lambda self: self.next() == TokenType.LOOP        or self.FAIL()
    POOL        = lambda self: self.next() == TokenType.POOL        or self.FAIL()
    THEN        = lambda self: self.next() == TokenType.THEN        or self.FAIL()
    WHILE       = lambda self: self.next() == TokenType.WHILE       or self.FAIL()
    CASE        = lambda self: self.next() == TokenType.CASE        or self.FAIL()
    ESAC        = lambda self: self.next() == TokenType.ESAC        or self.FAIL()
    NEW         = lambda self: self.next() == TokenType.NEW         or self.FAIL()
    OF          = lambda self: self.next() == TokenType.OF          or self.FAIL()
    NOT         = lambda self: self.next() == TokenType.NOT         or self.FAIL()
    TRUE        = lambda self: self.next() == TokenType.TRUE        or self.FAIL()
    EOF         = lambda self: self.peek() == TokenType.EOF