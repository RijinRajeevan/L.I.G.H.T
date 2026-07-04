import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedRadialProps {
    value: number; // 0 to 100
    size?: number;
    strokeWidth?: number;
    color?: string;
    label?: string;
}

export const AnimatedRadial: React.FC<AnimatedRadialProps> = ({
    value,
    size = 120,
    strokeWidth = 8,
    color = "stroke-gov-saffron",
    label = "CONFIDENCE"
}) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    return (
        <div className="relative flex flex-col items-center justify-center p-4">
            <svg
                width={size}
                height={size}
                className="transform -rotate-90 drop-shadow-[0_0_15px_rgba(212,175,55,0.4)]"
            >
                {/* Background Track */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    className="stroke-gray-800 fill-none"
                    strokeWidth={strokeWidth}
                />

                {/* Animated Progress */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    className={`${color} fill-none`}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{
                        duration: 2,
                        ease: [0.4, 0, 0.2, 1], // cinematic ease
                    }}
                />
            </svg>

            {/* Center Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center pt-2">
                <span className="text-[10px] uppercase font-black tracking-widest text-gray-500 mb-0.5">{label}</span>
                <motion.span
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1, duration: 0.5 }}
                    className={`text-2xl font-bold border-b border-transparent`}
                >
                    {value}<span className="text-sm font-light text-gray-400">%</span>
                </motion.span>
            </div>
        </div>
    );
};
