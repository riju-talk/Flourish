import type { Config } from "tailwindcss";

export default {
        darkMode: ["class"],
        content: [
                "./pages/**/*.{ts,tsx}",
                "./components/**/*.{ts,tsx}",
                "./app/**/*.{ts,tsx}",
                "./src/**/*.{ts,tsx}",
        ],
        prefix: "",
        theme: {
                container: {
                        center: true,
                        padding: '2rem',
                        screens: {
                                '2xl': '1400px'
                        }
                },
                extend: {
                        fontFamily: {
                                sans: ["Outfit", "sans-serif"],
                                serif: ["Fraunces", "serif"],
                        },
                        colors: {
                                // Flourish brand colors - warm cream + deep forest, editorial botanical look
                                flourish: {
                                        cream: '#F5F1E8',
                                        sage: '#A3B18A',
                                        green: '#4A7856',
                                        dark: '#1F3B2C',
                                        forest: '#16261E',
                                },
                                border: 'hsl(var(--border))',
                                input: 'hsl(var(--input))',
                                ring: 'hsl(var(--ring))',
                                background: 'hsl(var(--background))',
                                foreground: 'hsl(var(--foreground))',
                                primary: {
                                        DEFAULT: 'hsl(var(--primary))',
                                        foreground: 'hsl(var(--primary-foreground))'
                                },
                                secondary: {
                                        DEFAULT: 'hsl(var(--secondary))',
                                        foreground: 'hsl(var(--secondary-foreground))'
                                },
                                destructive: {
                                        DEFAULT: 'hsl(var(--destructive))',
                                        foreground: 'hsl(var(--destructive-foreground))'
                                },
                                muted: {
                                        DEFAULT: 'hsl(var(--muted))',
                                        foreground: 'hsl(var(--muted-foreground))'
                                },
                                accent: {
                                        DEFAULT: 'hsl(var(--accent))',
                                        foreground: 'hsl(var(--accent-foreground))'
                                },
                                popover: {
                                        DEFAULT: 'hsl(var(--popover))',
                                        foreground: 'hsl(var(--popover-foreground))'
                                },
                                card: {
                                        DEFAULT: 'hsl(var(--card))',
                                        foreground: 'hsl(var(--card-foreground))'
                                },
                                sidebar: {
                                        DEFAULT: 'hsl(var(--sidebar-background))',
                                        foreground: 'hsl(var(--sidebar-foreground))',
                                        primary: 'hsl(var(--sidebar-primary))',
                                        'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
                                        accent: 'hsl(var(--sidebar-accent))',
                                        'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
                                        border: 'hsl(var(--sidebar-border))',
                                        ring: 'hsl(var(--sidebar-ring))'
                                }
                        },
                        borderRadius: {
                                lg: 'var(--radius)',
                                md: 'calc(var(--radius) - 2px)',
                                sm: 'calc(var(--radius) - 4px)'
                        },
                        keyframes: {
                                'accordion-down': {
                                        from: {
                                                height: '0'
                                        },
                                        to: {
                                                height: 'var(--radix-accordion-content-height)'
                                        }
                                },
                                'accordion-up': {
                                        from: {
                                                height: 'var(--radix-accordion-content-height)'
                                        },
                                        to: {
                                                height: '0'
                                        }
                                },
                                'bounce-gentle': {
                                        '0%, 100%': { transform: 'translateY(0)' },
                                        '50%': { transform: 'translateY(-8px)' },
                                },
                                'pulse-soft': {
                                        '0%, 100%': { opacity: '1' },
                                        '50%': { opacity: '0.75' },
                                },
                                // Overrides Tailwind's built-in `bounce` (default: 1s, sharp
                                // cubic-bezier) with a slower, softer motion - used by branded
                                // loaders and the chat typing indicator via animate-bounce.
                                bounce: {
                                        '0%, 100%': {
                                                transform: 'translateY(-10%)',
                                                animationTimingFunction: 'cubic-bezier(0.45,0,0.55,1)'
                                        },
                                        '50%': {
                                                transform: 'translateY(0)',
                                                animationTimingFunction: 'cubic-bezier(0.45,0,0.55,1)'
                                        },
                                }
                        },
                        animation: {
                                'accordion-down': 'accordion-down 0.2s ease-out',
                                'accordion-up': 'accordion-up 0.2s ease-out',
                                'bounce-gentle': 'bounce-gentle 3s ease-in-out infinite',
                                'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
                                bounce: 'bounce 2.4s infinite',
                        }
                }
        },
        plugins: [require("tailwindcss-animate")],
} satisfies Config;
