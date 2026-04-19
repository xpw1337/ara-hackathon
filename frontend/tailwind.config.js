/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brutal-black': '#000000',
        'brutal-white': '#FFFFFF',
        'brutal-lime': '#CCFF00',
        'brutal-pink': '#FF6B9D',
        'brutal-mint': '#98FF98',
        'brutal-purple': '#C4A1FF',
        'brutal-yellow': '#FFE566',
        'brutal-coral': '#FF6B6B',
        'brutal-cyan': '#6BFFF6',
        'brutal-cream': '#FFF8E7',
      },
      fontFamily: {
        'mono': ['Space Mono', 'monospace'],
        'display': ['Space Grotesk', 'sans-serif'],
      },
      boxShadow: {
        'brutal': '4px 4px 0px 0px #000000',
        'brutal-lg': '8px 8px 0px 0px #000000',
        'brutal-hover': '2px 2px 0px 0px #000000',
      },
      borderWidth: {
        '3': '3px',
      }
    },
  },
  plugins: [],
}