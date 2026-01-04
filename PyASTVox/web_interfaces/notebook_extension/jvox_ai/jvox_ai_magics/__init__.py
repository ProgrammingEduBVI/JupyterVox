#
# Register JVox' AI magics with IPython
#

import logging
from IPython import get_ipython

from .jvox_ai_magics import JVoxAiMagics

from jvox_server_commons import jvox_server_config
from jvox_server_commons import jvox_logging

def load_ipython_extension(ipython):
    """ 
    Register the AI magics
    """
    
    logger = jvox_logging("ipython") 

    logger.info("JVox AI Magics started.")

    ipython.register_magics(JVoxAiMagics)

def unload_ipython_extension(ipython):
    """
    Unregister the AI magics
    """
    if 'jvoxAI' in ipython.magics_manager.magics['cell']:
        del ipython.magics_manager.magics['cell']['jvoxAI']
