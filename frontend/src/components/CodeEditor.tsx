import React from "react";
import Editor from "@monaco-editor/react";
import { Language } from "../types";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: Language;
  height?: string;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language,
  height = "400px",
}) => {
  const handleEditorChange = (newValue: string | undefined) => {
    onChange(newValue || "");
  };

  const getMonacoLanguage = (lang: Language): string => {
    switch (lang) {
      case "python":
        return "python";
      case "javascript":
        return "javascript";
      default:
        return "python";
    }
  };

  return (
    <div className="code-editor">
      <Editor
        height={height}
        language={getMonacoLanguage(language)}
        value={value}
        onChange={handleEditorChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
          roundedSelection: false,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          wordWrap: "on",
          tabSize: language === "python" ? 4 : 2,
          insertSpaces: true,
          detectIndentation: false,
          folding: true,
          foldingHighlight: true,
          bracketPairColorization: { enabled: true },
          guides: {
            indentation: true,
            bracketPairs: true,
          },
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: "on",
          quickSuggestions: {
            other: true,
            comments: false,
            strings: false,
          },
        }}
        loading={
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">Loading editor...</div>
          </div>
        }
      />
    </div>
  );
};
