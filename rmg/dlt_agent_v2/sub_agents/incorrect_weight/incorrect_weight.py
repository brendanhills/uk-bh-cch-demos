import json
import pandas as pd
from ..data.load_csv import load_parcel_data
from typing import List, Dict, Optional

def incorrect_weight_surcharge(data: List[Dict]) -> str:
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
            if row["IncorrectFormatDueToWeightOutOfTolerance"] == 1:
                reason = "Weight out of tolerance."
            else:
                reason = "weight is with in tolerance no need to surcharge."
            # Handle potential missing columns gracefully

            results.append({
                "AccountNumber": str(row.get("AccountNumber", "")),  # Ensure string type
                "Barcode": str(row.get("Barcode", "")),  # Ensure string type
                "AggregationKey": str(row.get("AggregationKey", "")),
                "TwoDBarcode": str(row.get("TwoDBarcode", "")),
                "CaseCreationDate": str(row.get("CaseCreationDate", "")),
                "CasePriority": str(row.get("CasePriority", "")),
                "CaseItemIdentifier": str(row.get("CaseItemIdentifier", "")),
                "DerivedFormatValueDescription": str(row.get("DerivedFormatValueDescription", "")),
                "PackageType": str(row.get("PackageType", "")),
                "SurchargeReason": reason,
            })
        print("results", results)
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})


def incorrect_weight_tool_wrapper(json_input: str) -> str:
    try:
        # Load the data using load_parcel_data
        parcel_json = load_parcel_data()

        # Check if load_parcel_data returned an error
        if "error" in json.loads(parcel_json):
            return parcel_json  # Return the error directly

        # Parse the JSON data
        data = json.loads(parcel_json)
        print("data", data)
        return incorrect_weight_surcharge(data)
    except json.JSONDecodeError as json_err:
        return json.dumps({"error": f"Invalid JSON input: {str(json_err)}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
