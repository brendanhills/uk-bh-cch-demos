import React, { useState } from 'react';
import { FullAnalysis } from '../types';
import { RoadIcon, MountainIcon, MapPinIcon, FolderIcon, FileIcon, ClipboardCopyIcon, CheckCircleIcon, DownloadIcon, GoogleDriveIcon } from './icons';
import SurfaceAnalysis from './SurfaceAnalysis';
import MapView from './MapView';

interface AnalysisResultProps {
  result: FullAnalysis;
  fileName: string;
  gpxContent: string;
  onFileNameChange: (newName: string) => void;
  onAnalysisChange: (updates: Partial<FullAnalysis>) => void;
  onSaveToDrive: () => void;
  isSaving: boolean;
  isSignedIn: boolean | null;
}

const StatCard: React.FC<{ icon: React.ReactNode; label: string; value: string | number; unit?: string }> = ({ icon, label, value, unit }) => (
    <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg flex items-center space-x-4">
        <div className="bg-brand-primary/10 p-2 rounded-full">
            {icon}
        </div>
        <div>
            <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
            <p className="text-lg font-bold text-slate-800 dark:text-slate-100">{value} <span className="text-sm font-normal">{unit}</span></p>
        </div>
    </div>
);

const CopyableField: React.FC<{ text: string }> = ({ text }) => {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = () => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex items-center space-x-2">
            <p className="flex-grow p-3 bg-slate-100 dark:bg-slate-700 rounded-md text-slate-800 dark:text-slate-100 font-mono text-sm break-all">{text}</p>
            <button
                onClick={handleCopy}
                className="p-3 bg-slate-200 dark:bg-slate-600 hover:bg-slate-300 dark:hover:bg-slate-500 rounded-md transition"
                title="Copy to clipboard"
            >
                {copied ? <CheckCircleIcon className="h-5 w-5 text-green-500" /> : <ClipboardCopyIcon className="h-5 w-5 text-slate-500 dark:text-slate-300" />}
            </button>
        </div>
    );
};

const EditableFileNameField: React.FC<{ value: string; onChange: (value: string) => void; }> = ({ value, onChange }) => {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = () => {
        navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex items-center space-x-2">
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="flex-grow w-full p-3 bg-slate-100 dark:bg-slate-700 rounded-md text-slate-800 dark:text-slate-100 font-mono text-sm break-all border border-transparent focus:ring-2 focus:ring-brand-primary focus:border-brand-primary outline-none"
            />
            <button
                onClick={handleCopy}
                className="p-3 bg-slate-200 dark:bg-slate-600 hover:bg-slate-300 dark:hover:bg-slate-500 rounded-md transition"
                title="Copy to clipboard"
            >
                {copied ? <CheckCircleIcon className="h-5 w-5 text-green-500" /> : <ClipboardCopyIcon className="h-5 w-5 text-slate-500 dark:text-slate-300" />}
            </button>
        </div>
    );
};

const AnalysisResult: React.FC<AnalysisResultProps> = ({ result, fileName, gpxContent, onFileNameChange, onAnalysisChange, onSaveToDrive, isSaving, isSignedIn }) => {
  const handleSaveFile = () => {
    if (!gpxContent) return;
    const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const driveButtonDisabled = !isSignedIn || isSaving;
  const isEditing = !!result.sourceLogEntry;
  const rideTypes = ["Road", "Gravel", "MTB", "Hiking"];
  const surfaceTypes = ["Paved", "Mixed", "Dirt"];
  const lengthCategories = ["Short", "Medium", "Medium-Long", "Long", "Multi-Day"];
  const climbingCategories = ["N/A", "Pan-flat", "Flat", "Rolling", "Lumpy", "Hilly", "Mountainous"];

  return (
    <div className="w-full bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 md:p-8 animate-fade-in space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Route Analysis Complete</h2>
        <p className="text-slate-600 dark:text-slate-300">Here's the breakdown of <span className="font-semibold text-brand-primary">{result.name}</span>.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <StatCard icon={<MapPinIcon className="h-6 w-6 text-brand-primary"/>} label="Location" value={`${result.location}, ${result.countryCode}`} />
          <StatCard icon={<RoadIcon className="h-6 w-6 text-brand-primary"/>} label="Distance" value={result.distance} unit="km" />
          <StatCard icon={<MountainIcon className="h-6 w-6 text-brand-primary"/>} label="Climbing" value={result.elevationGain} unit="m" />
      </div>
      
      <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg grid grid-cols-2 md:grid-cols-4 gap-4 items-center">
          <div>
            <p className="text-xs uppercase text-slate-500 dark:text-slate-400 tracking-wider text-center mb-1">Ride Type</p>
            <select
                value={result.rideType}
                onChange={(e) => onAnalysisChange({ rideType: e.target.value })}
                className="w-full p-2 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-100 font-semibold border-transparent focus:ring-2 focus:ring-brand-primary focus:border-brand-primary outline-none transition"
                aria-label="Change ride type"
            >
                {rideTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                ))}
            </select>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-500 dark:text-slate-400 tracking-wider text-center mb-1">Surface</p>
            <select
                value={result.surfaceType}
                onChange={(e) => onAnalysisChange({ surfaceType: e.target.value })}
                className="w-full p-2 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-100 font-semibold border-transparent focus:ring-2 focus:ring-brand-primary focus:border-brand-primary outline-none transition"
                aria-label="Change surface type"
            >
                {surfaceTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                ))}
            </select>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-500 dark:text-slate-400 tracking-wider text-center mb-1">Length</p>
             <select
                value={result.lengthCategory}
                onChange={(e) => onAnalysisChange({ lengthCategory: e.target.value })}
                className="w-full p-2 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-100 font-semibold border-transparent focus:ring-2 focus:ring-brand-primary focus:border-brand-primary outline-none transition"
                aria-label="Change length category"
            >
                {lengthCategories.map(type => (
                    <option key={type} value={type}>{type}</option>
                ))}
            </select>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-500 dark:text-slate-400 tracking-wider text-center mb-1">Climbing</p>
             <select
                value={result.climbingCategory}
                onChange={(e) => onAnalysisChange({ climbingCategory: e.target.value })}
                className="w-full p-2 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-100 font-semibold border-transparent focus:ring-2 focus:ring-brand-primary focus:border-brand-primary outline-none transition"
                aria-label="Change climbing category"
            >
                {climbingCategories.map(type => (
                    <option key={type} value={type}>{type}</option>
                ))}
            </select>
          </div>
      </div>

      <MapView gpxContent={gpxContent} />

      {(result.wayTypes?.length > 0 || result.surfaces?.length > 0) && (
        <SurfaceAnalysis wayTypes={result.wayTypes} surfaces={result.surfaces} />
      )}

      <div>
          <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-4">Suggested Organization</h3>
          
          <div className="space-y-4">
              <div>
                  <label className="text-sm font-medium text-slate-600 dark:text-slate-300 flex items-center mb-1">
                      <FolderIcon className="h-5 w-5 text-slate-500 dark:text-slate-400"/>
                      <span className="ml-2">Folder Path</span>
                  </label>
                  <CopyableField text={result.suggestedFolderPath} />
              </div>
              <div>
                  <label className="text-sm font-medium text-slate-600 dark:text-slate-300 flex items-center mb-1">
                      <FileIcon className="h-5 w-5 text-slate-500 dark:text-slate-400"/>
                      <span className="ml-2">New Filename</span>
                  </label>
                  <EditableFileNameField value={fileName} onChange={onFileNameChange} />
              </div>
          </div>
      </div>
      
      <div className="mt-2 pt-6 border-t border-slate-200 dark:border-slate-700 space-y-4">
        <button
            onClick={handleSaveFile}
            className="w-full bg-brand-secondary hover:bg-slate-800 dark:bg-brand-secondary dark:hover:bg-slate-500 text-white font-bold py-3 px-4 rounded-lg transition duration-300 ease-in-out flex items-center justify-center space-x-2 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-secondary"
        >
            <DownloadIcon className="h-5 w-5" />
            <span>Save New GPX File to Local</span>
        </button>

        <button
            onClick={onSaveToDrive}
            disabled={driveButtonDisabled}
            className="w-full bg-brand-primary text-white font-bold py-3 px-4 rounded-lg transition duration-300 ease-in-out flex items-center justify-center space-x-2 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary"
        >
            {isSaving ? (
                <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{isEditing ? 'Updating...' : 'Saving to Drive...'}</span>
                </>
            ) : (
                <>
                    <GoogleDriveIcon className="h-5 w-5" />
                    <span>{isEditing ? 'Update Route' : 'Save to GPX Routes in Google Drive'}</span>
                </>
            )}
        </button>
      </div>

    </div>
  );
};

export default AnalysisResult;