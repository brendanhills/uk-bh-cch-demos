import React from 'react';
import type { SurfaceBreakdownItem } from '../types';

interface SurfaceAnalysisProps {
  wayTypes: SurfaceBreakdownItem[];
  surfaces: SurfaceBreakdownItem[];
}

const typeColorMap: { [key: string]: string } = {
    // Way Types - cool tones
    'road': 'bg-sky-500',
    'path': 'bg-slate-400',
    'singletrack': 'bg-amber-600',
    'street': 'bg-slate-500',
    'stateroad': 'bg-sky-400',
    'cycleway': 'bg-emerald-500',
    'track': 'bg-orange-400',
  
    // Surfaces - warm tones
    'unpaved': 'bg-yellow-700',
    'asphalt': 'bg-gray-700',
    'paved': 'bg-gray-500',
    'gravel': 'bg-orange-500',
    'dirt': 'bg-amber-800',
    'concrete': 'bg-slate-300',

    // Generic/Unknown
    'unknown': 'bg-black',
    'default': 'bg-gray-400'
  };
  
const getColor = (name: string): string => {
    const key = name.toLowerCase().replace(/[\s-]/g, '');
    return typeColorMap[key] || typeColorMap['default'];
};

const formatDistance = (km: number): string => {
    if (km === 0) return '0 km';
    if (km < 0.1) return '< 100 m';
    if (km >= 10) return `${km.toFixed(1)} km`;
    return `${km.toFixed(2)} km`;
};

const BreakdownSection: React.FC<{ title: string; items: SurfaceBreakdownItem[] }> = ({ title, items }) => {
    if (!items || items.length === 0) return null;

    const totalDistance = items.reduce((sum, item) => sum + item.distance, 0);
    if (totalDistance === 0) return null;

    return (
        <div>
            <h4 className="font-bold text-slate-800 dark:text-slate-100 mb-3">{title}</h4>
            <div className="flex h-3 rounded-full overflow-hidden bg-slate-200 dark:bg-slate-700 mb-4">
                {items.map(item => (
                    <div
                        key={item.name}
                        className={`${getColor(item.name)} transition-all duration-500`}
                        style={{ width: `${(item.distance / totalDistance) * 100}%` }}
                        title={`${item.name}: ${formatDistance(item.distance)} (${((item.distance / totalDistance) * 100).toFixed(1)}%)`}
                    />
                ))}
            </div>
            <ul className="space-y-2 text-sm">
                {items.map(item => (
                    <li key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center">
                            <span className={`w-3 h-3 rounded-sm mr-3 ${getColor(item.name)}`}></span>
                            <span className="text-slate-700 dark:text-slate-300">{item.name}</span>
                        </div>
                        <span className="font-mono text-slate-500 dark:text-slate-400">{formatDistance(item.distance)}</span>
                    </li>
                ))}
            </ul>
        </div>
    )
}

const SurfaceAnalysis: React.FC<SurfaceAnalysisProps> = ({ wayTypes, surfaces }) => {
  return (
    <div>
        <h3 className="text-xl font-bold text-slate-800 dark:text-white">Way Types & Surfaces</h3>
        <div className="mt-4 bg-slate-100 dark:bg-slate-900/50 p-6 rounded-lg grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <BreakdownSection title="Way Types" items={wayTypes} />
            <BreakdownSection title="Surfaces" items={surfaces} />
        </div>
    </div>
  );
};

export default SurfaceAnalysis;