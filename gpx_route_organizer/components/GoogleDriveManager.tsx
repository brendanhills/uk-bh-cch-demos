import React from 'react';
import { GoogleDriveIcon } from './icons';
import { GapiStatus } from '../services/googleApiService';

interface GoogleDriveManagerProps {
    status: GapiStatus;
    isSignedIn: boolean | null;
    onSignIn: () => void;
    onSignOut: () => void;
}

const GoogleDriveManager: React.FC<GoogleDriveManagerProps> = ({ status, isSignedIn, onSignIn, onSignOut }) => {
    if (status === 'LOADING' || status === 'IDLE') {
        return (
            <div className="flex items-center space-x-2 p-2 rounded-lg bg-slate-200 dark:bg-slate-700 animate-pulse">
                <div className="w-6 h-6 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                <div className="w-24 h-4 bg-slate-300 dark:bg-slate-600 rounded"></div>
            </div>
        );
    }
    
    if (status === 'ERROR') {
        return null; // The error is displayed in the main App component
    }

    if (isSignedIn) {
        return (
            <div className="flex items-center space-x-2">
                <GoogleDriveIcon className="h-8 w-8 text-slate-600 dark:text-slate-300" />
                <button
                    onClick={onSignOut}
                    className="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-primary dark:hover:text-brand-primary"
                    title="Disconnect Google Drive"
                >
                    Disconnect
                </button>
            </div>
        );
    }

    return (
        <button
            onClick={onSignIn}
            className="flex items-center space-x-2 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold py-2 px-4 rounded-lg shadow transition-colors border border-slate-200 dark:border-slate-600"
        >
            <GoogleDriveIcon className="h-6 w-6" />
            <span>Connect to Drive</span>
        </button>
    );
};

export default GoogleDriveManager;