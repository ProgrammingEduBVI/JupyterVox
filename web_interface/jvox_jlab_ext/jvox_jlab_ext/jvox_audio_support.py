#
# Class for JVox audio generation
#

import json
import base64

import tornado
from jupyter_server.base.handlers import APIHandler

# import sys
# from pathlib import Path
# get the path to the interface package
# BASE_DIR = Path(__file__).resolve().parent
# web_api_path = f"{BASE_DIR}/../../../web_api/"
# if web_api_path not in sys.path:
#     sys.path.append(web_api_path)

# import jvox_interface
# 
from jupytervox.interface import jvox_interface    

class JVoxAudioRouteHandler(APIHandler):
    '''
    JVox endpoint for generating audio MP3 bytes given an input text
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface("default")
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
