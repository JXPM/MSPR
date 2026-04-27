/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '1.5rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      fontFamily: {
        display: ['"Instrument Serif"', 'Georgia', 'serif'],
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        // ObRail palette — éditorial, ferroviaire, durable
        forest: {
          50:  '#f3f6f3',
          100: '#e3ebe4',
          200: '#c7d7c9',
          300: '#9cb89f',
          400: '#6f9474',
          500: '#4d7653',
          600: '#3a5e40',
          700: '#2d4a33',
          800: '#253c2b',
          900: '#1a3d2e',
          950: '#0f2419',
        },
        cream: {
          50:  '#fbfaf7',
          100: '#f5f1ea',
          200: '#ebe3d5',
          300: '#dcceb6',
          400: '#c9b291',
        },
        rust: {
          400: '#d97055',
          500: '#c14d3c',
          600: '#a73d2f',
        },
        midnight: {
          500: '#2c3e6b',
          700: '#1e2a4a',
          900: '#131b33',
        },
        // Sémantique
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'train-slide': {
          '0%':   { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.6s ease-out forwards',
        'train-slide': 'train-slide 20s linear infinite',
      },
    },
  },
  plugins: [],
}
