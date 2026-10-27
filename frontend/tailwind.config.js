/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: "#FCFBF8",
          100: "#FDFBF7",
          DEFAULT: "#F8F3EA",   // Warm Cream Canvas
          200: "#EFE6D8",       // Soft Cream Surfaces
          300: "#E2D5C3",       // Borders
          400: "#D3C2AB",
          500: "#BAA58A",
        },
        espresso: {
          950: "#120B08",
          900: "#1C130E",       // Deepest Dark Espresso
          DEFAULT: "#2B1D17",   // Primary Structure Espresso
          800: "#2B1D17",
          700: "#3A2820",       // Dark Coffee
          600: "#4F372C",
          500: "#6F5142",       // Mocha
          400: "#91705D",
          300: "#B8794B",       // Caramel Accent
        },
        caramel: {
          DEFAULT: "#B8794B",
          hover: "#9E643A",
          light: "#F7ECE1",
        },
        copper: {
          DEFAULT: "#A9633E",
          hover: "#8C4E2D",
          light: "#F5E9E2",
        },
        charcoal: {
          DEFAULT: "#241A16",   // Deep Roast High-Contrast Text
          muted: "#6F625A",     // Secondary Descriptive Text
          subtle: "#8D8076",    // Metadata & Time
        },
        // High contrast semantic indicators
        soc: {
          danger: "#B94A48",
          dangerBg: "#FDF2F2",
          dangerBorder: "#F8D7DA",
          warning: "#B7791F",
          warningBg: "#FEF9E7",
          warningBorder: "#FCE8B2",
          info: "#2B6CB0",
          infoBg: "#EBF8FF",
          infoBorder: "#BEE3F8",
          success: "#2D7A4D",
          successBg: "#F0FDF4",
          successBorder: "#BBF7D0",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
      fontSize: {
        'xs': ['13px', '18px'],
        'sm': ['14.5px', '21px'],
        'base': ['16px', '24px'],
        'lg': ['18px', '26px'],
        'xl': ['20px', '28px'],
        '2xl': ['24px', '32px'],
        '3xl': ['30px', '38px'],
        '4xl': ['36px', '44px'],
      },
      boxShadow: {
        'card': '0 2px 8px -2px rgba(43, 29, 23, 0.08), 0 1px 4px -1px rgba(43, 29, 23, 0.04)',
        'elevated': '0 10px 25px -5px rgba(43, 29, 23, 0.12), 0 8px 10px -6px rgba(43, 29, 23, 0.08)',
        'espresso': '0 4px 14px 0 rgba(28, 19, 14, 0.25)',
      }
    },
  },
  plugins: [],
}
