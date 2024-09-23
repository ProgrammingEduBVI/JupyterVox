'''
Code for checking if a simple line of Python statement is correct or not.
Partially complete statement is consider as correct, e.g. "if a>b:"
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

# Error listener support for ANTLR4
from antlr4.error import ErrorListener

# import sibling packages
from . import utils as debug_utils

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
            # -1 is EOF, statement terminated early. May not be a real parsing
            # error.  Raise JVoxIncompleteSyntaxError
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
        
        #raise JVoxOtherParsingError("reportAttemptingFullContext")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex,
                                 prediction, configs):
        if self.verbose:
            print("Single line checker: ANTLR4 context sensitivity error")
            
        #raise JVoxOtherParsingError("reportContextSensitivity")


def add_prefix_for_dangling_elif(stmt):
    '''
    Add an "if" part if the input is a line of "elif" stmt.

    Need to do this because elif cannot be parsed by itself
    '''

    # this is the dummy "if" part to be added
    dummy_if = "if 5>4: return;\n"
    # add it before "elif" stmt
    stmt = dummy_if + stmt

    return stmt


def preprocess_stmt(stmt, verbose=True):
    '''
    Preprocess the single line statement for syntax check.

    Proprocessing steps:
    - remove leading space
    - For "elif", "else", "except", add dummpy prefix
    - return the number of leading spaces

    Return a SimpleNamespace object:
    1. leading_space_count: number of leading spaces
    2. stmt : preprocessed statement
    '''
    # return value
    ret_val = types.SimpleNamespace()
    ret_val.leading_space_count = 0
    
    # Count how many leading spaces are there, we will remove them when checking
    # syntax. but after checking, we need to adjust the offset for these removed
    # spaces
    while (stmt[ret_val.leading_space_count] == ' '):
        ret_val.leading_space_count += 1

    # remove leading spaces so that parsers won't report indentation error
    ret_val.stmt =  stmt.lstrip()

    # Add dummy prefix if the input is a line of "elif" or "else" or "except"
    # stmt. Need to do this because elif cannot be parsed by itself
    if ret_val.stmt.startswith("else") or ret_val.stmt.startswith("elif"):
        # this is the dummy "if" part to be added
        dummy_if = "if 5>4: return;\n"
        # add it before "elif" stmt
        ret_val.stmt = dummy_if + ret_val.stmt
    elif ret_val.stmt.startswith("except"):
        # this is the dummy "try" part to be added
        dummy_try = "try: jvoxa=1;\n"
        # add it before "elif" stmt
        ret_val.stmt = dummy_try + ret_val.stmt
        
    return ret_val

def is_correct_partial_statement(stmt, syntax_error, verbose=True):
    '''
    Check if a statement is a partial but correct statement. E.g., "if a>b:".

    Note that some statement can be correct even it is just partially
    completely, e.g. "elif a>b:" is a perfectly OK one line statement

    However, some partial statement can still be wrong. e.g., "[1,2,",
    is a wrong partial statement, it should be closed with ']'.

    Input parameters:
    1. stmt: the statement to check
    2. syntax_error, the SyntaxError exception from Python AST parser
    

    Return:
    1. True: is correct (and partial) statement
    2. False: not correct statement
    
    '''

    # add a new line character so that ANTLR4 will not panic
    if not stmt.endswith('\n'):
        stmt += '\n'

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

    try:
        tree = parser.single_input()
    except JVoxIncompleteSyntaxError as e:
        # Incomplete statement, but parse correctly so far. But we Need to first
        # check if this statement is really correct or not using the
        # syntax_error input.
        #if syntax_error.msg.startswith("\'[\' was never closed"):
        if syntax_error.msg.has("never closed"):
            # this is a real error
            return False

        # there could be other incorrect, partially parse-able statement
        # need more testing

        # this is indeed a correct partial statement
        return True
        
    except JVoxRealSyntaxError as e:
        # ANTLR4 also can't parse it, read syntax error
        return False

    # well, we really should not reach here
    print("partial statement check returns correct non-partial statement, " +
          "strange!")
    
    return True

def single_line_syntax_check(stmt, verbose=True):
    '''
    Check if a single line of Python statement parsing is correct or not.

    Note that some statement can be correct even it is just partially
    completely, e.g. "elif a>b:" is a perfectly OK one line statement

    However, some partial statement can still be wrong. e.g., "[1,2,",
    is a wrong partial statement, it should be closed with ']'.

    Input:
        1. stmt: the one line statement
        2. verbose: enable verbose output
    Returns a SimpleNamespace object:
        1. error_msg
        2. error_no: 0 - correct, no error; 1 - partial correct;
                     2 - syntax error; 
        3. orig_exception: For real syntax error, this is the SyntaxError
                           exception from Python AST parsing

    '''

    # preprocess the input statement
    prep = preprocess_stmt(stmt, verbose)

    # prepare return value
    ret_val = types.SimpleNamespace()
    ret_val.no = 0
    ret_val.error_no = 0 # being optimistic, assuming no error
    ret_val.error_msg = "There is no syntax error. "
    ret_val.offset = 1 # dummy offset

    # check if statement is empty
    if prep.stmt == "" or prep.stmt == "\n":
        ret_val.error_msg = "Empty line. "
        return ret_val

    # Let Python AST parse the statement, and catch the SyntaxError
    syntax_error = None
    try:
        ast.parse(prep.stmt)
    except SyntaxError as e:
        syntax_error = e

    # if no syntax_error
    indentation_note = (f"Note that, it has {prep.leading_space_count} " +
                        "leading spaces. ")
    if syntax_error is None:
        # add leading space count to the error message
        if prep.leading_space_count > 0:
            ret_val.error_msg += indentation_note
        return ret_val

    # if there is syntax error, use ANTRL to check if it is partial statement
    if is_correct_partial_statement(prep.stmt, syntax_error, verbose):
        # correct partial statement
        ret_val.error_no = 1
        ret_val.error_msg = ("Parsed correctly so far, " +
                             "but this line is a partial statement. ")
        ret_val.offset = 1 # dummy offset
        # add leading space count to the error message
        if prep.leading_space_count > 0:
            ret_val.error_msg += indentation_note
    else:
        # indeed has syntax error
        ret_val.error_no = 2
        # Get the offset number. Need to adjust for removed spaces
        ret_val.offset = syntax_error.offset + prep.leading_space_count 
        ret_val.error_msg = (str(syntax_error.msg) +
                             f", from column {ret_val.offset}. " )      
        ret_val.orig_exception = syntax_error
        # correct the reading of punctuation marks in the error message
        ret_val.error_msg = debug_utils.make_punc_readable(ret_val.error_msg)
        
    return ret_val
    
    
######################## old code should remove someday ###################
def single_line_parsing_check_old(stmt, verbose=True):
    '''
    Check if a single line of Python statement parsing is correct or not.

    Note that some statement can be correct even it is just partially
    completely, e.g. "elif a>b:" is a perfectly OK one line statement

    However, some partial statement can still be wrong. e.g., "[1,2,",
    is a wrong partial statement, it should be closed with ']'.

    Input:
        1. stmt: the one line statement
        2. verbose: enable verbose output
    Returns a SimpleNamespace object:
        1. error_msg
        2. error_no: 0 - correct, no error; 1 - partial correct;
                     2 - syntax error; 3 - other parsing error
        3. orig_exception: For real syntax error, this is the SyntaxError
                           exception from Python AST parsing

    '''
    stmt += '\n'
    
    # Count how many leading spaces are there, we will remove them when checking
    # syntax. but after checking, we need to adjust the offset for these removed
    # spaces
    leading_space_count = 0
    while (stmt[leading_space_count] == ' '):
        leading_space_count += 1
    
    # remove leading spaces. These will cause ANTRL4 to accept the input. Not
    # sure why.
    stmt = stmt.lstrip()

    # special treatment for partial statements: "elif"
    if stmt.startswith("elif"):
        stmt = add_prefix_for_dangling_elif(stmt)

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
    ret = types.SimpleNamespace()
    ret.error_no = 0 # being optimistic, assuming no error
    ret.error_msg = "There is no syntax error. "
    ret.offset = 1 # dummy offset
    
    try:
        tree = parser.single_input()
    except JVoxIncompleteSyntaxError as e:
        if e.original_msg.endswith("expecting {NEWLINE, ';'}"):
            # if just missing newline or ';' characters, we can treat this as
            # correct
            pass
        else:
            # Incomplete statement, but parse correctly so far.
            # Need to first check if this statement is really correct or not
            partial_correct, e2 = partial_statement_check(stmt, verbose)
            if partial_correct:
                # correct partial statement
                ret.error_no = 1
                ret.error_msg = ("There is no syntax error, " +
                                 "but this line is a partial statement. ")
                ret.orig_error_msg = e.original_msg
                ret.offset = 1 # dummy offset
            else:
                # incorrect partial statement
                ret.error_no = 2
                ret.error_msg = str(e2.msg) + f", from column {e2.offset}. " 
                # Get the offset number. Need to adjust for removed spaces
                ret.offset = e2.offset + leading_space_count 
                ret.orig_exception = e2
    except JVoxRealSyntaxError as e:
        # real parsing error
        ret.error_no = 2
        # for real parsing error, return Python's own parsing error message
        try:
            ast.parse(stmt, filename="JVoxDummyFile")
        except Exception as e2: # should be a SyntaxError type exception 
            ret.error_msg = str(e2.msg) + f", from column {e2.offset}." 
            # Get the offset number. Need to adjust for removed spaces
            ret.offset = e2.offset + leading_space_count 
            ret.orig_exception = e2
    except JVoxOtherParsingError as e:
        # real parsing error
        ret.error_no = 3
        ret.error_msg = e.message
        ret.offset = 1 # dummy offset

    # Append indentation information at the end, if statement is correct
    if ret.error_no <= 1 and  leading_space_count > 0:
        ret.error_msg += (f"Note that, it has {leading_space_count} "+
                          "leading spaces. ")

    # correct the reading of punctuation marks in the error message
    ret.error_msg = debug_utils.make_punc_readable(ret.error_msg)

    # done, return
    return ret
        

def partial_statement_check(stmt, verbose):
    '''
    Check partial/incomplete statement. Some can be correct, some can be wrong.

    Note that some statement can be correct even it is just partially
    completely, e.g. "elif a>b:" is a perfectly OK one line statement

    However, some partial statement can still be wrong. e.g., "[1,2,",
    is a wrong partial statement, it should be closed with ']'.

    Return:
    1. True/False: correct or wrong,
    2. SyntaxError or None: if wrong, also return the syntax error

    '''

    # use Python AST to get its SyntaxError
    exception = None
    try:
        ast.parse(stmt)
    except SyntaxError as e:
        exception = e

    # no error, strange
    if exception is None:
        print("Strange, partial line check returns no error for statement:",
              stmt)
        return True, None

    # has error, check if statement is really wrong
    if exception.msg.startswith("\'[\' was never closed"):
        # this is a real error
        return False,exception

    # there could be other errors, need more testing

    return True, None

