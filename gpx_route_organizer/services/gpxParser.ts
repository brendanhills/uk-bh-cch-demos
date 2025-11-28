import { haversineDistance } from '../utils/haversine';
import type { GPXData } from '../types';

export type TrackPoint = [number, number]; // [lat, lon]

export function extractTrackPoints(gpxContent: string): TrackPoint[] {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(gpxContent, "application/xml");
  
  const errorNode = xmlDoc.querySelector("parsererror");
  if (errorNode) {
    console.error("Failed to parse GPX for map points.");
    return [];
  }
  
  const trackPoints = Array.from(xmlDoc.querySelectorAll("trkpt"));
  
  if (trackPoints.length === 0) {
    return [];
  }
  
  return trackPoints
    .map(pt => {
      const latStr = pt.getAttribute('lat');
      const lonStr = pt.getAttribute('lon');
      if (latStr && lonStr) {
        const lat = parseFloat(latStr);
        const lon = parseFloat(lonStr);
        if (!isNaN(lat) && !isNaN(lon)) {
          return [lat, lon] as TrackPoint;
        }
      }
      return null;
    })
    .filter((p): p is TrackPoint => p !== null);
}

export function parseGPXFile(gpxContent: string, fileName: string): GPXData {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(gpxContent, "application/xml");

  const errorNode = xmlDoc.querySelector("parsererror");
  if (errorNode) {
    throw new Error("Failed to parse GPX file.");
  }

  const routeName = xmlDoc.querySelector("metadata > name")?.textContent || fileName.replace('.gpx', '');
  const trackPoints = Array.from(xmlDoc.querySelectorAll("trkpt"));

  if (trackPoints.length === 0) {
    throw new Error("No track points found in the GPX file.");
  }
  
  let startLat: number | undefined = undefined;
  let startLon: number | undefined = undefined;
  let totalDistance = 0;
  let totalElevationGain = 0;
  let duration = 0;

  let lastLat: number | null = null;
  let lastLon: number | null = null;
  let lastEle: number | null = null;
  
  const timeNodes = Array.from(xmlDoc.querySelectorAll("trkpt > time"));
  if (timeNodes.length > 1) {
    const startTime = new Date(timeNodes[0].textContent || '');
    const endTime = new Date(timeNodes[timeNodes.length - 1].textContent || '');
    if (!isNaN(startTime.getTime()) && !isNaN(endTime.getTime())) {
      duration = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60); // duration in hours
    }
  }


  trackPoints.forEach(pt => {
    const latStr = pt.getAttribute('lat');
    const lonStr = pt.getAttribute('lon');

    if (!latStr || !lonStr) return; 

    const lat = parseFloat(latStr);
    const lon = parseFloat(lonStr);
    
    if (isNaN(lat) || isNaN(lon)) return; 

    if (startLat === undefined) {
      startLat = lat;
      startLon = lon;
    }

    const eleEl = pt.querySelector('ele');
    const ele = eleEl?.textContent ? parseFloat(eleEl.textContent) : null;

    if (lastLat !== null && lastLon !== null) {
      totalDistance += haversineDistance(lastLat, lastLon, lat, lon);
    }
    
    if (ele !== null && !isNaN(ele) && lastEle !== null) {
      const eleDiff = ele - lastEle;
      if (eleDiff > 0) {
        totalElevationGain += eleDiff;
      }
    }

    lastLat = lat;
    lastLon = lon;
    if (ele !== null && !isNaN(ele)) {
      lastEle = ele;
    }
  });

  return {
    name: routeName,
    distance: parseFloat(totalDistance.toFixed(2)),
    elevationGain: parseFloat(totalElevationGain.toFixed(2)),
    duration: parseFloat(duration.toFixed(2)),
    startLat,
    startLon,
  };
}