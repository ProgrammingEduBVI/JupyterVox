// ==UserScript==
// @name         Debugging support test
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Debugging support test,
// @author       Wei Wang
// @match        https://colab.research.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// @connect      3.144.13.232
// @connect      localhost
// ==/UserScript==

console.log("JVox Debgging plugin start.");

var server_url = "http://3.144.13.232/jvox";
//var server_url = "http://localhost:5000/";

// get OS type, on MacOS, we will use command+options to avoid conflicting
// with VoiceOver. Note this way of detecting OS is deprecated, although it
// still works on Chrome. See https://stackoverflow.com/a/73619128 for a
// better solution
var isMac = navigator.platform.toUpperCase().indexOf('MAC')>=0;
console.log("JVox, isMac = ", isMac)

// function to replace punctuation marks with its actual text name
// so that text-to-speech will not ignore them
function jvox_make_puncs_readable(msg){
    console.log("xxx", msg)
    // make '(' readable
    msg = msg.replace("\'(\'", "\'left paren\'");

    // make ')' readable
    msg = msg.replace("\')\'", "\'right paren\'");

    // make ':' readable
    msg = msg.replace("\':\'", "\'colon\'");

    // make '[' readable
    msg = msg.replace("\'[\'", "\'left bracket\'");

    // make ']' readable
    msg = msg.replace("\']\'", "\'right bracket\'");

     // make '{' readable
    msg = msg.replace("\'{\'", "\'left curly bracket\'");

    // make '}' readable
    msg = msg.replace("\'}\'", "\'right curly bracket\'");

    return msg;
}

// create a common Audio object to read error messages
let a = new Audio();
let reading_rate = 3;

// Use Google Text-to-Speech (TTS) to talk
function jvox_gtts_speak(text, lang){
    let url= `https://translate.google.com/translate_tts?ie=UTF-8&tl=${lang}&client=tw-ob&q=${text}`;
    // add the sound to the audio element
    a.src = url;
    //For auto playing the sound
    a.load(); // this is to avoid losing the sound of first few seconds
    a.playbackRate = reading_rate;
    a.play();
}

// flag to control if we need to read error message immediately after it's generated
let read_error_immd = true;

// record the last error marker
let last_error_marker = {};
let last_error_uri = {}

// JVox function to read error marker's message with line number
function jvox_read_marker_message(marker){
    // read the error message
    let text_to_read = marker.message;

    // add line number to the message, if the message does not have it already
    if (text_to_read.indexOf("detected at line") == -1){
        let lineno_str = marker.startLineNumber.toString()
        text_to_read = text_to_read + ". Detected at line " + lineno_str
    }
    // play the message
    text_to_read = jvox_make_puncs_readable(text_to_read)
    jvox_gtts_speak(text_to_read, "en-US");

    return;
}

// JVox function to handle Monaco Marker changes.
// Will read error message.
function jvox_onDidChangeMarkers(uri){
    console.log("JVox: got marker change event");
    // if we are not supposed to read the error returns
    if (!read_error_immd){
        console.log("JVoX: not supposed to read error, quit");
        return;
    }

    const markers = unsafeWindow.monaco.editor.getModelMarkers({resource: uri});
    console.log(markers);

    // find the first marker that has error
    let len = markers.length;
    let i = 0;
    let marker = markers[0]
    for(i = 0; i< len; i++){
        let msg = markers[i].message;
        // check if this marker is due to error message
        if(msg.indexOf("Error") !== -1){
            marker = markers[i];
            break; //found, break on first find
        }
    }
    // not found error message, return
    if (i == len){
        return;
    }

    console.log("Jvox: found error marker:\n", marker);
    // save last error marker
    last_error_marker = marker;
    last_error_uri = uri;

    // read the error message
    jvox_read_marker_message(marker);

    return;
}


// jump the error line for uri's (cell's) error marker
function jvox_jump_to_error_line(marker, uri){
    console.log("JVox: jumping to last error site (line only)")
    let editors = unsafeWindow.monaco.editor.getEditors()

    let i = 0;
    let len = editors.length
    for(i = 0; i < len ; i++){
       let cell = editors[i];
       if (cell.getModel().uri == uri){
           console.log("JVox: found last error cell: ", cell)
           cell.setPosition({lineNumber: marker.startLineNumber, column: 0});
           cell.focus();

           // sound report to user
            let msg = "jumped to the beginning of error line " + marker.startLineNumber
            jvox_gtts_speak(msg, "en-US");

           break;
       }
    }

    if (i == len){
        // failed to find the cell, quit
        console.log("JVox: when jumping to error line, failed to find the error cell");
    }

    return null;

}

// find the cell that causing the last error
function jvox_find_error_cell(marker, uri){
    let editors = unsafeWindow.monaco.editor.getEditors()

    // find the cell that causing the error
    let i = 0;
    let len = editors.length;
    let error_cell = editors[0];
    for(i = 0; i < len ; i++){
       let cell = editors[i];
       if (cell.getModel().uri == uri){
           console.log("JVox: found last error cell: ", cell);
           error_cell = cell;
           break;
       }
    }

    if (i == len){
        // failed to find the cell, quit
        console.log("JVox: failed to find the error cell");
        return;
    }

    return error_cell;
}

// jump the error line for uri's (cell's) error marker
function jvox_jump_to_error_column_syntax_error(marker, uri){
    console.log("JVox: jumping to last error site (line and column)")
    let editors = unsafeWindow.monaco.editor.getEditors()

    // find the cell that causing the error
    let error_cell = jvox_find_error_cell(marker, uri)

    // if this is an indentation error, we can just jump to the beginning of the line
    if (marker.message.startsWith("IndentationError")){
        // jump to the line and column
        error_cell.setPosition({lineNumber: marker.startLineNumber,
                                column: 1});
        error_cell.focus();

        // sound report to user
        let msg = ("jumped to indentation error line " + marker.startLineNumber.toString() +
                   ", column one")
        jvox_gtts_speak(msg, "en-US");

        return
    }

    // get cell text
    let cell_txt = error_cell.getValue();
    // get the line text that causing the error
    let line_no = marker.startLineNumber
    let cell_txtArr = cell_txt.split('\n');
    var stmt_text = cell_txtArr[line_no-1];

    let surl = server_url + "/singlelinecheck";

    // send request to server to obtain speech mp3 file/blob as response
    GM_xmlhttpRequest({
        method: "POST",
        url: surl,
        headers: {
            "Content-Type": "application/json"
        },
        responseType: "json",
        data: JSON.stringify({"stmt":stmt_text}),
        onload: function(response) {
            console.log(response.responseType);
            console.log(response.response);
            console.log(response.response.message);
            console.log(response.response.offset);

            // jump to the line and column
            error_cell.setPosition({lineNumber: line_no,
                                    column: response.response.offset});
            error_cell.focus();

            // sound report to user
            let msg = ("jumped to error line " + marker.startLineNumber.toString() +
                       ", column " + response.response.offset.toString())
            jvox_gtts_speak(msg, "en-US");
        },
        onerror: function (response) {
            console.error("JVox syntax check HTTP error:" + response.statusText);
        }
    });

    return null;

}

// jump the error line for uri's (cell's) error marker
function jvox_jump_to_error_column(marker, uri){
    // dispatch to the correct jump-to function based on error type
    if ((marker.message.startsWith("SyntaxError:") || marker.message.startsWith("IndentationError"))){
        jvox_jump_to_error_column_syntax_error(marker, uri)
        return
    }
    else if (marker.message.startsWith("NameError:")){
        jvox_jump_to_error_column_name_error(marker, uri)
        return
    }
    else if (marker.message.startsWith("AttributeError:")){
        jvox_jump_to_error_column_attr_error(marker, uri)
        return
    }
    else if (marker.message.startsWith("TypeError:")){
        jvox_jump_to_error_column_type_error(marker, uri)
        return
    }
    else{
        // jump to line
        console.log("JVox: no column to jump to, because last error's type is not supported, last error message:", marker.message);
        jvox_jump_to_error_line(marker, uri)
        return
    }

}


function jvox_syntax_check_current_line(){
    console.log("Syntax check for current line")

    // obtain the text of current line
    let stmt_text = jvox_get_cursor_line();

    console.log("Contacting server to parsing check line: " + stmt_text)

    let surl = server_url + "/singlelinecheck";

    // send request to server to obtain speech mp3 file/blob as response
    GM_xmlhttpRequest({
        method: "POST",
        url: surl,
        headers: {
            "Content-Type": "application/json"
        },
        responseType: "json",
        data: JSON.stringify({"stmt":stmt_text}),
        onload: function(response) {
            console.log(response.responseType);
            console.log(response.response);
            console.log(response.response.message);

            // read the message
            jvox_gtts_speak(response.response.message, "en-US");

        },
        onerror: function (response) {
            console.error("JVox syntax check HTTP error:" + response.statusText);
        }
    });

    return;
}

// find the text of the line at the cursor
function jvox_get_cursor_line_number(){
    let editors = unsafeWindow.monaco.editor.getEditors()

    let i = 0;
    let len = editors.length
    let line = ""
    let line_nu = -1
    for(i = 0; i < len ; i++){
       let e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           line_nu = e.getPosition().lineNumber;
           //let cell_txt = e.getValue();
           //let cell_txtArr = cell_txt.split('\n');
           //line = cell_txtArr[line_nu-1];

           console.log("JVox cursor line number:", line_nu);
       }
    }

    return line_nu;
}

function jvox_OnDidCreateEditor(editor){
    console.log("jvox: create editor")
    console.log(editor)
}

window.onload = function()
{
    console.log("after load")
    console.log(unsafeWindow.monaco)
    unsafeWindow.monaco.editor.onDidChangeMarkers(([uri]) => {
       jvox_onDidChangeMarkers(uri);
    });
};

// key up even handler
function doc_keyUp(e) {

    // check if ctrlKey or metaKey is pressed first. On Mac, we use
    // metaKey to avoid conflicting with voice over; on others, we use
    // ctrlKey.
    let ctrl_or_meta = false;
    if (isMac){
        ctrl_or_meta = e.metaKey;
    }
    else{
        ctrl_or_meta = e.ctrlKey;
    }

    if (((!isMac) && e.altKey && e.ctrlKey && e.code === 'KeyE') ||
        ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyT') ){
        // alt+j => generate jvox speech
        console.log("JVox: got alt+ctrl+e")
        jvox_jump_to_error_line(last_error_marker, last_error_uri);
    }
    else if (((!isMac) & e.altKey && e.ctrlKey && e.code === 'KeyS') ||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyS')){
        // turn on/off the automatic error message reading
        console.log("JVox: got alt+ctrl+s")
        read_error_immd = !read_error_immd;
        console.log("JVox: automatic error reading is: ", read_error_immd);
        if (read_error_immd){
            jvox_gtts_speak(". Automatic error reading is on.", "en-US")
        }
        else{
            jvox_gtts_speak(". Automatic error reading is off.", "en-US")
        }
    }
    else if (((!isMac) && e.altKey && e.ctrlKey && e.code === 'KeyL')||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyL')){
        // read last error marker's message
        console.log("JVox: reading last error.")
        jvox_read_marker_message(last_error_marker);
    }
    else if (((!isMac) && e.altKey && e.ctrlKey && e.code === 'KeyC') ||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyC')) {
        // read last error marker's message
        console.log("JVox: Single line syntax check.")
        jvox_syntax_check_current_line();
    }
    else if (((!isMac) && e.altKey && ctrl_or_meta && e.code === 'KeyG')||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyJ')){
        // read last error marker's message
        console.log("JVox: jump to the line and column of last error.")
        jvox_jump_to_error_column(last_error_marker, last_error_uri);
    }
    // ctrl+arrow keys for sounded navigation
    else if (ctrl_or_meta && (e.code === 'ArrowUp'|| e.code === 'ArrowDown')){
        //
        console.log("JVox: got ctrl + arrow key", e)
        jvox_move_cursor_line(e)
    }
    else if (e.code === 'ArrowUp'|| e.code === 'ArrowDown'){
        //
        let line_nu = jvox_get_cursor_line_number()
        console.log("JVox: got arrow key", e, "at line", line_nu)
        if (line_nu != -1){
            jvox_gtts_speak("Line " + line_nu.toString(), "en-US")
        }
    }
    else if (((!isMac) && e.altKey && e.ctrlKey && e.code === 'KeyI') ||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyI')){
        //
        let line_nu = jvox_get_cursor_line_number()
        console.log("JVox: got alt+ctrl/meta+N", e, "at line", line_nu)
        if (line_nu != -1){
            jvox_gtts_speak("Line " + line_nu.toString(), "en-US")
        }
    }


}

// register the handler
document.addEventListener('keyup', doc_keyUp, false);

////////////////////////////////////////////////////////////////////
// Debugging support for run-time errors
////////////////////////////////////////////////////////////////////

// invoke runtime error support at the server
function call_runtime_support_service(error_msg, code, line_no, support_type, extra_data,
                                      response_func){
    let surl = server_url + "/runtimeerrorsupport";

    // construct json post data
    let post_data = {"error_msg":error_msg, "code":code, "line_no":line_no, "support_type":support_type}
    // combine with the extra data, which should also be a dictionary-like object
    if (!(extra_data == null)){
        post_data = Object.assign(post_data, extra_data)
    }

    GM_xmlhttpRequest({
        method: "POST",
        url: surl,
        headers: {
            "Content-Type": "application/json"
        },
        responseType: "json",
        data: JSON.stringify(post_data),
        onload: response_func,
        onerror: function (response) {
            console.error("JVox syntax check HTTP error:" + response.statusText);
        }
    });

    return;
}

// jump the error line and column for a name error
function jvox_jump_to_error_column_name_error(marker, uri){
    console.log("JVox: jumping to last error site for last name error (line and column)");

    let support_type = "col_no";

    // find the error cell
    let error_cell = jvox_find_error_cell(marker, uri);

    // the response handling function
    let response_func = function(response) {
            console.log(response.responseType);
            console.log(response.response);
            console.log(response.response.col_no);

            // jump to the line and column
            error_cell.setPosition({lineNumber: marker.startLineNumber,
                              column: response.response.col_no});
            error_cell.focus();

            // sound report to user
            if (response.response.col_no != 0 ){
                // if col_no return is not 0
                let msg = ("jumped to error line " + marker.startLineNumber.toString() +
                           ", column " + response.response.col_no.toString())
                jvox_gtts_speak(msg, "en-US");
            }
            else{
                // if col_no return is 0, means not finding the error
                let msg = ("jumped to error line " + marker.startLineNumber.toString() + ", column 1")
                jvox_gtts_speak(msg, "en-US");
            }
    }


    // extra data for testing
    let extra_data = {"extra_data":"test123x"};

    // call runtime error support
    call_runtime_support_service(marker.message, error_cell.getValue(), marker.startLineNumber,
                                 support_type, extra_data, response_func)

    return;

}

// jump the error line and column for an attribute error
function jvox_jump_to_error_column_attr_error(marker, uri){
    console.log("JVox: jumping to last error site for last attribute error (line and column)");
    console.log("JVox: reusing the jump-to support for name error");
    jvox_jump_to_error_column_name_error(marker, uri)
}

// jump the error line and column for an attribute error
function jvox_jump_to_error_column_type_error(marker, uri){
    console.log("JVox: jumping to last error site for last type error (line and column)");
    console.log("JVox: reusing the jump-to support for name error");
    jvox_jump_to_error_column_name_error(marker, uri)
}

// find the text of the line at the cursor
function jvox_get_cursor_line(){
    let editors = unsafeWindow.monaco.editor.getEditors()

    let i = 0;
    let len = editors.length
    let line = ""
    for(i = 0; i < len ; i++){
       let e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           let line_nu = e.getPosition().lineNumber;
           let cell_txt = e.getValue();
           let cell_txtArr = cell_txt.split('\n');
           line = cell_txtArr[line_nu-1];

           console.log("Line on cursor:" + line);
       }
    }

    return line;
}

// find the text of the line at the cursor
function jvox_move_cursor_line(arrow_key){
    let editors = unsafeWindow.monaco.editor.getEditors()

    let i = 0;
    let len = editors.length
    let line = ""
    for(i = 0; i < len ; i++){
       let e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           // get current line number
           let line_nu = e.getPosition().lineNumber;
           let col_nu = e.getPosition().column;
           // change the line number
           if (arrow_key.code === 'ArrowUp'){
               line_nu = line_nu - 1
           }
           else if (arrow_key.code === 'ArrowDown'){
               line_nu = line_nu + 1
           }

           // move the cursor
           e.setPosition({lineNumber: line_nu,
                          column: col_nu});

           // get the new column number, as sometimes, the
           // move can fail (e.g., moving beyond the last line)
           line_nu = e.getPosition().lineNumber;

           // notify the user
           jvox_gtts_speak("Line " + line_nu.toString(), "en-US")


           console.log("Line on cursor:" + line);
       }
    }

    return;
}
