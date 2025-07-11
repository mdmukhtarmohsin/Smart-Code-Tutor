export type Language = "python" | "javascript";

export interface CodeExecution {
  id: string;
  code: string;
  language: Language;
  output: string;
  error: string;
  isRunning: boolean;
  timestamp: Date;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
}

export interface ExecutionOutput {
  type: "start" | "stdout" | "stderr" | "result" | "complete" | "error";
  content?: string;
  success?: boolean;
  exit_code?: number;
  execution_time?: number;
  language?: Language;
  timestamp?: number;
  message?: string;
}

export interface ExplanationChunk {
  type:
    | "explanation_start"
    | "explanation_chunk"
    | "explanation_complete"
    | "error";
  data?: string;
  message?: string;
}

export interface ConnectionStatus {
  connected: boolean;
  connecting: boolean;
  error?: string;
}
