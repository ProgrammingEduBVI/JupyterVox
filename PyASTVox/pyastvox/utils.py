# utility functions
import ast
import re

def str_node(node):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
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

# output node to out_str,and visit its children
def ast_visit_non_print(node, out_str, level=0):
    #print('  ' * level + str_node(node))
    out_str.append('  ' * level + str_node(node))
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    ast_visit_non_print(item, out_str, level=level+1)
        elif isinstance(value, ast.AST):
            ast_visit_non_print(value, out_str, level=level+1)

def make_token_readable(token_string):
    '''
    Make token string more readable
    '''
    # space
    if token_string == ' ':
        return "space"
    
    # operators
    if token_string == "=":
        return "equals"
    elif token_string == "+":
        return "plus"
    elif token_string == "-":
        return "minus"

    # braces
    if token_string == "{":
        return "left curly brace"
    elif token_string == "}":
        return "right curly brace"
    elif token_string == "[":
        return "left bracket"
    elif token_string == "]":
        return "right bracket"
    
    # underscore
    if token_string == "_":
        return "underscore"

    # quote
    if token_string == "\"":
        return "quote"
    elif token_string == "'":
        return "single quote"
    
    # parenthesis
    if token_string == "(":
        return "left paren"
    elif token_string == ")":
        return "right paren"

    # for strings, add "string"
    if token_string[0] == "\"":
        return "string " + token_string
    elif token_string[0] == "'":
        return "string " + token_string
    
    # avoid reading a/A as an article
    if token_string == "a" or token_string == "A":
        return token_string + "-"

    # other tokens, just return the token string
    return token_string


def make_statement_readable(stmt):
    '''
    Make token string more readable
    '''

    # replace spaces first
    s = stmt.replace(' ', ' space ')
    
    # operators
    s = s.replace("=", "equals")
    s = s.replace("+", "plus")
    s = s.replace("-", "minus")
    s = s.replace("*", "asterisk")
    s = s.replace("/", "slash")

    # braces
    s = s.replace("{", "left curly brace")
    s = s.replace("}", "right curly brace")
    s = s.replace("[", "left bracket")
    s = s.replace("]", "right bracket")
    
    # underscore
    s = s.replace("_", "underscore")

    # quote
    s = s.replace("\"", "quote")
    s = s.replace("'", "single quote")
    
    # parenthesis
    s = s.replace("(", "left paren")
    s = s.replace(")", "right paren")
    
    # avoid reading a/A as an article
    if token_string == "a" or token_string == "A":
        return token_string + "-"

    # other tokens, just return the token string
    return s
