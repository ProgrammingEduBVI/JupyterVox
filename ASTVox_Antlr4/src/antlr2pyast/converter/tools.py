# Antlr4 to Python AST
# Tool functions

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast
import traceback

# Recursively set the load/store context for node and all children 
def update_load_store(node:ast.AST, is_load = True):
  '''
  Recursively set the load/store context for node and all children 
  '''
  ##### Begin: for debugging###############
  # sometimes I don't know who is updating the ctx
  # if isinstance(node, ast.Name):
  #  print("updating", node, "Load:", is_load)
  #  for line in traceback.format_stack():
  #      print(line.strip())
  ##### End: for debugging###############

  # set load/store for this node
  load_or_store = ast.Load() if is_load else ast.Store()
  if hasattr(node, 'ctx') :
      node.ctx = load_or_store

  # set load/store for children
  for field, value in ast.iter_fields(node):
        #print(field, "<xxxx>", value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    update_load_store(item, is_load)
        elif isinstance(value, ast.AST):
            update_load_store(value, is_load)

  # post processing for ast.Subscript. For an ast.Subscript node, the
  # "value"s ctx must always be load(), since the value is the list
  # name, and list name is read-only. The above code is too "eager"
  # that it updates all children. Hence it may update list name to
  # Store(). This should be corrected.
  # the same probably also holds for the "slice" field, if it does not
  # allow assignments
  if isinstance(node, ast.Subscript):
    node.value.ctx = ast.Load()
    update_load_store(node.slice, is_load=True)
  # the same problem holds for ast.Attribute as well
  if isinstance(node, ast.Attribute):
    node.value.ctx = ast.Load()
    
  return

# Convert a list of Python AST nodes into a single AST node
# or an ast.Tuple.
def list_to_node_or_tuple(
    nodes:list,
    is_load = True,
    update_children = True):
  '''
  Convert a list of Python AST nodes into a single AST node or an ast.Tuple.
  This is usually needed when the list is used as a target or value of an AST
  node.
  If there is one item in the list, return that item's Python AST node.
  If there are more then one items, return a ast.Tuple.
  '''
  # get the load/store context
  load_or_store = ast.Load() if is_load else ast.Store()
  # if asked, correct the load/store context for all children
  if update_children:
    for n in nodes:
      if not n is None: # nodes can have None items, see the comments below
        update_load_store(n, is_load)

  if len(nodes) == 1:
    ast_node = nodes[0]
  else:
    # remove None in nodes list. This is need to handle a special case
    # mentioned in function expr.convert_testlist_star_expr
    nodes = [x for x in nodes if not (x is None)]
    # convert list to testlist
    ast_node = ast.Tuple(nodes, load_or_store)

  return ast_node

# print an ANTLR4 tree node
# this is a recursive function
def print_a4ast_tree_node(node, level):
  out_str = ""

  # print indents
  indent = "    "
  for i in range(level):
    out_str += indent

  # print the tree node
  #out_str += type(node).__name__
  out_str += str(type(node))#.__name__

  # Non-terminal nodes has more info and children to print
  if not isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
    out_str += "(Rule: " + str(node.getRuleIndex()) + ")"
    out_str += "(children: " + str(len(node.children)) + ")"
  else: # if terminal node, we need its type
    out_str += ": " + node.getText()
    out_str += str(node.symbol)

  # print the output string
  print(out_str)

  # print children
  for i in range(node.getChildCount()):
    print_a4ast_tree_node(node.getChild(i), level+1)

  return

# print out an ANTLR4 AST tree
def print_a4ast_tree(ast_tree):
  print_a4ast_tree_node(ast_tree, 0)

  return

# functions to print Python AST tree
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
