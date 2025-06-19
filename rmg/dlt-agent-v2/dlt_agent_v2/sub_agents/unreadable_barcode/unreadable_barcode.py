def unreadable_barcode_surcharge(data: str) -> str:

    try:
        # Parse the input data
        if isinstance(data, str):
            data_list = json.loads(data)
        else:
            data_list = data

        results = []
        for row in data_list:
            surcharge_reason = ""
            if row.get("SurchargeableUnreadableBarcode", 0) == 1:
                surcharge_reason += "Unreadable barcode detected. "
            if not surcharge_reason:
                surcharge_reason = "No flags set."

            concatenated_postcode = str(row.get("TwoDDestinationPostcode", "")) + str(
                row.get("TwoDDestinationPostcodeSector", ""))
            results.append({
                "AccountNumber": row.get("AccountNumber"),
                "SurchargeReason": surcharge_reason,
                "ConcatenatedPostcode": concatenated_postcode,
            })
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})