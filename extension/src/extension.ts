import * as vscode from 'vscode';
import { IPCServer } from './ipc-server';
import { RooCodeInterface } from './roo-code-interface';

let ipcServer: IPCServer | undefined;
let rooInterface: RooCodeInterface | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Roo-Code Bridge extension is now active');

    // Initialize Roo-Code interface
    rooInterface = new RooCodeInterface(context);

    // Register commands
    const startCommand = vscode.commands.registerCommand('roo-code-bridge.start', async () => {
        if (ipcServer?.isRunning()) {
            vscode.window.showInformationMessage('Roo-Code Bridge server is already running');
            return;
        }

        const config = vscode.workspace.getConfiguration('roo-code-bridge.server');
        const port = config.get<number>('port', 9999);
        const host = config.get<string>('host', '127.0.0.1');

        ipcServer = new IPCServer(host, port, rooInterface!);
        
        try {
            await ipcServer.start();
            vscode.window.showInformationMessage(`Roo-Code Bridge server started on ${host}:${port}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start server: ${error}`);
        }
    });

    const stopCommand = vscode.commands.registerCommand('roo-code-bridge.stop', async () => {
        if (!ipcServer?.isRunning()) {
            vscode.window.showInformationMessage('Roo-Code Bridge server is not running');
            return;
        }

        await ipcServer.stop();
        vscode.window.showInformationMessage('Roo-Code Bridge server stopped');
    });

    const statusCommand = vscode.commands.registerCommand('roo-code-bridge.status', () => {
        if (ipcServer?.isRunning()) {
            const stats = ipcServer.getStats();
            vscode.window.showInformationMessage(
                `Server running on ${stats.host}:${stats.port} | Clients: ${stats.connectedClients} | Messages: ${stats.messagesProcessed}`
            );
        } else {
            vscode.window.showInformationMessage('Roo-Code Bridge server is not running');
        }
    });

    context.subscriptions.push(startCommand, stopCommand, statusCommand);

    // Auto-start server if configured
    const autoStart = vscode.workspace.getConfiguration('roo-code-bridge').get<boolean>('autoStart', false);
    if (autoStart) {
        vscode.commands.executeCommand('roo-code-bridge.start');
    }
}

export function deactivate() {
    if (ipcServer?.isRunning()) {
        ipcServer.stop();
    }
}