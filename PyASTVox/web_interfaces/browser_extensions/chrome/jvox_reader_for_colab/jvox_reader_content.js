//start script
console.log("JVox screen reader for Colab (Chrome) start")

// inject script into colab's page, so that we can access window.monaco
// code grab from https://stackoverflow.com/a/9517879
var s = document.createElement('script');
s.src = chrome.runtime.getURL('jvox_reader_inject.js');
// remove to look clean? https://stackoverflow.com/a/11571763
s.onload = function() { this.remove(); }; 
(document.head || document.documentElement).appendChild(s); //reappend?

// get OS type, on MacOS, we will use command+options to avoid conflicting
// with VoiceOver. Note this way of detecting OS is deprecated, although it
// still works on Chrome. See https://stackoverflow.com/a/73619128 for a
// better solution
var isMac = navigator.platform.toUpperCase().indexOf('MAC')>=0;
console.log("JVox SC content: isMac = ", isMac)

/* #########################################################
   Text to speech
##########################################################*/
// create a common Audio object to read statement chunks
let a = new Audio();
let reading_rate = 2;

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

/*##########################################################
   Hotkey handler
##########################################################*/

// handler for JVox hotkey.
function jvox_keyboard_shortcut(e) {

    // set the modifier keys for Windows/Linux and macOS
    // Currently on Windows be alt + corresponding letters
    // on Mac be Control + Options + corresponding letters
    let modifier_keys = e.altKey;
    if (isMac){
        modifier_keys = e.ctrl && e.alt;
    }
    
    // if (e.altKey && e.code === 'KeyJ') { // alt+n
    //     console.log("JVox SR: alt+j pressed");
    // 	chunkify_stmt_to_inject_js("read_then_next");
    // }

    if ((modifier_keys && e.code === 'KeyN') ||
        (modifier_keys && e.code === 'KeyL') ){
        // alt + N: jump to next chunk and read
        console.log("JVox SR content: got alt+n, or ctrl+opt+L")
        chunkify_stmt_to_inject_js("next");
    }
    else if ((modifier_keys && e.code === 'KeyP') ||
             (modifier_keys && e.code === 'KeyK')){
        // alt + N: jump to previous chunk and read
	console.log("JVox SR content: got alt+p, or ctrl+opt+K")
        chunkify_stmt_to_inject_js("pre");
    }
    else if ((modifier_keys && e.code === 'KeyX') ||
             (modifier_keys && e.code === 'KeyX')){
        // alt + X: jump to the beginning of current chunk and read
		 console.log("JVox SR content: got alt+x, or ctrl+opt+X")
        chunkify_stmt_to_inject_js("current");
    }
    else if ((modifier_keys && e.code === 'KeyJ') ||
             (modifier_keys && e.code === 'KeyJ')){
        // alt + N: jump to the beginning of current chunk and read
        console.log("JVox SR content: got alt+j, or ctrl+opt+J")
        chunkify_stmt_to_inject_js("read_then_next");
    }
}
// register the handler
document.addEventListener('keyup', jvox_keyboard_shortcut, false);

/* #########################################################
   Communication with inject.js for cursor position move
##########################################################*/

// send an event to the injected script to request chunkfiy current line
function move_cursor_to_inject_js(line, col){
    let data = {
        line_nu: line,
	col_nu: col
    };

    document.dispatchEvent(new CustomEvent('jvox_move_cursor_to_inject', {detail: data}));
}

/* #########################################################
   Communication with inject.js for Chunkify
##########################################################*/

// send an event to the injected script to request chunkfiy current line
function chunkify_stmt_to_inject_js(chunkify_command){
    let data = {
        command: chunkify_command, // 
    };

    document.dispatchEvent(new CustomEvent('jvox_chunkify_stmt_to_inject', {detail: data}));
}

// add event handler to response to injected script's statement line
// and column number response
document.addEventListener('jvox_chunkify_reply_form_inject', function (e) {
    // parse response from inject
    console.log(e)
    let [stmt, col_nu, chunkify_command] = e.detail;
    console.log('JVox SR content: from inject, stmt: ' + stmt + ", col:" + col_nu +
		", command: " + chunkify_command);
    
    // send the statement to background to obtain speech from JVox server
    jvox_chunkify_stmt_to_background(stmt, col_nu, chunkify_command);
});


/*##########################################################
   BEGIN: Communication with background.js for Chunkify
##########################################################*/

// handle the chunify response from the packground page.
function jvox_handle_chunkify_response_from_bg(chunkify_response) {

    console.log("JVox SR content: Chunkify server respose, ",
		`Chunks to read: ${chunkify_response.chunk_to_read}, `,
		`Chunks: ${chunkify_response.chunks}, `,
		`New col position: ${chunkify_response.new_pos}, `,
		`Chunk string: ${chunkify_response.chunk_string}, `,
		`Error message: ${chunkify_response.error_message}, `,
	       );

    if (chunkify_response.new_pos == -1){
        // server returns -1, no next/pre token to jump to
	console.log("JVox SR content: server return -1 for chunkify, do nothing")
        return
    }

    // read the chunk
    if (chunkify_response.error_message === ""){
        let msg = chunkify_response.chunk_to_read;
        console.log("JVox SR content: chunk to read is " + msg);
        jvox_gtts_speak(msg, "en-US");
    }
    else{
        let msg = chunkify_response.error_message;
        console.log("JVox SR content: chunkify error: " + msg);
        jvox_gtts_speak(msg, "en-US");
    }

    // move cursor, add one since Monaco's col number starts from 1 instead of 0
    move_cursor_to_inject_js(-1, chunkify_response.new_pos + 1)

    return;
}

// in case the communication with background script went wrong
function jvox_handle_chunkify_error_from_gb(error) {
    console.log(`Error: ${error}`);
}

// sned the statement to background script
function jvox_chunkify_stmt_to_background(stmt_text, col_nu, chunkify_command) {
    const sending = chrome.runtime.sendMessage({
	type: "chunkify_stmt",
	stmt: stmt_text,
	col_nu: col_nu,
	command: chunkify_command
    });
    sending.then(jvox_handle_chunkify_response_from_bg,
		jvox_handle_chunkify_error_from_gb);
}

