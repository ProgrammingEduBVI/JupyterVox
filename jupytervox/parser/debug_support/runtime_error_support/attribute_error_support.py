'''
JVox's debugging support for AttributeError.
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

def get_attribute_error_column(error_msg, code, line_no, verbose=True):
    '''
    Find the column number of the error attribute.

    Input:
    1. error_msg: the "AttributeError:..." message
    2. code: the code of the errored cell, all of the code in the cell should be
             passed in
    3. line_no: line number of the statement that cause the error
    4. verbose: enable verbose output or not

    Return:
    1. col_no: column number, or -1, if cannot find it
    '''

    # construct return object
    ret_val = types.SimpleNamespace()
    
    # extract the name of the attribute from error message
    pattern = "AttributeError: 'list' object has no attribute \'(.+)\'"
    p = re.compile(pattern)
    regex_ret = p.search(error_msg)

    if regex_ret is None:
        # did not find match
        print("Failed to find error attribute name in message:", error_msg)
        ret_val.col_no = 0
        return ret_val

    if verbose:
        attr_name = regex_ret.group(1)
        print("Find error attribute name:", regex_ret.group(1))

    #################################################################
    # Use regex to find the attribute in line.
    # Cannot find the attribute with Python AST because PyAST does not
    # prove an attribute's column number
    #################################################################

    # retrieve the error line
    error_line = code.split('\n')[line_no-1]

    # use regex to search for ".attr_name"
    founds = []
    for match in re.finditer(f".{attr_name}", error_line):
        founds.append(match.start()+1) # add one to skip '.' 

    if len(founds) == 0:
        print(f"failed to find attribute {attr_name} in code at line {line_no}:")
        print(code)
        print(f"The attribute error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    elif len(founds) > 1:
        print(f"Found more than one attributes {attr_name} in code at line",
              f"{line_no}:")
        print(code)
        print(f"The name error is {error_msg}")
        ret_val.col_no = 0
        return ret_val
    
    # Found one variable that matches, return the column number.  Note that,
    # need to add 1 since regex's column offset starts at 0, not 1
    ret_val.col_no = founds[0] + 1
    return ret_val


def handle_attribute_error(error_msg, code, line_no, support_type, extra_data,
                           verbose=True):
    '''
    Dispatcher for AttributeError handling. Invokes the corresponding error
    handler based on the "support_type" requested.

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
        return get_attribute_error_column(error_msg, code, line_no, verbose)
    else:
        print("AttributeError handling: unsupported request type: ",
              support_type)
        return None

    # should not reach here
    return None
