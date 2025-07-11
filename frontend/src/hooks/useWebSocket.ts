import { useState, useEffect, useCallback, useRef } from "react";
import { WebSocketClient } from "../utils/websocket";
import {
  WebSocketMessage,
  ConnectionStatus,
  ExecutionOutput,
  ExplanationChunk,
} from "../types";

export const useWebSocket = (clientId: string) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    connecting: false,
  });

  const [executionOutput, setExecutionOutput] = useState<ExecutionOutput[]>([]);
  const [explanation, setExplanation] = useState<string>("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);

  const wsClientRef = useRef<WebSocketClient | null>(null);

  // Initialize WebSocket client
  useEffect(() => {
    if (!wsClientRef.current) {
      wsClientRef.current = new WebSocketClient(clientId);

      wsClientRef.current.onMessage((message: WebSocketMessage) => {
        handleWebSocketMessage(message);
      });

      wsClientRef.current.onConnectionChange(
        (connected: boolean, error?: string) => {
          setConnectionStatus({
            connected,
            connecting: false,
            error,
          });
        }
      );
    }

    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
      }
    };
  }, [clientId]);

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    console.log("Received WebSocket message:", message);

    switch (message.type) {
      case "execution_start":
        setIsExecuting(true);
        setExecutionOutput([]);
        break;

      case "execution_output":
        if (message.data) {
          setExecutionOutput((prev) => [
            ...prev,
            message.data as ExecutionOutput,
          ]);
        }
        break;

      case "execution_complete":
        setIsExecuting(false);
        break;

      case "explanation_start":
        setIsExplaining(true);
        setExplanation("");
        break;

      case "explanation_chunk":
        if (message.data) {
          setExplanation((prev) => prev + message.data);
        }
        break;

      case "explanation_complete":
        setIsExplaining(false);
        break;

      case "error":
        console.error("WebSocket error:", message.message);
        setIsExecuting(false);
        setIsExplaining(false);
        if (message.message) {
          setExecutionOutput((prev) => [
            ...prev,
            {
              type: "error",
              content: message.message,
            },
          ]);
        }
        break;

      default:
        console.log("Unknown message type:", message.type);
    }
  }, []);

  const connect = useCallback(async () => {
    if (
      wsClientRef.current &&
      !connectionStatus.connected &&
      !connectionStatus.connecting
    ) {
      setConnectionStatus((prev) => ({ ...prev, connecting: true }));
      try {
        await wsClientRef.current.connect();
      } catch (error) {
        console.error("Failed to connect:", error);
        setConnectionStatus({
          connected: false,
          connecting: false,
          error: "Failed to connect",
        });
      }
    }
  }, [connectionStatus.connected, connectionStatus.connecting]);

  const executeCode = useCallback((code: string, language: string) => {
    if (wsClientRef.current && wsClientRef.current.isConnected()) {
      wsClientRef.current.executeCode(code, language);
    } else {
      console.error("WebSocket not connected");
    }
  }, []);

  const explainCode = useCallback(
    (code: string, output: string = "", error: string = "") => {
      if (wsClientRef.current && wsClientRef.current.isConnected()) {
        wsClientRef.current.explainCode(code, output, error);
      } else {
        console.error("WebSocket not connected");
      }
    },
    []
  );

  const clearOutput = useCallback(() => {
    setExecutionOutput([]);
    setExplanation("");
  }, []);

  return {
    connectionStatus,
    executionOutput,
    explanation,
    isExecuting,
    isExplaining,
    connect,
    executeCode,
    explainCode,
    clearOutput,
  };
};
