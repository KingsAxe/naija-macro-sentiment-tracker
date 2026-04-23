import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#050505",
        panel: "#101010",
        primary: "#1f1f1f",
        primaryBright: "#f5f5f5",
        signal: "#34d399",
        warning: "#f59e0b",
        danger: "#fb7185",
        accent: "#d4d4d4",
      },
      fontFamily: {
        sans: ["Space Grotesk", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 24px 70px rgba(2, 12, 32, 0.42)",
      },
    },
  },
  plugins: [],
};

export default config;
