import React, { createContext, useContext, useState, type ReactNode } from 'react';

interface LogEntry {
    id: string;
    timestamp: string;
    agent: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
}

interface SessionContextType {
    logs: LogEntry[];
    addLog: (agent: string, message: string, type?: 'info' | 'warning' | 'error' | 'success') => void;
    resetSession: () => void;
    isActive: boolean;
    startSession: () => void;
    endSession: () => void;
    sessionId: string;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const generateId = () => Math.random().toString(36).substring(2, 10);

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [isActive, setIsActive] = useState(false);
    const [sessionId, setSessionId] = useState<string>(generateId());

    const addLog = (agent: string, message: string, type: 'info' | 'warning' | 'error' | 'success' = 'info') => {
        const newLog: LogEntry = {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString().split('T')[1].slice(0, -1), // HH:MM:SS.mmm
            agent,
            message,
            type
        };
        setLogs(prev => [...prev, newLog]);
    };

    const resetSession = () => {
        setLogs([]);
        setIsActive(false);
    };

    const startSession = () => {
        resetSession();
        setSessionId(generateId());
        setIsActive(true);
        addLog("System", "Session Initialized. Neural Link Active.", "success");
    };

    const endSession = () => {
        resetSession();
        // In a real app, notify backend here
    };

    return (
        <SessionContext.Provider value={{ logs, addLog, resetSession, isActive, startSession, endSession, sessionId }}>
            {children}
        </SessionContext.Provider>
    );
};

export const useSession = () => {
    const context = useContext(SessionContext);
    if (!context) throw new Error("useSession must be used within SessionProvider");
    return context;
};
