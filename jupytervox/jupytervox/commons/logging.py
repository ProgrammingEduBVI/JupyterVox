#
# Logging interface for JVox server components
#

import logging
import inspect
import sys
import os

from . import jvox_server_config as jc

class jvox_logging:
    """
    Skeleton class for JVox logging utilities.
    """

    def __init__(self, log_type="general", log_to_stderr = True):
        """
        Initialize the jvox_logging class.

        Parameters
        ----------
        log_type: general, ipython, or JupyterLab

        log_to_stderr: log to Standard error or not
        """

        # fall back logging path
        self.log_path = "/tmp/jvox.log"

        self.setup_logging(log_type, log_to_stderr)
        

    def setup_logging(self, log_type, log_to_stderr):
        """
        setup logging
        """
        
        self.log_type = log_type

        # obitan log file name
        if (log_type == "ipython"):
            self.log_path = jc.jvox_ipython_log_path()
        elif log_type == "general":
            self.log_path = jc.jvox_general_log_path()
        elif log_type == "JupyterLab":
            self.log_path = jc.jvox_jupyterlab_log_path()

        self.logger = logging.getLogger(f"JVoxLogger_{self.log_type}")
        """ if self.logger.hasHandlers():
            # Handlers will be added below if not already present
            return # use existing handlers and settings """
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
       
        # File handler
        # Only add the file handler if a handler with the same log_path does not already exist
        handler_exists = False
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                if hasattr(handler, 'baseFilename') and handler.baseFilename == self.log_path:
                    handler_exists = True
                    break
        if not handler_exists:
            file_handler = logging.FileHandler(self.log_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
       
        # Stream handler (stderr)
        if not log_to_stderr:
            # Remove any existing StreamHandler to stderr
            handlers_to_remove = []
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and getattr(handler, 'stream', None) == sys.stderr:
                    handlers_to_remove.append(handler)
            for handler in handlers_to_remove:
                self.logger.removeHandler(handler)
        else:
            # check if stderr is already there
            # Check if any handler is already writing to stderr
            has_stderr = any(
                isinstance(h, logging.StreamHandler) and h.stream == sys.stderr 
                for h in self.logger.handlers
            )
            if not has_stderr:
                stream_handler = logging.StreamHandler(sys.stderr)
                stream_handler.setFormatter(formatter)
                self.logger.addHandler(stream_handler)

    def format_message(self, message):

        # get caller name
        stack = inspect.stack()
        # index 1 is this function, index 3 is the true caller
        caller_name = stack[2].function if len(stack) > 1 else "<unknown>"    

        # INSERT_YOUR_CODE
        # Also get the file name of the true caller (index 2 in stack)
        caller_file = stack[2].filename if len(stack) > 1 else "<unknown file>"
        # Only use the base file name (strip path)
        caller_file = os.path.basename(caller_file)

        new_msg = f"[{caller_file}:{caller_name}] {message}"
        return new_msg


    def info(self, msg, *args, **kwargs):
        """
        Wrapper for logging info, prepends caller's function name to the message.
        """

        # additional formatting
        new_msg = self.format_message(msg)
        
        self.logger.info(new_msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Wrapper for logging debug messages, prepends caller's function name to the message.
        """
  
        new_msg = self.format_message(msg)
        self.logger.debug(new_msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Wrapper for logging warning messages, prepends caller's function name to the message.
        """

        new_msg = self.format_message(msg)
        self.logger.warning(new_msg, *args, **kwargs)

        # INSERT_YOUR_CODE
    def error(self, msg, *args, **kwargs):
        """
        Wrapper for logging error messages, prepends caller's function name to the message.
        """
        new_msg = self.format_message(msg)
        self.logger.error(new_msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Wrapper for logging critical messages, prepends caller's function name to the message.
        """
        new_msg = self.format_message(msg)
        self.logger.critical(new_msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Wrapper for logging exceptions, prepends caller's function name to the message.
        """
        new_msg = self.format_message(msg)
        self.logger.error(new_msg, *args, exc_info=exc_info, **kwargs)
