import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#061126",
        panel: "#0b1b33",
        primary: "#0b3a78",
        primaryBright: "#2563eb",
        signal: "#2dd4bf",
        warning: "#f59e0b",
        danger: "#fb7185",
        accent: "#93c5fd",
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
