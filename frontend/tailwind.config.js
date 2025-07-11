/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: [
          "JetBrains Mono",
          "Consolas",
          "Monaco",
          "Courier New",
          "monospace",
        ],
      },
      colors: {
        "code-bg": "#1e1e1e",
        "code-text": "#d4d4d4",
      },
    },
  },
  plugins: [],
};
