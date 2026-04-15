# Data Storage Plans for Phytochemical Scraper

## Project Overview
This project scrapes phytochemical associations from the IMPPAT database (https://cb.imsc.res.in/imppat/basicsearch/phytochemical) for Indian medicinal plants. The scraper handles herb main names and synonyms, performs parallel scraping with pagination support, and currently stores data in a CSV format with deduplicated associations aggregated by main herb name. The goal is to restructure storage to maintain structured scraped data per individual query (herb name or synonym used in search), rather than aggregating by main herb.

Current data structure per association: `Herb | Part | IMPHY ID | Phytochemical Name`
Current storage: Single CSV row per main herb with pipe-separated associations.

## Plan 1: JSON File per Query (Selected)
Store each query's scraped data in a separate JSON file with structured objects.

### Structure
- File naming: `{query_name}.json` (normalized, e.g., "terminalia_chebula.json")
- Content: Array of association objects
```json
[
  {
    "herb": "Terminalia chebula",
    "part": "bark",
    "imphy_id": "IMPHY001187",
    "phytochemical": "[(2S,3R,4S,5S,6R)-3,4,5-trihydroxy-6-(hydroxymethyl)oxan-2-yl] (4aS,6aR,6aS,6bR,8R,8aR,9S,10R,11R,12aR,14bS)-8,10,11-trihydroxy-9-(hydroxymethyl)-2,2,6a,6b,9,12a-hexamethyl-1,3,4,5,6,6a,7,8,8a,10,11,12,13,14b-tetradecahydropicene-4a-carboxylate",
    "query_used": "terminalia chebula"
  }
]
```

### Advantages
- Human-readable and editable
- Easy to parse for analysis
- Maintains query-specific data without aggregation
- Supports nested structures for future extensions

### Disadvantages
- File proliferation (one per query)
- No built-in querying capabilities
- Manual deduplication required for analysis

### Implementation Steps
1. Modify scraper to collect associations per query
2. Create JSON serialization function
3. Update storage module to write individual JSON files
4. Add query normalization for filenames

## Detailed Implementation Plan for Plan 1: JSON File per Query

### Phase 1: Data Structure Refactoring
1. **Update Herb Model**: Modify `models/herb_model.py` to include a `query_results` field that stores associations per query instead of aggregating.
   - Change from storing aggregated data to a dictionary: `{query_name: [associations]}`
   - Each association remains a dict with keys: herb, part, imphy_id, phytochemical, query_used

2. **Modify Scraper Logic**: Update `scraper/scraper.py` to return query-specific results.
   - `scrape_single_query()` should return a list of association dicts for that query.
   - `scrape_herb()` should collect results per query (main name and each synonym) without merging.
   - `scrape_all_herbs()` should return a dict of `{query: associations}` instead of aggregated data.

3. **Update Data Processor**: Refactor `processor/data_processor.py`.
   - Remove deduplication logic since we're storing per query.
   - Change `process_data()` to accept the new dict format and prepare for storage.

### Phase 2: Storage Module Overhaul
1. **Create JSON Writer**: Add a new function in `storage/csv_writer.py` (rename to `storage/data_writer.py` for generality).
   - Function: `save_query_to_json(query_name, associations, output_dir)`
   - Normalize query_name for filename (lowercase, replace spaces with underscores, remove special chars).
   - Write JSON with proper formatting and UTF-8 encoding.
   - Handle file path creation and overwrite logic.

2. **Update Main Storage Logic**: Modify the storage call in `main.py`.
   - Instead of calling `save_to_csv()`, loop through each query and call `save_query_to_json()`.

### Phase 3: Configuration and Error Handling
1. **Update Settings**: Add JSON-specific settings in `config/settings.py`.
   - `output_format`: Set to "json"
   - `json_output_dir`: Path for JSON files (e.g., "data/output/json/")
   - `json_indent`: Indentation level for readability

2. **Error Handling**: Add robust error handling for JSON serialization and file I/O.
   - Catch JSON encoding errors for special characters in phytochemical names.
   - Handle file system errors (permissions, disk space).
   - Log warnings for failed queries but continue processing others.

### Phase 4: File Organization and Naming
1. **Directory Structure**: Create `data/output/json/` directory.
   - Ensure directory exists before writing files.
   - Consider subdirectories if many queries (e.g., by first letter).

2. **Filename Normalization**: Implement a utility function in `utils/helpers.py`.
   - `normalize_filename(name)`: Convert to lowercase, replace spaces/hyphens with underscores, remove invalid chars.
   - Ensure uniqueness if needed (though queries should be unique).

### Phase 5: Testing and Validation
1. **Unit Tests**: Create tests for new functions.
   - Test JSON serialization with sample data.
   - Test filename normalization.
   - Test scraper returns correct per-query structure.

2. **Integration Testing**: Run full pipeline with sample data.
   - Verify JSON files are created correctly.
   - Check data integrity (no data loss from current CSV format).
   - Validate JSON structure matches expected schema.

3. **Performance Considerations**: Monitor file I/O performance.
   - For large datasets, consider batch writing or async file operations.
   - Profile memory usage since keeping all associations in memory per query.

### Phase 6: Migration and Backward Compatibility
1. **Data Migration**: Provide a script to convert existing CSV data to JSON format if needed.
   - Parse the pipe-separated strings back into structured data.
   - Create JSON files for each herb.

2. **Configuration Toggle**: Allow switching between CSV and JSON output via settings.
   - Keep existing CSV logic for backward compatibility.
   - Add a flag to choose output format.

### Phase 7: Documentation and Maintenance
1. **Update README**: Document the new JSON storage format.
   - Explain file structure and naming conventions.
   - Provide examples of JSON content.

2. **Code Comments**: Add detailed docstrings to new functions.
   - Explain parameters, return values, and edge cases.

### Potential Challenges and Mitigations
- **File Proliferation**: With many queries, many files. Mitigation: Implement cleanup scripts or archiving.
- **Data Duplication**: Same associations may appear in multiple query files. Mitigation: Accept this for query-specific storage, or add optional deduplication.
- **Scalability**: For thousands of queries, consider database storage later. Mitigation: Start with file-based, monitor performance.
- **Unicode Handling**: Phytochemical names may have special chars. Mitigation: Ensure UTF-8 encoding throughout.

### Success Criteria
- Each query generates exactly one JSON file with its scraped associations.
- JSON structure is valid and parseable.
- No data loss compared to current CSV output.
- Pipeline runs without errors and maintains performance.
- Files are human-readable and suitable for further analysis.