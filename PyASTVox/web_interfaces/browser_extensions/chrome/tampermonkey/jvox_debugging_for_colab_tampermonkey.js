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
// ==/UserScript==

console.log("JVox Debgging plugin start.");

var server_url = "http://3.144.13.232/jvox";
//var server_url = "http://localhost:5000/";

// create a common Audio object to read error messages
let a = new Audio();
let reading_rate = 2;

// Use Google Text-to-Speech (TTS) to talk
function jvox_gtts_speak(text, lang){
    let url= `https://translate.google.com/translate_tts?ie=UTF-8&tl=${lang}&client=tw-ob&q=${text}`;
    // add the sound to the audio element
    a.src = url;
    //For auto playing the sound
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
           break;
       }
    }

    return null;

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

    if (e.altKey && e.ctrlKey && e.code === 'KeyE') {
        // alt+j => generate jvox speech
        console.log("JVox: got alt+ctrl+e")
        jvox_jump_to_error_line(last_error_marker, last_error_uri);
    }
    else if (e.altKey && e.ctrlKey && e.code === 'KeyS') {
        // turn on/off the automatic error message reading
        console.log("JVox: got alt+ctrl+s")
        read_error_immd = !read_error_immd;
        console.log("JVox: automatic error reading is: ", read_error_immd);
        if (read_error_immd){
            jvox_gtts_speak("Automatic error reading is on.", "en-US")
        }
        else{
            jvox_gtts_speak("Automatic error reading is off.", "en-US")
        }
    }
    else if (e.altKey && e.ctrlKey && e.code === 'KeyL') {
        // read last error marker's message
        console.log("JVox: reading last error.")
        jvox_read_marker_message(last_error_marker);
    }
    else if (e.altKey && e.ctrlKey && e.code === 'KeyC') {
        // read last error marker's message
        console.log("JVox: reading last error.")
        jvox_syntax_check_current_line();
    }
}

// register the handler
document.addEventListener('keyup', doc_keyUp, false);


///////////////////////////////////////////////
/// old code
///////////////////////////////////////////////
function jvox_onDidChangeMarkers_old(uri){
    console.log("got marker change event")
    console.log(uri)
    const markers = unsafeWindow.monaco.editor.getModelMarkers({resource: uri})
    console.log('markers:', markers.map(
    ({ message, startLineNumber, startColumn, endLineNumber, endColumn }) =>
      `${message} [${startLineNumber}:${startColumn}-${endLineNumber}:${endColumn}]`,
    ))
    console.log(markers)
    // try to find the editor with uri
    var editors = unsafeWindow.monaco.editor.getEditors()
    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       if (e.getModel().uri == uri){
           console.log("found editor")
           console.log(e)
           e.setPosition({lineNumber: 1, column: 2});
           e.focus();
           break
       }
    }
}
