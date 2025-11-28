import React from 'react';
import type { LogEntry } from '../types';
import { HistoryIcon, FileIcon } from './icons';
import Spinner from './Spinner';

interface RouteHistoryProps {
    entries: LogEntry[] | null;
    isLoading: boolean;
    onLoadRoute: (entry: LogEntry) => void;
}

const RouteHistory: React.FC<RouteHistoryProps> = ({ entries, isLoading, onLoadRoute }) => {
    return (
        <div className="w-full bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 md:p-8 animate-fade-in space-y-4">
            <div className="flex items-center space-x-3">
                <HistoryIcon className="h-6 w-6 text-brand-primary" />
                <h3 className="text-xl font-bold text-slate-800 dark:text-white">Route History</h3>
            </div>
            
            {isLoading && !entries && <Spinner />}

            {!isLoading && entries && entries.length === 0 && (
                <p className="text-slate-500 dark:text-slate-400 text-center py-4">
                    No routes have been saved to your Google Drive yet.
                </p>
            )}

            {!isLoading && entries && entries.length > 0 && (
                <div className="max-h-96 overflow-y-auto pr-2 -mr-2 space-y-2">
                    {entries.map((entry, index) => (
                        <button
                            key={`${entry.fileName}-${index}`}
                            onClick={() => onLoadRoute(entry)}
                            className="w-full text-left p-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200 flex items-start space-x-3 focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        >
                            <FileIcon className="h-5 w-5 text-slate-400 dark:text-slate-500 mt-0.5 flex-shrink-0" />
                            <div className="flex-grow">
                                <p className="font-semibold text-slate-800 dark:text-slate-100 break-all">{entry.fileName}</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">
                                    {entry.folderPath} &bull; {new Date(entry.dateAdded).toLocaleDateString()}
                                </p>
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RouteHistory;
