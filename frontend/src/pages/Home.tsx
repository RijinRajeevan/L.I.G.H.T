import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../state/SessionContext';
import { Hero } from '../components/Hero';
import { Gavel, FileText, Fingerprint, Receipt, Globe } from 'lucide-react';
import { motion } from 'framer-motion';

export const Home: React.FC = () => {
    const navigate = useNavigate();
    const { startSession } = useSession();
    const [updates, setUpdates] = useState<any[]>([]);

    useEffect(() => {
        fetch('/api/latest-updates')
            .then(res => res.json())
            .then(data => setUpdates(data.updates || []))
            .catch(() => { });
    }, []);

    const handleStart = () => {
        startSession();
        navigate('/session');
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col gap-8 md:gap-12"
        >
            <Hero onStart={handleStart} />

            {/* Services Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <ServiceCard
                    icon={<FileText size={32} />}
                    title="Certificates"
                    desc="Income, Caste, Residence & more."
                    color="text-gov-saffron"
                />
                <ServiceCard
                    icon={<Gavel size={32} />}
                    title="Legal / FIR"
                    desc="Criminal analysis & police complaints."
                    color="text-cyan-400"
                />
                <ServiceCard
                    icon={<Fingerprint size={32} />}
                    title="Aadhaar / ID"
                    desc="Updates & linking procedures."
                    color="text-emerald-400"
                />
                <ServiceCard
                    icon={<Globe size={32} />}
                    title="Passport / PAN"
                    desc="Application guide & form generation."
                    color="text-purple-400"
                />
            </div>

            {/* Procedure Updates from n8n */}
            <section className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
                <div className="flex items-center gap-3 mb-8">
                    <Receipt size={24} className="text-gov-saffron" />
                    <h3 className="text-2xl font-bold text-white tracking-tight">Live Procedure Updates</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {updates.length > 0 ? updates.map((u, i) => (
                        <div key={i} className="p-6 bg-white/5 rounded-2xl border border-white/5 hover:border-gov-saffron/30 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                                <h4 className="text-lg font-bold text-gray-200">{u.title}</h4>
                                <span className="text-xs font-black text-gov-saffron uppercase">{u.date}</span>
                            </div>
                            <p className="text-sm text-gray-400 leading-relaxed">{u.content}</p>
                        </div>
                    )) : (
                        <div className="col-span-2 text-center text-gray-500 py-10 italic">
                            No recent procedural changes detected by n8n workflow.
                        </div>
                    )}
                </div>
            </section>

            {/* Stats */}
            <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatItem label="Active Agents" value="6" color="text-blue-400" />
                <StatItem label="Accuracy" value="99.1%" color="text-green-400" />
                <StatItem label="Latency" value="<120ms" color="text-yellow-400" />
                <StatItem label="Bilingual" value="ML/EN" color="text-red-400" />
            </section>
        </motion.div>
    );
};

// Start Helper Components (inline for now)
const ServiceCard: React.FC<{ icon: React.ReactNode, title: string, desc: string, color: string }> = ({ icon, title, desc, color }) => (
    <div className="glass-panel p-8 hover:bg-white/10 transition-all duration-300 cursor-pointer group hover:-translate-y-1">
        <div className={`mb-4 p-3 rounded-xl bg-white/5 w-fit border border-white/5 ${color} group-hover:scale-110 transition-transform`}>
            {icon}
        </div>
        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed group-hover:text-gray-200 transition-colors">{desc}</p>
    </div>
);

const StatItem: React.FC<{ label: string, value: string, color: string }> = ({ label, value, color }) => (
    <div className="glass-panel p-6 flex flex-col items-center justify-center gap-1 hover:bg-white/5 transition-colors">
        <span className={`text-3xl md:text-4xl font-black ${color} tracking-tighter`}>{value}</span>
        <span className="text-[10px] uppercase tracking-widest text-gray-500 font-bold">{label}</span>
    </div>
);

// Helper Components

