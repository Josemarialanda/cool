from lexer import Token, TokenType
import sys
from anytree import Node
from anytree.exporter import DotExporter

class ParseTree:
    
    def __init__(self):
        self.root = Node("Program")
    
    def printTree(self):
        DotExporter(self.root,
        nodeattrfunc=lambda node: "fixedsize=true, width=1, height=1, shape=diamond",
        edgeattrfunc=lambda parent, child: "style=bold"
        ).to_picture("ParseTree.png")
    
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
              [TokenType.STAR,TokenType.SLASH],
              [TokenType.PLUS,TokenType.MINUS],
              [TokenType.LTOE,TokenType.LT,TokenType.EQ],
              TokenType.NOT,
              TokenType.ASSIGN]

class Parser:
    
    tokens : 'list[Token]'
    parseTree : ParseTree # TODO: generate parse tree
    
    def __init__(self, tokens):
        self.parseTree = ParseTree()
        self.tokens = tokens
        self.position = -1
        self.currentToken = self.tokens[self.position]
        
    def parse(self):
        self.PROGRAM(); 
        self.parseTree.printTree()
        return self.parseTree
        
    def next(self, step = 1):
        self.position += step
        self.currentToken = self.tokens[self.position]
        return self.tokens[self.position].tokenType
    
    def hasNext(self):
        return self.peek() != TokenType.EOF
    
    def peek(self, lookahead = 1):
        return self.tokens[self.position+lookahead].tokenType
    
    def FAIL(self, errorMessage):
        # self.currentToken = self.tokens[self.position-1]
        print(f'''
              Syntax error : {errorMessage}
              Line         : {self.currentToken.line}
              Column       : {self.currentToken.contextPosition}
              ''')
        sys.exit("Syntax errors")
    
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
        
        while self.peek() != TokenType.RIGHT_BRACE and self.peek(2) != TokenType.SEMICOLON:
            self.FEATURE()
            self.SEMICOLON()
        self.RIGHT_BRACE()
        
    def FEATURE(self):
        
        def FEATURE1():
            if self.peek() != TokenType.RIGHT_PAREN:         
                
                self.FORMAL()
                while self.peek() != TokenType.RIGHT_PAREN:
                    self.COMMA()
                    self.FORMAL()
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
    
    def FORMAL(self):
        self.OBJ_ID()
        self.COLON()
        self.TYPE_ID()
    
    def EXPR(self):

        def EXPR1():
            self.OBJ_ID()
            self.ASSIGN()
            self.EXPR()
        
        def EXPR2():
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
            elif self.peek(2) == TokenType.LEFT_PAREN:
                EXPR3()
                if self.peek() == TokenType.AT or self.peek() == TokenType.DOT: EXPR2()
            else:
                EXPR21()
                if self.peek() == TokenType.AT or self.peek() == TokenType.DOT: EXPR2()
                elif self.peek() == TokenType.PLUS: EXPR11()
                elif self.peek() == TokenType.MINUS: EXPR12()
                elif self.peek() == TokenType.STAR: EXPR13()
                elif self.peek() == TokenType.SLASH: EXPR14()
                elif self.peek() == TokenType.LT: EXPR16()
                elif self.peek() == TokenType.LTOE: EXPR17()
                elif self.peek() == TokenType.EQ: EXPR18()
                
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
    
    STRING      = lambda self, errorMessage = "Syntax error": self.next() == TokenType.STRING      or self.FAIL(errorMessage)
    NUMBER      = lambda self, errorMessage = "Syntax error": self.next() == TokenType.NUMBER      or self.FAIL(errorMessage)
    TYPE_ID     = lambda self, errorMessage = "Syntax error": self.next() == TokenType.TYPE_ID     or self.FAIL(errorMessage)
    OBJ_ID      = lambda self, errorMessage = "Syntax error": self.next() == TokenType.OBJ_ID      or self.FAIL(errorMessage)
    SELF        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.SELF        or self.FAIL(errorMessage)
    SELF_TYPE   = lambda self, errorMessage = "Syntax error": self.next() == TokenType.SELF_TYPE   or self.FAIL(errorMessage)
    LEFT_PAREN  = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LEFT_PAREN  or self.FAIL(errorMessage)
    RIGHT_PAREN = lambda self, errorMessage = "Syntax error": self.next() == TokenType.RIGHT_PAREN or self.FAIL(errorMessage)
    LEFT_BRACE  = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LEFT_BRACE  or self.FAIL(errorMessage)
    RIGHT_BRACE = lambda self, errorMessage = "Syntax error": self.next() == TokenType.RIGHT_BRACE or self.FAIL(errorMessage)
    COMMA       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.COMMA       or self.FAIL(errorMessage)
    DOT         = lambda self, errorMessage = "Syntax error": self.next() == TokenType.DOT         or self.FAIL(errorMessage)
    MINUS       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.MINUS       or self.FAIL(errorMessage)
    PLUS        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.PLUS        or self.FAIL(errorMessage)
    COLON       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.COLON       or self.FAIL(errorMessage)
    SEMICOLON   = lambda self, errorMessage = "Syntax error": self.next() == TokenType.SEMICOLON   or self.FAIL(errorMessage)
    SLASH       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.SLASH       or self.FAIL(errorMessage)
    STAR        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.STAR        or self.FAIL(errorMessage)
    EQ          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.EQ          or self.FAIL(errorMessage)
    LT          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LT          or self.FAIL(errorMessage)
    GT          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.GT          or self.FAIL(errorMessage)
    LTOE        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LTOE        or self.FAIL(errorMessage)
    GTOE        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.GTOE        or self.FAIL(errorMessage)
    ASSIGN      = lambda self, errorMessage = "Syntax error": self.next() == TokenType.ASSIGN      or self.FAIL(errorMessage)
    TILDE       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.TILDE       or self.FAIL(errorMessage)
    AT          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.AT          or self.FAIL(errorMessage)
    CLASS       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.CLASS       or self.FAIL(errorMessage)
    ELSE        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.ELSE        or self.FAIL(errorMessage)
    FALSE       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.FALSE       or self.FAIL(errorMessage)
    FI          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.FI          or self.FAIL(errorMessage)
    IF          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.IF          or self.FAIL(errorMessage)
    IN          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.IN          or self.FAIL(errorMessage)
    INHERITS    = lambda self, errorMessage = "Syntax error": self.next() == TokenType.INHERITS    or self.FAIL(errorMessage)
    ISVOID      = lambda self, errorMessage = "Syntax error": self.next() == TokenType.ISVOID      or self.FAIL(errorMessage)
    LET         = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LET         or self.FAIL(errorMessage)
    LOOP        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.LOOP        or self.FAIL(errorMessage)
    POOL        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.POOL        or self.FAIL(errorMessage)
    THEN        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.THEN        or self.FAIL(errorMessage)
    WHILE       = lambda self, errorMessage = "Syntax error": self.next() == TokenType.WHILE       or self.FAIL(errorMessage)
    CASE        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.CASE        or self.FAIL(errorMessage)
    ESAC        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.ESAC        or self.FAIL(errorMessage)
    NEW         = lambda self, errorMessage = "Syntax error": self.next() == TokenType.NEW         or self.FAIL(errorMessage)
    OF          = lambda self, errorMessage = "Syntax error": self.next() == TokenType.OF          or self.FAIL(errorMessage)
    NOT         = lambda self, errorMessage = "Syntax error": self.next() == TokenType.NOT         or self.FAIL(errorMessage)
    TRUE        = lambda self, errorMessage = "Syntax error": self.next() == TokenType.TRUE        or self.FAIL(errorMessage)
    EOF         = lambda self: self.peek() == TokenType.EOF