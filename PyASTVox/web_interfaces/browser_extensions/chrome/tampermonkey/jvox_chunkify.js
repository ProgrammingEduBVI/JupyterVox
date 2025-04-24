// ==UserScript==
// @name         Chunkify Statement
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

//var server_url = "http://3.144.13.232/jvox";
var server_url = "http://localhost:5000/";

// get OS type, on MacOS, we will use command+options to avoid conflicting
// with VoiceOver. Note this way of detecting OS is deprecated, although it
// still works on Chrome. See https://stackoverflow.com/a/73619128 for a
// better solution
var isMac = navigator.platform.toUpperCase().indexOf('MAC')>=0;
console.log("JVox, isMac = ", isMac)

// create a common Audio object to read statement chunks
let a = new Audio();
let reading_rate = 2;

// add hotkeys
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

    if (((!isMac) && e.altKey && e.code === 'KeyN') ||
        ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyN') ){
        // alt + N: jump to next chunk and read
        console.log("JVox: got alt+n")
        jvox_chunk_navigate("next");
    }
    else if (((!isMac) && e.altKey && e.code === 'KeyP') ||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyP')){
        // alt + N: jump to previous chunk and read
        console.log("JVox: got alt+p")
        jvox_chunk_navigate("pre");
    }
    else if (((!isMac) & e.altKey && e.code === 'KeyX') ||
             ((isMac) && e.shiftKey && e.ctrlKey && e.code === 'KeyX')){
        // alt + N: jump to the beginning of current chunk and read
        console.log("JVox: got alt+x")
        jvox_chunk_navigate("current");
    }

}

// register the handler
document.addEventListener('keyup', doc_keyUp, false);

// get the statement on cursor
function jvox_get_cursor_line(){
    var editors = unsafeWindow.monaco.editor.getEditors()

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           var line_nu = e.getPosition().lineNumber;
           var cell_txt = e.getValue();
           var cell_txtArr = cell_txt.split('\n');
           var line = cell_txtArr[line_nu-1];

           console.log("Line on cursor:" + line);
       }
    }

    return line;
}

// chunkify statement
// cmd can be "next", "pre", "cur"
// if is_start is True, jump to the corresponding token's start, otherwise to the end
function jvox_chunk_navigate(cmd){
    var editors = unsafeWindow.monaco.editor.getEditors()

    console.log("Read chunk with cmd: " + cmd);

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           var line_nu = e.getPosition().lineNumber;
           var col_nu = e.getPosition().column;

           var cell_txt = e.getValue();
           var cell_txtArr = cell_txt.split('\n');
           var stmt_text = cell_txtArr[line_nu-1];

           console.log("Current Cursor position, line: " + line_nu + ", col: " + col_nu);

           // contact server to find the corresponding token's position
           col_nu = col_nu - 1; // monaco col nubmer starts at 1 instead 0, so minus 1
           var surl = server_url + "/chunkify";
           GM_xmlhttpRequest({
               method: "POST",
               url: surl,
               headers: {
                   "Content-Type": "application/json"
               },
               responseType: "json",
               data: JSON.stringify({"stmt":stmt_text,
                                    "cur_pos":col_nu.toString(),
                                    "chunk_len":"3",
                                    "command":cmd}),
               onload: function(response) {
                   console.log(response.responseType);
                   console.log(response.response);


                   //get the new position
                   var new_col = response.response.new_pos;

                   if (new_col == -1){
                       // server returns -1, no next/pre token to jump to
                       return
                   }

                   // move the cursor to the new position
                   console.log("new col position is " + new_col);

                   var cell = find_focused_cell()
                   var line_nu = cell.getPosition().lineNumber;
                   new_col = new_col + 1; //adjust new_col since monaco's col number starts from 1 instead of 0

                   cell.setPosition({lineNumber: line_nu, column: new_col});

                   // read the chunk
                   if (response.response.error_message === ""){
                       let msg = response.response.chunk_to_read;
                       console.log("chunk to read is " + msg);
                       jvox_gtts_speak(msg, "en-US");
                   }
                   else{
                       let msg = response.response.error_message;
                       console.log("chunkify error: " + msg);
                       jvox_gtts_speak(msg, "en-US");
                   }

               },
               onerror: function (response) {
                   console.error("Speech Request error:" + response.statusText);
               }
           });
       }
    }


    return;
}

function find_focused_cell(){
    var editors = unsafeWindow.monaco.editor.getEditors()

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           console.log("Found focused cell:" + e)
           return e;
       }
    }

    return null;

}

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
