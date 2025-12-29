#
# Class for JVox read single line
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