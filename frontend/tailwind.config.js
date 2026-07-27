/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        linkedin: {
          blue: '#0A66C2',
          hover: '#004182',
          light: '#E8F0FE',
          bg: '#F3F2EF',
          card: '#FFFFFF',
          darkBg: '#0F172A',
          darkCard: '#1E293B',
          darkBorder: '#334155'
        }
      }
    },
  },
  plugins: [],
}
