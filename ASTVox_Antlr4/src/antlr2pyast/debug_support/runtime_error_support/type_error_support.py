'''
JVox's debugging support for TypeError.
'''

# system packages
import types # for SimpleNamespace
import re # for using regex to extract error information
import pydoc # for converting type name string to type

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

def get_operand_type_error_column(error_msg, code, line_no, verbose=True):
    '''
    Find the column number of the operator who has the operand error.

    Input:
    1. error_msg: the "TypeError:..." message
    2. code: the code of the errored cell, all of the code in the cell should be
             passed in
    3. line_no: line number of the statement that cause the error
    4. verbose: enable verbose output or not

    Return:
    1. col_no: column number, or -1, if cannot find it
    '''

    # construct return object
    ret_val = types.SimpleNamespace()
    
    # extract the name of the operator from error message
    pattern = "TypeError: unsupported operand type\(s\) for (.+): \'(.+)\' and \'(.+)\'"
    p = re.compile(pattern)
    regex_ret = p.search(error_msg)

    if regex_ret is None:
        # did not find match
        print("Failed to find error operator in message:", error_msg)
        ret_val.col_no = 0
        return ret_val

    if verbose:
        op_name = regex_ret.group(1)
        print("Find error operator:", regex_ret.group(1))

    #################################################################
    # Use tokenization to find the operator in line.
    # Cannot find the operator with Python AST because PyAST does not
    # prove an operator's column number.
    #################################################################

    # retrieve the error line
    error_line = code.split('\n')[line_no-1]
    
    # tokenize the string
    input_stream = antlr4.InputStream(error_line)
    lexer = Python3Lexer(input_stream)
    tokens = lexer.getAllTokens()

    # iterate over the tokens to find the name
    founds = []
    offset = -1
    for t in tokens:
        if t.text == op_name:
            founds.append(t.start)

    if len(founds) == 0:
        print(f"failed to find attribute {op_name} in code at line {line_no}:")
        print(code)
        print(f"The attribute error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    elif len(founds) > 1:
        print(f"Found more than one attributes {op_name} in code at line",
              f"{line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    
    # Found one variable that matches, return the column number.  Note that,
    # need to add 1 since ANTLR4's column offset starts at 0, not 1
    ret_val.col_no = founds[0] + 1
    return ret_val

def get_list_index_type_error_column(error_msg, code, line_no, verbose=True):
    '''
    Find the column number of the list index that is causing this error

    Input:
    1. error_msg: the "TypeError:..." message
    2. code: the code of the errored cell, all of the code in the cell should be
             passed in
    3. line_no: line number of the statement that cause the error
    4. verbose: enable verbose output or not

    Return:
    1. col_no: column number, or -1, if cannot find it
    '''

    # construct return object
    ret_val = types.SimpleNamespace()
    
    # extract the name of the operator from error message
    pattern = "TypeError: list indices must be integers or slices, not (.+)"
    p = re.compile(pattern)
    regex_ret = p.search(error_msg)

    if regex_ret is None:
        # did not find match
        print("Failed to find wrong list index type in message:", error_msg)
        ret_val.col_no = 0
        return ret_val

    if verbose:
        type_name = regex_ret.group(1)
        print("Find wrong index type:", regex_ret.group(1))

    # determine the Python type based on type_name
    try:
        wrong_type = pydoc.locate(type_name)
    except Exception as e:
        print(f"Failed to find type for type name {type_name}",
              f"with exception {e}")
        ret_val.col_no = 0
        return ret_val

    # parse the cell code
    try:
        tree = ast.parse(code)
    except Exception as e:
        # really should not get here, the syntax should be correct before
        # generating a runtime error
        print("Parsing error when handling wrong index type error with exception,", e)
        ret_val.col_no = 0
        return ret_val

    if verbose:
        debug_utils.ast_visit(tree)

    # find the name in the code
    data = types.SimpleNamespace(wrong_type=wrong_type, line_no=line_no)
    nodes = debug_utils.find_node_at_line(tree, data, has_wrong_index_node,
                                          verbose)

    if len(nodes) == 0:
        print(f"failed to wrong typed index of {wrong_type} in code at line {line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    elif len(nodes) > 1:
        print(f"Found more than one wrong typed index of {wrong_type} in code at line",
              f"{line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    
    # Found one variable that matches, return the column number.  Note that,
    # need to add 1 since Python AST's column offset starts at 0, not 1
    ret_val = types.SimpleNamespace()
    ret_val.col_no = nodes[0].col_offset + 1
    return ret_val

def get_any_index_type_error_column(error_msg, code, line_no, verbose=True):
    '''
    Find the column number of the list index that is causing this error

    Input:
    1. error_msg: the "TypeError:..." message
    2. code: the code of the errored cell, all of the code in the cell should be
             passed in
    3. line_no: line number of the statement that cause the error
    4. verbose: enable verbose output or not

    Return:
    1. col_no: column number, or -1, if cannot find it
    '''

    # construct return object
    ret_val = types.SimpleNamespace()

    # parse the cell code
    try:
        tree = ast.parse(code)
    except Exception as e:
        # really should not get here, the syntax should be correct before
        # generating a runtime error
        print("Parsing error when handling wrong index type error with exception,", e)
        ret_val.col_no = 0
        return ret_val

    if verbose:
        debug_utils.ast_visit(tree)

    # find the name in the code
    data = types.SimpleNamespace(line_no=line_no)
    nodes = debug_utils.find_node_at_line(tree, data, is_index_node, verbose)

    if len(nodes) == 0:
        print(f"failed to index/subscript in code at line {line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    elif len(nodes) > 1:
        print(f"Found more than index/subscrpit in code at line {line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    
    # Found one variable that matches, return the column number.  Note that,
    # need to add 1 since Python AST's column offset starts at 0, not 1
    ret_val = types.SimpleNamespace()
    ret_val.col_no = nodes[0].col_offset + 1
    return ret_val

def has_wrong_index_node(node, data):
    '''
    Given a tree node, check if it has an index node with a specific wrong
    type in it. If yes, return the wrong index node.

    Input:
    1. node: the node to be checked
    2. data: the data for checking, fields are,
       - wrong_type: the wrong index type to search for
       - line_no: line number of the error

    Return:
    1. node: None, if not found; otherwise the node to be returned

    '''

    # needs to be an ast.Subscript node at the correct line
    if (not isinstance(node, ast.Subscript) or
        node.lineno != data.line_no):
        return None

    # check if the slice field is a match
    if data.wrong_type == str:
        if ((not isinstance(node.slice, ast.Constant)) or
            (not isinstance(node.slice.value, str))):
            return None
        else:
            return node.slice
    elif data.wrong_type == tuple:
        if (not isinstance(node.slice, ast.Tuple)):
            return None
        else:
            return node.slice
    else:
        return None

def is_index_node(node, data):
    '''
    Given a tree node, check if it is an ast.Subscript node

    Input:
    1. node: the node to be checked
    2. data: the data for checking, fields are,
       - wrong_type: the wrong index type to search for
       - line_no: line number of the error

    Return:
    1. node: None, if not found; otherwise the node to be returned
    '''

    # needs to be an ast.Subscript node at the correct line
    if (isinstance(node, ast.Subscript) and
        node.lineno == data.line_no):
        return node.slice
    else:
        return None

    
def handle_type_error(error_msg, code, line_no, support_type, extra_data,
                      verbose=True):
    '''
    Dispatcher for type error handling. Invokes the corresponding error handler
    based on the "support_type" requested and error message

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

    if (error_msg.startswith("TypeError: unsupported operand type(s) for") and
        support_type == "col_no"):
        return get_operand_type_error_column(error_msg, code, line_no, verbose)
    elif (error_msg.startswith("TypeError: list indices must be integers or " +
                               "slices, not") and
        support_type == "col_no"):
        return get_list_index_type_error_column(error_msg, code, line_no,
                                                verbose)
    elif (error_msg.startswith("TypeError: slice indices must be integers " +
                               "or None or have an __index__ method") and
        support_type == "col_no"):
        return get_any_index_type_error_column(error_msg, code, line_no,
                                               verbose)
    elif support_type == "col_no":
        # other find column number request is not supported yet
        print("TypeError handling: unsupported col_no request for message:",
              error_msg)
        ret_val = types.SimpleNamespace(col_no=0)
        return ret_val
    else:
        print("TypeError handling: unsupported request type: ", support_type)
        return None

    # should not reach here
    return None

