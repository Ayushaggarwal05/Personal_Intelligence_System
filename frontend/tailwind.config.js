/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds — elevation hierarchy
        bgApp:      '#131816',
        bgSidebar:  '#1A211E',
        bgPanel:    '#202824',
        bgCard:     '#262F2A',
        bgHover:    '#313B35',

        // Accents
        accent:     '#4D7C73',
        accentHover:'#5D8F85',
        sage:       '#98B6A7',
        sageSoft:   '#B8CEC4',

        // Text
        txtPrimary: '#F4F6F5',
        txtSecond:  '#CAD2CE',
        txtMuted:   '#9CA8A3',
        txtDisabled:'#67736D',

        // Borders
        border:     '#303935',
        borderFocus:'#5E8C82',

        // Status
        success:    '#7FAE8C',
        warning:    '#D2B96B',
        error:      '#C96F6F',
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        heading: ['Manrope', 'Inter', 'sans-serif'],
        mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        card: '16px',
        btn:  '10px',
        input:'10px',
        chip: '6px',
      },
      transitionDuration: {
        smooth: '220ms',
      },
      boxShadow: {
        card:   '0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)',
        panel:  '0 4px 16px rgba(0,0,0,0.25)',
        btn:    '0 2px 8px rgba(77,124,115,0.25)',
        btnHover:'0 4px 16px rgba(77,124,115,0.35)',
        glow:   '0 0 20px rgba(77,124,115,0.12)',
      },
    },
  },
  plugins: [],
}
