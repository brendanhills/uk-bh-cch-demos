import gpxpy
import re

import geopy.distance


with open('GOTOES_big.gpx', 'r') as f:
    gpx_orig = gpxpy.parse(f)

gpx_compressed = gpxpy.gpx.GPX()
# Create first track in our GPX:
gpx_compressed_track = gpxpy.gpx.GPXTrack()
gpx_compressed.tracks.append(gpx_compressed_track)
# Create first segment in our GPX track:
gpx_compressed_segment = gpxpy.gpx.GPXTrackSegment()
gpx_compressed_track.segments.append(gpx_compressed_segment)

last_point = None
kept_point_count = 0

for orig_track in gpx_orig.tracks:
    for orig_segment in orig_track.segments:
        for orig_point in orig_segment.points:
            if last_point is None:
                last_point = orig_point
                continue  
            if orig_point.time.second % 2 == 0:  #only keep 50% of points
                distance_since_last = geopy.distance.geodesic((last_point.latitude, last_point.longitude), (orig_point.latitude, orig_point.longitude)).meters
                print(f'distance {round(distance_since_last,2)}m speed = {round(distance_since_last/5,2)}m/s,  ')
                if distance_since_last > 5: #only add if we have moved more than 5 metres
                    print(f'Added point at {orig_point.time} distance {round(distance_since_last,2)}m speed = {round(distance_since_last/5*3.6,2)}km/h ')
                    gpx_compressed_segment.points.append(orig_point)      
                    kept_point_count += 1  
                    last_point = orig_point

dropped_point_count = orig_segment.points.__len__() - kept_point_count 
               
print('Created GPX:', gpx_compressed.to_xml())
print(f'{kept_point_count} points')
print(f'{dropped_point_count} points dropped')
with open('GOTOES_big_compressed.gpx', 'w') as f:
    f.write(gpx_compressed.to_xml())