const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/views/**/*.py',
    './app/api/**/*.py',
    './app/static/js/**/*.js',
    './assets/css/**/*.css'
  ],
  darkMode: 'class',
  // 确保自定义组件类不被purge移除
  safelist: [
    // 表单组件
    { pattern: /^form-(input|textarea|select|checkbox|radio|switch|file|label|group|error|help|success)/ },
    // 按钮组件
    { pattern: /^btn(-primary|-secondary|-success|-danger|-warning|-info|-outline|-ghost)?/ },
    { pattern: /^btn--(sm|lg|xl|loading)/ },
    // 卡片组件
    { pattern: /^card(__|--)?/ },
    // 导航组件
    { pattern: /^nav(-item|-subitem|-submenu)?/ },
    { pattern: /^nav--(vertical|pills)/ },
    { pattern: /^nav-item--(active|disabled)/ },
    { pattern: /^sidebar(__|--)?/ },
    { pattern: /^breadcrumb(__|__)?/ },
    { pattern: /^tab(s|--active)?/ },
    // 模态框组件
    { pattern: /^modal(-backdrop|-dialog|-content)?/ },
    { pattern: /^modal__(header|title|close|body|footer)/ },
    { pattern: /^modal-dialog--(sm|md|lg|xl|2xl|fullscreen)/ },
    // 通知组件
    { pattern: /^alert(-success|-error|-warning|-info|-dismissible|-fixed)?/ },
    { pattern: /^alert__(icon|content|title|message|close)/ },
    { pattern: /^toast(__|--)?/ },
    { pattern: /^notification-(list|item)/ },
    { pattern: /^notification-item__(header|title|time|message|actions)/ },
    { pattern: /^badge(-primary|-secondary|-success|-danger|-warning|-info)?(--sm|--lg)?/ }
  ],
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
          light: '#dbeafe',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        },
        secondary: '#10b981',
        accent: '#f59e0b',
        danger: '#ef4444',
        warning: '#f97316',
        gold: '#ffd700',
        success: '#22c55e',
        muted: '#64748b',
        up: '#22c55e',
        down: '#dc3545',
        gray: {
          750: '#374151'
        }
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