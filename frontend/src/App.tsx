import React, { useState, useEffect, useMemo } from "react";
import { CodeEditor } from "./components/CodeEditor";
import { OutputPanel } from "./components/OutputPanel";
import { ExplanationPanel } from "./components/ExplanationPanel";
import { Header } from "./components/Header";
import { StatusBar } from "./components/StatusBar";
import { useWebSocket } from "./hooks/useWebSocket";
import { Language } from "./types";

function App() {
  const [code, setCode] = useState<string>(
    '# Welcome to Smart Code Tutor!\n# Write your Python or JavaScript code here\n\nprint("Hello, World!")'
  );
  const [language, setLanguage] = useState<Language>("python");

  // Generate a stable client ID that doesn't change on re-renders
  const clientId = useMemo(() => {
    return `client_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  const {
    connectionStatus,
    executionOutput,
    explanation,
    isExecuting,
    isExplaining,
    connect,
    executeCode,
    explainCode,
    clearOutput,
  } = useWebSocket(clientId);

  // Auto-connect on mount
  useEffect(() => {
    connect();
  }, [connect]);

  const handleRunCode = () => {
    if (code.trim()) {
      executeCode(code, language);
    }
  };

  const handleExplainCode = () => {
    if (code.trim()) {
      const output = executionOutput
        .filter((item) => item.type === "stdout")
        .map((item) => item.content)
        .join("\n");

      const error = executionOutput
        .filter((item) => item.type === "stderr" || item.type === "error")
        .map((item) => item.content)
        .join("\n");

      explainCode(code, output, error);
    }
  };

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    // Update default code based on language
    if (newLanguage === "python") {
      setCode(
        '# Welcome to Smart Code Tutor!\n# Write your Python code here\n\nprint("Hello, World!")'
      );
    } else {
      setCode(
        '// Welcome to Smart Code Tutor!\n// Write your JavaScript code here\n\nconsole.log("Hello, World!");'
      );
    }
    clearOutput();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        language={language}
        onLanguageChange={handleLanguageChange}
        onRunCode={handleRunCode}
        onExplainCode={handleExplainCode}
        onClearOutput={clearOutput}
        isExecuting={isExecuting}
        isExplaining={isExplaining}
        connectionStatus={connectionStatus}
      />

      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Code Editor */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200 px-4 py-3">
                <h2 className="text-lg font-semibold text-gray-900">
                  Code Editor
                </h2>
                <p className="text-sm text-gray-600">
                  Write your {language} code here
                </p>
              </div>
              <div className="p-4">
                <CodeEditor
                  value={code}
                  onChange={setCode}
                  language={language}
                  height="400px"
                />
              </div>
            </div>

            {/* Output Panel */}
            <OutputPanel
              output={executionOutput}
              isExecuting={isExecuting}
              language={language}
            />
          </div>

          {/* Right Column - Explanation */}
          <div>
            <ExplanationPanel
              explanation={explanation}
              isExplaining={isExplaining}
              hasCode={code.trim().length > 0}
              onExplainCode={handleExplainCode}
            />
          </div>
        </div>
      </main>

      <StatusBar connectionStatus={connectionStatus} />
    </div>
  );
}

export default App;
