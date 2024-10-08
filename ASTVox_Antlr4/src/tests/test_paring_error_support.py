# set module search path
import os
ast2pyast_path = os.path.abspath('../antlr2pyast/')
import sys
sys.path.append(ast2pyast_path)

# system packages
import argparse
import re
import traceback

# Python AST package
import ast

# JVox debugging support packages
from debug_support import single_line_check as one_chk
from debug_support import code_snippet_check as snippet_chk
from debug_support import runtime_error_support as rt_error

####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--statement', help='a single statement to test',
                    dest='stmt')
parser.add_argument('-t', '--type', help=("type of code check: oneLineSyntax," +
                                          "snippetSyntax"),
                    dest='type')
parser.add_argument('-v', '--verbose', action='store_true',
                    dest='verbose', help='enable verbose output' )

args = parser.parse_args()

if (args.stmt is None):
    print("Missing parameter: statement")
    parser.print_help()
if (args.type is None):
    print("Missing parameter: type of code check")
    parser.print_help()

# check if stmt is correct
if args.type == "oneLineSyntax":
    #args.stmt = "print(\'x)\n"
    ret = one_chk.single_line_syntax_check(args.stmt, args.verbose)
    print(ret)
elif args.type == "snippetSyntax":
    #args.stmt = "print(x)\nprint(y)"
    ret = snippet_chk.code_snippet_syntax_check(args.stmt, args.verbose)
    print(ret)
else:
    print("Unknown type of code check:", args.type)
    parser.print_help()
        
