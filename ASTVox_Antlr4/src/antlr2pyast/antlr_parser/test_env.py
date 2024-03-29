# Used to test the coding envorinment
# Python3 and Antlr4 versions must match
# I am currentl using Python3 3.9/3.10 and Antlr4 4.13.0

from antlr4 import *
from Python3Lexer import Python3Lexer
from Python3Parser import Python3Parser

str = "False\n"

def main():
    #input_stream = InputStream('print("hello world")\n')
    input_stream = InputStream(str)
    lexer = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    tree = parser.single_input()
    print(type(tree))
    print(tree.getRuleIndex())
    print(tree.children)
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()
