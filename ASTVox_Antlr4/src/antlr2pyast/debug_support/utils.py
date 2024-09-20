#
# Utility functions, classes for debugging support
#

def make_punc_readable(msg):
    '''
    Makes certain punctuation marks readable in error mssages
    '''
    
    # make '(' to 'left paren'
    msg = msg.replace("\'(\'", "\'left paren\'")
    
    # make ')' to 'right paren'
    msg = msg.replace("\')\'", "\'right paren\'")

    # make ':' to 'colon'
    msg = msg.replace("\':\'", "\'colon\'")

    # read '['
    msg = msg.replace("\'[\'", "\'left brace\'")

    # read ']'
    msg = msg.replace("\']\'", "\'right brace\'")

    # read '{'
    msg = msg.replace("\'{\'", "\'left curely brace\'")

    # read '}'
    msg = msg.replace("\'}\'", "\'right curly brace\'")
    
    return msg

