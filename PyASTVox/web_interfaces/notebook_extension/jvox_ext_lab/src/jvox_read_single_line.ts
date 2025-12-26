import {
  JupyterFrontEnd,
} from '@jupyterlab/application';

import { INotebookTracker} from '@jupyterlab/notebook';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { ICommandPalette } from '@jupyterlab/apputils';

import { requestAPI } from './request';

import { jvox_speak } from './jvox_utils';


// read current line at cursor and send the line to the server to
// retrieve reading
function jvox_read_line(notebookTracker: INotebookTracker)
{
    const panel = notebookTracker.currentWidget;
    if (!panel) {
	console.warn('No active notebook');
	return;
    }
		
    const cell = panel.content.activeCell;
    if (!cell) {
	console.warn('No active cell');
	return;
    }
    
    const editor = cell.editor;
    if (!(editor instanceof CodeMirrorEditor)) {
	console.warn('Editor is not CodeMirror');
	return;
    }
    
    const cm = editor.editor; // CodeMirror 6 EditorView
    const cursor = cm.state.selection.main.head;
    const line = cm.state.doc.lineAt(cursor);
    
    const lineText = line.text;
    const lineNumber = line.number;
    
    // log the line
    console.log(`Line ${lineNumber}: ${lineText}`);

    // send line to server extension
    const dataToSend = { stmt: lineText };
    requestAPI('readline', {
	body: JSON.stringify(dataToSend),
	method: 'POST'
    })
	.then(reply => {
	    console.log(reply);
	    jvox_handle_readline_response(reply);
	})
	.catch(reason => {
	    console.error(
		`Error on JVox read single line with ${dataToSend}.\n${reason}`
	    );
	});
}

// register the command for JVox single-line screen read
export function jvox_add_readline_command(
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    palette: ICommandPalette)
{

    // add new command that read current line at cursor
    const { commands } = app;
    const commandID = 'jvox:read-cursor-line';
    
    commands.addCommand(commandID, {
	label: 'Read Current Cursor Line',
	execute: () => jvox_read_line(notebookTracker)
    });
    
    // Register a default hotkey: Ctrl+Alt+J (Cmd+Alt+J on macOS)
    app.commands.addKeyBinding({
	command: commandID,
	keys: ['Accel Alt J'],
	selector: '.jp-Notebook.jp-mod-editMode'
    });
    
    palette.addItem({ command: commandID, category: 'JVox Operations' });
}

// Process the speech in text and audio from the server extension
async function jvox_handle_readline_response(response: Response){
    console.debug("JVox readline response:", response);

    // Unpack JSON
    const data = await response.json();
  
    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.debug("speech text:", speechText);

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    jvox_speak(audioUrl);

    return;
}
