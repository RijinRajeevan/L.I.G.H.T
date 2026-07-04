import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { fadeUp, drawPath, staggerContainer } from './ui/motion';
import { AnimatedRadial } from './ui/AnimatedRadial';

export const IntelligenceConsole: React.FC = () => {
    const [confidence, setConfidence] = useState(0);

    useEffect(() => {
        const timer = setTimeout(() => setConfidence(82), 500);
        return () => clearTimeout(timer);
    }, []);

    return (
        <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="show"
            className="w-full grid grid-cols-1 lg:grid-cols-3 gap-6 text-white"
        >
            {/* Main Console Area */}
            <motion.div variants={fadeUp} className="lg:col-span-2 glass-panel p-8 relative overflow-hidden group">
                {/* Optional dark aesthetic overlay inspired by the image, keep it extremely subtle */}
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gov-saffron/50 to-transparent" />

                <div className="flex justify-between items-start mb-12 relative z-10">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight mb-2 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                            Justice Intelligence Console
                        </h2>
                        <p className="text-sm text-gray-400 font-mono">Ref: NYA-7729-2024 | Active Case: Industrial Arbitration Case #402</p>
                    </div>
                    <div className="flex gap-3">
                        <button className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-gray-300 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 hover:text-white transition-colors">
                            Save Snapshot
                        </button>
                        <button className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-gov-saffron bg-gov-saffron/10 border border-gov-saffron/30 rounded-lg hover:bg-gov-saffron hover:text-gov-bg transition-colors shadow-[0_0_15px_rgba(212,175,55,0.2)]">
                            Generate Report
                        </button>
                    </div>
                </div>

                {/* Radar Chart (Custom SVG for pristine animation as requested) */}
                <div className="flex justify-center items-center py-12 relative z-10">
                    <div className="relative w-80 h-80 flex items-center justify-center">
                        {/* Radar Background Grids */}
                        <svg viewBox="0 0 200 200" className="absolute inset-0 w-full h-full opacity-20">
                            {[0.4, 0.7, 1].map((scale, i) => (
                                <polygon
                                    key={i}
                                    points="100,20 176,75 147,165 53,165 24,75"
                                    fill="none"
                                    stroke="#D4AF37"
                                    strokeWidth="1"
                                    className="transform origin-center"
                                    style={{ transform: `scale(${scale})` }}
                                />
                            ))}
                            {/* Axis Lines */}
                            <line x1="100" y1="100" x2="100" y2="20" stroke="#555" strokeWidth="1" />
                            <line x1="100" y1="100" x2="176" y2="75" stroke="#555" strokeWidth="1" />
                            <line x1="100" y1="100" x2="147" y2="165" stroke="#555" strokeWidth="1" />
                            <line x1="100" y1="100" x2="53" y2="165" stroke="#555" strokeWidth="1" />
                            <line x1="100" y1="100" x2="24" y2="75" stroke="#555" strokeWidth="1" />
                        </svg>

                        {/* Animated Radar Data Polygon */}
                        <svg viewBox="0 0 200 200" className="absolute inset-0 w-full h-full drop-shadow-[0_0_15px_rgba(212,175,55,0.6)]">
                            <motion.polygon
                                points="100,40 160,85 130,150 60,140 40,80"
                                fill="rgba(212,175,55,0.15)"
                                stroke="#D4AF37"
                                strokeWidth="2"
                                variants={drawPath}
                            />
                        </svg>

                        {/* Labels */}
                        <span className="absolute top-0 text-[10px] font-bold text-gray-400 tracking-widest uppercase">Legal Depth</span>
                        <span className="absolute right-0 text-[10px] font-bold text-gray-400 tracking-widest uppercase origin-left translate-x-4">Evidence</span>
                        <span className="absolute bottom-0 text-[10px] font-bold text-gray-400 tracking-widest uppercase translate-y-4">Precedent</span>
                        <span className="absolute left-0 text-[10px] font-bold text-gray-400 tracking-widest uppercase origin-right -translate-x-4">Logic</span>
                    </div>
                </div>

                {/* Legal Output Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                    <motion.div variants={fadeUp} className="p-5 rounded-xl border border-white/10 bg-white/5 hover:-translate-y-2 hover:bg-white/10 transition-all duration-300 hover:shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
                        <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Top Citation</h4>
                        <p className="font-medium text-sm text-gray-200 leading-snug">Kesavananda Bharati v. State of Kerala (1973)</p>
                    </motion.div>

                    <motion.div variants={fadeUp} className="p-5 rounded-xl border border-red-500/30 bg-red-500/5 hover:-translate-y-2 hover:bg-red-500/10 transition-all duration-300 hover:shadow-[0_10px_30px_rgba(239,68,68,0.2)]">
                        <h4 className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-2">Key Risk</h4>
                        <p className="font-medium text-sm text-red-100 leading-snug">Potential jurisdictional conflict identified in Para 4.</p>
                    </motion.div>

                    <motion.div variants={fadeUp} className="p-5 rounded-xl border border-purple-500/30 bg-purple-500/5 hover:-translate-y-2 hover:bg-purple-500/10 transition-all duration-300 hover:shadow-[0_10px_30px_rgba(168,85,247,0.2)]">
                        <h4 className="text-[10px] font-black text-purple-400 uppercase tracking-widest mb-2">Ethical Check</h4>
                        <p className="font-medium text-sm text-purple-100 leading-snug">100% Bias-mitigation verified for current draft.</p>
                    </motion.div>
                </div>
            </motion.div>

            {/* Sidebar Analytics */}
            <motion.div variants={fadeUp} className="flex flex-col gap-6">

                {/* AI Observability Top Panel */}
                <div className="glass-panel p-6">
                    <h3 className="text-[10px] font-black tracking-[0.2em] text-gov-saffron uppercase flex items-center gap-2 mb-6">
                        <div className="w-1.5 h-1.5 rounded-full bg-gov-saffron animate-pulse" />
                        Neural Link AI Observability
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col items-center justify-center p-4 bg-white/5 rounded-xl border border-white/5">
                            <AnimatedRadial value={confidence} size={100} strokeWidth={6} color="stroke-emerald-400" />
                        </div>
                        <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex flex-col justify-center gap-3">
                            <h4 className="text-[9px] font-black text-gray-500 uppercase tracking-widest">Processing Latency</h4>
                            <div className="space-y-2">
                                <div className="h-1 bg-blue-500 rounded-full w-[80%]" />
                                <div className="h-1 bg-gov-saffron rounded-full w-[95%]" />
                                <div className="h-1 bg-purple-500 rounded-full w-[60%]" />
                            </div>
                            <span className="text-2xl font-bold mt-2 tracking-tighter">42<span className="text-sm font-light text-gray-500">ms</span></span>
                        </div>
                    </div>
                </div>

                {/* Cognitive Timeline */}
                <div className="glass-panel p-6 flex-1 flex flex-col relative overflow-hidden">
                    <h3 className="text-[10px] font-black tracking-[0.2em] text-gray-400 uppercase mb-6">Cognitive Timeline</h3>

                    <div className="relative pl-6 space-y-6 flex-1">
                        {/* Animated Vertical Line */}
                        <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: "100%" }}
                            transition={{ duration: 2, ease: "easeOut" }}
                            className="absolute left-[11px] top-2 w-[1px] bg-gradient-to-b from-blue-500 via-gov-saffron to-purple-500"
                        />

                        <TimelineNode color="bg-blue-500" title="System Reasoning" desc="Parsing complex industrial labor regulations..." delay={0.2} />
                        <TimelineNode color="bg-gov-saffron" title="Legal Analysis" desc="Correlating evidence with ID Act 1947 Section 10..." delay={0.4} />
                        <TimelineNode color="bg-red-500" title="Risk Evaluation" desc="Scanning for contradictory case law..." delay={0.6} pulse={true} />
                        <TimelineNode color="bg-purple-500" title="Ethical Compliance" desc="Pending final fairness validation..." delay={0.8} />
                    </div>

                    {/* Auto-scroll Logs (Simulated) */}
                    <div className="mt-6 p-4 bg-black/40 rounded-xl border border-white/5 font-mono text-[10px] text-emerald-400 leading-relaxed h-32 overflow-hidden relative">
                        <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-black/60 to-transparent pointer-events-none" />
                        <motion.div
                            initial={{ y: 20 }}
                            animate={{ y: -80 }}
                            transition={{ duration: 15, ease: "linear", repeat: Infinity }}
                            className="space-y-2"
                        >
                            <p># [09:12:44] RECV: User Input Stream Parsed</p>
                            <p className="text-gray-500">_&gt; [09:12:45] EXEC: Semantic_Search_DB_Law</p>
                            <p># [09:12:45] LOG: Hit found in ID_ACT_47_SEC_10</p>
                            <p className="text-gov-saffron"># [09:12:46] CALC: Confidence_Rating_Init(0.78)</p>
                            <p className="text-red-400"># [09:12:46] VAR: Risk_Flag_Set = High</p>
                            <p># [09:12:47] SYNC: <span className="text-gov-saffron">Justice_Nodes_Active</span></p>
                            <p># [09:12:48] PUSH: Stream To Visual Radar</p>
                            <p># [09:12:44] RECV: User Input Stream Parsed</p>
                            <p className="text-gray-500">_&gt; [09:12:45] EXEC: Semantic_Search_DB_Law</p>
                            <p># [09:12:45] LOG: Hit found in ID_ACT_47_SEC_10</p>
                        </motion.div>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
};

const TimelineNode: React.FC<{ color: string, title: string, desc: string, delay: number, pulse?: boolean }> = ({ color, title, desc, delay, pulse }) => (
    <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay, duration: 0.5, ease: "easeOut" }}
        className="relative"
    >
        <div className={`absolute -left-6 top-1.5 w-2.5 h-2.5 rounded-full ${color} ${pulse ? 'animate-pulse ring-4 ring-red-500/20' : ''}`} />
        <h4 className={`text-xs font-bold ${color.replace('bg-', 'text-')} mb-1`}>{title}</h4>
        <p className="text-xs text-gray-400 leading-relaxed">{desc}</p>
    </motion.div>
);
