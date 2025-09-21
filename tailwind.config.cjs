const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/views/**/*.py',
    './app/api/**/*.py',
    './app/static/js/**/*.js'
  ],
  darkMode: 'class',
  theme: {
    container: { center: true, padding: '1rem' },
    extend: {
      screens: {
        xs: '480px'
      },
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          dark: '#1d4ed8',
          light: '#3b82f6'
        },
        secondary: '#10b981',
        accent: '#f59e0b',
        danger: '#22c55e',
        warning: '#f97316',
        gold: '#ffd700',
        success: '#ef4444',
        muted: '#64748b',
        up: '#22c55e',
        down: '#dc3545'
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
        mono: ['JetBrains Mono', ...defaultTheme.fontFamily.mono]
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        'prediction-sm': '0 2px 8px rgba(0,0,0,0.10)',
        'prediction': '0 4px 12px rgba(0,0,0,0.15)'
      },
      spacing: {
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
        '3xl': '4rem'
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px'
      }
    }
  },
  plugins: [
    function({ addBase }) {
      addBase({
        ':root': {
          '--header-height': '64px',
          '--sidebar-width': '220px',
          '--sidebar-collapsed': '80px',
          '--content-max-width': '1440px'
        }
      });
    }
  ]
};