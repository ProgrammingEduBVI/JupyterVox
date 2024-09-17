'''
Code for checking if a simple line Python is correct or not.
Partially complete statement is consider as correct, e.g. "if a>b:"
'''

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# AST tree generation/conversion packages
from converter import antlr2pyast
from converter import tools
import ast

# Error listener support for ANTLR4
from antlr4.error import ErrorListener

# Custom exception for JVox parsing
class JVoxRealSyntaxError(SyntaxError):
    '''
    Real syntax error instead of incomplete statements
    '''
    pass

class JVoxIncompleteSyntaxError(SyntaxError):
    '''
    Syntax error because the statement is incomplete, e.g., "if a>b:"
    is an acceptable one line statement, but it is incomplete in terms
    of parsing.
    '''
    pass

class JVoxOtherParsingError(Exception):
    '''
    Other parsing errors, including ANTRL4 errors of AttemptingFullContext​,
    ContextSensitivity​, and Ambiguity.
    '''
    pass

# Custom error listener to raise the correct exceptions
class JVox_Single_Line_Error_Listener(ErrorListener.ErrorListener):
    '''
    Custom ANTRL4 parsing error listener class for JVox

    1. For Syntax error: if it is due to incomplete statement, raise
       JVoxIncompleteSyntaxError; if it is other syntax errors, raise
       JVoXRealSyntaxError.
    2. For all other errors of  AttemptingFullContext​, ContextSensitivity​, and
       Ambiguity, raise JVoxOtherParsingError.    
    '''

    def __init__(self, verbose = True):
        self.verbose = True
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if offendingSymbol.type == -1:
            # -1 is EOF, statement terminated early. not a real parsing error.
            # Raise JVoxIncompleteSyntaxError
            if self.verbose:
                print("Single line checker: incomplete parsing error:", msg)
            e = JVoxIncompleteSyntaxError("Incomplete statement")
            e.raw_error = e
            e.lineno = line
            e.offset = column
            e.original_msg = msg
            raise e
        else:
            # Other syntax error, these are real errors.
            # Raise JVoxRealSyntaxError
            if self.verbose:
                print("Single line checker: Other syntax error:", msg)
            e = JVoxRealSyntaxError("Other syntax errors")
            e.raw_error = e
            e.lineno = line
            e.offset = column
            e.original_msg = msg
            raise e

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact,
                        ambigAlts, configs):
        if self.verbose:
            print("Single line checker: ANTLR4 ambiguity error")
                
        raise JVoxOtherParsingError("reportAmbiguity")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex,
                                    stopIndex, conflictingAlts, configs):
        if self.verbose:
            print("Single line checker: ANTLR4 attempting full context error")
        
        raise JVoxOtherParsingError("reportAttemptingFullContext")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex,
                                 prediction, configs):
        if self.verbose:
            print("Single line checker: ANTLR4 context sensitivity error")
            
        raise JVoxOtherParsingError("reportContextSensitivity")


def single_line_parsing_check(stmt, verbose=True):
    '''
    Check if a single line of Python statement parsing is correct or not.

    Input:
        1. stmt: the one line statement
        2. verbose: enable verbose output
    Returns a dict with the following fields:
        1. error_msg
        2. error_no: 0 - correct, no error; 1 - partial correct;
                     2 - syntax error; 3 - other parsing error
    '''

    # create the ANTLR4 parser class
    input_stream = antlr4.InputStream(stmt)
    lexer = Python3Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = Python3Parser(stream)

    # supress the console error reporting, necessary?
    # for l in parser._listeners: 
    #     if isinstance(l, antlr4.error.ErrorListener.ConsoleErrorListener):
    #         parser._listeners.remove(l)
    #         break

    # add JVox error listener
    parser.addErrorListener(JVox_Single_Line_Error_Listener(verbose))

    # parse and handle the error
    ret = {} # should use SimpleNamespace, see https://stackoverflow.com/a/41765294
    ret["error_no"] = 0 # being optimistic, assuming no error
    ret["error_msg"] = ""
    try:
        tree = parser.single_input()
    except JVoxIncompleteSyntaxError as e:
        if e.original_msg.endswith("expecting {NEWLINE, ';'}"):
            # if just missing newline or ';' characters, we can treat this as
            # correct
            pass
        else:
            # incomplete statement, but parse correctly so far
            ret["error_no"] = 1
            ret["error_msg"] = e.original_msg
    except JVoxRealSyntaxError as e:
        # real parsing error
        ret["error_no"] = 2
        # for real parsing error, return Python's own parsing error message
        try:
            ast.parse(stmt, filename="")
        except Exception as e2: # should be a SyntaxError type exception 
            ret["error_msg"] = str(e2)
    except JVoxOtherParsingError as e:
        # real parsing error
        ret["error_no"] = 3
        ret["error_msg"] = e.message

    # done, return
    return ret
        
        