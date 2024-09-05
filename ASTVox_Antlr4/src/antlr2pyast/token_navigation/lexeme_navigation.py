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

  return False # by default, consider node is not readable

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
def find_cur_lexeme(stmt, cur_pos, verbose=False):
    # parse the statement in to an ANTLR4 AST tree
    a4tree = antlr2pyast.generate_ast_tree(stmt)

    if verbose:
        tools.print_a4ast_tree(a4tree)

    # convert the ANTLR4 tree into Python AST tree
    pyast_tree, converter = antlr2pyast.convert_tree(a4tree)
    # add parent link to the converted PyAST tree
    pyast_tree_link_parent(pyast_tree)

    if verbose:
        tools.ast_visit(pyast_tree)

    # find the lowest-level Antlr4 tree node for the lexeme at
    # current cursor position, cur_pos
    found, anl4_node, pyast_node = find_cursor_in_ANL4tree(a4tree, cur_pos)
    if not found:
        if verbose:
            print("Failed to find the lexeme for statement:", stmt,
                  "at position:", cur_pos)

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
    
    
