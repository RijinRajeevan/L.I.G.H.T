import React from 'react';
import { Outlet } from 'react-router-dom';
import { NeuralLink } from './components/NeuralLink';
import { useSession } from './state/SessionContext';
import { GovFooter } from './components/GovFooter';

export const Layout: React.FC = () => {
    const { logs, isActive } = useSession();

    return (
        <div className="flex flex-col h-screen bg-gov-bg text-gov-text font-sans overflow-hidden selection:bg-gov-saffron/30 selection:text-gov-saffron">

            <div className="flex flex-col lg:flex-row flex-1 relative overflow-hidden">
                {/* Main Content Area */}
                <main className="flex-1 flex flex-col relative z-10 overflow-y-auto custom-scrollbar order-1 lg:order-1">
                    <div className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-6 lg:p-10">
                        <Outlet />
                    </div>
                    <GovFooter />
                </main>

                {/* Neural Link Sidebar (Right) - Fixed Desktop / Hidden Mobile */}
                {isActive && (
                    <aside className="hidden lg:block w-[400px] border-l border-white/5 bg-black/40 backdrop-blur-2xl z-50 shadow-2xl relative order-2">
                        <div className="absolute inset-0 bg-gradient-to-b from-gov-blue/50 to-transparent pointer-events-none" />
                        <NeuralLink logs={logs} />
                    </aside>
                )}
            </div>
        </div>
    );
};
