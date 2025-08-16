import * as net from 'net';

export interface IPCMessage {
    id?: string;
    type: string;
    data?: any;
}

export interface IPCResponse {
    id?: string;
    type: string;
    data?: any;
    error?: {
        code: string;
        message: string;
    };
}

export interface ClientSession {
    id: string;
    socket: net.Socket;
    authenticated: boolean;
    buffer: string;
    context: any;
}

export interface FileInfo {
    name: string;
    path: string;
    type: 'file' | 'directory';
    size?: number;
    modified?: Date;
}

export interface SearchResult {
    file: string;
    line: number;
    column: number;
    text: string;
    match: string;
}

export interface Diagnostic {
    uri: string;
    range: {
        start: { line: number; character: number };
        end: { line: number; character: number };
    };
    severity: 'error' | 'warning' | 'info' | 'hint';
    message: string;
    source?: string;
}

export interface TaskResult {
    success: boolean;
    output?: string;
    error?: string;
    exitCode?: number;
    taskId?: string;
}

export interface RooCodeCapabilities {
    commands: string[];
    tools: string[];
    features: string[];
    version: string;
}