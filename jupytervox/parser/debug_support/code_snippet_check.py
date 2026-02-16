'''
Code for checking if a snippet of Python code.
'''

# system packages
import types # for SimpleNamespace

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# AST tree generation/conversion packages
from converter import antlr2pyast
from converter import tools
import ast

# import sibling packages
from . import utils as debug_utils

def code_snippet_syntax_check(stmts, verbose=True):
    '''
    Check if a code snippet's syntax is correct or not.

    Input:
        1. stmts: the one line statement
        2. verbose: enable verbose output
    Returns a SimpleNamespace object with the following fields:
        1. error_msg
        2. line_no: line number of error site
        3. offset: column number of error site
        4. orig_exception: original SyntaxError exception
        5. error_no: 0: correct, no error; 1: syntax error
    '''

    # parse and handle the error
    ret = types.SimpleNamespace()
    ret.error_no = 0 # being optimistic, assuming no error
    ret.error_msg = ""

    try:
        tree = ast.parse(stmts)
    except SyntaxError as e:
        ret.error_no = True
        # handle the syntax errors
        ret.error_msg = str(e.msg) + ", from column " + str(e.offset)
        # correct the reading of punctuation marks in the error message
        ret.error_msg = debug_utils.make_punc_readable(ret.error_msg)
        # record line information
        ret.line_no = e.lineno
        ret.offset = e.offset
        ret.orig_exception = e
    
    if ret.error_no == 0:
        # code snippet is correct
        ret.error_msg = "Code snippet syntax is correct"
        ret.line_no = 1
        ret.orig_exception = None
        ret.offset = 1

    # done, return
    return ret
        
        
