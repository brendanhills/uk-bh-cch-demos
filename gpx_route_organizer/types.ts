export interface GPXData {
  name: string;
  distance: number; // in kilometers
  elevationGain: number; // in meters
  duration: number; // in hours
  startLat?: number;
  startLon?: number;
}

export interface SurfaceBreakdownItem {
  name:string;
  distance: number; // in kilometers
}

export interface AnalysisResult {
  rideType: string;
  surfaceType: string;
  lengthCategory: string;
  climbingCategory: string;
  location: string;
  country: string;
  countryCode: string;
  suggestedFolderPath: string;
  suggestedFileName: string;
  wayTypes: SurfaceBreakdownItem[];
  surfaces: SurfaceBreakdownItem[];
}

export interface FullAnalysis extends GPXData, AnalysisResult {
  sourceLogEntry?: LogEntry | null;
}

export interface LogEntry {
  rowIndex: number;
  location: string;
  rideType: string;
  distance: string;
  elevation: string;
  surface: string;
  length: string;
  climbing: string;
  folderPath: string;
  fileName: string;
  dateAdded: string;
  mapImage: string;
  fileId?: string;
  mapImageFileId?: string;
}