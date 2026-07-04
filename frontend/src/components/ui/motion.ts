import type { Variants } from 'framer-motion';

export const springConfig = {
    type: "spring",
    stiffness: 100,
    damping: 20
};

export const cinematicEase: [number, number, number, number] = [0.4, 0, 0.2, 1];

export const staggerContainer: Variants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
            delayChildren: 0.1,
            ease: cinematicEase,
        }
    }
};

export const fadeUp: Variants = {
    hidden: { opacity: 0, y: 30 },
    show: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.8,
            ease: cinematicEase
        }
    },
    exit: {
        opacity: 0,
        y: -10,
        transition: {
            duration: 0.4,
            ease: cinematicEase
        }
    }
};

export const fadeDown: Variants = {
    hidden: { opacity: 0, y: -30 },
    show: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.8,
            ease: cinematicEase
        }
    }
};

export const scaleIn: Variants = {
    hidden: { opacity: 0, scale: 0.95 },
    show: {
        opacity: 1,
        scale: 1,
        transition: {
            duration: 1.2,
            ease: cinematicEase
        }
    }
};

export const drawPath: Variants = {
    hidden: { pathLength: 0, opacity: 0 },
    show: {
        pathLength: 1,
        opacity: 1,
        transition: {
            pathLength: { duration: 1.5, ease: "easeInOut" },
            opacity: { duration: 0.1 }
        }
    }
};

// Reusable sweeping light effect over dark mode cards
export const sweepLight: Variants = {
    hidden: { x: "-100%" },
    show: {
        x: "200%",
        transition: {
            repeat: Infinity,
            repeatType: "loop" as const,
            duration: 6,
            ease: "linear",
            repeatDelay: 2
        }
    }
};
