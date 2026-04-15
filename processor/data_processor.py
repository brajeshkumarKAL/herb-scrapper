def process_data(scraped_data):
    processed = []
    for main_name, records in scraped_data:
        if isinstance(records, str):
            processed.append({"Herb": main_name, "Phytochemical Associations": f"Error: {records}"})
            continue
        seen = {}
        for record in records:
            identifier = record.get("identifier", "")
            if not identifier:
                continue
            if identifier not in seen:
                seen[identifier] = record
        associations = " || ".join(
            " | ".join(
                [item.get(field, "").strip() for field in ["plant", "part", "identifier", "compound"]]
            )
            for item in seen.values()
        )
        processed.append({"Herb": main_name, "Phytochemical Associations": associations})
    return processed
