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
            # Ensure required fields are present
            required_fields = ["herb", "part", "imphy_id", "phytochemical", "query_used"]
            if not all(field in assoc for field in required_fields):
                continue
            # Clean the data
            cleaned_assoc = {
                "herb": assoc["herb"].strip(),
                "part": assoc["part"].strip(),
                "imphy_id": assoc["imphy_id"].strip(),
                "phytochemical": assoc["phytochemical"].strip(),
                "query_used": assoc["query_used"].strip(),
            }
            # Only add if imphy_id is not empty
            if cleaned_assoc["imphy_id"]:
                valid_associations.append(cleaned_assoc)
        
        if valid_associations:
            processed_data[query] = valid_associations
    
    return processed_data
