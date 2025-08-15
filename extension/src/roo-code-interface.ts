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

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('Roo-Code Bridge');
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
                'runTask'
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

    async runTask(taskName: string): Promise<TaskResult> {
        this.log(`Running task: ${taskName}`);
        
        try {
            const tasks = await vscode.tasks.fetchTasks();
            const task = tasks.find(t => t.name === taskName);
            
            if (!task) {
                throw new Error(`Task '${taskName}' not found`);
            }
            
            const execution = await vscode.tasks.executeTask(task);
            
            // Wait for task to complete (simplified - in production, use proper event handling)
            return new Promise((resolve) => {
                const disposable = vscode.tasks.onDidEndTask((e) => {
                    if (e.execution === execution) {
                        disposable.dispose();
                        resolve({
                            success: true,
                            output: 'Task completed'
                        });
                    }
                });
                
                // Timeout after 30 seconds
                setTimeout(() => {
                    disposable.dispose();
                    resolve({
                        success: false,
                        error: 'Task timeout'
                    });
                }, 30000);
            });
        } catch (error: any) {
            this.log(`Task failed: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
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