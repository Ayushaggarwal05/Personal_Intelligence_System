/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgMain: '#0c0c0e',
        bgSidebar: '#121216',
        bgCard: 'rgba(22, 22, 28, 0.6)',
        accentPurple: '#a855f7',
        accentCyan: '#06b6d4',
      }
    },
  },
  plugins: [],
}
