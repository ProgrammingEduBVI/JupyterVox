console.log("JVox screen reader injected script starts.")
console.log("Monaco handle from window.monaco:")
console.log(window.monaco)


/*##########################################################
  Get cell code from Monaco
##########################################################*/

// Iterate over the editors (i.e., cells) to find the one with active keyboard
// focus. Get the cursor position (line and col) of the cursor, than extract
// the text of the line where the cursor is at. 
// Returns the text of line.
function jvox_get_cursor_line(){
    // get all the cursors
    var editors = window.monaco.editor.getEditors()

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       
       if (e.hasTextFocus()){
           // cell has focus
           var line_nu = e.getPosition().lineNumber; // cursor line num
	   var col_nu = e.getPosition().column;
           var cell_txt = e.getValue(); // all text in cell
           var cell_txtArr = cell_txt.split('\n'); // convert to array of lines
           var line = cell_txtArr[line_nu-1]; // extract the cursor line

           console.log("JVox SR inject: line at cursor: ", line);
	   console.log("JVox SR inject: curse position, line: " +
		       line_nu + ", col: " + col_nu);
       }
    }
    
    return [line, col_nu];
}

/*##########################################################
  Event handler for chunkify
##########################################################*/

// add event handler to response to content script's request of
// chunkify statement
document.addEventListener('jvox_chunkify_stmt_to_inject', function (e) {
    // console.log(e)
    let data = e.detail;
    // get the chunkify command from request, as we need to send this command
    // back to content.js later, this is one way to keep this command info.
    let chunkify_command = data.command 
    console.log('jvox_inject: cursor-stmt request received', data);

    // grab the statement and column of the cursor
    let [stmt_line, col_nu] = jvox_get_cursor_line();

    // send the statement and column number to content.js
    console.log("JVox SR inject: send to background with line: " + stmt_line +
		", col: " + col_nu);
    document.dispatchEvent(new CustomEvent('jvox_chunkify_reply_form_inject',
     					   {detail: [stmt_line,
						     col_nu,
						     e.detail.command]}));
});

/*##########################################################
  Event handler for move cursor in current cell
##########################################################*/

function find_focused_cell(){
    let editors = window.monaco.editor.getEditors()

    let i = 0;
    let len = editors.length
    for(i = 0; i < len ; i++){
       let e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           console.log("Found focused cell:" + e)
           return e;
       }
    }

    return null;

}

// add event handler to response to content script's request of
// moving cursor
document.addEventListener('jvox_move_cursor_to_inject', function (e) {
    // console.log(e)
    let data = e.detail;
    let line_nu = e.detail.line_nu;
    let col_nu = e.detail.col_nu;

    console.log(`JVox SR inject: move cursor to line ${line_nu}, col ${col_nu}`)

    let cell = find_focused_cell()
    if (line_nu == -1){ // request does not have line number, use current line
	line_nu = cell.getPosition().lineNumber;
    }
    
    cell.setPosition({lineNumber: line_nu, column: col_nu});
    
});
