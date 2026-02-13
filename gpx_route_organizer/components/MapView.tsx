import React, { useEffect, useRef, useMemo } from 'react';
import { extractTrackPoints } from '../services/gpxParser';

declare const L: any;

interface MapViewProps {
  gpxContent: string;
}

const MapView: React.FC<MapViewProps> = ({ gpxContent }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const featureGroupRef = useRef<any>(null);

  const trackPoints = useMemo(() => extractTrackPoints(gpxContent), [gpxContent]);

  // Effect for initializing and cleaning up the map instance
  useEffect(() => {
    if (typeof L !== 'undefined' && mapContainerRef.current && !mapRef.current) {
      // Fix for default icon issue with module bundlers.
      // This is moved inside the effect to ensure L is defined before we modify it.
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });
      
      mapRef.current = L.map(mapContainerRef.current);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(mapRef.current);
      
      featureGroupRef.current = L.featureGroup().addTo(mapRef.current);
    }
    
    // Cleanup function to run when component unmounts
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []); // Empty dependency array means this runs once on mount and cleanup on unmount

  // Effect for updating map layers when track points change
  useEffect(() => {
    if (mapRef.current && featureGroupRef.current && trackPoints.length > 0) {
      const fg = featureGroupRef.current;
      fg.clearLayers(); // Clear previous route layers

      const polyline = L.polyline(trackPoints, { color: '#0ea5e9', weight: 4 });
      fg.addLayer(polyline);

      // Define custom icons
      const greenIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });

      const redIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });

      // Add markers with custom colors
      const startPoint = trackPoints[0];
      fg.addLayer(L.marker(startPoint, { icon: greenIcon }).bindPopup('<b>Route Start</b>'));
      
      if(trackPoints.length > 1) {
          const endPoint = trackPoints[trackPoints.length - 1];
          fg.addLayer(L.marker(endPoint, { icon: redIcon }).bindPopup('<b>Route End</b>'));
      }
      
      // Zoom to fit the new route
      mapRef.current.fitBounds(fg.getBounds().pad(0.1));
    }
  }, [trackPoints]); // This effect re-runs whenever trackPoints change

  if (trackPoints.length === 0) {
    return null;
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-4">Route Map</h3>
      <div id="map-container" ref={mapContainerRef} className="h-64 md:h-80 w-full rounded-lg shadow-md z-0" />
    </div>
  );
};

export default MapView;