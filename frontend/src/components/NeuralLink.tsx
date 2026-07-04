import React, { useEffect, useRef } from 'react';

interface Log {
    timestamp: string;
    agent: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
}

interface NeuralLinkProps {
    logs: Log[];
}

// Agent color map using only CIVIA palette colors
const AGENT_COLORS: Record<string, { border: string; dot: string; label: string }> = {
    System: { border: 'border-blue-500/50', dot: 'bg-blue-500', label: 'text-blue-400' },
    Legal: { border: 'border-gov-gold/50', dot: 'bg-gov-gold', label: 'text-gov-gold' },
    Risk: { border: 'border-red-500/50', dot: 'bg-red-500', label: 'text-red-400' },
    Ethics: { border: 'border-purple-500/50', dot: 'bg-purple-500', label: 'text-purple-400' },
    Confidence: { border: 'border-cyan-400/50', dot: 'bg-cyan-400', label: 'text-cyan-400' },
};

const getAgentColors = (agent: string) =>
    AGENT_COLORS[agent] ?? { border: 'border-white/20', dot: 'bg-gov-text-muted', label: 'text-gov-text-muted' };

// Renders a single log message — parses JSON into rich UI, falls back to plain text
const LogContent: React.FC<{ agent: string; msg: string }> = ({ agent, msg }) => {
    try {
        const jsonMatch = msg.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const parsed = JSON.parse(jsonMatch[0]);

            if (agent === 'Legal') {
                return (
                    <div className="space-y-2 text-xs">
                        {parsed.sections && Array.isArray(parsed.sections) && (
                            <div>
                                <div className="text-gov-gold font-semibold mb-1">📋 Applicable Sections:</div>
                                <div className="pl-2 space-y-0.5">
                                    {parsed.sections.slice(0, 3).map((sec: string, i: number) => (
                                        <div key={i} className="text-gov-text-muted">§ {sec}</div>
                                    ))}
                                </div>
                            </div>
                        )}
                        {parsed.reasoning && (
                            <div>
                                <div className="text-blue-400 font-semibold mb-0.5">💡 Reasoning:</div>
                                <div className="pl-2 text-gov-text-muted">{parsed.reasoning}</div>
                            </div>
                        )}
                    </div>
                );
            }

            if (agent === 'Risk') {
                return (
                    <div className="space-y-1.5 text-xs">
                        {parsed.severity && (
                            <div className="flex items-center gap-2">
                                <span className="text-red-400 font-semibold">⚠️ Severity:</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${parsed.severity.toLowerCase().includes('high') ? 'bg-red-500/20 text-red-300'
                                        : parsed.severity.toLowerCase().includes('med') ? 'bg-yellow-500/20 text-yellow-300'
                                            : 'bg-green-500/20 text-green-300'
                                    }`}>{parsed.severity}</span>
                            </div>
                        )}
                        {parsed.concerns && (
                            <div className="pl-1 text-gov-text-muted">
                                {(Array.isArray(parsed.concerns) ? parsed.concerns : [parsed.concerns]).map((c: string, i: number) => (
                                    <div key={i}>• {c}</div>
                                ))}
                            </div>
                        )}
                    </div>
                );
            }

            if (agent === 'Ethics') {
                return (
                    <div className="flex items-center gap-2 text-xs">
                        <span className="text-purple-400 font-semibold">🛡️ Veto:</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${parsed.veto ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'
                            }`}>{parsed.veto ? 'BLOCKED' : 'APPROVED'}</span>
                        {parsed.reason && <span className="text-gov-text-muted">{parsed.reason}</span>}
                    </div>
                );
            }

            if (agent === 'Confidence') {
                const score = Number(parsed.score ?? 0);
                return (
                    <div className="space-y-1.5 text-xs">
                        <div className="flex items-center gap-2">
                            <span className="text-cyan-400 font-semibold">📊 Score:</span>
                            <div className="flex-1 bg-white/10 rounded-full h-1.5 overflow-hidden">
                                <div
                                    className={`h-full transition-all ${score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                    style={{ width: `${Math.min(score, 100)}%` }}
                                />
                            </div>
                            <span className="text-gov-text font-bold">{score}%</span>
                        </div>
                        {parsed.reasoning && <div className="text-gov-text-muted pl-1">{parsed.reasoning}</div>}
                    </div>
                );
            }

            // Fallback JSON display (other agents)
            return (
                <div className="text-[10px] font-mono text-gov-text-muted bg-black/20 rounded p-2 leading-snug break-all">
                    {JSON.stringify(parsed)}
                </div>
            );
        }
    } catch { /* Not JSON — render as plain text */ }

    return <span className="break-words text-gov-text-muted text-xs">{msg}</span>;
};

export const NeuralLink: React.FC<NeuralLinkProps> = ({ logs }) => {
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="h-full flex flex-col text-gov-text overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-white/5 flex items-center gap-3 shrink-0">
                <div className="w-6 h-6 rounded bg-gov-gold/10 border border-gov-gold/30 flex items-center justify-center text-[11px]">
                    &gt;_
                </div>
                <div>
                    <div className="text-[9px] font-bold uppercase tracking-widest text-gov-gold">Neural Link</div>
                    <div className="text-[9px] text-gov-text-muted">Live Agent Analysis</div>
                </div>
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            </div>

            {/* Log stream */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {logs.length === 0 && (
                    <div className="text-center mt-8 text-gov-text-muted text-[10px] uppercase tracking-widest opacity-40">
                        Awaiting pipeline activity...
                    </div>
                )}

                {logs.map((log, idx) => {
                    const colors = getAgentColors(log.agent);
                    return (
                        <div
                            key={idx}
                            className={`relative pl-3 border-l-2 ml-1 ${colors.border}`}
                        >
                            {/* Dot */}
                            <div className={`absolute -left-[5px] top-0 w-2 h-2 rounded-full ${colors.dot}`} />

                            {/* Header */}
                            <div className="flex items-center justify-between mb-1">
                                <span className={`text-[10px] font-bold uppercase tracking-wide ${colors.label}`}>
                                    {log.agent}
                                </span>
                                <span className="text-[9px] text-gov-text-muted font-mono">{log.timestamp}</span>
                            </div>

                            {/* Content */}
                            <div className="bg-white/5 rounded px-2.5 py-2 border border-white/5">
                                <LogContent agent={log.agent} msg={log.message} />
                            </div>
                        </div>
                    );
                })}

                <div ref={endRef} />
            </div>
        </div>
    );
};
