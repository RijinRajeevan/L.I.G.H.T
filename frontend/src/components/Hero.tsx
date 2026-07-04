import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Shield } from 'lucide-react';

interface HeroProps {
    onStart: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onStart }) => {
    return (
        <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            className="w-full h-screen bg-gov-navy flex flex-col items-center justify-center p-4"
        >
            <div className="flex flex-col items-center justify-center text-center max-w-2xl">

                {/* Minimal Shield Icon */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6 }}
                    className="mb-8 p-4 bg-gov-navy-light rounded-2xl border border-white/10 shadow-lg"
                >
                    <Shield size={64} className="text-gov-gold" strokeWidth={1.5} />
                </motion.div>

                {/* Typography */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="mb-2"
                >
                    <h1 className="text-gov-text text-5xl md:text-6xl font-bold tracking-wider mb-2">
                        L.I.G.H.T. <span className="text-gov-gold">NYAYA VAANI</span>
                    </h1>
                    <p className="text-gov-text-muted text-sm md:text-base tracking-[0.2em] uppercase font-medium">
                        Legal Information & Guidance Help Terminal
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="mt-8 relative"
                >
                    <button
                        onClick={onStart}
                        className="flex items-center gap-3 px-8 py-4 rounded-lg bg-gov-gold text-gov-navy hover:bg-yellow-500 transition-colors duration-200 shadow-md font-bold tracking-wider uppercase text-sm"
                    >
                        Enter System
                        <ArrowRight size={18} strokeWidth={2} />
                    </button>
                </motion.div>

            </div>

            {/* Footer Text */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="absolute bottom-8 text-center"
            >
                <div className="text-[10px] tracking-widest text-gov-text-muted uppercase flex items-center gap-3 font-mono">
                    <span>Protocol V3.0.42</span>
                    <span className="opacity-50">|</span>
                    <span>Secure Connection Established</span>
                </div>
            </motion.div>
        </motion.section>
    );
};
