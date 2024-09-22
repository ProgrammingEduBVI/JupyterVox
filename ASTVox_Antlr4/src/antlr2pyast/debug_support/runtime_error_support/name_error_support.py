'''
JVox's debugging support for NameError.
'''

# system packages
import types # for SimpleNamespace
import re # for using regex to extract error information

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# AST tree generation/conversion packages
from converter import antlr2pyast
from converter import tools
import ast

# import sibling packages
from .. import utils as debug_utils

def get_name_error_column(error_msg, code, line_no, verbose=True):
    '''
    Find the column number of the error name.

    I only used lexical analysis (tokenization) to search for the name, because
    it does require significantly amount of work to parse than tokenize. The
    problem is always leading spaces, partial statement etc.

    Input:
    1. error_msg: the "NameError:..." message
    2. code: the code of the errored cell, all of the code in the cell should be
             passed in
    3. line_no: line number of the statement that cause the error
    4. verbose: enable verbose output or not

    Return:
    1. col_no: column number, or -1, if cannot find it
    '''

    # extract the name of the variable from error message
    pattern = "NameError: name \'(.*)\' is not defined"
    p = re.compile(pattern)
    regex_ret = p.search(error_msg)

    if regex_ret is None:
        # did not find match
        print("Failed to find error obj name in message:", error_msg)
        return -1

    if verbose:
        var_name = regex_ret.group(1)
        print("Find error obj name:", regex_ret.group(1))


    # parse the cell code
    try:
        tree = ast.parse(code)
    except Exception as e:
        # really should not get here, the syntax should be correct before
        # generating a runtime error
        print("Parsing when handling name error with exception,", e)
        return -1

    if verbose:
        ast_visit(tree)

    # find the name in the code
    nodes = find_name_in_line(tree, var_name, line_no, verbose)

    if len(nodes) == 0:
        print(f"failed to find variable {var_name} in code at line {line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        return -1
    elif len(nodes) > 1:
        print(f"Found more than one variable {var_name} in code at line",
              f"{line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        return -1
    
    # Found one variable that matches, return the column number.  Note that,
    # need to add 1 since Python AST's column offset starts at 0, not 1
    ret_val = types.SimpleNamespace()
    ret_val.col_no = nodes[0].col_offset + 1
    return ret_val
    
    # # tokenize the string
    # input_stream = antlr4.InputStream(stmt)
    # lexer = Python3Lexer(input_stream)
    # tokens = lexer.getAllTokens()

    # # iterate over the tokens to find the name
    # found_count = 0
    # offset = -1
    # for t in tokens:
    #     if t.text == error_name:
    #         found_count += 1
    #         if offset == -1:
    #             offset = t.start
                
    # # check if found one
    # if found_count == 0:
    #     print(f"Failed to find name: {error_name}, in statement: {stmt}, " +
    #           f"for error message: {error_msg}.")
    # elif found_count > 1:
    #     print(f"Find {found_count} instances of name: {error_name}, " + 
    #           f"in statement: {stmt}, for error message: {error_msg}.")
    # else:
    #     if verbose:
    #         print(f"Find name: {error_name}, at column {offset}, " +
    #               f"in statement: {stmt}, for error message: {error_msg}.")
    
    # return offset
        
def find_name_in_line(node, var_name, line_no, verbose=True):
    '''
    Given an AST tree node, find the name in its children at the
    specified line

    Input:
    1. node: the root node of the AST tree
    2. var_name: the name of the variable to be searched
    3. line_no: the line number of the variable to be searched
    4. verbose: verbose output
    
    Return:
    1. a list of node that matches
    '''

    # create the list to be returned
    found = []

    # check if this node is the one we are searching for
    if (isinstance(node, ast.Name) and node.id == var_name and
        node.lineno == line_no):
        # match found
        found.append(node)

    # search the children 
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    found = found + find_name_in_line(item, var_name, line_no,
                                                      verbose)
        elif isinstance(value, ast.AST):
            found = found + find_name_in_line(value, var_name, line_no,
                                              verbose)

    return found

def handle_name_error(error_msg, code, line_no, support_type, extra_data,
                      verbose=True):
    '''
    Dispatcher for name error handling. Invokes the corresponding error handler
    based on the "support_type" requested.

    Input:
    - error_msg: full error message
    - code: full code in cell
    - line_no: error line number
    - support_type: string that specifies the support requested
      possible value:
         - col_no: column of the variable causing name error
    - extra_data: other data (for future extension)
    - verbose: verbose output or not

    Return:
    - dictionary with fields for corresponding error's return values
    '''

    if support_type == "col_no":
        return get_name_error_column(error_msg, code, line_no, verbose)
    else:
        print("NameError handling: unsupported request type:", support_type)
        return None

    # should not reach here
    return None


def str_node(node):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        if hasattr(node, "col_offset"):
          col_text = f"(line: {node.lineno}, col: {node.col_offset})"
        else:
          col_text = ""
        return rv + ')' + col_text
    else:
        return repr(node)
def ast_visit(node, level=0):
    print('  ' * level + str_node(node))
    for field, value in ast.iter_fields(node):
        #print(field, "<xxxx>", value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    ast_visit(item, level=level+1)
        elif isinstance(value, ast.AST):
            ast_visit(value, level=level+1)
