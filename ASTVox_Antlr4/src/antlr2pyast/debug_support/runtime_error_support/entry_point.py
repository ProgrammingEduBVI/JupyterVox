'''
Entry point functions for JVox's debugging support for run-time errors
'''

from . import name_error_support

def handle_runtime_error(error_msg, code, line_no, support_type, extra_data,
                         verbose=True):
    '''
    Entry point function for JVox run-time error support. Dispatches support
    request to the correct error handler based on error type.

    Input:
    - error_msg: full error message
    - code: full code in cell
    - line_no: error line number
    - support_type: string that specifies the support requested
    - extra_data: other data (for future extension)
    - verbose: verbose output or not

    Return:
    - dictionary with fields for corresponding error's return values
    '''

    # dispatch the error to corresponding error handling packages
    if error_msg.startswith("NameError"):
        ret_val = name_error_support.get_name_error_column(error_msg, code,
                                                           line_no, verbose)
        return ret_val
    else:
        print("Runtime error handler: unsupported error type,"
              "error message received:", error_msg)
        return None


    # should not reach here
    return None

    
    
