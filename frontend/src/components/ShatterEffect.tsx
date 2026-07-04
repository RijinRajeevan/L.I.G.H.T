import React, { useEffect, useState } from 'react';

interface ShatterEffectProps {
    trigger: boolean;
    onComplete?: () => void;
}

export const ShatterEffect: React.FC<ShatterEffectProps> = ({ trigger, onComplete }) => {
    const [active, setActive] = useState(false);

    useEffect(() => {
        if (trigger) {
            setActive(true);
            const timer = setTimeout(() => {
                setActive(false);
                if (onComplete) onComplete();
            }, 1000); // 1s animation
            return () => clearTimeout(timer);
        }
    }, [trigger, onComplete]);

    if (!active) return null;

    return (
        <div className="fixed inset-0 z-[100] pointer-events-none flex items-center justify-center bg-black/80">
            <div className="text-9xl font-black text-red-600 animate-ping opacity-75 absolute">
                REFUSED
            </div>
            <div className="absolute inset-0 bg-red-500/20 mix-blend-overlay animate-pulse" />
            {/* Fragments can be added here for more complex visual */}
        </div>
    );
};
