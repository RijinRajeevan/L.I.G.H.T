import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeUp, staggerContainer } from './ui/motion';
import { AnimatedRadial } from './ui/AnimatedRadial';
import { ChevronDown, Code, Cpu } from 'lucide-react';

export const NeuralPanel: React.FC = () => {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <div className="w-full flex justify-end">
            <motion.div
                layout
                className={`glass-panel overflow-hidden border border-white/10 transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] ${isExpanded ? 'w-full lg:w-[400px]' : 'w-[200px]'}`}
            >
                {/* Header / Toggle */}
                <div
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors border-b border-white/5"
                >
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gov-saffron flex items-center justify-center -ml-1">
                            <Cpu size={16} className="text-gov-bg" />
                        </div>
                        <div className="flex flex-col">
                            <h3 className="text-white font-black tracking-widest italic text-xs uppercase">Neural Link</h3>
                            {isExpanded && <span className="text-[9px] text-gov-saffron/80 uppercase font-mono tracking-widest">AI Observability v2.4</span>}
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {isExpanded && (
                            <div className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                <span className="text-[9px] font-bold text-emerald-400 tracking-wider">OPTIMAL</span>
                            </div>
                        )}
                        <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} className="text-gray-500">
                            <ChevronDown size={16} />
                        </motion.div>
                    </div>
                </div>

                {/* Expanded Content */}
                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                            className="p-5 flex flex-col gap-6"
                        >
                            {/* System Health Bars */}
                            <motion.div variants={staggerContainer} initial="hidden" animate="show" className="space-y-4">
                                <ProgressBar title="System Engine" color="bg-blue-500" value={98} latency="0.04ms" delay={0.1} />
                                <ProgressBar title="Legal Heuristics" color="bg-gov-saffron" value={100} latency="1.22ms" delay={0.2} />
                                <ProgressBar title="Risk Assessment" color="bg-red-500" value={14} latency="0.15ms" delay={0.3} />
                                <ProgressBar title="Ethics Protocol" color="bg-purple-500" value={95} latency="0.68ms" delay={0.4} />
                            </motion.div>

                            {/* Center Confidence & Stats */}
                            <motion.div variants={fadeUp} initial="hidden" animate="show" className="flex items-center justify-center p-4">
                                <AnimatedRadial value={89.2} size={140} strokeWidth={8} color="stroke-gov-saffron" label="GLOBAL CONFIDENCE" />
                            </motion.div>

                            <div className="grid grid-cols-4 gap-2 text-center pb-4 border-b border-white/5">
                                <div>
                                    <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Accuracy</div>
                                    <div className="text-sm font-bold text-gray-200">99.98%</div>
                                </div>
                                <div>
                                    <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Drift</div>
                                    <div className="text-sm font-bold text-emerald-400">-0.02</div>
                                </div>
                                <div>
                                    <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Safety</div>
                                    <div className="text-sm font-bold text-purple-400">S-Tier</div>
                                </div>
                                <div>
                                    <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Bias</div>
                                    <div className="text-sm font-bold text-gov-saffron">Low</div>
                                </div>
                            </div>

                            {/* Developer Console (Streaming Logs) */}
                            <motion.div variants={fadeUp} initial="hidden" animate="show" className="bg-gov-bg/80 rounded-xl border border-white/5 p-4 overflow-hidden">
                                <div className="flex items-center justify-between mb-3 border-b border-white/10 pb-2">
                                    <div className="flex items-center gap-2 text-gray-400">
                                        <Code size={12} />
                                        <span className="text-[9px] font-bold uppercase tracking-widest">Developer Console</span>
                                    </div>
                                </div>
                                <div className="h-40 overflow-y-auto font-mono text-[9px] leading-relaxed space-y-1 relative">
                                    <p className="text-emerald-500">[INFO] Initializing neural architecture...</p>
                                    <p className="text-blue-400">[AUTH] Handshake verified. Shard 102 active.</p>
                                    <p className="text-gray-500">&gt;&gt;&gt; Load weights from s3://models/vision_core_v4</p>
                                    <p className="text-gov-saffron">[WARN] Entropy threshold approaching 0.45.</p>
                                    <p className="text-emerald-500">[INFO] Optimizing response parameters.</p>
                                    <p className="text-purple-400">[COMP] Regulation-G flag: Pass.</p>
                                    <p className="text-red-500 animate-pulse">[ALERT] High latency in Tokyo-01 node.</p>
                                    <p className="text-gray-500">&gt;&gt;&gt; Traceback (most recent call last): 0x00...</p>
                                    <p className="text-emerald-500">[INFO] Context window expanded (128k).</p>
                                    <p className="text-gov-saffron italic opacity-50 border-t border-white/5 mt-2 pt-2">_ STREAMING DATA...</p>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
};

const ProgressBar: React.FC<{ title: string, color: string, value: number, latency: string, delay: number }> = ({ title, color, value, latency, delay }) => (
    <motion.div
        variants={fadeUp}
        custom={delay}
        className="flex flex-col gap-1"
    >
        <div className="flex justify-between items-end">
            <span className={`text-[10px] font-black uppercase tracking-widest ${color.replace('bg-', 'text-')}`}>{title}</span>
            <span className="text-[9px] font-mono text-gray-500">{latency}</span>
        </div>
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 1.5, delay: delay + 0.5, ease: "easeOut" }}
                className={`h-full ${color} rounded-full relative`}
            >
                <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent" />
            </motion.div>
        </div>
    </motion.div>
);
