# Antlr4 to Python AST
# Conversion function for loops, including
#   for_stmt
#   while_stmt

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# Convert for_stmt to ast.For
def convert_for_stmt(listener, ctx:Python3Parser.BlockContext):
  '''
  Convert for_stmt to ast.For
  rules: for_stmt: 'for' exprlist 'in' testlist ':' block ('else' ':' block)?;
  '''

  # generate the "target" from the exprlist (children[1])
  target = tools.list_to_node_or_tuple(ctx.children[1].pyast_tree,
                                       is_load=False)

  # generate the "iter" from the testlist (children[3])
  # if ctx.children[3].getChildCount() == 1:
  #   iter = ctx.children[3].pyast_tree
  # else:
  #   iter = ast.Tuple(elts=ctx.children[3].pyast_tree, ctx=ast.Load())
  iter = tools.list_to_node_or_tuple(ctx.children[3].pyast_tree, is_load=True)

  # generate the "body" from the block (children[5])
  # seems body is always a list
  if len(ctx.children) < 6:
    # no body
    body = [None]
  elif type(ctx.children[5].pyast_tree) is list:
    body = ctx.children[5].pyast_tree
  else:
    # childrent[5] is not a list, convert to list
    body = [ctx.children[5].pyast_tree]

  # get the "else" block, if there is one
  if ctx.getChildCount() != 9:
    # no "else" block
    orelse = []
  else:
    # has "else" block
    if type(ctx.children[8].pyast_tree) is list:
      orelse = ctx.children[8].pyast_tree
    else:
      # childrent[6] is not a list, convert to list
      orelse = [ctx.children[8].pyast_tree]

  # construct the ast.For node
  # there are also "orelse" and "type_comment" in ast.For, not sure how to use
  # these two for now... so I set "orelse" to []
  ctx.pyast_tree = ast.For(target, iter, body, orelse)

  return

# convert while_stmt to ast.While
def convert_while_stmt(listener, ctx:Python3Parser.While_stmtContext):
  '''
  Convert while_stmt to ast.While
  rule: while_stmt: 'while' test ':' block ('else' ':' block)?;
  '''

  # get the "test" field
  test = ctx.children[1].pyast_tree

  # get the "body" field
  if type(ctx.children[3].pyast_tree) is list:
    body = ctx.children[3].pyast_tree
  else:
    # childrent[3] is not a list, convert to list
    body = [ctx.children[3].pyast_tree]

  # get the "else" block, if there is one
  if ctx.getChildCount() != 7:
    # no "else" block
    orelse = []
  else:
    # has "else" block
    if type(ctx.children[6].pyast_tree) is list:
      orelse = ctx.children[6].pyast_tree
    else:
      # childrent[6] is not a list, convert to list
      orelse = [ctx.children[6].pyast_tree]

  # generate the ast.While node
  ctx.pyast_tree = ast.While(test, body, orelse)

  return
