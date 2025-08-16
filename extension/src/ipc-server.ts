import * as net from 'net';
import { EventEmitter } from 'events';
import { RooCodeInterface } from './roo-code-interface';
import { IPCMessage, IPCResponse, ClientSession } from './types';

export class IPCServer extends EventEmitter {
    private server: net.Server | undefined;
    private clients: Map<string, ClientSession> = new Map();
    private host: string;
    private port: number;
    private running: boolean = false;
    private messagesProcessed: number = 0;
    private rooInterface: RooCodeInterface;

    constructor(host: string, port: number, rooInterface: RooCodeInterface) {
        super();
        this.host = host;
        this.port = port;
        this.rooInterface = rooInterface;
        
        // Set up Roo-Code event forwarding
        this.rooInterface.onClientNotification((event: string, data: any) => {
            this.broadcastToClients(event, data);
        });
    }

    async start(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.server = net.createServer((socket) => {
                this.handleConnection(socket);
            });

            this.server.on('error', (error) => {
                console.error('Server error:', error);
                reject(error);
            });

            this.server.listen(this.port, this.host, () => {
                this.running = true;
                console.log(`IPC server listening on ${this.host}:${this.port}`);
                resolve();
            });
        });
    }

    private handleConnection(socket: net.Socket) {
        const clientId = `${socket.remoteAddress}:${socket.remotePort}`;
        console.log(`Client connected: ${clientId}`);

        const session: ClientSession = {
            id: clientId,
            socket,
            authenticated: false,
            buffer: '',
            context: {}
        };

        this.clients.set(clientId, session);

        socket.on('data', (data) => {
            session.buffer += data.toString();
            this.processBuffer(session);
        });

        socket.on('end', () => {
            console.log(`Client disconnected: ${clientId}`);
            this.clients.delete(clientId);
        });

        socket.on('error', (error) => {
            console.error(`Client error ${clientId}:`, error);
            this.clients.delete(clientId);
        });

        // Send welcome message
        this.sendResponse(socket, {
            type: 'welcome',
            data: {
                version: '0.1.0',
                capabilities: this.rooInterface.getCapabilities()
            }
        });
    }

    private processBuffer(session: ClientSession) {
        let newlineIndex;
        while ((newlineIndex = session.buffer.indexOf('\n')) !== -1) {
            const messageStr = session.buffer.substring(0, newlineIndex);
            session.buffer = session.buffer.substring(newlineIndex + 1);

            try {
                const message: IPCMessage = JSON.parse(messageStr);
                this.handleMessage(session, message);
            } catch (error) {
                console.error('Failed to parse message:', error);
                this.sendError(session.socket, 'PARSE_ERROR', 'Invalid JSON message');
            }
        }
    }

    private async handleMessage(session: ClientSession, message: IPCMessage) {
        console.log(`Processing message: ${message.type} from ${session.id}`);
        this.messagesProcessed++;

        try {
            switch (message.type) {
                case 'authenticate':
                    await this.handleAuthenticate(session, message);
                    break;
                
                case 'execute':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleExecute(session, message);
                    break;

                case 'readFile':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleReadFile(session, message);
                    break;

                case 'writeFile':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleWriteFile(session, message);
                    break;

                case 'listFiles':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleListFiles(session, message);
                    break;

                case 'search':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleSearch(session, message);
                    break;

                case 'getActiveFile':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleGetActiveFile(session, message);
                    break;

                case 'getDiagnostics':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleGetDiagnostics(session, message);
                    break;

                case 'runTask':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleRunTask(session, message);
                    break;

                case 'configureProvider':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleConfigureProvider(session, message);
                    break;

                case 'approvalResponse':
                    if (!session.authenticated) {
                        this.sendError(session.socket, 'AUTH_REQUIRED', 'Authentication required');
                        return;
                    }
                    await this.handleApprovalResponse(session, message);
                    break;

                default:
                    this.sendError(session.socket, 'UNKNOWN_MESSAGE', `Unknown message type: ${message.type}`);
            }
        } catch (error: any) {
            console.error('Error handling message:', error);
            this.sendError(session.socket, 'INTERNAL_ERROR', error.message);
        }
    }

    private async handleAuthenticate(session: ClientSession, message: IPCMessage) {
        const { apiKey } = message.data || {};
        
        // Simple authentication - in production, validate against secure store
        if (apiKey && apiKey.length > 0) {
            session.authenticated = true;
            this.sendResponse(session.socket, {
                type: 'authenticated',
                data: { success: true }
            });
        } else {
            this.sendError(session.socket, 'AUTH_FAILED', 'Invalid API key');
        }
    }

    private async handleExecute(session: ClientSession, message: IPCMessage) {
        const { command } = message.data || {};
        if (!command) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Command is required');
            return;
        }

        const result = await this.rooInterface.executeCommand(command);
        this.sendResponse(session.socket, {
            type: 'executeResult',
            data: result
        });
    }

    private async handleReadFile(session: ClientSession, message: IPCMessage) {
        const { path } = message.data || {};
        if (!path) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Path is required');
            return;
        }

        const content = await this.rooInterface.readFile(path);
        this.sendResponse(session.socket, {
            type: 'fileContent',
            data: { path, content }
        });
    }

    private async handleWriteFile(session: ClientSession, message: IPCMessage) {
        const { path, content } = message.data || {};
        if (!path || content === undefined) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Path and content are required');
            return;
        }

        await this.rooInterface.writeFile(path, content);
        this.sendResponse(session.socket, {
            type: 'writeSuccess',
            data: { path }
        });
    }

    private async handleListFiles(session: ClientSession, message: IPCMessage) {
        const { directory, pattern } = message.data || {};
        const files = await this.rooInterface.listFiles(directory, pattern);
        this.sendResponse(session.socket, {
            type: 'fileList',
            data: { files }
        });
    }

    private async handleSearch(session: ClientSession, message: IPCMessage) {
        const { query, options } = message.data || {};
        if (!query) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Query is required');
            return;
        }

        const results = await this.rooInterface.search(query, options);
        this.sendResponse(session.socket, {
            type: 'searchResults',
            data: { results }
        });
    }

    private async handleGetActiveFile(session: ClientSession, message: IPCMessage) {
        const activeFile = await this.rooInterface.getActiveFile();
        this.sendResponse(session.socket, {
            type: 'activeFile',
            data: activeFile
        });
    }

    private async handleGetDiagnostics(session: ClientSession, message: IPCMessage) {
        const { uri } = message.data || {};
        const diagnostics = await this.rooInterface.getDiagnostics(uri);
        this.sendResponse(session.socket, {
            type: 'diagnostics',
            data: { diagnostics }
        });
    }

    private async handleRunTask(session: ClientSession, message: IPCMessage) {
        const { prompt, config } = message.data || {};
        if (!prompt) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Prompt is required');
            return;
        }

        const result = await this.rooInterface.runTask(prompt, config);
        this.sendResponse(session.socket, {
            type: 'taskResult',
            data: result
        });
    }

    private async handleConfigureProvider(session: ClientSession, message: IPCMessage) {
        const config = message.data;
        if (!config) {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Configuration is required');
            return;
        }

        const success = await this.rooInterface.configureProvider(config);
        this.sendResponse(session.socket, {
            type: 'configurationResult',
            data: { success }
        });
    }

    private async handleApprovalResponse(session: ClientSession, message: IPCMessage) {
        const { approved, response } = message.data || {};
        if (typeof approved !== 'boolean') {
            this.sendError(session.socket, 'INVALID_PARAMS', 'Approval status is required');
            return;
        }

        const success = await this.rooInterface.sendApprovalResponse(approved, response);
        this.sendResponse(session.socket, {
            type: 'approvalResult',
            data: { success }
        });
    }

    private broadcastToClients(event: string, data: any) {
        const message = JSON.stringify({
            type: 'event',
            data: { event, data }
        }) + '\n';

        for (const [clientId, session] of this.clients.entries()) {
            if (session.authenticated) {
                try {
                    session.socket.write(message);
                } catch (error) {
                    console.error(`Failed to send event to client ${clientId}:`, error);
                }
            }
        }
    }

    private sendResponse(socket: net.Socket, response: IPCResponse) {
        const message = JSON.stringify(response) + '\n';
        socket.write(message);
    }

    private sendError(socket: net.Socket, code: string, message: string) {
        this.sendResponse(socket, {
            type: 'error',
            error: { code, message }
        });
    }

    async stop(): Promise<void> {
        return new Promise((resolve) => {
            // Close all client connections
            for (const [clientId, session] of this.clients) {
                session.socket.end();
            }
            this.clients.clear();

            if (this.server) {
                this.server.close(() => {
                    this.running = false;
                    console.log('IPC server stopped');
                    resolve();
                });
            } else {
                resolve();
            }
        });
    }

    isRunning(): boolean {
        return this.running;
    }

    getStats() {
        return {
            host: this.host,
            port: this.port,
            connectedClients: this.clients.size,
            messagesProcessed: this.messagesProcessed
        };
    }
}