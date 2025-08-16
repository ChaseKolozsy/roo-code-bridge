import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';
import { FileInfo, SearchResult, Diagnostic, TaskResult, RooCodeCapabilities } from './types';

const execAsync = promisify(exec);
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const readdirAsync = promisify(fs.readdir);
const statAsync = promisify(fs.stat);

export class RooCodeInterface {
    private context: vscode.ExtensionContext;
    private outputChannel: vscode.OutputChannel;
    private rooCodeAPI: any = null;
    private rooCodeExtension: vscode.Extension<any> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('Roo-Code Bridge');
        this.initializeRooCodeConnection();
    }

    private async initializeRooCodeConnection() {
        try {
            // Roo-Code's extension ID (from the implementation details)
            const ROO_CODE_EXTENSION_ID = 'rooveterinaryinc.roo-cline';
            
            // Get the Roo-Code extension
            this.rooCodeExtension = vscode.extensions.getExtension(ROO_CODE_EXTENSION_ID);
            
            if (!this.rooCodeExtension) {
                this.log('Roo-Code extension not found');
                return;
            }
            
            // Activate if not already active
            if (!this.rooCodeExtension.isActive) {
                await this.rooCodeExtension.activate();
                this.log('Roo-Code extension activated');
            }
            
            // Get the API
            this.rooCodeAPI = this.rooCodeExtension.exports;
            
            if (this.rooCodeAPI) {
                this.log('Connected to Roo-Code API successfully');
                this.setupRooCodeEventListeners();
            } else {
                this.log('Roo-Code API not available');
            }
        } catch (error: any) {
            this.log(`Failed to connect to Roo-Code: ${error.message}`);
        }
    }

    private setupRooCodeEventListeners() {
        if (!this.rooCodeAPI) return;

        try {
            // Listen for task events
            this.rooCodeAPI.on('taskStarted', (taskId: string) => {
                this.log(`Task started: ${taskId}`);
                this.notifyClients('taskStarted', { taskId });
            });

            this.rooCodeAPI.on('taskCompleted', (taskId: string, tokenUsage: any, toolUsage: any, meta: any) => {
                this.log(`Task completed: ${taskId}`);
                this.notifyClients('taskCompleted', { taskId, tokenUsage, toolUsage, meta });
            });

            this.rooCodeAPI.on('taskAborted', (taskId: string) => {
                this.log(`Task aborted: ${taskId}`);
                this.notifyClients('taskAborted', { taskId });
            });

            // Listen for messages (the key part for communication)
            this.rooCodeAPI.on('message', (messageEvent: any) => {
                this.log(`Message from Roo-Code: ${JSON.stringify(messageEvent)}`);
                this.notifyClients('rooCodeMessage', messageEvent);
            });

            this.log('Roo-Code event listeners set up');
        } catch (error: any) {
            this.log(`Error setting up event listeners: ${error.message}`);
        }
    }

    private clientNotificationCallbacks: ((event: string, data: any) => void)[] = [];

    public onClientNotification(callback: (event: string, data: any) => void) {
        this.clientNotificationCallbacks.push(callback);
    }

    private notifyClients(event: string, data: any) {
        this.clientNotificationCallbacks.forEach(callback => {
            try {
                callback(event, data);
            } catch (error: any) {
                this.log(`Error notifying client: ${error.message}`);
            }
        });
    }

    getCapabilities(): RooCodeCapabilities {
        return {
            version: '0.1.0',
            commands: [
                'execute',
                'readFile',
                'writeFile',
                'listFiles',
                'search',
                'getActiveFile',
                'getDiagnostics',
                'runTask',
                'configureProvider',
                'approvalResponse'
            ],
            tools: [
                'terminal',
                'fileSystem',
                'search',
                'diagnostics',
                'tasks'
            ],
            features: [
                'authentication',
                'streaming',
                'contextManagement',
                'errorHandling'
            ]
        };
    }

    async executeCommand(command: string): Promise<any> {
        this.log(`Executing command: ${command}`);
        
        try {
            // Check if it's a VS Code command
            if (command.startsWith('vscode.')) {
                return await vscode.commands.executeCommand(command.substring(7));
            }
            
            // Otherwise, execute as shell command
            const { stdout, stderr } = await execAsync(command, {
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
            });
            
            return {
                success: true,
                stdout,
                stderr
            };
        } catch (error: any) {
            this.log(`Command failed: ${error.message}`);
            return {
                success: false,
                error: error.message,
                code: error.code
            };
        }
    }

    async readFile(filePath: string): Promise<string> {
        this.log(`Reading file: ${filePath}`);
        
        try {
            const absolutePath = this.resolveFilePath(filePath);
            const content = await readFileAsync(absolutePath, 'utf8');
            return content;
        } catch (error: any) {
            this.log(`Failed to read file: ${error.message}`);
            throw new Error(`Failed to read file: ${error.message}`);
        }
    }

    async writeFile(filePath: string, content: string): Promise<void> {
        this.log(`Writing file: ${filePath}`);
        
        try {
            const absolutePath = this.resolveFilePath(filePath);
            
            // Ensure directory exists
            const dir = path.dirname(absolutePath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
            
            await writeFileAsync(absolutePath, content, 'utf8');
            
            // Open the file in editor if it's in workspace
            const uri = vscode.Uri.file(absolutePath);
            if (vscode.workspace.getWorkspaceFolder(uri)) {
                const document = await vscode.workspace.openTextDocument(uri);
                await vscode.window.showTextDocument(document);
            }
        } catch (error: any) {
            this.log(`Failed to write file: ${error.message}`);
            throw new Error(`Failed to write file: ${error.message}`);
        }
    }

    async listFiles(directory?: string, pattern?: string): Promise<FileInfo[]> {
        this.log(`Listing files in: ${directory || 'workspace'}`);
        
        try {
            const baseDir = directory 
                ? this.resolveFilePath(directory)
                : vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
            
            const files = await this.scanDirectory(baseDir, pattern);
            return files;
        } catch (error: any) {
            this.log(`Failed to list files: ${error.message}`);
            throw new Error(`Failed to list files: ${error.message}`);
        }
    }

    private async scanDirectory(dir: string, pattern?: string): Promise<FileInfo[]> {
        const files: FileInfo[] = [];
        const entries = await readdirAsync(dir);
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry);
            const stat = await statAsync(fullPath);
            
            // Skip hidden files and node_modules
            if (entry.startsWith('.') || entry === 'node_modules') {
                continue;
            }
            
            // Apply pattern filter if provided
            if (pattern && !this.matchPattern(entry, pattern)) {
                continue;
            }
            
            files.push({
                name: entry,
                path: fullPath,
                type: stat.isDirectory() ? 'directory' : 'file',
                size: stat.size,
                modified: stat.mtime
            });
        }
        
        return files;
    }

    private matchPattern(filename: string, pattern: string): boolean {
        // Simple glob pattern matching
        const regexPattern = pattern
            .replace(/\./g, '\\.')
            .replace(/\*/g, '.*')
            .replace(/\?/g, '.');
        
        const regex = new RegExp(`^${regexPattern}$`);
        return regex.test(filename);
    }

    async search(query: string, options?: any): Promise<SearchResult[]> {
        this.log(`Searching for: ${query}`);
        
        const results: SearchResult[] = [];
        const config = {
            include: options?.include || '**/*',
            exclude: options?.exclude || '**/node_modules/**',
            maxResults: options?.maxResults || 100
        };
        
        try {
            // Use VS Code's built-in search
            const searchPattern = new vscode.RelativePattern(
                vscode.workspace.workspaceFolders?.[0] || '',
                config.include
            );
            
            const files = await vscode.workspace.findFiles(searchPattern, config.exclude, config.maxResults);
            
            for (const file of files) {
                const document = await vscode.workspace.openTextDocument(file);
                const text = document.getText();
                const lines = text.split('\n');
                
                lines.forEach((line, lineNumber) => {
                    const columnIndex = line.toLowerCase().indexOf(query.toLowerCase());
                    if (columnIndex !== -1) {
                        results.push({
                            file: file.fsPath,
                            line: lineNumber + 1,
                            column: columnIndex + 1,
                            text: line,
                            match: query
                        });
                    }
                });
            }
        } catch (error: any) {
            this.log(`Search failed: ${error.message}`);
            throw new Error(`Search failed: ${error.message}`);
        }
        
        return results;
    }

    async getActiveFile(): Promise<any> {
        const editor = vscode.window.activeTextEditor;
        
        if (!editor) {
            return null;
        }
        
        return {
            path: editor.document.uri.fsPath,
            language: editor.document.languageId,
            selection: {
                start: {
                    line: editor.selection.start.line,
                    character: editor.selection.start.character
                },
                end: {
                    line: editor.selection.end.line,
                    character: editor.selection.end.character
                }
            },
            content: editor.document.getText()
        };
    }

    async getDiagnostics(uri?: string): Promise<Diagnostic[]> {
        this.log(`Getting diagnostics for: ${uri || 'all files'}`);
        
        const diagnostics: Diagnostic[] = [];
        
        if (uri) {
            const vscodeUri = vscode.Uri.file(uri);
            const vscodeDiagnostics = vscode.languages.getDiagnostics(vscodeUri);
            
            for (const diag of vscodeDiagnostics) {
                diagnostics.push(this.convertDiagnostic(uri, diag));
            }
        } else {
            // Get all diagnostics
            const allDiagnostics = vscode.languages.getDiagnostics();
            
            for (const [fileUri, fileDiagnostics] of allDiagnostics) {
                for (const diag of fileDiagnostics) {
                    diagnostics.push(this.convertDiagnostic(fileUri.fsPath, diag));
                }
            }
        }
        
        return diagnostics;
    }

    private convertDiagnostic(uri: string, diag: vscode.Diagnostic): Diagnostic {
        const severityMap = {
            [vscode.DiagnosticSeverity.Error]: 'error' as const,
            [vscode.DiagnosticSeverity.Warning]: 'warning' as const,
            [vscode.DiagnosticSeverity.Information]: 'info' as const,
            [vscode.DiagnosticSeverity.Hint]: 'hint' as const
        };
        
        return {
            uri,
            range: {
                start: {
                    line: diag.range.start.line,
                    character: diag.range.start.character
                },
                end: {
                    line: diag.range.end.line,
                    character: diag.range.end.character
                }
            },
            severity: severityMap[diag.severity],
            message: diag.message,
            source: diag.source
        };
    }

    async runTask(prompt: string, config?: any): Promise<TaskResult> {
        this.log(`Running Roo-Code task: ${prompt.substring(0, 100)}...`);
        
        if (!this.rooCodeAPI) {
            return {
                success: false,
                error: 'Roo-Code API not available'
            };
        }

        try {
            // Use Roo-Code's startNewTask method
            const taskId = await this.rooCodeAPI.startNewTask({
                configuration: config || {
                    apiProvider: 'openai-compatible',
                    apiModelId: 'qwen-3-coder',
                    apiUrl: 'http://localhost:3000/v1',
                    contextLength: 131000,
                    maxTokens: 4096,
                    temperature: 0.7
                },
                text: prompt
            });

            this.log(`Roo-Code task started with ID: ${taskId}`);
            
            return {
                success: true,
                output: `Task started with ID: ${taskId}`,
                taskId: taskId
            };
        } catch (error: any) {
            this.log(`Roo-Code task failed: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Add method to configure Roo-Code provider
    async configureProvider(config: any): Promise<boolean> {
        this.log(`Configuring Roo-Code provider: ${JSON.stringify(config)}`);
        
        if (!this.rooCodeAPI) {
            this.log('Roo-Code API not available for configuration');
            return false;
        }

        try {
            await this.rooCodeAPI.setConfiguration(config);
            this.log('Roo-Code provider configured successfully');
            return true;
        } catch (error: any) {
            this.log(`Failed to configure Roo-Code provider: ${error.message}`);
            return false;
        }
    }

    // Add method to send approval responses
    async sendApprovalResponse(approved: boolean, response?: string): Promise<boolean> {
        this.log(`Sending approval response: ${approved ? 'approved' : 'denied'}`);
        
        if (!this.rooCodeAPI) {
            this.log('Roo-Code API not available for approval response');
            return false;
        }

        try {
            if (approved) {
                await this.rooCodeAPI.pressPrimaryButton();
            } else {
                await this.rooCodeAPI.pressSecondaryButton();
            }
            
            // If there's a text response, send it
            if (response) {
                await this.rooCodeAPI.sendMessage(response);
            }
            
            this.log('Approval response sent successfully');
            return true;
        } catch (error: any) {
            this.log(`Failed to send approval response: ${error.message}`);
            return false;
        }
    }

    // Check if Roo-Code is ready
    isRooCodeReady(): boolean {
        return this.rooCodeAPI?.isReady() || false;
    }

    private resolveFilePath(filePath: string): string {
        if (path.isAbsolute(filePath)) {
            return filePath;
        }
        
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            return path.join(workspaceFolder.uri.fsPath, filePath);
        }
        
        return path.resolve(filePath);
    }

    private log(message: string) {
        const timestamp = new Date().toISOString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
        
        const debug = vscode.workspace.getConfiguration('roo-code-bridge').get<boolean>('debug', false);
        if (debug) {
            console.log(`[Roo-Code Bridge] ${message}`);
        }
    }
}