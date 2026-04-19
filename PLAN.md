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

## Matching Website Column Names and Extracting References
This project currently stores scraped rows with field names that differ from the website table headings. To fix this:

1. Identify exact website column headings from the target page.
   - `Indian medicinal plant`
   - `Plant part`
   - `IMPPAT Phytochemical identifier`
   - `Phytochemical name`
   - `References`

2. Map scraper output fields to the website headings.
   - Rename current output keys so the JSON uses the exact website names.
   - Keep values unchanged, only change field names in stored output.

3. Extract the References column from the scraped page.
   - Update HTML parsing in `scraper/scraper.py` to locate the References cell in each table row.
   - Preserve text content or links as appropriate, storing it in the new field.

4. Extend the data model and storage schema.
   - Add a `References` property to each association object.
   - Ensure JSON output includes this field for every entry.

5. Validate against sample output.
   - Use a representative page or query to verify output keys exactly match website headings.
   - Confirm `References` appears in the JSON data and contains the expected content.

6. Update documentation and tests.
   - Document the new exact output field names in `README.md` or `PLAN.md`.
   - Add unit tests for column name mapping and References extraction.

## Detailed Implementation Plan for Plan 1: JSON File per Query

### Phase 1: Data Structure Refactoring
1. **Update Herb Model**: Modify `models/herb_model.py` to include a `query_results` field that stores associations per query instead of aggregating.
   - Change from storing aggregated data to a dictionary: `{query_name: [associations]}`
   - Each association remains a dict with keys: herb, part, imphy_id, phytochemical, query_used

2. **Modify Scraper Logic**: Update `scraper/scraper.py` to return query-specific results.
   - `scrape_single_query()` should return a list of association dicts for that query.
   - `scrape_herb()` should collect results per query (main name and each synonym) without merging.
   - `scrape_all_herbs()` should return a dict of `{query: associations}` instead of aggregated data.

#### Synonym Search Strategy (≤20 Results Threshold)
The scraper implements a conditional synonym search strategy to balance data completeness with efficiency:

**Why Search Synonyms When Main Name Returns ≤20 Results**
- **Indicates incomplete coverage**: If the main herb name returns 0-20 phytochemicals, the database likely lacks comprehensive records under the primary name alone.
- **Captures alternative naming data**: Plants have multiple recognized names across languages and regions. For example, "Fever nut" might return different results than "Wrightia tinctoria" (the scientific name).
- **Unlocks additional records**: Different query names hit different database entries that reference the same plant by different identifiers.

**Why Skip Synonyms When Main Name Returns >20 Results**
- **Indicates good coverage**: 20+ results suggest the main name is well-documented and comprehensive.
- **Reduces redundant data**: The same phytochemical associations often appear under multiple names, creating duplicates and wasted effort.
- **Optimizes performance**: Each query requires browser navigation, searching, and pagination. Skipping unnecessary synonym searches saves time and reduces website load.
- **Practical resource management**: With 1006 herbs and multiple synonyms each, exhaustive searching would be prohibitively slow.

**Threshold Rationale**
The 20-result threshold is a practical balance:
- Low enough to trigger synonym searches for under-documented plants
- High enough to indicate the main name is reasonably comprehensive
- Can be tuned based on analysis needs (lower threshold = more exhaustive but slower; higher threshold = faster but potentially incomplete)

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

## Plan 2: Controlled Query Batching and Idempotent Resume
### Problem
Running all 1006 herb queries in one go is too slow and may require multiple sessions. The scraper must support running a fixed number of queries per execution and skip the already completed queries on subsequent runs.

### Goals
- Add a `max_queries_per_run` configuration option.
- Process a limited batch of pending queries each execution.
- Persist progress so completed queries are skipped in the next run.
- Keep behavior idempotent: repeated runs must not rerun finished queries.

### Design Overview
1. **Stable query ordering**
   - Build a deterministic ordered list of query strings from the input file.
   - Use the same order every run so indexing remains consistent.
   - Treat each query string independently, including synonyms.

2. **Configuration settings**
   - Add `max_queries_per_run` to `config/settings.py`.
   - Add `query_progress_file` to store checkpoint data.
   - Optionally add `run_all_pending` or use `0` / `None` to mean process all remaining queries.

3. **Progress persistence**
   - Use a JSON checkpoint file such as `data/output/query_progress.json`.
   - Store completed query identifiers and/or the last completed index.
   - Example shape:
     ```json
     {
       "completed_queries": ["terminalia chebula", "phyllanthus emblica"],
       "last_completed_index": 2
     }
     ```

4. **Query selection workflow**
   - On startup, load the input queries and the progress checkpoint.
   - Compute pending queries by removing `completed_queries` from the ordered list.
   - Select the first `max_queries_per_run` pending queries for the current execution.
   - If no pending queries remain, exit cleanly.

5. **Idempotent completion logic**
   - After a query is scraped and saved successfully, mark it as completed in the checkpoint.
   - Persist the checkpoint after each successful query or after each batch.
   - If a query fails, do not mark it completed so it will be retried on the next run.
   - Use output file existence as a secondary safeguard: if a query already has a JSON file, treat it as completed.

6. **Resume behavior**
   - On the next run, read the checkpoint and skip any already completed queries.
   - Start processing at the next pending query instead of repeating earlier work.
   - This ensures run 1 processes queries 1-5, run 2 processes 6-10, etc.

### Implementation Steps
1. **Extend configuration**
   - Add `max_queries_per_run` and `query_progress_file` to `config/settings.py`.
   - Add a comment describing that `0` / `None` means run all remaining queries.

2. **Query lifecycle management**
   - Add a helper in `processor/data_loader.py` or a new scheduler module.
   - Implement `load_ordered_queries()` to extract query strings in a stable order.
   - Implement `load_completed_queries(progress_file)` to read the checkpoint safely.
   - Implement `save_completed_queries(progress_file, completed_queries)`.

3. **Batch selection**
   - In `main.py`, determine `pending_queries = ordered_queries - completed_queries`.
   - Slice `pending_queries[:max_queries_per_run]` to get the current batch.
   - Log the start index, end index, and total pending count.

4. **Execution and checkpoint updates**
   - Run scraping for the selected batch only.
   - Save each query's JSON file as normal.
   - After successful save, append the query to `completed_queries` and persist the checkpoint.
   - Keep a durable record so partial runs are safe.

5. **Safe restart and recovery**
   - If the progress file is missing, infer completed queries from existing JSON files as a fallback.
   - If a query JSON file exists but the query is not in the checkpoint, optionally add it to the checkpoint before starting.
   - Avoid re-running queries that already produced output.

6. **Reporting and logging**
   - Print or log batch progress and remaining query count.
   - Report queries skipped due to completion.
   - Report any failures so the user can rerun just remaining queries.

### Testing and Validation
1. **Unit tests**
   - Test `load_ordered_queries()` returns stable ordering.
   - Test `load_completed_queries()` and `save_completed_queries()` handle missing and malformed checkpoint files.
   - Test the batch selection logic for `max_queries_per_run`.
   - Test idempotence by simulating a run with completed queries.

2. **Integration test**
   - Run the scraper on a small sample list of 10 queries with `max_queries_per_run=3`.
   - Verify run 1 processes queries 1-3, run 2 processes 4-6, run 3 processes 7-9, and run 4 processes query 10.
   - Confirm completed queries are skipped on each subsequent execution.

3. **Edge cases**
   - Verify behavior when `max_queries_per_run` is larger than remaining pending queries.
   - Verify behavior when all queries are already completed.

## Plan 3: Save Empty Result Files for No-Result Herbs
### Problem
When a herb search returns zero matches on the website, the current pipeline skips writing any file. This makes it hard to distinguish between herbs that were never processed and herbs that were processed with no results.

### Goals
- Always create a JSON file for each herb processed, even if the search returned no results.
- Represent no-result herbs with an empty array or explicit empty-result payload.
- Preserve the existing filename strategy and keep results easy to audit.

### Design Overview
1. **Empty file representation**
   - Use an empty JSON array `[]` for herbs with no returned associations.
   - Optionally include metadata in a wrapper object if more context is needed later.

2. **Create file per processed herb**
   - After scraping a herb (main name and synonyms), write a JSON file even when `processed_data` is empty.
   - Ensure the filename still reflects the herb query used.
   - An empty file means the herb was searched and processed, but no phytochemical matches were found and even no match for all of its synonyms as well.

3. **Distinguish between no results and failures**
   - If scraping succeeds but returns no rows, save an empty file.
   - If scraping fails due to an error, do not mark the herb completed and do not create an empty result file.
   - Log the difference clearly in `logs/herb_processing.log`.

4. **Progress and resume integration**
   - Mark a herb as completed once its file is written, even if empty.
   - This prevents repeated retries for herbs that legitimately have no results.

### Implementation Steps
1. **Update scraper/save pipeline**
   - After `process_data()` returns an empty dict for a herb, create a JSON file with `[]` as content.
   - Use the same normalized filename method used for result files.

2. **Adjust logging**
   - Log `Saved 0 associations for herb X` or `Saved empty file for herb X` when no results are found.
   - Keep the log entry format consistent with non-empty saves.

3. **Update progress logic**
   - Treat an empty-result file as a successful completion.
   - Store herb name in `completed_herbs` so the herb is skipped on the next run.

4. **Test and validate**
   - Verify run behavior for a no-result herb creates a file like `uraria_picta.json`.
   - Confirm the file is valid JSON and contains `[]`.
   - Confirm the herb is marked complete in `query_progress_file`.

### Documentation
- Document the new empty-result file behavior in `README.md` and `PLAN.md`.
- Explain that empty files mean “searched and found no results,” not “not processed yet.”
   - Verify failed queries remain pending after a rerun.

### Documentation
- Update `README.md` with the new batching and resume options.
- Document how to set `max_queries_per_run` and how progress is stored.
- Explain the idempotent retry behavior for repeated runs.

### Success Criteria for Batching
- The scraper processes at most `max_queries_per_run` pending queries per execution.
- Completed queries are skipped on subsequent runs.
- Progress persists across executions in a checkpoint file.
- Partial or failed runs do not corrupt completed state.
- The user can run the scraper repeatedly until all queries are finished, without reprocessing already completed queries.
