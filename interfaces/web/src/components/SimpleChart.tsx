import React from 'react';

interface SimpleChartProps {
  data: number[];
  height?: number;
  width?: string | number;
}

export const SimpleChart: React.FC<SimpleChartProps> = ({ data, height = 200, width = "100%" }) => {
  if (!data || data.length < 2) {
    return (
      <div style={{ height, width, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--gray)', fontSize: '12px', background: 'var(--lightGray)', borderRadius: '16px' }}>
        Données insuffisantes pour le graphique
      </div>
    );
  }

  const max = Math.max(...data) || 1;
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((val - min) / range) * 80 - 10;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div style={{ height, width, position: 'relative', background: 'var(--white)', borderRadius: '24px', padding: '20px', border: 'var(--border-main)' }}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
        <polyline
          points={points}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      <div style={{ position: 'absolute', top: '10px', right: '20px', fontSize: '10px', fontWeight: 900, color: 'var(--accent)' }}>
        MAX: {max.toLocaleString()} Ar
      </div>
      <div style={{ position: 'absolute', bottom: '10px', right: '20px', fontSize: '10px', fontWeight: 900, color: 'var(--gray)' }}>
        MIN: {min.toLocaleString()} Ar
      </div>
    </div>
  );
};
