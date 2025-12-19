import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

# import JVox packages
import sys
sys.path.append("../../../pyastvox")
sys.path.append("../../../../ASTVox_Antlr4/src/antlr2pyast/")
import jvox_screenreader

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
    #     data = {"greetings": "Hello {}, enjoy JupyterLab!".format(input_data["name"])}
    #     print(data)
    #     self.finish(json.dumps(data))
    def post(self):
        data = {
            'text':"got " + request.json['stmt'],
        }
        print("speech post:", request.json['stmt'])
        print("speech post return:", data)
        
        self.finish(json.dumps(data))

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

    
