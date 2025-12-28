import {
    JupyterFrontEnd,
  //  JupyterFrontEndPlugin
} from '@jupyterlab/application';
 
import { INotebookTracker } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';
 
import { requestAPI } from './request';
 
 //import { EditorView } from '@codemirror/view';
 
import { CodeEditor } from '@jupyterlab/codeeditor';
 
//import { jvox_speak } from './jvox_audio_request';

import { jvox_getLineAndCursor, jvox_speak } from './jvox_utils';
 
import { JVoxCommandRegistry } from './jvox_command_registry';
 
 export class jvox_ReadChunk {
    private chunk_len: number = 3;

    // Register "read next chunk", "read previous chunk", and "read current chunk" commands
	public jvox_registerReadChunkCommands(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {

        // rext next chunk
		const { commands } = app;
		const commandObj = JVoxCommandRegistry.getCommandById('jvox:read-next-chunk');
		if (!commandObj) {
			console.error("JVox command registry: command 'jvox:read-next-error' not found.");
			return;
		}

		commands.addCommand(commandObj.id, {
			label: commandObj.label,
			execute: () => this.jvox_readChunk(notebookTracker, "next")
		});

		app.commands.addKeyBinding({
			command: commandObj.id,
			keys: commandObj.hotkeys,
			selector: commandObj.selector
		});

		palette.addItem({ command: commandObj.id, category: 'JVox Operations' });

		// read previous chunk
		const prevCommandObj = JVoxCommandRegistry.getCommandById('jvox:read-previous-chunk');
		if (!prevCommandObj) {
			console.error("JVox command registry: command 'jvox:read-previous-chunk' not found.");
			return;
		}

		commands.addCommand(prevCommandObj.id, {
			label: prevCommandObj.label,
			execute: () => this.jvox_readChunk(notebookTracker, "pre")
		});

		app.commands.addKeyBinding({
			command: prevCommandObj.id,
			keys: prevCommandObj.hotkeys,
			selector: prevCommandObj.selector
		});

		palette.addItem({ command: prevCommandObj.id, category: 'JVox Operations' });

		// read current chunk
		const currentCommandObj = JVoxCommandRegistry.getCommandById('jvox:read-current-chunk');
		if (!currentCommandObj) {
			console.error("JVox command registry: command 'jvox:read-current-chunk' not found.");
			return;
		}

		commands.addCommand(currentCommandObj.id, {
			label: currentCommandObj.label,
			execute: () => this.jvox_readChunk(notebookTracker, "current")
		});

		app.commands.addKeyBinding({
			command: currentCommandObj.id,
			keys: currentCommandObj.hotkeys,
			selector: currentCommandObj.selector
		});

		palette.addItem({ command: currentCommandObj.id, category: 'JVox Operations' });
	}

    /**
     * Retrieves the text and cursor position of the line at the current cursor in the active cell.
     * @param notebookTracker The INotebookTracker instance for tracking the active notebook and cell.
     * @returns An object of the form { lineText: string, cursor: number }, or null if unavailable.
     */
    private jvox_readChunk(notebookTracker:INotebookTracker,
                           readCommand: string)
    {
        const cursorInfo = jvox_getLineAndCursor(notebookTracker);
        console.log("JVox: Line and Cursor info:", cursorInfo);

        if (!cursorInfo){
            console.log("JVox: cannot obtain cursor to read chunk");
            return;
        }

        // send line to server extension
        const dataToSend = { 
            statement: cursorInfo.lineText,
            cursor_pos: cursorInfo.column,
            command: readCommand,
            chunk_len: this.chunk_len
         };
        requestAPI('readChunk', {
            body: JSON.stringify(dataToSend),
            method: 'POST'
        })
            .then(reply => {
                console.log(reply);
                this.jvox_handleReadChunkResponse(reply, cursorInfo);
            })
            .catch(reason => {
                console.error(
                    `Error on JVox read chunk with ${dataToSend}.\n${reason}`
                );
            });

        return;
    }

    private async jvox_handleReadChunkResponse(
        response: Response,
        cursorInfo: any)
    {
        console.debug("JVox read chunk response:", response);

        // Unpack JSON
        const data = await response.json();
      
        // Access the speech in text and audio
        const speechText = data.chunk_to_read;
        const base64Audio = data.audio;

        // play audio
        console.debug("speech text:", speechText);
        // Extract BASE64 encoded audio bytes, and play the audio
        const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
        jvox_speak(audioUrl);

        // set new cursor position
        const editor: CodeEditor.IEditor = cursorInfo.editor;
        editor.setCursorPosition({
            column: data.new_pos,
            line: cursorInfo.line
        });
        editor.focus()

        return;
    }
 }
