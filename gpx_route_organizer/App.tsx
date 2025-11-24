
import React, { useState, useCallback, useEffect } from 'react';
import type { FullAnalysis, LogEntry } from './types';
import { parseGPXFile } from './services/gpxParser';
import { getRouteAnalysis } from './services/geminiService';
import { useGoogleDrive } from './hooks/useGoogleDrive';

import FileUpload from './components/FileUpload';
import AnalysisResult from './components/AnalysisResult';
import Spinner from './components/Spinner';
import GoogleDriveManager from './components/GoogleDriveManager';
import RouteHistory from './components/RouteHistory';
import { HistoryIcon } from './components/icons';

// Declare html2canvas for TypeScript since it's loaded from a script tag.
declare const html2canvas: any;

const App: React.FC = () => {
  const [gpxFile, setGpxFile] = useState<File | null>(null);
  const [gpxFileContent, setGpxFileContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<FullAnalysis | null>(null);
  const [editedFileName, setEditedFileName] = useState<string>("");
  const [creativeName, setCreativeName] = useState<string>("");
  const [sourceLogEntry, setSourceLogEntry] = useState<LogEntry | null>(null);


  const [logEntries, setLogEntries] = useState<LogEntry[] | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);
  const [isHistoryVisible, setIsHistoryVisible] = useState<boolean>(false);

  const { status: gapiStatus, isSignedIn, error: gapiError, signIn, signOut, saveFile, getLogEntries, getGpxFileContent } = useGoogleDrive();

  const handleFileSelect = useCallback((file: File) => {
    setGpxFile(file);
    setAnalysisResult(null);
    setError(null);
    setEditedFileName("");
    setCreativeName("");
    setSourceLogEntry(null); // Clear editing state
  }, []);

  const handleAnalysisChange = useCallback((updates: Partial<FullAnalysis>) => {
    setAnalysisResult(prevResult => {
      if (!prevResult) return null;

      const newResult = { ...prevResult, ...updates };

      const typeCodeMap: { [key: string]: string } = { 'Road': 'R', 'Gravel': 'G', 'MTB': 'M', 'Hiking': 'H' };
      const typeCode = typeCodeMap[newResult.rideType] || 'X';
      const distance = Math.round(newResult.distance);
      const location = newResult.location.replace(/\s/g, '');
      const climbingCategory = newResult.climbingCategory;
      
      const climbingPart = (climbingCategory && climbingCategory !== "N/A") ? `-${climbingCategory}` : '';

      const newFileName = `${typeCode}-${distance}km-${creativeName}-${location}${climbingPart}.gpx`;

      newResult.suggestedFileName = newFileName;
      if (updates.rideType) {
        newResult.suggestedFolderPath = `${newResult.country}/${newResult.rideType}`;
      }
      
      setEditedFileName(newFileName);
      
      return newResult;
    });
  }, [creativeName]);

  const handleSaveToDrive = async () => {
    if (!analysisResult || !gpxFileContent) return;

    let mapImageData: string | undefined = undefined;
    try {
        const mapElement = document.getElementById('map-container');
        if (mapElement && typeof html2canvas !== 'undefined') {
            const canvas = await html2canvas(mapElement, { useCORS: true });
            mapImageData = canvas.toDataURL('image/png');
        }
    } catch (e) {
        console.error("Could not capture map image:", e);
    }

    setIsSaving(true);
    setError(null);
    try {
      await saveFile({
        folderPath: analysisResult.suggestedFolderPath,
        fileName: editedFileName,
        fileContent: gpxFileContent,
        mimeType: 'application/gpx+xml',
        analysisData: analysisResult,
        mapImageData: mapImageData,
        sourceLogEntry: sourceLogEntry,
      });
      setSourceLogEntry(null); // Clear editing state after successful save
      // After saving, refresh the log entries
      fetchLogEntries();
    } catch (err) {
      setError(err instanceof Error ? `Failed to save to Google Drive: ${err.message}` : "An unknown error occurred while saving.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadRouteFromHistory = async (entry: LogEntry) => {
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    setGpxFile(null);
    setSourceLogEntry(null);

    try {
      const gpxContent = await getGpxFileContent(entry.folderPath, entry.fileName);
      setGpxFileContent(gpxContent);

      const gpxData = parseGPXFile(gpxContent, entry.fileName);
      
      const loadedAnalysis: FullAnalysis = {
        ...gpxData,
        rideType: entry.rideType,
        surfaceType: entry.surface,
        lengthCategory: entry.length,
        climbingCategory: entry.climbing,
        location: entry.location,
        country: entry.folderPath.split('/')[0] || '',
        countryCode: '',
        suggestedFolderPath: entry.folderPath,
        suggestedFileName: entry.fileName,
        wayTypes: [], // Not stored in log, will be empty
        surfaces: [], // Not stored in log, will be empty
        sourceLogEntry: entry, // Link the original log entry to the analysis
      };

      setAnalysisResult(loadedAnalysis);
      setEditedFileName(entry.fileName);
      setSourceLogEntry(entry); // Set the source entry for editing logic

      const fileNameParts = entry.fileName.split('-');
      if (fileNameParts.length > 2) {
        setCreativeName(fileNameParts[2]);
      } else {
        setCreativeName('route');
      }

    } catch (err) {
        setError(err instanceof Error ? `Failed to load route: ${err.message}` : 'An unknown error occurred while loading.');
    } finally {
        setIsLoading(false);
    }
  };

  const fetchLogEntries = useCallback(async () => {
    if (!isSignedIn) return;
    setIsHistoryLoading(true);
    try {
      const entries = await getLogEntries();
      setLogEntries(entries);
    } catch (error) {
      console.error("Failed to fetch log entries", error);
    } finally {
      setIsHistoryLoading(false);
    }
  }, [isSignedIn, getLogEntries]);

  useEffect(() => {
    if (isSignedIn) {
      fetchLogEntries();
    } else {
      setLogEntries(null);
    }
  }, [isSignedIn, fetchLogEntries]);

  useEffect(() => {
    const processFile = async () => {
      if (!gpxFile) return;

      setIsLoading(true);
      setError(null);
      setAnalysisResult(null);

      try {
        const gpxContent = await gpxFile.text();
        setGpxFileContent(gpxContent);

        const gpxData = parseGPXFile(gpxContent, gpxFile.name);
        const geminiAnalysis = await getRouteAnalysis(gpxData, gpxContent);
        
        setAnalysisResult({ ...gpxData, ...geminiAnalysis });
        setEditedFileName(geminiAnalysis.suggestedFileName);

        const fileNameParts = geminiAnalysis.suggestedFileName.split('-');
        if (fileNameParts.length > 2) {
          setCreativeName(fileNameParts[2]);
        } else {
          setCreativeName('route');
        }

      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };

    processFile();
  }, [gpxFile]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-sans flex flex-col items-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-3xl mx-auto">
        <header className="mb-8">
            <div className="flex justify-between items-start">
                <div className="text-left">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white">
                        GPX Route <span className="text-brand-primary">Organizer</span>
                    </h1>
                    <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">
                        Intelligently analyze, classify, and rename your cycling route files.
                    </p>
                </div>
                <div className="flex-shrink-0 mt-2">
                    <GoogleDriveManager
                        status={gapiStatus}
                        isSignedIn={isSignedIn}
                        onSignIn={signIn}
                        onSignOut={signOut}
                    />
                </div>
            </div>
        </header>

        <main className="space-y-6">
          { gapiStatus === 'ERROR' && (
              <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg relative" role="alert">
                <strong className="font-bold">Google Drive Error: </strong>
                <span className="block sm:inline">{gapiError?.message || 'The Google Drive integration failed to load.'}</span>
              </div>
            )
          }

          <FileUpload onFileSelect={handleFileSelect} disabled={isLoading} />

          {isSignedIn && (
            <div className="flex justify-center">
                <button
                    onClick={() => setIsHistoryVisible(prev => !prev)}
                    className="w-full max-w-sm text-slate-600 dark:text-slate-300 font-bold py-3 px-4 rounded-lg transition duration-300 ease-in-out flex items-center justify-center space-x-2 hover:bg-slate-100 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 border border-slate-200 dark:border-slate-700"
                >
                    <HistoryIcon className="h-5 w-5" />
                    <span>{isHistoryVisible ? 'Hide History' : 'Show History'}</span>
                </button>
            </div>
           )}

          {isSignedIn && isHistoryVisible && (
              <RouteHistory
                  entries={logEntries}
                  isLoading={isHistoryLoading}
                  onLoadRoute={handleLoadRouteFromHistory}
              />
          )}
          
          {isLoading && (
            <div className="bg-white dark:bg-slate-800 p-8 rounded-xl shadow-lg flex flex-col items-center">
              <Spinner />
              <p className="mt-4 text-slate-600 dark:text-slate-300 font-medium">Analyzing your route... this may take a moment.</p>
            </div>
          )}

          {error && (
            <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg relative" role="alert">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {analysisResult && gpxFileContent && (
            <div className="space-y-6">
              <AnalysisResult
                result={analysisResult}
                fileName={editedFileName}
                gpxContent={gpxFileContent}
                onFileNameChange={setEditedFileName}
                onAnalysisChange={handleAnalysisChange}
                onSaveToDrive={handleSaveToDrive}
                isSaving={isSaving}
                isSignedIn={isSignedIn}
              />
            </div>
          )}
        </main>

        <footer className="text-center mt-12 text-sm text-slate-500 dark:text-slate-400">
            <p>Powered by React, Tailwind CSS, and Gemini</p>
            <p>Version 1.5.3</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
