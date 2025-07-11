import React from "react";

interface ExplanationPanelProps {
  explanation: string | null;
  isExplaining: boolean;
  hasCode: boolean;
  onExplainCode: () => void;
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  explanation,
  isExplaining,
  hasCode,
  onExplainCode,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-fit">
      <div className="border-b border-gray-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-900">
          Code Explanation
        </h2>
        <p className="text-sm text-gray-600">
          AI-powered code analysis and explanation
        </p>
      </div>

      <div className="p-4">
        {!explanation && !isExplaining ? (
          <div className="text-center py-12">
            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Get Code Explanation
            </h3>
            <p className="text-gray-600 mb-6">
              Click the button below to get an AI-powered explanation of your
              code
            </p>
            <button
              onClick={onExplainCode}
              disabled={!hasCode}
              className={`px-4 py-2 rounded-md font-medium ${
                hasCode
                  ? "bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              Explain Code
            </button>
          </div>
        ) : isExplaining ? (
          <div className="text-center py-12">
            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4 animate-pulse">
              <svg
                className="w-6 h-6 text-blue-600 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Analyzing Code...
            </h3>
            <p className="text-gray-600">
              AI is analyzing your code and generating an explanation
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Explanation</h3>
              <button
                onClick={onExplainCode}
                disabled={!hasCode}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
              >
                Re-explain
              </button>
            </div>
            <div className="prose prose-sm max-w-none">
              <div
                className="text-gray-700 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{
                  __html: explanation?.replace(/\n/g, "<br>") || "",
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
