from codeGen import CodeGen
from lexer import Lexer
from parser import Parser
import sys

def main(source):
    # Feed source to lexer
    lexer = Lexer(source)
    lexer.scan()
    if lexer.errors != []:
        for error in lexer.errors:
            print(error)
        sys.exit("syntax errors")
    else:
        # Feed token stream to parser
        parser = Parser(lexer.tokens)
        AST = parser.parse()
        # Feed AST to code generator
        codeGen = CodeGen(AST)
        

if __name__ == "__main__":
    if (len(sys.argv)-1) != 1: print("Argument error!")
    else:
        try:
            source = sys.argv[1]
            main(source)
        except FileNotFoundError:
            print("File not found!")