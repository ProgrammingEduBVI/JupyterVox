#
# classes to add JVox custom AI magics
# Adapted from https://github.com/jupyter-ai-contrib/jupyter-ai-magic-commands/tree/main
#

import base64
import json
import os
import re
import sys
import warnings
from typing import Any, Optional

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import HTML, JSON, Markdown, Math

import logging

from .jvox_ai_backend import jvox_gemini_interface as ai_interface

@magics_class
class JVoxAiMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)

    @cell_magic
    def jvoxAI(self, line: str, cell: str) -> Any:
        """
        Defines "%%jvoxAI" cell magic.

        Currently only support generating a new code cell.

        It will take the whole cell input as prompts, and use an AI to gnerate 
        a new cell of code. 
        """
        print(cell)

        self.run_ai_cell(cell)

    def run_ai_cell(self, cell_text):

        # generate the prompt to send to AI
        prompt = self.prepare_prompte_with_error(cell_text)

        print(f"prompt is {prompt}")

        response = ai_interface.generate(prompt)

        self.shell.set_next_input(response, replace=False)
        return HTML("AI generated code inserted below &#11015;&#65039;")

    def prepare_prompte(self, cell_text):

        prefix = "Write Python code for:"

        postfix = "Provide raw code only. No explanations, no preamble, and no markdown backticks."

        prompt = f"{prefix}, {cell_text}. {postfix}"

        return prompt

    def prepare_prompte_with_error(self, cell_text):

        prefix = "Write Python code for:"

        postfix = """Intentionally include one subtle logic or runtime error commonly found in AI-generated code. 
        Provide raw code only. No explanations, no preamble, and no markdown backticks."""

        prompt = f"{prefix}, {cell_text}. {postfix}"

        return prompt