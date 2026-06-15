/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#dae6ff",
          200: "#bdd1ff",
          300: "#92b1ff",
          400: "#6586ff",
          500: "#4361ee",
          600: "#3046d4",
          700: "#2837aa",
          800: "#1f2a82",
          900: "#192261",
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: "0 0 60px -10px rgba(67,97,238,0.45)",
      },
    },
  },
  plugins: [],
};
