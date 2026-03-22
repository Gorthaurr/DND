import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Core palette — GitHub Dark + Gold
        parchment: {
          DEFAULT: "#E6EDF3",
          50: "#f0f6fc",
          100: "#e6edf3",
          200: "#c9d1d9",
          300: "#8b949e",
          400: "#6e7681",
        },
        ink: {
          DEFAULT: "#0D1117",
          light: "#161B22",
          dark: "#010409",
        },
        gold: {
          DEFAULT: "#C23A2E",
          light: "#E04A3E",
          dark: "#8B2A20",
          dim: "#6B1F18",
        },
        accent: {
          DEFAULT: "#C23A2E",
          light: "#E04A3E",
          dark: "#8B2A20",
        },
        "dark-wood": {
          DEFAULT: "#161B22",
          light: "#1C2128",
          dark: "#0D1117",
        },
        "light-wood": {
          DEFAULT: "#30363D",
          light: "#484F58",
          dark: "#21262D",
        },
        blood: {
          DEFAULT: "#DA3633",
          light: "#f85149",
          glow: "#ff1744",
        },
        forest: {
          DEFAULT: "#2e7d32",
          light: "#4caf50",
          glow: "#69f0ae",
        },
        arcane: {
          DEFAULT: "#7c4dff",
          light: "#b388ff",
          dark: "#4a148c",
          glow: "#d500f9",
        },
        ember: {
          DEFAULT: "#C23A2E",
          light: "#E04A3E",
          dark: "#8B2A20",
          glow: "#E04A3E",
        },
        frost: {
          DEFAULT: "#64b5f6",
          light: "#90caf9",
          dark: "#1565c0",
        },
        // UI surfaces — blue-black palette
        surface: {
          DEFAULT: "#0D1117",
          raised: "#161B22",
          overlay: "#1C2128",
          card: "#161B22",
        },
      },
      fontFamily: {
        medieval: ["Cinzel", "Georgia", "serif"],
        body: ["Crimson Text", "Georgia", "serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "2xs": ["0.8rem", { lineHeight: "1.2rem" }],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "dark-vignette":
          "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.8) 100%)",
        "gold-shimmer":
          "linear-gradient(90deg, transparent 0%, rgba(194,58,46,0.06) 50%, transparent 100%)",
      },
      boxShadow: {
        glow: "0 0 15px rgba(194, 58, 46, 0.2)",
        "glow-sm": "0 0 8px rgba(194, 58, 46, 0.15)",
        "glow-lg": "0 0 30px rgba(194, 58, 46, 0.3)",
        "inner-glow": "inset 0 0 20px rgba(194, 58, 46, 0.06)",
        arcane: "0 0 20px rgba(124, 77, 255, 0.2)",
        ember: "0 0 20px rgba(194, 58, 46, 0.2)",
      },
      borderColor: {
        subtle: "rgba(48, 54, 61, 0.5)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        shimmer: "shimmer 3s ease-in-out infinite",
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        typing: "typing 1.5s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 15px rgba(194, 58, 46, 0.1)" },
          "50%": { boxShadow: "0 0 30px rgba(194, 58, 46, 0.3)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        typing: {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "1" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
export default config;
