#
# Class for chunk-reading support
#

import json
import base64

import tornado
from jupyter_server.base.handlers import APIHandler

import sys
from pathlib import Path
# get the path to the interface package
BASE_DIR = Path(__file__).resolve().parent
web_api_path = f"{BASE_DIR}/../../../web_api/"
if web_api_path not in sys.path:
    sys.path.append(web_api_path)

import jvox_interface   

class JVoxChunkedReadingRouteHandler(APIHandler):
    '''
    JVox endpoint for generating audio MP3 bytes given an input text
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface.jvox_interface("default")
        # print("hello jvox:", jvox)

        # extract input information
        input_data = self.get_json_body()
        statement = input_data["statement"]
        cursor_pos = int(input_data["cursor_pos"])
        command = input_data["command"]
        chunk_len = int(input_data["chunk_len"])

        result = jvox.chunkify_statement(statement, cursor_pos, command, chunk_len, True)
        print(result)

        print(result.chunk_to_read)

        if not result.chunk_to_read:
            audioText = result.error_message
        else: 
            audioText = result.chunk_to_read
            

        print("Chunk to read:", audioText)

        # generate audio bytes
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(audioText)
        
        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

         # Prepare and send the JSON
        reply = {
            "new_pos": result.new_pos,
            "chunk_to_read": result.chunk_to_read,
            "error_message": result.error_message,
            "audio": encoded_audio
            }

        # send the JSON
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(reply))    