import React, { useEffect, useState } from 'react';
import { Scale, Sparkles } from 'lucide-react';

interface WelcomeAnimationProps {
    onComplete: () => void;
}

export const WelcomeAnimation: React.FC<WelcomeAnimationProps> = ({ onComplete }) => {
    const [stage, setStage] = useState(0);

    useEffect(() => {
        const sequence = [
            setTimeout(() => setStage(1), 500),   // Ignition
            setTimeout(() => setStage(2), 1500),  // Chakra Formation
            setTimeout(() => setStage(3), 2500),  // Tricolor Flow
            setTimeout(() => setStage(4), 3500),  // Text Reveal
            setTimeout(() => setStage(5), 5500),  // Exit
            setTimeout(onComplete, 6000)          // Unmount
        ];
        return () => sequence.forEach(clearTimeout);
    }, [onComplete]);

    if (stage === 6) return null;

    return (
        <div className={`fixed inset-0 z-[100] flex items-center justify-center bg-[#020617] transition-opacity duration-700 ${stage === 5 ? 'opacity-0' : 'opacity-100'}`}>

            {/* Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gov-blue/20 rounded-full blur-[100px] transition-all duration-1000 ${stage >= 1 ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}`} />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
            </div>

            <div className="relative z-10 flex flex-col items-center">

                {/* Central Motif: Ashoka Chakra inspired */}
                <div className={`relative w-32 h-32 mb-12 transition-all duration-1000 ${stage >= 2 ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`}>
                    {/* Glowing Ring */}
                    <div className="absolute inset-0 rounded-full border-2 border-gov-blue/30 animate-spin-slow shadow-[0_0_30px_rgba(15,23,42,0.6)]" />

                    {/* Spokes (Abstract Chakra) */}
                    {[...Array(24)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute top-1/2 left-1/2 w-full h-[1px] bg-gradient-to-r from-transparent via-gov-saffron/50 to-transparent -translate-x-1/2 -translate-y-1/2"
                            style={{ transform: `translate(-50%, -50%) rotate(${i * 15}deg)` }}
                        />
                    ))}

                    {/* Shield Core */}
                    <div className="absolute inset-0 flex items-center justify-center backdrop-blur-sm bg-black/30 rounded-full border border-white/10">
                        <Scale className="text-white w-12 h-12 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
                    </div>
                </div>

                {/* Digital Tricolor Streams */}
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-screen h-64 pointer-events-none transition-opacity duration-1000 ${stage >= 3 ? 'opacity-100' : 'opacity-0'}`}>
                    <div className="absolute top-[40%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#FF9933] to-transparent animate-flow blur-sm" />
                    <div className="absolute top-[50%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white to-transparent animate-flow blur-md delay-100" />
                    <div className="absolute top-[60%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#138808] to-transparent animate-flow blur-sm delay-200" />
                </div>

                {/* Text Reveal */}
                <div className={`text-center space-y-4 transition-all duration-1000 ${stage >= 4 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
                    <h1 className="text-7xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-400 drop-shadow-2xl">
                        NYAYA-SETU
                    </h1>

                    <div className="flex items-center justify-center gap-3">
                        <div className="h-[1px] w-12 bg-gov-saffron/50" />
                        <span className="text-lg md:text-xl font-light tracking-[0.5em] text-gov-saffron/90 uppercase">
                            Justice Reimagined
                        </span>
                        <div className="h-[1px] w-12 bg-gov-green/50" />
                    </div>

                    <div className="mt-8 flex items-center justify-center gap-2 text-xs text-gray-500 font-mono border border-white/5 bg-white/5 py-1 px-3 rounded-full mx-auto w-fit">
                        <Sparkles size={12} className="text-yellow-400" />
                        <span>AI-POWERED JUDICIARY SYSTEM v2.0</span>
                    </div>
                </div>
            </div>

            {/* Bottom Branding */}
            <div className={`absolute bottom-10 left-0 w-full text-center transition-opacity duration-1000 ${stage >= 4 ? 'opacity-100' : 'opacity-0'}`}>
                <p className="text-[10px] tracking-widest text-gray-600 uppercase font-bold">
                    Department of Justice • Government of India
                </p>
            </div>
        </div>
    );
};
