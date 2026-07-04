import React, { useState, useEffect, useCallback } from 'react';
import { Cpu, ChevronRight, Play, RotateCcw, ChevronLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// ─── Node definitions ─────────────────────────────────────────────────────────
const NODES = [
    {
        id: 'input',
        label: 'User Input',
        sublabel: 'Citizen Query',
        color: '#60A5FA',
        glow: 'rgba(96,165,250,0.4)',
        description: 'Raw natural language input from the citizen is received and tokenised.',
    },
    {
        id: 'filter',
        label: 'Content Filter',
        sublabel: 'Safety Guard',
        color: '#F87171',
        glow: 'rgba(248,113,113,0.4)',
        description: 'Ethics & safety check. Screens for harmful, illegal, or off-scope content before routing.',
    },
    {
        id: 'classifier',
        label: 'Service Classifier',
        sublabel: 'Intent Router',
        color: '#C6A756',
        glow: 'rgba(198,167,86,0.4)',
        description: 'NLP keyword + embedding classifier routes the query: Legal Assistance or General Civic Service.',
    },
    {
        id: 'legal',
        label: 'Legal Agent',
        sublabel: 'RAG · ChromaDB',
        color: '#A78BFA',
        glow: 'rgba(167,139,250,0.4)',
        description: 'Retrieves relevant statutes, case law and IPC sections from the ChromaDB vector store. Generates grounded legal advice.',
    },
    {
        id: 'civic',
        label: 'Civic Agent',
        sublabel: 'Service Navigator',
        color: '#34D399',
        glow: 'rgba(52,211,153,0.4)',
        description: 'Handles non-legal civic queries: ration cards, land records, welfare schemes, documents.',
    },
    {
        id: 'risk',
        label: 'Risk Assessor',
        sublabel: 'Severity Analyser',
        color: '#FB923C',
        glow: 'rgba(251,146,60,0.4)',
        description: 'Evaluates potential legal risk severity (Low / Medium / High) and flags urgent cases for human escalation.',
    },
    {
        id: 'ethics',
        label: 'Ethics Guard',
        sublabel: 'Veto Layer',
        color: '#EC4899',
        glow: 'rgba(236,72,153,0.4)',
        description: 'Final fairness & bias check. Can veto any output that violates ethical guidelines or discriminates.',
    },
    {
        id: 'confidence',
        label: 'Confidence Engine',
        sublabel: 'Score & Validate',
        color: '#22D3EE',
        glow: 'rgba(34,211,238,0.4)',
        description: 'Scores response trustworthiness 0–100%. Below threshold triggers fallback or human-in-the-loop.',
    },
    {
        id: 'output',
        label: 'Response Package',
        sublabel: 'Citizen Delivery',
        color: '#86EFAC',
        glow: 'rgba(134,239,172,0.4)',
        description: 'Structured output: Action plan, required documents, statutes, audio TTS, and downloadable pre-filled forms.',
    },
];

// ─── Edges (source → target) ─────────────────────────────────────────────────
const EDGES = [
    { from: 'input', to: 'filter', label: 'raw query' },
    { from: 'filter', to: 'classifier', label: 'clean input' },
    { from: 'classifier', to: 'legal', label: 'legal intent' },
    { from: 'classifier', to: 'civic', label: 'civic intent' },
    { from: 'legal', to: 'risk', label: 'legal response' },
    { from: 'civic', to: 'risk', label: 'civic response' },
    { from: 'risk', to: 'ethics', label: 'risk-tagged' },
    { from: 'ethics', to: 'confidence', label: 'approved' },
    { from: 'confidence', to: 'output', label: 'validated' },
];

const DEMO_QUERY = "My landlord locked me out of my apartment without notice. What are my legal rights?";

const PIPELINE_STEPS = [
    { nodeId: 'input', log: '→ Received: "My landlord locked me out..."', ms: 4 },
    { nodeId: 'filter', log: '✓ Safety check passed. No harmful content.', ms: 28 },
    { nodeId: 'classifier', log: '⚡ Intent: Legal Assistance (confidence 0.94)', ms: 12 },
    { nodeId: 'legal', log: '📖 Retrieved: Transfer of Property Act §108, BNS §323', ms: 186 },
    { nodeId: 'risk', log: '⚠️  Risk Severity: MEDIUM — Possible eviction violation.', ms: 34 },
    { nodeId: 'ethics', log: '🛡️  Ethics check: PASS. No bias detected.', ms: 21 },
    { nodeId: 'confidence', log: '📊 Confidence Score: 87% — Response approved.', ms: 9 },
    { nodeId: 'output', log: '✅ Package ready: 3 statutes, 2 action steps, form pre-filled.', ms: 7 },
];

// Layout positions on a 600x900 SVG canvas
const NODE_POS: Record<string, { x: number; y: number }> = {
    input: { x: 300, y: 60 },
    filter: { x: 300, y: 175 },
    classifier: { x: 300, y: 295 },
    legal: { x: 140, y: 420 },
    civic: { x: 460, y: 420 },
    risk: { x: 300, y: 545 },
    ethics: { x: 300, y: 665 },
    confidence: { x: 300, y: 785 },
    output: { x: 300, y: 905 },
};

const CANVAS_W = 600;
const CANVAS_H = 980;
const NODE_R = 34;

export const LangGraphVisualizer: React.FC = () => {
    const [activeNode, setActiveNode] = useState<string | null>(null);
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);
    const [step, setStep] = useState(-1);
    const [running, setRunning] = useState(false);
    const [logs, setLogs] = useState<{ nodeId: string; text: string; ms: number }[]>([]);
    const [activeEdges, setActiveEdges] = useState<Set<string>>(new Set());

    const navigate = useNavigate();

    const reset = useCallback(() => {
        setStep(-1);
        setRunning(false);
        setLogs([]);
        setActiveNode(null);
        setActiveEdges(new Set());
    }, []);

    const runDemo = useCallback(() => {
        reset();
        setTimeout(() => setRunning(true), 50);
    }, [reset]);

    useEffect(() => {
        if (!running) return;
        if (step >= PIPELINE_STEPS.length - 1) {
            setRunning(false);
            return;
        }
        const next = step + 1;
        const delay = next === 0 ? 300 : 800 + PIPELINE_STEPS[next - 1].ms * 4;
        const timer = setTimeout(() => {
            setStep(next);
            const s = PIPELINE_STEPS[next];
            setActiveNode(s.nodeId);
            setLogs(prev => [...prev, { nodeId: s.nodeId, text: s.log, ms: s.ms }]);

            // Activate relevant edges
            setActiveEdges(prev => {
                const next2 = new Set(prev);
                EDGES.forEach(e => {
                    if (e.to === s.nodeId) next2.add(`${e.from}-${e.to}`);
                });
                return next2;
            });
        }, delay);
        return () => clearTimeout(timer);
    }, [running, step]);

    const getNode = (id: string) => NODES.find(n => n.id === id)!;
    const displayNode = hoveredNode ? getNode(hoveredNode) : activeNode ? getNode(activeNode) : null;

    return (
        <div className="min-h-screen bg-gov-navy text-gov-text font-sans flex flex-col">

            {/* ── Header ── */}
            <header className="border-b border-white/5 bg-gov-navy-light px-8 py-4 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-6">
                    <button
                        onClick={() => navigate('/session')}
                        className="flex items-center gap-2 text-[10px] text-gov-gold hover:underline uppercase tracking-widest font-bold"
                    >
                        <ChevronLeft size={14} />
                        Back to Chat
                    </button>

                    <div className="h-6 w-px bg-white/10" />

                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gov-gold/10 border border-gov-gold/30 flex items-center justify-center">
                            <Cpu size={16} className="text-gov-gold" />
                        </div>
                        <div>
                            <h1 className="text-sm font-bold tracking-widest uppercase text-gov-text">CIVIA · LangGraph Pipeline</h1>
                            <p className="text-[10px] text-gov-text-muted tracking-widest">Multi-Agent Civic AI — Hackathon Demo</p>
                        </div>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={reset}
                        className="flex items-center gap-2 px-4 py-2 border border-white/10 text-gov-text-muted text-xs uppercase tracking-widest rounded hover:bg-white/5 transition-colors"
                    >
                        <RotateCcw size={13} /> Reset
                    </button>
                    <button
                        onClick={runDemo}
                        disabled={running}
                        className="flex items-center gap-2 px-5 py-2 bg-gov-gold text-gov-navy font-bold text-xs uppercase tracking-widest rounded hover:bg-yellow-500 disabled:opacity-50 transition-colors"
                    >
                        <Play size={13} /> {running ? 'Running...' : 'Run Demo'}
                    </button>
                </div>
            </header>

            {/* ── Body ── */}
            <div className="flex-1 flex flex-col lg:flex-row gap-0 overflow-hidden">

                {/* ── Graph Panel ── */}
                <div className="flex-1 flex flex-col items-center justify-start overflow-y-auto py-6 px-4 bg-gov-navy">

                    {/* Demo query pill */}
                    <div className="mb-6 px-5 py-3 border border-white/10 rounded-full bg-gov-navy-light text-gov-text-muted text-xs flex items-center gap-3 max-w-xl text-center">
                        <ChevronRight size={14} className="text-gov-gold shrink-0" />
                        <span className="italic">"{DEMO_QUERY}"</span>
                    </div>

                    {/* SVG Flow Graph */}
                    <svg
                        viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
                        className="w-full max-w-lg"
                        style={{ maxHeight: '820px' }}
                    >
                        <defs>
                            {NODES.map(n => (
                                <radialGradient key={n.id} id={`glow-${n.id}`} cx="50%" cy="50%" r="50%">
                                    <stop offset="0%" stopColor={n.color} stopOpacity="0.3" />
                                    <stop offset="100%" stopColor={n.color} stopOpacity="0" />
                                </radialGradient>
                            ))}
                            <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
                                <path d="M0,0 L0,7 L8,3.5 z" fill="rgba(255,255,255,0.2)" />
                            </marker>
                            <marker id="arrow-active" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
                                <path d="M0,0 L0,7 L8,3.5 z" fill="#C6A756" />
                            </marker>
                        </defs>

                        {/* Edges */}
                        {EDGES.map(edge => {
                            const from = NODE_POS[edge.from];
                            const to = NODE_POS[edge.to];
                            const edgeKey = `${edge.from}-${edge.to}`;
                            const isActive = activeEdges.has(edgeKey);

                            // Offset for branching edges
                            const fromX = from.x;
                            const toX = to.x;
                            const fromY = from.y + NODE_R;
                            const toY = to.y - NODE_R;

                            // Bezier control points
                            const midY = (fromY + toY) / 2;
                            const d = `M ${fromX} ${fromY} C ${fromX} ${midY}, ${toX} ${midY}, ${toX} ${toY}`;

                            return (
                                <g key={edgeKey}>
                                    <path
                                        d={d}
                                        fill="none"
                                        stroke={isActive ? '#C6A756' : 'rgba(255,255,255,0.07)'}
                                        strokeWidth={isActive ? 2 : 1.5}
                                        markerEnd={isActive ? 'url(#arrow-active)' : 'url(#arrow)'}
                                        style={{
                                            transition: 'stroke 0.4s ease, stroke-width 0.4s ease',
                                            filter: isActive ? 'drop-shadow(0 0 4px rgba(198,167,86,0.5))' : 'none'
                                        }}
                                        strokeDasharray={isActive ? 'none' : '5 4'}
                                    />
                                    {/* Edge label */}
                                    <text
                                        x={(fromX + toX) / 2 + (edge.from === 'classifier' && edge.to === 'legal' ? -36 : edge.from === 'classifier' && edge.to === 'civic' ? 36 : 8)}
                                        y={(fromY + toY) / 2}
                                        fill={isActive ? '#C6A756' : 'rgba(255,255,255,0.2)'}
                                        fontSize="9"
                                        fontFamily="monospace"
                                        textAnchor="middle"
                                        style={{ transition: 'fill 0.4s ease' }}
                                    >
                                        {edge.label}
                                    </text>
                                </g>
                            );
                        })}

                        {/* Nodes */}
                        {NODES.map(n => {
                            const pos = NODE_POS[n.id];
                            const isActive = activeNode === n.id;
                            const isHovered = hoveredNode === n.id;
                            const wasVisited = logs.some(l => l.nodeId === n.id);

                            return (
                                <g
                                    key={n.id}
                                    transform={`translate(${pos.x}, ${pos.y})`}
                                    onClick={() => setHoveredNode(hoveredNode === n.id ? null : n.id)}
                                    onMouseEnter={() => setHoveredNode(n.id)}
                                    onMouseLeave={() => setHoveredNode(null)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    {/* Glow halo when active */}
                                    {(isActive || isHovered) && (
                                        <circle r={NODE_R + 20} fill={`url(#glow-${n.id})`}>
                                            {isActive && (
                                                <animate attributeName="r" values={`${NODE_R + 10};${NODE_R + 25};${NODE_R + 10}`} dur="1.5s" repeatCount="indefinite" />
                                            )}
                                        </circle>
                                    )}

                                    {/* Outer ring */}
                                    <circle
                                        r={NODE_R + 4}
                                        fill="none"
                                        stroke={wasVisited || isActive ? n.color : 'rgba(255,255,255,0.05)'}
                                        strokeWidth={isActive ? 2 : 1}
                                        opacity={isActive ? 1 : 0.5}
                                        style={{ transition: 'stroke 0.4s ease, opacity 0.4s ease' }}
                                    >
                                        {isActive && (
                                            <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="1.5s" repeatCount="indefinite" />
                                        )}
                                    </circle>

                                    {/* Main circle */}
                                    <circle
                                        r={NODE_R}
                                        fill={isActive || wasVisited ? `${n.color}25` : 'rgba(28,37,65,0.9)'}
                                        stroke={isActive ? n.color : wasVisited ? `${n.color}80` : 'rgba(255,255,255,0.1)'}
                                        strokeWidth={isActive ? 2.5 : 1.5}
                                        style={{ transition: 'all 0.4s ease', filter: isActive ? `drop-shadow(0 0 10px ${n.glow})` : 'none' }}
                                    />

                                    {/* Icon - rendered as text emoji since SVG doesn't support lucide directly */}
                                    <text textAnchor="middle" dominantBaseline="central" y={-8} fontSize="16" fill={isActive || wasVisited ? n.color : 'rgba(255,255,255,0.3)'}>
                                        {n.id === 'input' ? '⌨' : n.id === 'filter' ? '🔍' : n.id === 'classifier' ? '⚡' : n.id === 'legal' ? '⚖' : n.id === 'civic' ? '🏛' : n.id === 'risk' ? '⚠' : n.id === 'ethics' ? '🛡' : n.id === 'confidence' ? '📊' : '✅'}
                                    </text>

                                    {/* Node label */}
                                    <text textAnchor="middle" y={10} fontSize="9" fontWeight="bold" fill={isActive || wasVisited ? n.color : 'rgba(255,255,255,0.5)'} fontFamily="sans-serif" style={{ transition: 'fill 0.4s ease' }}>
                                        {n.label}
                                    </text>

                                    {/* Sublabel */}
                                    <text textAnchor="middle" y={22} fontSize="7.5" fill="rgba(255,255,255,0.25)" fontFamily="monospace">
                                        {n.sublabel}
                                    </text>
                                </g>
                            );
                        })}
                    </svg>
                </div>

                {/* ── Right Panel ── */}
                <div className="w-full lg:w-[380px] shrink-0 border-l border-white/5 flex flex-col bg-gov-navy-light overflow-hidden">

                    {/* Node Details */}
                    <div className="p-5 border-b border-white/5 shrink-0">
                        <p className="text-[9px] text-gov-text-muted uppercase tracking-widest mb-3">
                            {hoveredNode ? 'Node Details' : activeNode ? 'Active Node' : 'Click any node to inspect'}
                        </p>
                        {displayNode ? (
                            <div
                                key={displayNode.id}
                                className="p-4 rounded-xl border"
                                style={{ borderColor: `${displayNode.color}40`, background: `${displayNode.color}08` }}
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base" style={{ background: `${displayNode.color}20` }}>
                                        {displayNode.id === 'input' ? '⌨' : displayNode.id === 'filter' ? '🔍' : displayNode.id === 'classifier' ? '⚡' : displayNode.id === 'legal' ? '⚖' : displayNode.id === 'civic' ? '🏛' : displayNode.id === 'risk' ? '⚠' : displayNode.id === 'ethics' ? '🛡' : displayNode.id === 'confidence' ? '📊' : '✅'}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold" style={{ color: displayNode.color }}>{displayNode.label}</div>
                                        <div className="text-[9px] font-mono text-gov-text-muted">{displayNode.sublabel}</div>
                                    </div>
                                </div>
                                <p className="text-xs text-gov-text-muted leading-relaxed">{displayNode.description}</p>
                            </div>
                        ) : (
                            <div className="p-4 rounded-xl border border-white/5 text-gov-text-muted text-xs italic">
                                Run the demo or hover a node to see details.
                            </div>
                        )}
                    </div>

                    {/* Live Execution Log */}
                    <div className="flex-1 flex flex-col min-h-0 p-4">
                        <p className="text-[9px] text-gov-text-muted uppercase tracking-widest mb-3 shrink-0">Live Execution Log</p>
                        <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                            {logs.length === 0 && (
                                <div className="text-xs text-gov-text-muted italic opacity-50 text-center mt-8">Press "Run Demo" to execute the pipeline</div>
                            )}
                            {logs.map((log, i) => {
                                const node = getNode(log.nodeId);
                                return (
                                    <div
                                        key={i}
                                        className="flex flex-col gap-1 p-3 rounded-lg border"
                                        style={{
                                            borderColor: `${node.color}25`,
                                            background: `${node.color}08`,
                                            animation: 'fadeIn 0.3s ease forwards'
                                        }}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="text-[10px] font-bold uppercase tracking-wide" style={{ color: node.color }}>{node.label}</span>
                                            <span className="text-[9px] font-mono text-gov-text-muted">{log.ms}ms</span>
                                        </div>
                                        <span className="text-[11px] text-gov-text font-mono leading-relaxed">{log.text}</span>
                                    </div>
                                );
                            })}
                            {running && step < PIPELINE_STEPS.length - 1 && (
                                <div className="flex items-center gap-2 p-3 text-gov-gold text-[10px] font-mono animate-pulse">
                                    <span>▶</span> Processing next node...
                                </div>
                            )}
                            {!running && step === PIPELINE_STEPS.length - 1 && (
                                <div className="mt-2 p-3 rounded-lg border border-green-500/20 bg-green-500/5 text-xs text-green-400 font-bold">
                                    ✅ Pipeline complete — {logs.reduce((s, l) => s + l.ms, 0)}ms total
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Stats Bar */}
                    <div className="p-4 border-t border-white/5 grid grid-cols-3 gap-3 shrink-0">
                        {[
                            { label: 'Agents', val: '7' },
                            { label: 'Total Latency', val: step === PIPELINE_STEPS.length - 1 ? `${logs.reduce((s, l) => s + l.ms, 0)}ms` : '—' },
                            { label: 'Confidence', val: step >= 7 ? '87%' : '—' },
                        ].map(stat => (
                            <div key={stat.label} className="text-center p-2 rounded-lg bg-gov-navy border border-white/5">
                                <div className="text-xs font-bold text-gov-text">{stat.val}</div>
                                <div className="text-[9px] text-gov-text-muted uppercase tracking-widest mt-0.5">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>

            <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
      `}</style>
        </div>
    );
};
