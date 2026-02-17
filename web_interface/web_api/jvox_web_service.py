# import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file

# import jupytervox packages
import jvox_interface

app = Flask(__name__)
jvox = None

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/speech/<stmt>',methods=['GET'])
def genSpeech(stmt):
    speech = stmt
    print("speech get:", speech)
    return jsonify({'text':speech})

@app.route('/speech2/post',methods=['POST'])
def gen_speech_post():
    dat = {
    'text':"got " + request.json['stmt'],
    }
    print("speech post:", request.json['stmt'])
    print("speech post return:", dat)
    
    return jsonify(dat)

@app.route('/speech3/post',methods=['POST'])
def gen_speech_post_jvox():
    # retrieve statement
    stmt = request.json['stmt']
    print("web api get statement", stmt)

    # generate speech with jvox
    jvox_speech = jvox.gen_speech_for_one(stmt, True)
    print(jvox_speech)

    # generate the mp3 file
    file_name = "/tmp/jvox.mp3"
    jvox.gen_mp3_from_speech(jvox_speech, file_name)
    
    # return the speech
    # return jsonify(jvox_speech)
    return send_file(file_name, mimetype="audio/mpeg")

@app.route('/tokennavigate',methods=['POST'])
def token_navigation():
    # retrieve statement, current position, and navigation command
    stmt = request.json['stmt']
    cur_pos = int(request.json['pos'])
    cmd = request.json['cmd']
    
    print("web token navi api get statement:", stmt, "cur_pos:", cur_pos,
          "cmd:", cmd )

    # navigate based on command
    if cmd == "next":
        next_token = jvox.find_next_token_start(stmt, cur_pos, True)
        print("next token:", next_token)
        dat = {"start": next_token["start"], "stop":next_token["stop"]}
    elif cmd == "pre":
        pre_token = jvox.find_previous_token_start(stmt, cur_pos, True)
        print("previous token:", pre_token)
        dat = {"start": pre_token["start"], "stop":pre_token["stop"]}
    elif cmd == "cur":
        cur_token = jvox.find_cur_token_start_stop(stmt, cur_pos, True)
        print("Current token:", cur_token)
        dat = {"start": cur_token["start"], "stop":cur_token["stop"]}

    return jsonify(dat)


@app.route('/singlelinecheck',methods=['POST'])
def single_line_check():
    # retrieve the statement to check
    stmt = request.json['stmt']
    print("Web single line check get statement:", stmt)

    # check the statement
    ret_val = jvox.single_line_parsing_check(stmt, True)
    # return the error message or correct confirmation message
    dat = {"message":ret_val.msg, "offset":ret_val.offset}

    return jsonify(dat)

@app.route('/snippetsyntaxcheck',methods=['POST'])
def snippet_syntax_check():
    # retrieve the statement to check
    stmts = request.json['stmts']
    print("Web single line check get statements:", stmts)

    # check the statement
    ret = jvox.code_snippet_parsing_check(stmts, True)
    # return the error message or correct confirmation message
    dat = {"message":ret.msg, "line_no":ret.line_no, "offset":ret.offset,
           "error_no":ret.error_no}

    return jsonify(dat)

@app.route('/runtimeerrorsupport',methods=['POST'])
def runtime_error_support():
    # Retrieve the error message, code, line number, and support type.
    # Retrieve here, so that missing fields will cause exception in this step
    error_msg = request.json['error_msg']
    code = request.json['code']
    line_no = request.json['line_no']
    support_type = request.json['support_type']

    # load the request data
    print("JVox runtime error support requested with data:")
    for key in request.json.keys():
        if key != "code":
            v = request.json[key]
            print(f"{key}: {v}")
    # print code at last
    print(f"Code:\n{code}")
    # print(request.json)

    # Pass on the data. Note that, the request's whole json data are passed on,
    # in case additional data are required for runtime error support.
    ret_val = jvox.handle_runtime_error(error_msg, code, line_no, support_type,
                                        request.get_json(), True)
    # convert the returned SimpleNamespace to dictionary
    dat = vars(ret_val)

    return jsonify(dat)

@app.route('/chunkify',methods=['POST'])
def chunkify_statement():
    # Retrieve the statement to chunkify
    stmt = request.json['stmt']
    cur_pos = int(request.json['cur_pos'])
    chunk_len = int(request.json['chunk_len'])
    command = request.json['command']
    print(f"Statement to chunkify: {stmt} at position {cur_pos}, " +
          f"with command {command}, and max chunk length {chunk_len}.")

    # check the statement
    ret_val = jvox.chunkify_statement(stmt, cur_pos, command, chunk_len, True)
    # return the error message or correct confirmation message
    dat = {"chunks":ret_val.chunks,
           "new_pos":ret_val.new_pos,
           "chunk_to_read":ret_val.chunk_to_read,
           "error_message":ret_val.error_message,
           "chunk_string":ret_val.chunk_string
           }
    print(f"Chunkify returns: {dat}")

    return jsonify(dat)

if __name__ == "__main__":
    jvox = jvox_interface.jvox_interface("default")
    print("hello jvox:", jvox)
    # start the web service. this function will not return until the service is
    # terminate. so run this function at the end
    app.run()
    
