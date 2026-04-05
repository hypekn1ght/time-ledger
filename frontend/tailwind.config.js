/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0D0D0F',
        surface: '#18181B',
        border: '#27272A',
        'text-primary': '#FAFAFA',
        'text-secondary': '#A1A1AA',
        gold: '#E5A50A',
        blue: '#3B82F6',
        purple: '#A855F7',
        slate: '#64748B',
        danger: '#EF4444',
        success: '#22C55E',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
