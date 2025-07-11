import React from "react";
import { Wifi, WifiOff, AlertCircle, CheckCircle } from "lucide-react";
import { ConnectionStatus } from "../types";

interface StatusBarProps {
  connectionStatus: ConnectionStatus;
}

export const StatusBar: React.FC<StatusBarProps> = ({ connectionStatus }) => {
  return (
    <footer className="bg-gray-800 text-white py-2 px-4">
      <div className="container mx-auto flex items-center justify-between">
        {/* Connection Status */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {connectionStatus.connected ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-400" />
                <Wifi className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">
                  Connected to server
                </span>
              </>
            ) : connectionStatus.connecting ? (
              <>
                <div className="w-4 h-4 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-yellow-400">Connecting...</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4 text-red-400" />
                <WifiOff className="w-4 h-4 text-red-400" />
                <span className="text-sm text-red-400">
                  {connectionStatus.error || "Disconnected from server"}
                </span>
              </>
            )}
          </div>
        </div>

        {/* App Info */}
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <span>Smart Code Tutor v1.0.0</span>
          <span>•</span>
          <span>Powered by Gemini AI</span>
          <span>•</span>
          <span>Secure E2B Execution</span>
        </div>
      </div>
    </footer>
  );
};
