import { WebSocketMessage, ExecutionOutput, ExplanationChunk } from "../types";

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private clientId: string;

  private onMessageCallback?: (message: WebSocketMessage) => void;
  private onConnectionChangeCallback?: (
    connected: boolean,
    error?: string
  ) => void;

  constructor(clientId: string) {
    this.clientId = clientId;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `ws://localhost:8000/ws/${this.clientId}`;
        console.log(`Attempting to connect to: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log(`WebSocket connected successfully to ${wsUrl}`);
          this.reconnectAttempts = 0;
          this.onConnectionChangeCallback?.(true);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.onMessageCallback?.(message);
          } catch (error) {
            console.error("Error parsing WebSocket message:", error);
          }
        };

        this.ws.onclose = (event) => {
          console.log(
            `WebSocket disconnected: code=${event.code}, reason='${event.reason}', wasClean=${event.wasClean}`
          );
          this.onConnectionChangeCallback?.(false);

          // Attempt to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              console.log(
                `Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`
              );
              this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
          } else {
            console.error(
              `Max reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`
            );
          }
        };

        this.ws.onerror = (error) => {
          console.error(`WebSocket error for ${wsUrl}:`, error);
          console.error(
            `WebSocket readyState: ${this.ws?.readyState} (0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED)`
          );
          this.onConnectionChangeCallback?.(false, "Connection error");
          reject(error);
        };
      } catch (error) {
        console.error("Failed to create WebSocket:", error);
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  executeCode(code: string, language: string): void {
    this.send({
      action: "execute_code",
      code,
      language,
    });
  }

  explainCode(code: string, output: string = "", error: string = ""): void {
    this.send({
      action: "explain_code",
      code,
      output,
      error,
    });
  }

  onMessage(callback: (message: WebSocketMessage) => void): void {
    this.onMessageCallback = callback;
  }

  onConnectionChange(
    callback: (connected: boolean, error?: string) => void
  ): void {
    this.onConnectionChangeCallback = callback;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
