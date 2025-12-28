import json
import base64

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from gtts import gTTS

# import JVox packages
import sys
from pathlib import Path
# get the path to the interface package
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(f"{BASE_DIR}/../../../web_api/")
sys.path.append(BASE_DIR)

import jvox_interface

# I am not sure why additional Python files in this directory cannot
# load, although jvox_interface from a different path works correctly.
# So I am leaving all common variables and classes in this file. 
EXTENSION_URL = "jvox-lab-ext"

class HelloRouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": (
                "Hello1, world!"
                f"'/{EXTENSION_URL}/hello' endpoint started correctly. "
            ),
        }))

        
class JVoxScreenReaderRouteHandler(APIHandler):
    '''
    JVox screen reader endpoint for reading a single line
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface.jvox_interface("default")
        print("hello jvox:", jvox)
        
        # retrieve statement
        input_data = self.get_json_body()
        stmt = input_data["stmt"]
        print("JVox readline web api got statement", stmt)

        # generate speech with jvox
        jvox_speech = jvox.gen_speech_for_one(stmt, True)
        print(jvox_speech)

        # generate audio bytes
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(jvox_speech)
        

        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON
        result = {
                "speech": jvox_speech,
                "audio": encoded_audio
            }

        # send the JSON
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))

class JVoxAudioRouteHandler(APIHandler):
    '''
    JVox endpoint for generating audio MP3 bytes given an input text
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface.jvox_interface("default")
        # print("hello jvox:", jvox)
        
        # retrieve statement
        input_data = self.get_json_body()
        jvox_speech = input_data["speech"]
        print("JVox audio web api got speech:", jvox_speech)

        # generate audio bytes
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(jvox_speech)
        
        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON
        reply = {
                "speech": jvox_speech,
                "audio": encoded_audio
            }

        # send the JSON
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(reply))

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


def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # register the hello testing interface
    hello_route_pattern = url_path_join(base_url, EXTENSION_URL, "hello")
    handlers = [(hello_route_pattern, HelloRouteHandler)]

    web_app.add_handlers(host_pattern, handlers)

    # add JVox screen reader endpoint
    jvox_screenreader_route_pattern = url_path_join(base_url, EXTENSION_URL, "readline")
    handlers = [(jvox_screenreader_route_pattern, JVoxScreenReaderRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # add JVox audio endpoint
    jvox_audio_route_pattern = url_path_join(base_url, EXTENSION_URL, "audio")
    handlers = [(jvox_audio_route_pattern, JVoxAudioRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Add JVox chunked reading endpoint
    jvox_chunked_route_pattern = url_path_join(base_url, EXTENSION_URL, "readChunk")
    handlers = [(jvox_chunked_route_pattern, JVoxChunkedReadingRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    
