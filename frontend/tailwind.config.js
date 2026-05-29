/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // PwC brand palette
        pwc: {
          orange: '#D04A02',
          'orange-dark': '#A53C02',
          'orange-light': '#EB6914',
          navy: '#1B1F2A',
          'navy-light': '#252B3B',
          'navy-muted': '#2E3547',
          slate: '#3D4663',
          'gray-cool': '#8892A4',
          'gray-light': '#B8C0CC',
          'surface': '#F4F5F7',
          'surface-dark': '#ECEEF2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0,0,0,0.10), 0 1px 2px -1px rgba(0,0,0,0.06)',
        'card-lg': '0 4px 16px 0 rgba(0,0,0,0.12)',
        'glow-orange': '0 0 24px rgba(208,74,2,0.25)',
      },
    },
  },
  plugins: [],
}
