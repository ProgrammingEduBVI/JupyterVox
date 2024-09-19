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
    
    return msg

