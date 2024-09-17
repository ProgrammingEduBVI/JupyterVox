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

####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--statement', help='a single statement to test',
                    dest='stmt')
parser.add_argument('-v', '--verbose', action='store_true',
                    dest='verbose', help='enable verbose output' )

args = parser.parse_args()

if (args.stmt is None):
    print("Missing parameter: statement")
    parser.print_help()

# check if stmt is correct
args.stmt = "print(\'x)\n"
ret = one_chk.single_line_parsing_check(args.stmt, args.verbose)
print(ret)
        
