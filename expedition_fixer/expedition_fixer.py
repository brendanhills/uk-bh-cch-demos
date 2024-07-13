import gpxpy
import geopy.distance
from weather_openmeteo import getWeatherForLocation, getTempForTime
import argparse

# Load a GPX file
def readOriginalGPX(input_file):
    with open(input_file, 'r') as f:
        gpx_orig = gpxpy.parse(f)
    return gpx_orig

#create temp extension element
def createGpxtpxExtension(mod_etree, temp): 
    extension_element = mod_etree.Element(f'gpxtpx:TrackPointExtension')
    atemp_elememt = mod_etree.SubElement(extension_element, f'gpxtpx:atemp')
    atemp_elememt.text = f'{temp}'
    #extension_element.append(atemp_elememt)
    return extension_element


# Create a new GPX file
def createNewGPX(gpx_orig, output_file):

    try:
        # Load LXML or fallback to cET or ET 
        import lxml.etree as mod_etree  # type: ignore
    except:
        try:
            import xml.etree.cElementTree as mod_etree # type: ignore
        except:
            import xml.etree.ElementTree as mod_etree # type: ignore 

  

    # Create an empty GPX:
    gpx_compressed = gpxpy.gpx.GPX()

    #copy the header from the original
    gpx_compressed.name = gpx_orig.name
    gpx_compressed.description = gpx_orig.description 
    gpx_compressed.author_name = gpx_orig.author_name
    gpx_compressed.author_email = gpx_orig.author_email
    gpx_compressed.author_link = gpx_orig.author_link
    gpx_compressed.keywords = gpx_orig.keywords
    gpx_compressed.creator = gpx_orig.creator
    gpx_compressed.version = gpx_orig.version
    gpx_compressed.extensions = gpx_orig.extensions
    gpx_compressed.nsmap = gpx_orig.nsmap

    first_location = (gpx_orig.tracks[0].segments[0].points[0].latitude, gpx_orig.tracks[0].segments[0].points[0].longitude)
    start_date = gpx_orig.tracks[0].segments[0].points[0].time
    end_date = gpx_orig.tracks[-1].segments[-1].points[-1].time
    print(f'First location: {first_location}')
    print(f'Start date: {start_date}')
    print(f'End date: {end_date}')

    weather = getWeatherForLocation(first_location[0], first_location[1], start_date, end_date )
    print(f'{weather}')

    # Create first track in our GPX:
    gpx_compressed_track = gpxpy.gpx.GPXTrack()
    gpx_compressed_track.name = gpx_orig.tracks[0].name
    gpx_compressed_track.description = gpx_orig.tracks[0].description
    gpx_compressed_track.type = gpx_orig.tracks[0].type
    gpx_compressed.tracks.append(gpx_compressed_track)
    # Create first segment in our GPX track:
    gpx_compressed_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_compressed_track.segments.append(gpx_compressed_segment)
    #TODO: create a segment per day...

    last_point = None
    kept_point_count = 0

    for orig_track in gpx_orig.tracks:
        for orig_segment in orig_track.segments:
            for orig_point in orig_segment.points:
                if last_point is None:
                    last_point = orig_point
                    continue  
                if orig_point.time.second % 5 == 0:  #only keep 1/x of points
                    distance_since_last = geopy.distance.geodesic((last_point.latitude, last_point.longitude), (orig_point.latitude, orig_point.longitude)).meters
                    #print(f'distance {round(distance_since_last,2)}m speed = {round(distance_since_last/5,2)}m/s,  ')
                    if distance_since_last > 2: #only add if we have moved more than y metres
                        print(f'Added point at {orig_point.time} distance {round(distance_since_last,2)}m speed = {round(distance_since_last/5*3.6,2)}km/h ')
                        temp = getTempForTime(orig_point.time, weather)
                        orig_point.extensions.append(createGpxtpxExtension(mod_etree, temp))
                    
                        gpx_compressed_segment.points.append(orig_point)      
                        kept_point_count += 1  
                        last_point = orig_point

    dropped_point_count = orig_segment.points.__len__() - kept_point_count 
                
    print(f'Created GPX: {gpx_compressed.to_xml()}')
    print(f'{kept_point_count} points')
    print(f'{dropped_point_count} points dropped')
    with open(output_file, 'w') as f:
        f.write(gpx_compressed.to_xml())



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input", help = "input filename")
    parser.add_argument("-o","--output", help = "output filename")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    gpx_orig = readOriginalGPX(input_file)
    createNewGPX(gpx_orig, output_file)


if __name__ == '__main__':
    main()