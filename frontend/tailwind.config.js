/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // CIVIA Enterprise Theme Colors
        'gov-navy': '#0B132B',
        'gov-navy-light': '#1C2541',
        'gov-gold': '#C6A756',
        'gov-text': '#EAEAEA',
        'gov-text-muted': '#A9B0C3',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shatter': 'shatter 0.5s ease-in-out forwards',
      },
      keyframes: {
        shatter: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(1.1)', opacity: '0' },
        }
      }
    },
  },
  plugins: [],
}
