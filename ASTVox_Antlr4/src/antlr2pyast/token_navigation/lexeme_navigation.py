'''
Code for navigating through the lexemes within a statement. 
'''

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# AST tree generation/conversion packages
from converter import antlr2pyast
from converter import tools
import ast

# add parent field for each tree node in PyAST tree
def pyast_tree_link_parent(node, level=0):
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    item.parent = node
                    pyast_tree_link_parent(item, level=level+1)
        elif isinstance(value, ast.AST):
            value.parent = node
            pyast_tree_link_parent(value, level=level+1)

    return # nothing to return, dummy

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


# return the uppermost-level ANTRL4 AST tree node of the lexeme at current
# cursor position. From the tree node, it's possible to get the lexeme text
# (getText method), start/stop tokens (start/stop fields), and the corresponding
# PyAST tree (pyast_tree field).
#
# Input parameters:
#   stmt: the statement to parse
#   cur_pos: current cursor position in the statement
# 
# Return:
#   uppermost-level ANTLR4 node for current lexeme
def find_readable_antlr4_node(node, cur_pos):
  # if the input is a terminal node, returns None. There is no PyAST tree
  # node for a terminal node,
  if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
    return None

  # check if the cursor is in the current node
  start_pos = node.start.start
  end_pos = node.stop.stop

  # if current cursor position is not in this tree node, return None
  if (cur_pos < start_pos) or (cur_pos > end_pos):
    return None

  # check if current node's PyAST tree is readable or not. If yes, return this
  # node. With a recursive tree traversal algorithm, the first node that got hit
  # should also be the highest-level readable node
  if is_node_readable(node.pyast_tree):
    return node

  # if curent node is not readable, check if any of its children can be read,
  # return on the first hit
  for i in range(node.getChildCount()):
    c = node.getChild(i)

    return_node = find_readable_antlr4_node(c, cur_pos)

    if return_node is not None:
      return return_node

  # failed to find the readable node
  return None
 
# Find the uppermost-level ANTRL4 AST tree node of the lexeme at current cursor
# position, given an ANTRL4 AST tree. From the tree node, it's possible to get
# the lexeme text (getText method), start/stop tokens (start/stop fields), and
# the corresponding PyAST tree (pyast_tree field).
#
# Input parameters:
#   stmt: the statement to parse
#   cur_pos: current cursor position in the statement
# 
# Return:
#   uppermost-level ANTLR4 node for current lexeme
def find_cur_lexeme(stmt, cur_pos, verbose=False):
    # parse the statement in to an ANTLR4 AST tree
    a4tree = antlr2pyast.generate_ast_tree(stmt)

    if verbose:
        print("Anltr4 AST tree is:")
        tools.print_a4ast_tree(a4tree)

    # convert the ANTLR4 tree into Python AST tree
    pyast_tree, converter = antlr2pyast.convert_tree(a4tree)
    if verbose:
        print("Python AST tree is:")
        tools.ast_visit(pyast_tree)

    # find the highest-level Antlr4 tree node for the lexeme at
    # current cursor position, cur_pos
    readable_a4_node = find_readable_antlr4_node(a4tree, cur_pos)
    if readable_a4_node is None:
        if verbose:
            print("Failed to locate the start/end of readable lexeme for "+
                  "statement:", stmt, "at position:", cur_pos)
        return None


    # ready to return. debug print before returning
    if verbose:
        print("Found the highest readable lexeme:", readable_a4_node.getText())
        print("ANTRL4 tree node is:")
        tools.print_a4ast_tree(readable_a4_node)
        print("Corresponding PyAST node is:")
        tools.ast_visit(readable_a4_node.pyast_tree)

    return readable_a4_node



################################################################################
# Old code
################################################################################

# return the uppermost-level ANTRL4 AST tree node of the lexeme at current
# cursor position. From the tree node, it's possible to get the lexeme text
# (getText method), start/stop tokens (start/stop fields), and the corresponding
# PyAST tree (pyast_tree field).
#
# Input parameters:
#   stmt: the statement to parse
#   cur_pos: current cursor position in the statement
# 
# Return:
#   uppermost-level ANTLR4 node for current lexeme
def find_cur_lexeme_old(stmt, cur_pos, verbose=False):

    # check if cursor is at a space, for spaces, we are not returning any lexeme.
    # Basically, we assume a space should be read. Not sure if this is a correct
    
    # parse the statement in to an ANTLR4 AST tree
    a4tree = antlr2pyast.generate_ast_tree(stmt)

    if verbose:
        print("Anltr4 AST tree is:")
        tools.print_a4ast_tree(a4tree)

    # convert the ANTLR4 tree into Python AST tree
    pyast_tree, converter = antlr2pyast.convert_tree(a4tree)
    # add parent link to the converted PyAST tree
    pyast_tree_link_parent(pyast_tree)

    if verbose:
        print("Python AST tree is:")
        tools.ast_visit(pyast_tree)

    # find the lowest-level Antlr4 tree node for the lexeme at
    # current cursor position, cur_pos
    found, anl4_node, pyast_node = find_cursor_in_ANL4tree(a4tree, cur_pos)
    if not found:
        if verbose:
            print("Failed to find the token for statement:", stmt,
                  "at position:", cur_pos,
                  "; char at cursor is: " + stmt[cur_pos] + ".")

        return None
    
    if verbose:
        print("PyAST node for lexeme at current cursor:")
        tools.ast_visit(pyast_node)

    # back-tracing the PyAST tree to find the highest level of readable lexeme
    # from the pyast_node.
    readable_pyast_node = find_readable_pyast_node(pyast_node)

    if readable_pyast_node is None:
        if verbose:
            print("Failed to find readable lexeme for statement:", stmt,
                  "at position:", cur_pos)

        return None

    if verbose:
        print("Highest readable PyAST node for lexeme at current cursor:")
        tools.ast_visit(readable_pyast_node)

    # find the highest-level ANTLR4 tree node that is linked to the
    # readable_pyast_node, or readable lexeme. This ANTRL4 node can help us find
    # the start and end of the lexeme.
    readable_a4_node = find_pyast_node_in_ANL4tree(a4tree, readable_pyast_node)
    if readable_a4_node is None:
        if verbose:
            print("Failed to locate the start/end of readable lexeme for "+
                  "statement:", stmt, "at position:", cur_pos)
        return None


    # ready to return. debug print before returning
    if verbose:
        print("Found the highest readable lexeme:", readable_a4_node.getText())
        print("ANTRL4 tree node is:")
        tools.print_a4ast_tree(readable_a4_node)

    return readable_a4_node
    
# backtracking to find the PyAST node that can read
# assuming the lowest level node is readable.
def find_readable_pyast_node(node):

  # check if node is readable or not
  if not is_node_readable(node):
    return None

  # get node's parent
  parent = node.parent

  # if parent is readable, check parent's parent recursively
  if is_node_readable(parent):
    return find_readable_pyast_node(parent)
  else:
  # if parent is not readable, return this node instead
    return node

# find the highest level ANTLR4 node corresponds to the PyAST node
def find_pyast_node_in_ANL4tree(a4_node, pyast_node):

  # if terminal node, we have reached the bottom, and no node found
  if isinstance(a4_node, antlr4.tree.Tree.TerminalNodeImpl):
    return None

  # if found, return current ANTLR4 node
  if a4_node.pyast_tree is pyast_node:
    return a4_node

  # check each child
  for i in range(a4_node.getChildCount()):
    c = a4_node.getChild(i)
    if not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl):
      # not a terminal node, keep searching
      ret_node = find_pyast_node_in_ANL4tree(c, pyast_node)
      if ret_node is not None:
        # found! just return the first one
        return ret_node

  # failed to find the PyAST node
  return None

# given the cursor position (cursor_pos), find the nearest ANTLR4 AST tree node
# and corresponding PyAST tree node
# returns:
#   True/False: find the terminal node or not
#   ANTLR4 tree node
#   AST tree node
def find_cursor_in_ANL4tree(node, cursor_pos):

  # if terminal node, return False and Nones. Should never reach here
  if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
    print("find_cursor_in_ANL4tree: hit term node, shouldn't happen, bug?")
    return False,None,None

  # check each child
  for i in range(node.getChildCount()):
    c = node.getChild(i)
    if not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl):
      # not a terminal node, keep searching
      found, anl4_node, pyast_node = find_cursor_in_ANL4tree(c, cursor_pos)
      if found:
        # found the terminal node, pass on the returned nodes
        return found, anl4_node, pyast_node
    else:
      # a terminal node, check if it contains the curespor position
      s = c.getSymbol()
      # print(s.text, s.start, s.stop)
      if (s.start <= cursor_pos) and (cursor_pos <= s.stop):
        # cursor is in this terminal node
        return True, node, node.pyast_tree


  # failed to find the terminal node
  return False, None, None
