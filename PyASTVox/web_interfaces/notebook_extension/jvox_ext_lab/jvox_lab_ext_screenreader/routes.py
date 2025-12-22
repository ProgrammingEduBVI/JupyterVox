import json
import base64
import io

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from gtts import gTTS

# import JVox interface
import sys
from pathlib import Path
# get the path to the interface package
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(f"{BASE_DIR}/../../../web_api/")

import jvox_interface


class HelloRouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": (
                "Hello1, world!"
                " This is the '/jvox-lab-ext-screenreader/hello' endpoint."
                " Try visiting me in your browser!"
            ),
        }))

        
class JVoxScreenReaderRouteHandler(APIHandler):
    '''
    JVox screen reader endpoint
    '''
    @tornado.web.authenticated
    # def post(self):
    #     # input_data is a dictionary with a key "name"
    #     input_data = self.get_json_body()
    #     data = {"greetings": "Hello {}, enjoy JupyterLab!".format(input_data["stmt"])}
    #     print(data)
    #     self.finish(json.dumps(data))
    def post(self):
    #     # data = {
    #     #     'text':"got " + request.json['stmt'],
    #     # }
    #     # print("speech post:", request.json['stmt'])
    #     # print("speech post return:", data)
        jvox = jvox_interface.jvox_interface("default")
        print("hello jvox:", jvox)
        
        # retrieve statement
        input_data = self.get_json_body()
        stmt = input_data["stmt"]
        print("web api get statement", stmt)

        # generate speech with jvox
        jvox_speech = jvox.gen_speech_for_one(stmt, True)
        print(jvox_speech)

        # prepare returned json
        # data = {
        #     'speech': jvox_speech,
        # }

        # self.finish(json.dumps(data))

        # generate the mp3 file
        file_name = "/tmp/jvox.mp3"
        jvox.gen_mp3_from_speech(jvox_speech, file_name)
    
        # return the speech
        # return jsonify(jvox_speech)
        # return send_file(file_name, mimetype="audio/mpeg")

        # self.set_header("Content-Type", "audio/mpeg")
        # with open(file_name, "rb") as f:
        #     self.write(f.read())

        # self.finish()

        # Read the binary bytes of the file
        # with open(file_name, "rb") as f:
        #     mp3_bytes = f.read()

        # 2. Generate speech using gTTS
        tts = gTTS(text=jvox_speech, lang='en')
        # 3. Save to a bytes buffer instead of a file
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        
        # 4. Seek to the beginning of the buffer to read it
        mp3_fp.seek(0)
        mp3_bytes = mp3_fp.read()
        

        # Encode bytes to Base64 string
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON
        result = {
                "speech": jvox_speech,
                "audio": encoded_audio
            }

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))
        

def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    hello_route_pattern = url_path_join(base_url, "jvox-lab-ext-screenreader", "hello")
    handlers = [(hello_route_pattern, HelloRouteHandler)]

    web_app.add_handlers(host_pattern, handlers)

    # add JVox screen reader endpoint
    jvox_screenreader_route_pattern = url_path_join(base_url, "jvox-lab-ext-screenreader", "speech")
    handlers = [(jvox_screenreader_route_pattern, JVoxScreenReaderRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    
