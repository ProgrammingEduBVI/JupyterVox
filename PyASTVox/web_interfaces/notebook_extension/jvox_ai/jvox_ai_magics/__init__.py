

import logging
from IPython import get_ipython

from .jvox_ai_magics import JVoxAiMagics

def load_ipython_extension(ipython):
    """ 
    Register the AI magics
    """
    logging.info("load_ipython_extension executed.")
    #print("XXXXXXXXXXXXXXXXXXXXXXXX")
    ipython.register_magics(JVoxAiMagics)

def unload_ipython_extension(ipython):
    """
    Unregister the AI magics
    """
    if 'jvoxAI' in ipython.magics_manager.magics['cell']:
        del ipython.magics_manager.magics['cell']['jvoxAI']
