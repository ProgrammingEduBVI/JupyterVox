'''
Code for breaking down a statement into smaller readable chunks. 
'''

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# AST tree generation/conversion packages
from converter import antlr2pyast
from converter import tools
import ast

# import check_chunk for readability check
from . import check_chunk as cc


def chunk_statement(stmt, cur_pos=0, chunk_len=5,verbose=False):
    '''
    Chunk a statement into smaller readable chunks. 

    Input parameters:
    1. stmt: the statement to chunk
    2. cur_pos: current cursor position, should be zero most of the time
    3. chunk_len: maximum number of tokens for a readable chunk
    4. verbose: enable verbose print output
    
    Return:
    1. chunks: a list of chunks
    '''

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

    # from cursor position 0, iteratively find the next readable chunk
    chunk_nodes = []
    chunk_ends = []
    cursor_pos = cur_pos
    while cursor_pos < len(stmt):
        print("Cursor position:", cursor_pos)
        # skip spaces
        while cursor_pos < len(stmt) and stmt[cursor_pos] == ' ':
            cursor_pos += 1 

        # find the next readable chunk
        chunk_node = find_readable_chunk(a4tree, cursor_pos, chunk_len, 
                                         verbose)
        if isinstance(chunk_node, antlr4.tree.Tree.TerminalNodeImpl):
           # a terminal node is returned, record this node,
           # and move cursor to the next position
           chunk_ends.append(chunk_node.symbol.stop)
           chunk_nodes.append(chunk_node)
           cursor_pos = chunk_node.symbol.stop + 1
        elif chunk_node is not None:
            # a non-terminal node is returned, record this node,
            # and move cursor to the next position
            chunk_ends.append(chunk_node.stop.stop)
            chunk_nodes.append(chunk_node)
            # move cursor to the end of the chunk found
            cursor_pos = chunk_node.stop.stop + 1
        else:
            # None is returned, something is wrong
            print("None is returned for cursor position", cursor_pos)
            break
            
    print("chunk_ends:", chunk_ends)

    # break the original statement into smaller chunks based on the
    # chunk nodes found
    text_chunks = []
    cursor_pos = cur_pos
    for chunk_end in chunk_ends:
        # cut the text of the chunk
        chunk = stmt[cursor_pos:chunk_end+1]
        cursor_pos = chunk_end+1 # move cursor to the end of the chunk

        # add trailing space to the chunk. Here we assume that spaces
        # goes with the previous chunk
        while cursor_pos < len(stmt) and stmt[cursor_pos] == ' ':
            chunk += ' '
            cursor_pos += 1

        # append the chunk text
        text_chunks.append(chunk)
        

    return text_chunks 
        

def find_readable_chunk(node, cur_pos, chunk_len, verbose=True):
  '''
  Return the uppermost-level ANTRL4 AST tree node of the lexeme at current
  cursor position. From the tree node, it's possible to get the lexeme text
  (getText method), start/stop tokens (start/stop fields), and the corresponding
  PyAST tree (pyast_tree field).

  Input parameters:
    node: the root node of the ANTLR4 AST tree
    cur_pos: current cursor position in the statement
    chunk_len: maximum number of tokens for a readable chunk
    verbose: enable verbose print output

  Return:
    1. uppermost-level ANTLR4 node representing the chunk found
  '''
  # if the input is a terminal node, returns it if it's at the current 
  # cursor position
  if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
      if ((cur_pos >= node.symbol.start) and 
          (cur_pos <= node.symbol.stop)):
        return node
      else:
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
  if cc.is_node_readable_with_chunk_len(node, chunk_len):
    return node

  # if curent node is not readable, check if any of its children can be read,
  # return on the first hit
  for i in range(node.getChildCount()):
    c = node.getChild(i)

    return_node = find_readable_chunk(c, cur_pos, chunk_len, verbose)

    if return_node is not None:
      return return_node

  # failed to find the readable chunk
  return None