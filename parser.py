from lexer import Token, TokenType

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
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = -1
        self.word = self.tokens[self.position].tokenType
        
    def nextWord(self):
        self.position += 1
        self.word = self.tokens[self.position].tokenType
        return self.word
    
    def fail(self):
        # report syntax errors
        # attempt error recovery or exit
        print("Something went wrong...")
    
    def program(self):
        self.nextWord()
        if self.class_():
            if self.word.tokenType != TokenType.EOF: self.fail()
    
    def class_(self):
         if (self.word == TokenType.CLASS and 
             self.nextWord() == TokenType.TYPE_ID):
             if (self.nextWord() == TokenType.INHERITS and 
                 self.nextWord() == TokenType.TYPE_ID):
                 # in the middle of something here...
    
    def feature1(self):
        pass
    
    def feature2(self):
        pass
    
    def formal(self):
        pass
    
    def expr1(self):
        pass
    
    def expr2(self):
        pass
    
    def expr3(self):
        pass
    
    def expr4(self):
        pass
    
    def expr5(self):
        pass
    
    def expr6(self):
        pass
    
    def expr7(self):
        pass
    
    def expr8(self):
        pass
    
    def expr9(self):
        pass
    
    def expr10(self):
        pass
    
    def expr11(self):
        pass
    
    def expr12(self):
        pass
    
    def expr13(self):
        pass
    
    def expr14(self):
        pass
    
    def expr15(self):
        pass
    
    def expr16(self):
        pass
    
    def expr17(self):
        pass
    
    def expr18(self):
        pass
    
    def expr19(self):
        pass
    
    def expr20(self):
        pass
    
    def expr21(self):
        pass
    
    def expr22(self):
        pass
    
    def expr23(self):
        pass
    
    def expr24(self):
        pass
    
    def expr25(self):
        pass
    
    
    
    
    