import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#081019",
        panel: "#101b27",
        signal: "#6ee7b7",
        warning: "#f59e0b",
        danger: "#fb7185",
        accent: "#7dd3fc",
      },
      fontFamily: {
        sans: ["Space Grotesk", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 20px 60px rgba(0, 0, 0, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
