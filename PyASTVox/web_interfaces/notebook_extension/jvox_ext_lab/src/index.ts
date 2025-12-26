import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { INotebookTracker, NotebookActions } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';
import { ILSPDocumentConnectionManager } from '@jupyterlab/lsp';

import { requestAPI } from './request';

/**
 * JVox packages
 */
import { jvox_add_readline_command } from './jvox_read_single_line'
import {
    jvox_debugSupport
} from './jvox_debug_support'

/**
 * Initialization data for the jvox-lab-ext-screenreader extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    id: 'jvox-lab-ext-screenreader:plugin',
    description: 'A JupyterLab extension for JVox for screen reading',
    autoStart: true,
    requires: [INotebookTracker, ICommandPalette, ILSPDocumentConnectionManager],
    optional: [ISettingRegistry],
    activate: (
	app: JupyterFrontEnd,
	notebookTracker: INotebookTracker,
	palette: ICommandPalette,
	lspManager: ILSPDocumentConnectionManager,
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

		/*
		 * Register JVox debug support
		 */
		const jvox_debug = new jvox_debugSupport();
		// register an event handler to process the 
		// NotebookActions.executed.connect(jvox_on_execution_finished);
		// Use a wrapper to pass the extra parameters
		NotebookActions.executed.connect((sender, args) => {
			jvox_debug.jvox_onExecutionFinished(sender,
				args,
				notebookTracker,
				lspManager);
		});

		// register an event handler to monitor the connection signal
		// to LSP server
		lspManager.connected.connect((manager, connectionData) => {
			const { connection, virtualDocument } = connectionData;
			jvox_debug.jvox_onLSPConnected(notebookTracker, manager, connection, virtualDocument);
		});

		// add commands for JVox debug support
		jvox_debug.jvox_registerDebugSupportCommands(app, notebookTracker, palette);

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

export default plugin;
