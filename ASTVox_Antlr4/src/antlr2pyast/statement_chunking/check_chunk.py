'''
Code for checking if a chunk is readable. 
'''
# import system packages
import ast

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# check if an ast.BinOp readable
# only basic ones can be read
def is_binOp_readable(node):
    readable = True;
    # only read if left/right operands are num or constant or ID
    if ((not isinstance(node.left, ast.Num)) and
        (not isinstance(node.left, ast.Constant)) and
        (not isinstance(node.left, ast.Name))):
      readable = False
    if ((not isinstance(node.right, ast.Num)) and
        (not isinstance(node.right, ast.Constant)) and
        (not isinstance(node.right, ast.Name))):
      readable = False

    # if one of the operand is string, also unreadable
    if (isinstance(node.left, ast.Constant) and
        isinstance(node.left.value, str)):
      readable = False

    if (isinstance(node.right, ast.Constant) and
        isinstance(node.right.value, str)):
      readable = False

    # return if BinOp is readable
    return readable;

# check if an ast.Compare readable
# only basic ones can be read
def is_compare_readable(node):
    readable = True;
    # only readable if left operand is num or constant or ID
    if ((not isinstance(node.left, ast.Num)) and
        (not isinstance(node.left, ast.Constant)) and
        (not isinstance(node.left, ast.Name))):
      readable = False

    # only readable if there is only one comparators
    if len(node.comparators) > 1:
        readable = False

    # only readable if there the comparator is simple
    if ((not isinstance(node.comparators[0], ast.Num)) and
        (not isinstance(node.comparators[0], ast.Constant)) and
        (not isinstance(node.comparators[0], ast.Name))):
      readable = False

    # return if BinOp is readable
    return readable;

# check if an ast.Assign readable
# only basic ones can be read
def is_assignment_readable(node):
    readable = True;
    # only read if this is an simple assignment
    
    if ((not len(node.targets) == 1) and 
        (not isinstance(node.targets[0], ast.Name))):
      readable = False
    if ((not isinstance(node.value, ast.Num)) and
        (not isinstance(node.value, ast.Constant)) and
        (not isinstance(node.value, ast.Name))):
      readable = False

    # return if assignment is readable
    return readable;

# check if an ast.AugAssign readable
# only basic ones can be read
def is_augAssign_readable(node):
    readable = True;
    # only read if this is an simple Augmented assignment
    if not isinstance(node.target, ast.Name):
      readable = False
    if ((not isinstance(node.value, ast.Num)) and
        (not isinstance(node.value, ast.Constant)) and
        (not isinstance(node.value, ast.Name))):
      readable = False

    # return if assignment is readable
    return readable;

# check if an ast.Call node readable
# only basic ones can be read 
def is_call_readable(node):
    readable = True;
    # only read if this is an simple function call

    # function name should be a simple name, not a
    # class/package member function
    if not isinstance(node.func, ast.Name):
      readable = False

    # only readable if there are one or two arguments
    if not len(node.args) <= 2:
        readable = False

    # only readable if argument is simple
    if ((len(node.args) >= 1) and
        (not isinstance(node.args[0], ast.Constant)) and
        (not isinstance(node.args[0], ast.Name))):
      readable = False

    if ((len(node.args) >= 2) and
        (not isinstance(node.args[1], ast.Constant)) and
        (not isinstance(node.args[1], ast.Name))):
      readable = False

    # only readable if no keyworded params
    if len(node.keywords) != 0:
        readable = False

    # return if assignment is readable
    return readable;

# check if an PyAST node is readable or not
def is_node_readable(node):
    #  constants are readable
    if isinstance(node, ast.Constant):
        return True;

    #  Names are readable
    if isinstance(node, ast.Name):
        return True;

    #  Numbers are readable
    if isinstance(node, ast.Num):
        return True;

    # simple binary operation is readable
    if isinstance(node, ast.BinOp):
        return is_binOp_readable(node)

    # simple comparison is readable
    if isinstance(node, ast.Compare):
        return is_compare_readable(node)

    # simple assignments are readable
    if isinstance(node, ast.Assign):
        return is_assignment_readable(node)

    # simple assignments are readable
    if isinstance(node, ast.AugAssign):
        return is_augAssign_readable(node)
                      
    # simple function call/invocation is readable
    if isinstance(node, ast.Call):
        return is_call_readable(node)

    return False # by default, consider node is not readable

# check if an PyAST node is readable or not
def is_node_readable_with_chunk_len(node, chunk_len):
    # determine the number of tokens in the chunk
    token_count = all_tokens_in_node(node)
    # determine if a node is a readable chunk only based on the number
    # of tokens in the chunk
    if (token_count <= chunk_len):
       return True
    else:
       return False

def all_tokens_in_node(node):
   '''
   Travesal the AST tree from the input node, and return all tokens in the 
   tree.

   Tree traversal is probably an overkill, but its more modular this way.   
   '''
   token_count = 0
   if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
      token_count = 1
   else:
      for i in range(node.getChildCount()):
         token_count += all_tokens_in_node(node.getChild(i))

   return token_count
    