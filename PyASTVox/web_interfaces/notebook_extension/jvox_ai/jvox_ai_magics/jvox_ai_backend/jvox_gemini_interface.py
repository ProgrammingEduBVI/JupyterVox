#
# Interface for talking with Gemini
#

from google import genai

import os

from jvox_server_commons import jvox_logging

gemini_model_name = "gemini-2.5-flash-lite"

def generate(prompt):
    logger = jvox_logging("general", log_to_stderr=False)

    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    logger.debug(f"API Key is {API_KEY}")
    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model=gemini_model_name, contents=prompt
    )

    return response.text