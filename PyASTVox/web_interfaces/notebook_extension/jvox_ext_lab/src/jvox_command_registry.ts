// a central repository to manage commands and their hotkeys

export class JVoxCommandRegistry {
    public static commands = [
		{
            id: 'jvox:read-line-at-Cursor',
            label: 'Read the Line at Cursor',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt R']
        },
        {
            id: 'jvox:read-last-error',
            label: 'Read Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt E']
        },
        {
            id: 'jvox:jump-to-last-error-column',
            label: 'Jump to the Line and Column of Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt J']
        },
        {
            id: 'jvox:goto-last-error-line',
            label: 'Goto the Line of Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt G']
        },
        {
            id: 'jvox:check-cell-syntax',
            label: 'Check the Syntax of Current Cell at Cursor', 
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt C']
        },
        {
            id: 'jvox:verify-current-line',
            label: 'Check Current Cursor Line',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt V']
        },
        {
            id: 'jvox:read-next-chunk',
            label: 'Read Next Chunk from Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt N']
        },
        {
            id: 'jvox:read-previous-chunk',
            label: 'Read Previous Chunk from Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt P']
        },
        {
            id: 'jvox:read-current-chunk',
            label: 'Read the Chunk at Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt K']
        }
    ];

    /**
     * Get the command object by its id.
     */
    public static getCommandById(id: string) {
        return this.commands.find(cmd => cmd.id === id);
    }
}