import json
import pandas as pd
from typing import List, Dict, Optional
from ..data.load_csv import load_parcel_data

def incorrect_format_surcharge(data: List[Dict]) -> str:
    try:
        df = pd.DataFrame(data)
        print("processed_data", df)
        required_columns = ["AccountNumber",
                   "Barcode",
                   "AggregationKey",
                   "ReasonForIncorrectFormat",
                   "TwoDBarcode",
                   "CaseCreationDate",
                   "CasePriority",
                   "IncorrectFormatOutOfTolerance",
                   "IncorrectFormatDueToWeightOutOfTolerance",
                   "CaseItemIdentifier",
                   "DerivedFormatValueDescription",
                   "PackageType"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return json.dumps({"error": f"Missing columns: {missing_columns}"})
        results = []
        for _, row in df.iterrows():
                results.append({
                "AccountNumber": str(row.get("AccountNumber", "")),  # Ensure string type
                "Barcode": str(row.get("Barcode", "")),  # Ensure string type
                "AggregationKey" : str(row.get("AggregationKey", "")),
                "ReasonForIncorrectFormat": str(row.get("ReasonForIncorrectFormat", "")),
                "TwoDBarcode":  str(row.get("TwoDBarcode", "")),
                "CaseCreationDate": str(row.get("CaseCreationDate", "")),
                "CasePriority": str(row.get("CasePriority", "")),
                "IncorrectFormatOutOfTolerance": row.get("IncorrectFormatOutOfTolerance"),
                "IncorrectFormatDueToWeightOutOfTolerance": row.get("IncorrectFormatDueToWeightOutOfTolerance"),
                "CaseItemIdentifier": str(row.get("CaseItemIdentifier", "")),
                "DerivedFormatValueDescription": str(row.get("DerivedFormatValueDescription", "")),
                "PackageType": str(row.get("PackageType", "")),
            })
        # print("*********results**********\n\n", results)
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})



def incorrect_format_tool_wrapper(json_input: str) -> str:
    try:
        # Load the data using load_parcel_data
        parcel_json = load_parcel_data()

        # Check if load_parcel_data returned an error
        if "error" in json.loads(parcel_json):
            return parcel_json  # Return the error directly

        # Parse the JSON data
        data = json.loads(parcel_json)
        # print("*********data\n\n*********", data)
        return incorrect_format_surcharge(data)
    except json.JSONDecodeError as json_err:
        return json.dumps({"error": f"Invalid JSON input: {str(json_err)}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})


# incorrect_format_tool_wrapper(load_parcel_data)