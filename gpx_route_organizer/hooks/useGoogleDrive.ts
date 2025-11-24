import { useState, useEffect } from 'react';
import googleApiService, { GapiState } from '../services/googleApiService';

export const useGoogleDrive = () => {
    const [gapiState, setGapiState] = useState<GapiState>(googleApiService.getState());

    useEffect(() => {
        // Initialize the service if it hasn't been started yet.
        // This is safe to call multiple times.
        googleApiService.initialize();

        const handleStateChange = (newState: GapiState) => {
            setGapiState(newState);
        };

        // Subscribe to state changes from the service
        googleApiService.subscribe(handleStateChange);

        // Unsubscribe on component unmount
        return () => {
            googleApiService.unsubscribe(handleStateChange);
        };
    }, []);

    return {
        ...gapiState,
        signIn: googleApiService.signIn,
        signOut: googleApiService.signOut,
        saveFile: googleApiService.saveFile, // This now handles both save and update
        getLogEntries: googleApiService.getLogEntries,
        getGpxFileContent: googleApiService.getGpxFileContent,
    };
};