import React from "react";
import { Terminal, Loader } from "lucide-react";
import { ExecutionOutput, Language } from "../types";

interface OutputPanelProps {
  output: ExecutionOutput[];
  isExecuting: boolean;
  language: Language;
}

export const OutputPanel: React.FC<OutputPanelProps> = ({
  output,
  isExecuting,
  language,
}) => {
  const renderOutputLine = (item: ExecutionOutput, index: number) => {
    switch (item.type) {
      case "start":
        return (
          <div key={index} className="text-blue-400 mb-2">
            ▶ Starting {item.language} execution...
          </div>
        );

      case "stdout":
        return (
          <div key={index} className="text-green-400">
            {item.content}
          </div>
        );

      case "stderr":
      case "error":
        return (
          <div key={index} className="text-red-400">
            {item.content || item.message}
          </div>
        );

      case "result":
        return (
          <div
            key={index}
            className={`mt-2 ${
              item.success ? "text-green-400" : "text-red-400"
            }`}
          >
            ▶ Process {item.success ? "completed successfully" : "failed"}
            {item.exit_code !== undefined && ` (exit code: ${item.exit_code})`}
          </div>
        );

      case "complete":
        return (
          <div key={index} className="text-blue-400 mt-2">
            ✓ Execution completed
            {item.execution_time && ` in ${item.execution_time.toFixed(3)}s`}
          </div>
        );

      default:
        return (
          <div key={index} className="text-gray-400">
            {JSON.stringify(item)}
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Output Console
          </h2>
          {isExecuting && (
            <div className="flex items-center space-x-2 text-blue-600">
              <Loader className="w-4 h-4 animate-spin" />
              <span className="text-sm">Running...</span>
            </div>
          )}
        </div>
        <p className="text-sm text-gray-600">
          Execution results will appear here
        </p>
      </div>

      <div className="console-output">
        {output.length === 0 && !isExecuting ? (
          <div className="text-gray-500 italic">
            No output yet. Click "Run Code" to execute your {language} code.
          </div>
        ) : (
          output.map((item, index) => renderOutputLine(item, index))
        )}

        {isExecuting && (
          <div className="flex items-center space-x-2 text-yellow-400 mt-2">
            <Loader className="w-4 h-4 animate-spin" />
            <span>Executing code...</span>
          </div>
        )}
      </div>
    </div>
  );
};
