import { GoogleGenAI, Type } from "@google/genai";
import type { GPXData, AnalysisResult } from '../types';

// FIX: The API key must be retrieved from the environment variable `process.env.API_KEY`.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const analysisSchema = {
  type: Type.OBJECT,
  properties: {
    rideType: { type: Type.STRING, description: "The primary activity type (e.g., Road, Gravel, MTB, Hiking)." },
    surfaceType: { type: Type.STRING, description: "The primary surface type of the ride (e.g., Paved, Mixed, Dirt)." },
    lengthCategory: { type: Type.STRING, description: "Classification of the ride's length." },
    climbingCategory: { type: Type.STRING, description: "Classification of the ride's climbing (e.g., Pan-flat, Rolling, Hilly, Mountainous)." },
    location: { type: Type.STRING, description: "The closest major city or well-known region for the ride." },
    country: { type: Type.STRING, description: "The country where the route is located (e.g., United Kingdom, Spain)." },
    countryCode: { type: Type.STRING, description: "The 2 or 3 letter ISO 3166-1 alpha-2 or alpha-3 country code (e.g., GB, ESP)." },
    suggestedFolderPath: { type: Type.STRING, description: "A suggested folder path, combining the full country name and ride type (e.g., 'Spain/Road')." },
    suggestedFileName: { type: Type.STRING, description: "A strategically generated filename for the route." },
    wayTypes: {
      type: Type.ARRAY,
      description: "Breakdown of distances for different way types found on the route.",
      items: {
        type: Type.OBJECT,
        properties: {
          name: { type: Type.STRING, description: "Name of the way type (e.g., Road, Path, Singletrack)." },
          distance: { type: Type.NUMBER, description: "Distance in kilometers for this way type." }
        },
        required: ["name", "distance"],
      }
    },
    surfaces: {
        type: Type.ARRAY,
        description: "Breakdown of distances for different surface types found on the route.",
        items: {
          type: Type.OBJECT,
          properties: {
            name: { type: Type.STRING, description: "Name of the surface type (e.g., Asphalt, Gravel, Paved)." },
            distance: { type: Type.NUMBER, description: "Distance in kilometers for this surface type." }
          },
          required: ["name", "distance"],
        }
      },
  },
  required: ["rideType", "surfaceType", "lengthCategory", "climbingCategory", "location", "country", "countryCode", "suggestedFolderPath", "suggestedFileName", "wayTypes", "surfaces"],
};

export async function getRouteAnalysis(gpxData: GPXData, gpxContent: string): Promise<AnalysisResult> {
  const { name, distance, elevationGain, duration, startLat, startLon } = gpxData;
  const climbingMetersPerKm = distance > 0 ? elevationGain / distance : 0;
  const averageSpeed = duration > 0 ? distance / duration : 0; // km/h

  const locationDataPrompt = startLat && startLon 
    ? `- Start Coordinates: Lat ${startLat.toFixed(5)}, Lon ${startLon.toFixed(5)}`
    : '';
    
  const locationInstruction = startLat && startLon
    ? `1.  **Location & Country:** Based on the start coordinates, identify the closest town/village, the country it's in, and its 2-3 letter ISO country code.`
    : `1.  **Location & Country:** Identify the closest major population center, its country, and its 2-3 letter ISO country code from the route name.`;

  const prompt = `
You are an expert cycling and hiking route analyst. Based on the following GPX file data and its full XML content, provide a detailed analysis.
The file name or route name might contain clues about the location and type of activity.

**Route Data:**
- Name: "${name}"
- Total Distance: ${distance.toFixed(1)} km
- Total Elevation Gain: ${elevationGain.toFixed(0)} meters
- Average Speed: ${averageSpeed.toFixed(1)} km/h
${locationDataPrompt}
- Climbing Ratio: ${climbingMetersPerKm.toFixed(1)} m/km

**Analysis Instructions:**
${locationInstruction}
2.  **Activity Type & Surface:** Infer the most likely activity type (Road, MTB, Gravel, Hiking) and overall surface type (Paved, Dirt, Mixed).
    - **A key indicator is the average speed.** Speeds below 6 km/h strongly suggest hiking. Speeds above 8 km/h are more typical for biking. Use this as a primary factor.
    - Also consider keywords in the route name (e.g., "hike", "walk", "ride").
3.  **Length Category:** Classify the length using these rules:
    - Short: < 30km
    - Medium: 30-69km
    - Medium-Long: 70-99km
    - Long: 100-200km
    - Multi-Day: > 200km
4.  **Climbing Category:** Classify the climbing difficulty using the 'Climbing Ratio (m/km)' value. Choose one of the following category names based on these rules:
    - Pan-flat: 0–4 m/km (Totally flat. Think time trial courses, Dutch countryside, or beach roads.)
    - Flat: 5–9 m/km (Still very gentle. You’ll barely notice the elevation. Ideal for base miles or recovery rides.)
    - Rolling: 10–14 m/km (Gently undulating terrain. You’re shifting gears more often, but not really climbing.)
    - Lumpy: 15–19 m/km (Starts to bite. Repeated short climbs and descents. No big mountains, but no rest.)
    - Hilly: 20–29 m/km (Frequent climbs, possibly steeper or more sustained. Could be punchy or grindy.)
    - Mountainous: 30+ m/km (Big climbing territory. Long, sustained ascents or relentless climbing all day.)
5.  **Folder Path:** Suggest a folder path. It should be in the format 'CountryName/ActivityType' (e.g., 'United Kingdom/Gravel', 'Switzerland/Hiking'). Use the full country name you identified in step 1.
6.  **File Name:** Generate a new, strategic filename with hyphens as separators. The structure is: [TypeCode]-[Distance]km-[CreativeName]-[Location]-[Climbing]. The final name should end with ".gpx".
    - **Type Code:** A single letter: "G" for Gravel, "M" for MTB, "R" for Road, "H" for Hiking.
    - **Distance:** The total distance, rounded to the nearest whole number, followed by "km" (e.g., "${Math.round(distance)}km").
    - **CreativeName:** Create a short, fun, and descriptive name for the activity based on the original name ("${name}") and the route data. It should be a logical combination that captures the essence of the route. Use underscores instead of spaces.
    - **Location:** The identified location (no spaces).
    - **Climbing:** The climbing category you determined in step 4 (e.g., "Pan-flat", "Rolling", "Hilly", "Mountainous").
    Example for an original name of "My Awesome Ride" that is a hilly road ride in Mallorca: "R-125km-Mallorca_Climb_Fest-Mallorca-Hilly.gpx".
7.  **Way Types & Surfaces Breakdown:** Analyze the provided full GPX track data to break down the route into different way types (e.g., Road, Path, Singletrack, Street, State Road, Cycleway) and surface types (e.g., Paved, Unpaved, Asphalt, Gravel). For each category (Way Types, Surfaces), provide an array of the types found and the total distance in kilometers for each. Sort each array by distance descending. The sum of distances for each breakdown should roughly equal the total route distance.

Return your analysis as a single, valid JSON object that adheres to the provided schema.

**Full GPX Data:**
\`\`\`xml
${gpxContent.substring(0, 100000)}
\`\`\`
`;
  
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
      },
    });

    const jsonString = response.text.trim();
    return JSON.parse(jsonString) as AnalysisResult;

  } catch (error) {
    console.error("Error calling Gemini API:", error);
    throw new Error("Failed to get analysis from Gemini API. Please check your API key and network connection.");
  }
}