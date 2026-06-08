// src/frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0a0905',
        parchment: '#3a3020',
        bamboo: '#2a2018',
        vermillion: '#cc3300',
        fire: '#ff4400',
        aged: '#886655',
        bark: '#443322',
        ember: '#ff8800',
      },
      fontFamily: {
        display: ['Impact', '"Arial Black"', 'sans-serif'],
        body: ['Georgia', 'serif'],
        mono: ['"Courier New"', 'monospace'],
      },
    },
  },
  plugins: [],
}
