// This will be on the window object after the scripts are loaded.
declare const google: any;
import type { FullAnalysis, LogEntry } from '../types';

const CLIENT_ID = process.env.GOOGLE_CLIENT_ID || '1010302896033-2o04vo34r0pi6logvjfa7jmss3ss01v8.apps.googleusercontent.com';

const SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets';
const LOG_SPREADSHEET_NAME = 'GPX Route Organizer Log';
const ROOT_FOLDER_NAME = 'GPX Routes';
const LOG_SHEET_ID_KEY = 'gpxOrganizerLogSheetId';

export type GapiStatus = 'IDLE' | 'LOADING' | 'READY' | 'ERROR';

export interface GapiState {
    status: GapiStatus;
    isSignedIn: boolean | null;
    error: Error | null;
}

interface SaveFileParams {
    folderPath: string;
    fileName: string;
    fileContent: string;
    mimeType: string;
    analysisData: FullAnalysis;
    mapImageData?: string;
    sourceLogEntry?: LogEntry | null;
}

type StateListener = (newState: GapiState) => void;

class GoogleApiService {
    private state: GapiState = {
        status: 'IDLE',
        isSignedIn: null,
        error: null,
    };
    private listeners: Set<StateListener> = new Set();
    private tokenClient: any = null;
    private isInitialized = false;
    private accessToken: string | null = null;
    private logSpreadsheetId: string | null = null;
    private folderIdCache: Map<string, string> = new Map();

    constructor() {
        this.handleGisLoaded = this.handleGisLoaded.bind(this);
        this.signIn = this.signIn.bind(this);
        this.signOut = this.signOut.bind(this);
        this.saveFile = this.saveFile.bind(this);
        this.getLogEntries = this.getLogEntries.bind(this);
        this.getGpxFileContent = this.getGpxFileContent.bind(this);
    }

    public subscribe(listener: StateListener): void {
        this.listeners.add(listener);
        listener(this.state);
    }

    public unsubscribe(listener: StateListener): void {
        this.listeners.delete(listener);
    }

    private notify(): void {
        this.listeners.forEach(listener => listener(this.state));
    }

    private setState(newState: Partial<GapiState>): void {
        this.state = { ...this.state, ...newState };
        this.notify();
    }

    public getState(): GapiState {
        return this.state;
    }

    public initialize(): void {
        if (this.isInitialized) return;
        this.isInitialized = true;
        this.setState({ status: 'LOADING' });

        if (!CLIENT_ID) {
            console.error("Google Client ID is not configured.");
            this.setState({ status: 'ERROR', error: new Error('Google Client ID not configured.') });
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.onload = this.handleGisLoaded;
        script.onerror = () => this.setState({ status: 'ERROR', error: new Error('Failed to load Google Identity Services.') });
        document.body.appendChild(script);
    }

    private handleGisLoaded(): void {
        try {
            this.tokenClient = google.accounts.oauth2.initTokenClient({
                client_id: CLIENT_ID,
                scope: SCOPES,
                callback: (tokenResponse: any) => {
                    if (tokenResponse.error) {
                        this.setState({ isSignedIn: false, error: new Error(tokenResponse.error_description || 'An error occurred during authentication.') });
                        return;
                    }
                    this.accessToken = tokenResponse.access_token;
                    this.setState({ isSignedIn: true });
                },
            });
            this.setState({ status: 'READY' });
            this.tokenClient.requestAccessToken({ prompt: '' });
        } catch (error) {
            this.setState({ status: 'ERROR', error: error instanceof Error ? error : new Error('GIS Client initialization failed.') });
        }
    }

    public signIn(): void {
        if (this.state.status !== 'READY' || !this.tokenClient) return;
        this.tokenClient.requestAccessToken({ prompt: 'consent' });
    }

    public signOut(): void {
        if (this.accessToken) {
            google.accounts.oauth2.revoke(this.accessToken, () => {});
            this.accessToken = null;
            localStorage.removeItem(LOG_SHEET_ID_KEY); // Clear stored ID
            this.logSpreadsheetId = null;
            this.folderIdCache.clear();
            this.setState({ isSignedIn: false });
        }
    }
    
    private async findOrCreateFolder(name: string, parentId: string): Promise<string> {
        const cacheKey = `${parentId}/${name}`;
        if (this.folderIdCache.has(cacheKey)) {
            return this.folderIdCache.get(cacheKey)!;
        }
    
        const query = `'${parentId}' in parents and name='${name}' and mimeType='application/vnd.google-apps.folder' and trashed=false`;
        const fields = 'files(id)';
        const listUrl = `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}&fields=${encodeURIComponent(fields)}`;
    
        const listResponse = await fetch(listUrl, { headers: { 'Authorization': `Bearer ${this.accessToken}` } });
        if (!listResponse.ok) throw new Error('Failed to list folders.');
        const listResult = await listResponse.json();
    
        if (listResult.files && listResult.files.length > 0) {
            this.folderIdCache.set(cacheKey, listResult.files[0].id);
            return listResult.files[0].id;
        }
    
        const fileMetadata = { name, mimeType: 'application/vnd.google-apps.folder', parents: [parentId] };
        const createResponse = await fetch(`https://www.googleapis.com/drive/v3/files?fields=id`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(fileMetadata),
        });
        if (!createResponse.ok) throw new Error('Failed to create folder.');
        const createResult = await createResponse.json();
        this.folderIdCache.set(cacheKey, createResult.id);
        return createResult.id;
    }
    
    private async getFolderIdByPath(path: string): Promise<string> {
        const folderNames = path.split('/').filter(name => name);
        let parentId = 'root';
    
        for (const folderName of folderNames) {
            parentId = await this.findOrCreateFolder(folderName, parentId);
        }
        return parentId;
    }

    private async findLogSheetId(): Promise<string | null> {
        if (this.logSpreadsheetId) return this.logSpreadsheetId;
    
        const storedId = localStorage.getItem(LOG_SHEET_ID_KEY);
        if (storedId) {
            const verifyUrl = `https://www.googleapis.com/drive/v3/files/${storedId}?fields=id,trashed`;
            const verifyResponse = await fetch(verifyUrl, { headers: { 'Authorization': `Bearer ${this.accessToken}` } });
            if (verifyResponse.ok) {
                const file = await verifyResponse.json();
                if (!file.trashed) {
                    this.logSpreadsheetId = storedId;
                    return storedId;
                }
            }
            localStorage.removeItem(LOG_SHEET_ID_KEY); // Clean up stale ID
        }
    
        try {
            const gpxRoutesFolderId = await this.getFolderIdByPath(ROOT_FOLDER_NAME);
            const query = `'${gpxRoutesFolderId}' in parents and name='${LOG_SPREADSHEET_NAME}' and mimeType='application/vnd.google-apps-spreadsheet' and trashed=false`;
            const searchUrl = `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}&fields=files(id)`;
            
            const searchResponse = await fetch(searchUrl, { headers: { 'Authorization': `Bearer ${this.accessToken}` } });
            if (!searchResponse.ok) return null;
            const searchResult = await searchResponse.json();
    
            if (searchResult.files && searchResult.files.length > 0) {
                const foundId = searchResult.files[0].id;
                this.logSpreadsheetId = foundId;
                localStorage.setItem(LOG_SHEET_ID_KEY, foundId);
                return this.logSpreadsheetId;
            }
            return null;
        } catch (error) {
            console.error("Error finding log sheet by search:", error);
            return null;
        }
    }

    public async getLogEntries(): Promise<LogEntry[]> {
        if (!this.state.isSignedIn) return [];

        const spreadsheetId = await this.findLogSheetId();
        if (!spreadsheetId) return [];

        const getUrl = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/Sheet1!A2:M`;
        const response = await fetch(getUrl, {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch log entries from Google Sheet.');
        }
        const result = await response.json();
        const rows = result.values || [];

        return rows.map((row: string[], index: number): LogEntry => ({
            rowIndex: index + 2, // Sheets are 1-indexed and we skip the header
            location: row[0] || '',
            rideType: row[1] || '',
            distance: row[2] || '',
            elevation: row[3] || '',
            surface: row[4] || '',
            length: row[5] || '',
            climbing: row[6] || '',
            folderPath: row[7] || '',
            fileName: row[8] || '',
            dateAdded: row[9] || '',
            mapImage: row[10] || '',
            fileId: row[11] || undefined,
            mapImageFileId: row[12] || undefined,
        })).reverse();
    }

    private async findFileInFolder(fileName: string, folderId: string): Promise<string | null> {
        const query = `'${folderId}' in parents and name='${fileName}' and trashed=false`;
        const listUrl = `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}&fields=files(id)`;

        const response = await fetch(listUrl, {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        if (!response.ok) throw new Error('Failed to search for file.');

        const result = await response.json();
        if (result.files && result.files.length > 0) {
            return result.files[0].id;
        }
        return null;
    }

    public async getGpxFileContent(folderPath: string, fileName: string): Promise<string> {
        if (!this.state.isSignedIn) throw new Error('Not signed in.');

        const fullFolderPath = `${ROOT_FOLDER_NAME}/${folderPath}`;
        const folderId = await this.getFolderIdByPath(fullFolderPath);
        const fileId = await this.findFileInFolder(fileName, folderId);

        if (!fileId) {
            throw new Error(`File "${fileName}" not found in Drive.`);
        }

        const downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
        const response = await fetch(downloadUrl, {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });

        if (!response.ok) {
            throw new Error('Failed to download GPX file from Drive.');
        }
        return await response.text();
    }
    
    private async findOrCreateLogSheet(): Promise<string> {
        const existingId = await this.findLogSheetId();
        if (existingId) return existingId;
    
        const gpxRoutesFolderId = await this.getFolderIdByPath(ROOT_FOLDER_NAME);
        
        const createSheetUrl = 'https://sheets.googleapis.com/v4/spreadsheets';
        const sheetMetadata = {
            properties: { title: LOG_SPREADSHEET_NAME }
        };
        const createSheetResponse = await fetch(createSheetUrl, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(sheetMetadata)
        });
        if (!createSheetResponse.ok) throw new Error('Failed to create log sheet using Sheets API.');
        const newSheet = await createSheetResponse.json();
        
        const fileId = newSheet.spreadsheetId;
        const moveUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?addParents=${gpxRoutesFolderId}&removeParents=root&fields=id`;
        const moveResponse = await fetch(moveUrl, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        if (!moveResponse.ok) console.error("Could not move log sheet to folder, it will remain in root.");
        
        this.logSpreadsheetId = fileId;
        localStorage.setItem(LOG_SHEET_ID_KEY, fileId);
    
        const headers = [['Location', 'Ride Type', 'Distance (km)', 'Elevation (m)', 'Surface', 'Length', 'Climbing', 'Folder Path', 'Filename', 'Date Added', 'Map Image', 'File ID', 'Map Image File ID']];
        const updateValuesUrl = `https://sheets.googleapis.com/v4/spreadsheets/${this.logSpreadsheetId}/values/Sheet1!A1?valueInputOption=RAW`;
        await fetch(updateValuesUrl, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${this.accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ values: headers })
        });
    
        return this.logSpreadsheetId;
    }

    private async appendToLogSheet(analysisData: FullAnalysis, fileName: string, fileId: string, mapImageUrl?: string, mapImageFileId?: string): Promise<void> {
        try {
            const spreadsheetId = await this.findOrCreateLogSheet();
            const newRow = [
                analysisData.location, analysisData.rideType, analysisData.distance,
                analysisData.elevationGain, analysisData.surfaceType, analysisData.lengthCategory,
                analysisData.climbingCategory, analysisData.suggestedFolderPath, fileName,
                new Date().toISOString(),
                mapImageUrl ? `=IMAGE("${mapImageUrl}", 1)` : '',
                fileId,
                mapImageFileId || ''
            ];

            const appendUrl = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/Sheet1!A1:append?valueInputOption=USER_ENTERED`;
            const response = await fetch(appendUrl, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.accessToken}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ values: [newRow] })
            });

            if (!response.ok) {
                 const errorBody = await response.json();
                 console.error('Failed to append row to Google Sheet:', errorBody);
            }
        } catch (error) {
            console.error('An error occurred while logging to Google Sheet:', error);
        }
    }

    private async deleteFile(fileId: string): Promise<void> {
        if (!fileId) return;
        const deleteUrl = `https://www.googleapis.com/drive/v3/files/${fileId}`;
        const response = await fetch(deleteUrl, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        if (!response.ok) {
            console.error(`Failed to delete file ${fileId}. Status: ${response.status}`);
        }
    }

    private async clearSheetRow(rowIndex: number): Promise<void> {
        const spreadsheetId = await this.findOrCreateLogSheet();
        const range = `Sheet1!A${rowIndex}:M${rowIndex}`;
        const clearUrl = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${range}:clear`;
        await fetch(clearUrl, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
    }

    public async saveFile({ folderPath, fileName, fileContent, mimeType, analysisData, mapImageData, sourceLogEntry }: SaveFileParams): Promise<void> {
        if (!this.state.isSignedIn || !this.accessToken) {
            throw new Error('You must be signed in to save files to Google Drive.');
        }

        try {
            // Step 1: Upload new files (map image first, then GPX)
            let newMapImageUrl: string | undefined;
            let newMapImageFileId: string | undefined;
            if (mapImageData) {
                const gpxRoutesFolderId = await this.getFolderIdByPath(ROOT_FOLDER_NAME);
                const mapImagesFolderId = await this.findOrCreateFolder('Map Images', gpxRoutesFolderId);
                const response = await fetch(mapImageData);
                const imageBlob = await response.blob();
                const imageFileName = `${fileName.replace('.gpx', '')}.png`;
                const imageMetadata = { name: imageFileName, parents: [mapImagesFolderId] };
                const imageFormData = new FormData();
                imageFormData.append('metadata', new Blob([JSON.stringify(imageMetadata)], { type: 'application/json' }));
                imageFormData.append('file', imageBlob, imageFileName);

                const imageUploadResponse = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${this.accessToken}` },
                    body: imageFormData,
                });

                if (imageUploadResponse.ok) {
                    const imageFile = await imageUploadResponse.json();
                    if (imageFile.id) {
                        newMapImageFileId = imageFile.id;
                        newMapImageUrl = `https://drive.google.com/uc?id=${newMapImageFileId}`;
                    }
                }
            }
            
            const fullFolderPath = `${ROOT_FOLDER_NAME}/${folderPath}`;
            const folderId = await this.getFolderIdByPath(fullFolderPath);

            const fileMetadata = { name: fileName, parents: [folderId] };
            const file = new Blob([fileContent], { type: mimeType });
            const formData = new FormData();
            formData.append('metadata', new Blob([JSON.stringify(fileMetadata)], { type: 'application/json' }));
            formData.append('file', file);
            
            const uploadResponse = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.accessToken}` },
                body: formData,
            });

            if (!uploadResponse.ok) {
                const errorBody = await uploadResponse.json();
                throw new Error(errorBody.error?.message || 'Failed to upload GPX file.');
            }
            const newGpxFile = await uploadResponse.json();
            const newGpxFileId = newGpxFile.id;

            // Step 2: If this is an update, delete the old files and log entry
            if (sourceLogEntry) {
                // Delete GPX file
                if (sourceLogEntry.fileId) {
                    await this.deleteFile(sourceLogEntry.fileId);
                } else {
                    console.warn('Old fileId not found in log, attempting to find by name...');
                    const oldFullFolderPath = `${ROOT_FOLDER_NAME}/${sourceLogEntry.folderPath}`;
                    const oldFolderId = await this.getFolderIdByPath(oldFullFolderPath);
                    const oldFileId = await this.findFileInFolder(sourceLogEntry.fileName, oldFolderId);
                    if (oldFileId) {
                        await this.deleteFile(oldFileId);
                    } else {
                        console.warn(`Could not find old file by name to delete: ${sourceLogEntry.fileName}`);
                    }
                }

                // Delete Map Image file
                if (sourceLogEntry.mapImageFileId) {
                    await this.deleteFile(sourceLogEntry.mapImageFileId);
                } else {
                    console.warn('Old mapImageFileId not found in log, attempting to find by name...');
                    const mapImageFileName = `${sourceLogEntry.fileName.replace('.gpx', '')}.png`;
                    const gpxRoutesFolderId = await this.getFolderIdByPath(ROOT_FOLDER_NAME);
                    const mapImagesFolderId = await this.findOrCreateFolder('Map Images', gpxRoutesFolderId);
                    const oldMapImageId = await this.findFileInFolder(mapImageFileName, mapImagesFolderId);
                    if (oldMapImageId) {
                        await this.deleteFile(oldMapImageId);
                    } else {
                         console.warn(`Could not find old map image by name to delete: ${mapImageFileName}`);
                    }
                }
                await this.clearSheetRow(sourceLogEntry.rowIndex);
            }

            // Step 3: Append the new record to the log
            await this.appendToLogSheet(analysisData, fileName, newGpxFileId, newMapImageUrl, newMapImageFileId);
            
        } catch (error: any) {
            console.error('Error saving file to Google Drive:', error);
            const message = error.message || 'An unknown error occurred while saving the file.';
            throw new Error(message);
        }
    }
}

const googleApiService = new GoogleApiService();
export default googleApiService;