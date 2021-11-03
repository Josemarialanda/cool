from lexer import Lexer
from parser import Parser
import sys

def main(source):
    lexer = Lexer(source)
    lexer.scan()
    if lexer.errors != []:
        for error in lexer.errors:
            print(error)
        sys.exit("One or more syntax errors")
    else:
        # feed tokens to parser
        pass

if __name__ == "__main__":
    if (len(sys.argv)-1) != 1: print("Argument error!")
    else:
        try:
            source = sys.argv[1]
            main(source)
        except FileNotFoundError:
            print("File not found!")