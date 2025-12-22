import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { INotebookTracker } from '@jupyterlab/notebook';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { ICommandPalette } from '@jupyterlab/apputils';

import { requestAPI } from './request';

/**
 * Initialization data for the jvox-lab-ext-screenreader extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    id: 'jvox-lab-ext-screenreader:plugin',
    description: 'A JupyterLab extension for JVox for screen reading',
    autoStart: true,
    requires: [INotebookTracker, ICommandPalette],
    optional: [ISettingRegistry],
    activate: (
	app: JupyterFrontEnd,
	notebookTracker: INotebookTracker,
	palette: ICommandPalette,
	settingRegistry: ISettingRegistry | null
    ) => {
	console.log('JupyterLab extension jvox-lab-ext-screenreader is activated!');

	// initialize setting registry
	if (settingRegistry) {
	    settingRegistry
		.load(plugin.id)
		.then(settings => {
		    console.log('jvox-lab-ext-screenreader settings loaded:', settings.composite);
		})
		.catch(reason => {
		    console.error('Failed to load settings for jvox-lab-ext-screenreader.', reason);
		});
	}

	// server extension connection test
	requestAPI('hello')
	    .then(response => {
		jvox_server_hello_test(response);
	    })
	    .catch(reason => {
		console.error(
		    `The jvox_lab_ext_screenreader server extension appears to be missing.\n${reason}`
		);
	    });
	
	// add the command of JVox single-line screen read 
	jvox_add_readline_command(app, notebookTracker, palette);
	
    }
};

// A simple async function to print the reponse form "hello" endpoint,
// for testing server connection
async function jvox_server_hello_test(response: Response)
{
    const data = await response.json();
    console.log(data);

    return;
}

// read current line at cursor and send the line to the server to
// retrieve reading
function jvox_read_line(notebookTracker: INotebookTracker)
{
    console.log("in function");
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
    requestAPI('speech', {
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
function jvox_add_readline_command(
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


// Create a static audio object for playing sound. This is because
// creating an audio object right before playing causes an awkward
// scilence/delay before the screenreading sound.
const audio = new Audio();
let reading_rate = 2; // increasing speech speed.
// Process the speech in text and audio from the server extension
async function jvox_handle_readline_response(response: Response){
    console.log(response);

    // Unpack JSON
    const data = await response.json();
  
    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.log("speech text:", speechText);

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    audio.src = audioUrl;
    audio.playbackRate = reading_rate;

    try {
	await audio.play();
	console.log("Audio playing successfully.");
    } catch (err) {
	console.error("Playback failed. Make sure you've interacted with the page.", err);
    }
}

export default plugin;
