import React from "react";
import { Play, Brain, Trash2, Wifi, WifiOff } from "lucide-react";
import { Language, ConnectionStatus } from "../types";

interface HeaderProps {
  language: Language;
  onLanguageChange: (language: Language) => void;
  onRunCode: () => void;
  onExplainCode: () => void;
  onClearOutput: () => void;
  isExecuting: boolean;
  isExplaining: boolean;
  connectionStatus: ConnectionStatus;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  onRunCode,
  onExplainCode,
  onClearOutput,
  isExecuting,
  isExplaining,
  connectionStatus,
}) => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Smart Code Tutor
              </h1>
              <p className="text-xs text-gray-500">Interactive Code Learning</p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value as Language)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
            </select>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={onRunCode}
                disabled={isExecuting || !connectionStatus.connected}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>{isExecuting ? "Running..." : "Run Code"}</span>
              </button>

              <button
                onClick={onExplainCode}
                disabled={isExplaining || !connectionStatus.connected}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Brain className="w-4 h-4" />
                <span>{isExplaining ? "Explaining..." : "Explain Code"}</span>
              </button>

              <button
                onClick={onClearOutput}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear</span>
              </button>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {connectionStatus.connected ? (
                <div className="flex items-center space-x-1 text-green-600">
                  <Wifi className="w-4 h-4" />
                  <span className="text-sm">Connected</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-red-600">
                  <WifiOff className="w-4 h-4" />
                  <span className="text-sm">
                    {connectionStatus.connecting
                      ? "Connecting..."
                      : "Disconnected"}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
