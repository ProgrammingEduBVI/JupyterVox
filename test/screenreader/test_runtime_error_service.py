# set module search path

# system packages
import argparse
import re
import traceback
import requests

####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', help='the name of the code file',
                    dest='code_file',  required=True)
parser.add_argument('-l', '--line', help=("line number"), dest='line_no',
                    type=int,  required=True)
parser.add_argument('-e', '--error', help='runtime error message',
                    dest='error_msg',  required=True)
parser.add_argument('-t', '--type', help='support type requested',
                    dest='type',  required=True)
parser.add_argument('-u', '--url', help='web service url',
                    dest='url', required=True)
parser.add_argument('-v', '--verbose', action='store_true',
                    dest='verbose', help='enable verbose output' )

args = parser.parse_args()

# if (args.file is None):
#     print("Missing parameter: code filename")
#     parser.print_help()

# if (args.line_no is None):
#     print("Missing parameter: line number")
#     parser.print_help()

# if (args.error_msg is None):
#     print("Missing parameter: full error message")
#     parser.print_help()

# if (args.type is None):
#     print("Missing parameter: support type requested")
#     parser.print_help()

# if (args.url is None):
#     print("Missing parameter: web service url")
#     parser.print_help()

# open load the code into one string
code = open(args.code_file, 'r').read()

# construct data to post
post_data = {"error_msg":args.error_msg,
             "code":code,
             "line_no":args.line_no,
             "support_type":args.type,
             "other":"test123"}

# post the request
result = requests.post(args.url, json=post_data)

try:
    print(result.json())
except:
    # likely server error
    print("some went wrong, check url and server log\n")
    print(result.text)

