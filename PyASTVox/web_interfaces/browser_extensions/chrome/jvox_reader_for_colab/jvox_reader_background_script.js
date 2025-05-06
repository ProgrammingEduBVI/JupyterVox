chrome.runtime.onInstalled.addListener(() => {
    console.log("JVox screen reader background script started")
});

var server_url = "http://3.144.13.232/jvox";
//var server_url = "http://127.0.0.1:5000/";

/*##########################################################
  Communication with content.js
##########################################################*/

/*
 * Function to handle content script's messages.
 * Cannot be an "async" function to allow correct sendResponse behavior, base on
 * https://stackoverflow.com/a/53024910.
 *
 * Since this function cann't be async, then we can't use "await" on
 * jvox_gen_speech_sound. So "then" as a call back is the only solution.
 *
 * JSON encoding part is from https://stackoverflow.com/a/10072601
 */
function jvox_bg_handle_content_message(request, sender, sendResponse) {
    console.log(`JVox SR Bg: Message from content type: ${request.type}, `)


    if (request.type === "chunkify_stmt"){
	console.log(`JVox SR Bg: Chunkify request with stmt: ${request.stmt}, `,
		    `col: ${request.col_nu}, command: ${request.command}`)

	jvox_bg_chunkify_statement(request.stmt, request.col_nu,
				   request.command).then(chunkify_response =>{
				       sendResponse(chunkify_response);;
	});
	
    }
    
    // must return true to keep the communication channe alive. Otherwise,
    // content script will receive undefined as response. Seems to be a Chrome
    // bug: see, https://stackoverflow.com/a/53024910 and
    // https://crbug.com/1185241
    return true;
}

// add listener to handle send statement message
chrome.runtime.onMessage.addListener(jvox_bg_handle_content_message);


/*##########################################################
  Chunkify Statement
##########################################################*/

// size of each chunk
var chunkify_len = "3";

// async function to communicate with JVox server to obtain reading in mp3
// "Async” allows "await" in the caller.
// "fetch" part obtain from JS document：
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function jvox_bg_chunkify_statement(stmt, col_nu, command){
    // contact server to find the corresponding token's position
    col_nu = col_nu - 1; // monaco col nubmer starts at 1 instead 0, so minus 1
    let surl = server_url + "/chunkify";
    let data = {"stmt":stmt,
                "cur_pos":col_nu.toString(),
                "chunk_len":chunkify_len,
                "command":command};

    console.log(`JVox SR Bg: sending chunkify request to server ${surl}`)

    const response = await fetch(surl, {
	method: "POST",
	mode: "cors",
	cache: "no-cache",
	credentials: "same-origin",
	headers: {
	    "Content-Type": "application/json",
	},
	redirect: "follow", 
	referrerPolicy: "no-referrer", 
	body: JSON.stringify(data), // body data type must match "Content-Type" header
    });

    console.log("JVox SR Bg: got reply type:", response.headers.get("content-type"))
    
    // get the json response from the server
    let chunkify_response = await response.json() // wait the response json to resolve
    
    console.log("JVox SR Bg: Chunkify server respose, ",
		`Chunks to read: ${chunkify_response.chunk_to_read}, `,
		`Chunks: ${chunkify_response.chunks}, `,
		`New col position: ${chunkify_response.new_pos}, `,
		`Chunk string: ${chunkify_response.chunk_string}, `,
		`Error message: ${chunkify_response.error_message}, `,
	       );

    return chunkify_response
}
