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
        bgApp:      'var(--bg-app)',
        bgSidebar:  'var(--bg-sidebar)',
        bgPanel:    'var(--bg-panel)',
        bgCard:     'var(--bg-card)',
        bgHover:    'var(--bg-hover)',

        // Accents
        accent:     'var(--accent)',
        accentHover:'var(--accent-hover)',
        sage:       'var(--sage)',
        sageSoft:   'var(--sage-soft)',

        // Text
        txtPrimary: 'var(--txt-primary)',
        txtSecond:  'var(--txt-second)',
        txtMuted:   'var(--txt-muted)',
        txtDisabled:'var(--txt-disabled)',

        // Borders
        border:     'var(--border)',
        borderFocus:'var(--border-focus)',

        // Status
        success:    'var(--success)',
        warning:    'var(--warning)',
        error:      'var(--error)',
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
