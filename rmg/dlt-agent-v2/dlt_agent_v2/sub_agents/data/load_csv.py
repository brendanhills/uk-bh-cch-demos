import pandas as pd
import os
import json

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "data_agents.csv")
#CSV_FILE_PATH=r".\data_agents_2.csv"
# CSV_FILE_PATH = "data_agents.csv"

def load_parcel_data() -> str:
    print(f"Reading date file {CSV_FILE_PATH}")
    # print("Starting load_parcel_data")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        #print("five rows of data", df.head())
        columns = ["AccountNumber",
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
        df = df[columns]
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        #print("*******data**********", df.head())
        if df.empty:
            raise ValueError("No data loaded from csv")
        parcel_data_records = df.to_dict(orient="records")
        parcel_json = json.dumps(parcel_data_records)
        # print("parcel_json\n", parcel_json)
        return parcel_json
    except FileNotFoundError:
        # print(f"Error: File not found at {CSV_FILE_PATH}")
        return json.dumps({"error": f"File not found at {CSV_FILE_PATH}"})
    except ValueError as ve:
        print(f"Error: {ve}")
        return json.dumps({"error": str(ve)})
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return json.dumps({"error": str(e)})


# load_parcel_data()


