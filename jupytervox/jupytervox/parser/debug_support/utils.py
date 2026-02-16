#
# Utility functions, classes for debugging support
#

import ast

def make_punc_readable(msg):
    '''
    Makes certain punctuation marks readable in error mssages
    '''
    
    # make '(' to 'left paren'
    msg = msg.replace("\'(\'", "\'left paren\'")
    
    # make ')' to 'right paren'
    msg = msg.replace("\')\'", "\'right paren\'")

    # make ':' to 'colon'
    msg = msg.replace("\':\'", "\'colon\'")

    # read '['
    msg = msg.replace("\'[\'", "\'left bracket\'")

    # read ']'
    msg = msg.replace("\']\'", "\'right bracket\'")

    # read '{'
    msg = msg.replace("\'{\'", "\'left curly bracket\'")

    # read '}'
    msg = msg.replace("\'}\'", "\'right curly bracket\'")
    
    return msg

def find_node_at_line(node, data, check_func, verbose=True):
    '''
    Given an AST tree node, find the desired node in its children.

    Input:
    1. node: the root node of the AST tree
    2. data: data used to find a match, it's field depends on the implementation
             of check_func
    3. check_func: the check_func
    4. verbose: verbose output
    
    Return:
    1. a list of node that matches
    '''

    # create the list to be returned
    found = []

    # check if this node is the one we are searching for
    ret_node = check_func(node, data)
    if (ret_node is not None):
        # match found
        found.append(ret_node)

    # search the children 
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    found = found + find_node_at_line(item, data, check_func,
                                                      verbose)
        elif isinstance(value, ast.AST):
            found = found + find_node_at_line(value, data, check_func,
                                              verbose)

    return found


# AST print function with line and column number
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

        
