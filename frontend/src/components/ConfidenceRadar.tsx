import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface ConfidenceData {
    subject: string;
    A: number; // Current Confidence
    fullMark: number;
}

interface ConfidenceRadarProps {
    data: ConfidenceData[];
}

export const ConfidenceRadar: React.FC<ConfidenceRadarProps> = ({ data }) => {
    // Defensive check
    if (!data || data.length === 0) return null;

    return (
        <div className="w-full h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Confidence"
                        dataKey="A"
                        stroke="#10B981"
                        strokeWidth={2}
                        fill="#10B981"
                        fillOpacity={0.3}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};
