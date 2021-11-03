from lexer import Token, TokenType

'''
Cool syntax

program ::= [[class;]]+
class   ::= class TYPE [[inherits TYPE]] { [[feature]]* }
feature ::= ID ()

....

'''

precedence = [TokenType.DOT,
              TokenType.AT,
              TokenType.TILDE,
              TokenType.ISVOID,
              [TokenType.STAR,TokenType.DOT],
              [TokenType.PLUS,TokenType.MINUS],
              [TokenType.LTOE,TokenType.LT,TokenType.EQ],
              TokenType.NOT,
              TokenType.ASSIGN,
              ]

class Parser:
    
    tokens : 'list[Token]'
    
    
    
    