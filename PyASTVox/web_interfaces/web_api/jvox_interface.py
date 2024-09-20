#!/usr/bin/python3

# interface between PyASTVox and the web service

# packages for AST parsing
import ast
# packages for Text2Speech and audio manipulation
from gtts import gTTS

# help import sibling directories
import sys
sys.path.append("../../pyastvox")
sys.path.append("../../../ASTVox_Antlr4/src/antlr2pyast/")

# other system packages
import traceback
import types

# load the Vox parser utilities
import utils

# import JVox speech generator
from jvox_screenreader import jvox_screenreader

# import token/lexeme navigation packages
from token_navigation import token_navigation
from token_navigation import lexeme_navigation as lex_nav

# import single line parsing checking packages
from debug_support import single_line_check as one_chk
from debug_support import code_snippet_check as snippet_chk

class jvox_interface:
    vox_gen = None;
    jvox = None;
    style = "default";

    # constructor    
    def __init__(self, style="default"):
        self.jvox =  jvox_screenreader()

    # generate the speech for one statement
    def gen_speech_for_one(self, stmt, verbose):
        speech = self.jvox.generate_for_one(stmt, verbose)

        return speech

    # generate the mp3 file
    def gen_mp3_from_speech(self, speech, file_name):
        tts = gTTS(speech, slow=False)
        tts.save(file_name)
        print("jvox created mp3 file at", file_name)

        return

    # find next token
    def find_next_token_start(self, stmt, cur_pos, verbose):
        next_token = token_navigation.next_token(stmt, cur_pos, verbose)

        return {"start":next_token['next_start'],
                "stop":next_token['next_stop']}

    # find previous token
    def find_previous_token_start(self, stmt, cur_pos, verbose):
        previous_token = token_navigation.previous_token(stmt, cur_pos, verbose)

        return {"start":previous_token['pre_start'],
                "stop":previous_token['pre_stop']}

    # find current token start stop
    def find_cur_token_start_stop(self, stmt, cur_pos, verbose):
        cur_token = token_navigation.current_token_start_stop(stmt, cur_pos,
                                                               verbose)

        return {"start":cur_token['start'], "stop":cur_token['stop']}

    # find current lexeme or token
    def find_cur_lexeme_token(self, stmt, cur_pos, verbose):
        cur_token = lex_nav.find_lexeme_token_at_pos(stmt, cur_pos,
                                                     verbose)
        return {"start":cur_token['start'], "stop":cur_token['stop']}
    
    # find next lexeme or token
    def find_next_lexeme_token(self, stmt, cur_pos, verbose):
        next_token = lex_nav.find_next_lexeme_token(stmt, cur_pos,
                                            verbose)
        return {"start":next_token['start'], "stop":next_token['stop']}

    # find next lexeme or token
    def find_prev_lexeme_token(self, stmt, cur_pos, verbose):
        prev_token = lex_nav.find_prev_lexeme_token(stmt, cur_pos,
                                                    verbose)
        return {"start":prev_token['start'], "stop":prev_token['stop']}

    # check if a single statement is correct or not
    def single_line_parsing_check(self, stmt, verbose):
        # add a new line to the statement to suppress the "i want newline or ;"
        # parsing error for ANTLR4
        stmt += '\n'
        check_result = one_chk.single_line_parsing_check(stmt, verbose)

        # generate the speech to be returned to the user
        ret_val = types.SimpleNamespace()
        if check_result.error_no == 0:
            ret_val.msg = check_result.error_msg
            ret_val.offset = 1
        elif check_result.error_no == 1:
            ret_val.msg = check_result.error_msg
            ret_val.offset = 1
        elif check_result.error_no == 2:
            ret_val.msg = "Syntax error: " + check_result.error_msg
            ret_val.offset = check_result.offset
        elif check_result.error_no == 3:
            ret_val.msg = "Other parsing error: " + check_result.error_msg
            ret_val.offset = 1

        return ret_val

    # check the syntax of a code snippet
    # returns the error message, line number, and column number
    def code_snippet_parsing_check(self, stmts, verbose):
        # check the statements
        check_ret = snippet_chk.code_snippet_syntax_check(stmts, verbose)

        # create the return object
        ret_val = types.SimpleNamespace()
        ret_val.msg = check_ret.error_msg
        ret_val.line_no = check_ret.line_no
        ret_val.offset = check_ret.offset
        ret_val.error_no = check_ret.error_no

        return ret_val

        
