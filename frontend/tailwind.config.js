/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                heading: ['Audiowide', 'sans-serif'],
                body: ['"Chakra Petch"', 'sans-serif'],
            },
            colors: {
                'night-sky': '#000000',
                'cyber-blue': '#E60012',      // Bright blood red (primary accent)
                'cyber-pink': '#C0C0C0',      // Silver/chrome
                'light-text': '#E8E8E8',      // Bright silver text
                'dark-accent': '#1a1a1a',     // Dark charcoal
                'chrome': '#D4D4D4',          // Chrome highlight
                'blood-red': '#E60012',       // Bright blood red
                'blood-red-dark': '#B8000F',  // Darker blood red for hover
            },
            boxShadow: {
                'cyber-glow': '0 0 15px 3px rgba(230, 0, 18, 0.5)',
                'pink-glow': '0 0 15px 3px rgba(192, 192, 192, 0.3)',
                'chrome-glow': '0 0 20px 5px rgba(212, 212, 212, 0.2)',
            },
            backgroundImage: {
                'grainy-pattern': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4' viewBox='0 0 4 4'%3E%3Cpath fill='%23222222' fill-opacity='0.4' d='M1 3h1v1H1V3zm2-2h1v1H3V1z'%3E%3C/path%3E%3C/svg%3E\")",
            }
        },
    },
    plugins: [],
}
