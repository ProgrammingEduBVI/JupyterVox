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
from debug_support.runtime_error_support import entry_point as rt_error

####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', help='the name of the code file',
                    dest='file')
parser.add_argument('-l', '--line', help=("line number"), dest='line_no',
                    type=int)
parser.add_argument('-e', '--error', help='runtime error message',
                    dest='error_msg')
parser.add_argument('-t', '--type', help='support type requested',
                    dest='type')
parser.add_argument('-v', '--verbose', action='store_true',
                    dest='verbose', help='enable verbose output' )

args = parser.parse_args()

if (args.file is None):
    print("Missing parameter: code filename")
    parser.print_help()

if (args.line_no is None):
    print("Missing parameter: line number")
    parser.print_help()

if (args.error_msg is None):
    print("Missing parameter: full error message")
    parser.print_help()

if (args.type is None):
    print("Missing parameter: support type requested")
    parser.print_help()


# open load the code into one string
code = open(args.file, 'r').read()

ret = rt_error.handle_runtime_error(args.error_msg, code, args.line_no,
                                    args.type, None, args.verbose)

print(ret)

