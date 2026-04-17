def process_data(scraped_data):
    """
    Process scraped data from dict format {query: associations} to cleaned format.
    Removes invalid records and ensures data consistency.
    """
    processed_data = {}
    
    for query, associations in scraped_data.items():
        if isinstance(associations, str):
            # Error case - skip this query
            continue
            
        # Filter out invalid associations
        valid_associations = []
        for assoc in associations:
            if not isinstance(assoc, dict):
                continue

            # Map old field names to the new website-matching keys for compatibility
            herb_value = assoc.get("Indian medicinal plant") or assoc.get("herb") or ""
            part_value = assoc.get("Plant part") or assoc.get("part") or ""
            identifier_value = assoc.get("IMPPAT Phytochemical identifier") or assoc.get("imphy_id") or ""
            compound_value = assoc.get("Phytochemical name") or assoc.get("phytochemical") or ""
            references_value = assoc.get("References") or assoc.get("references") or ""
            query_used_value = assoc.get("query_used") or query

            required_fields = [herb_value, part_value, identifier_value, compound_value]
            if not all(isinstance(field, str) and field.strip() for field in required_fields):
                continue

            cleaned_assoc = {
                "Indian medicinal plant": herb_value.strip(),
                "Plant part": part_value.strip(),
                "IMPPAT Phytochemical identifier": identifier_value.strip(),
                "Phytochemical name": compound_value.strip(),
                "References": references_value.strip(),
                "query_used": query_used_value.strip(),
            }

            if cleaned_assoc["IMPPAT Phytochemical identifier"]:
                valid_associations.append(cleaned_assoc)
        
        if valid_associations:
            processed_data[query] = valid_associations
    
    return processed_data
