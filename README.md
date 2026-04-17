# Phytochemical Data Scraper

A production-grade Python web scraper for extracting phytochemical associations from the IMPPAT database (https://cb.imsc.res.in/imppat/basicsearch/phytochemical) for Indian medicinal plants.

## Features

- **Parallel Processing**: Concurrent scraping with configurable semaphore limits
- **Query Flexibility**: Scrapes main herb names and synonyms with fallback logic
- **Structured Storage**: Stores scraped data per individual query in JSON format
- **Pagination Support**: Automatically handles paginated results
- **Error Handling**: Robust error handling and logging
- **Configurable Output**: Supports both JSON and CSV output formats

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Install Playwright browser:
   ```bash
   playwright install chromium
   ```

## Configuration

Edit `config/settings.py` to customize:

- `headless`: Run browser in headless mode (default: True)
- `browser_timeout`: Browser timeout in milliseconds (default: 300000)
- `output_format`: Output format - "json" or "csv" (default: "json")
- `json_output_dir`: Directory for JSON output files (default: "data/output/json/")
- `json_indent`: JSON indentation level (default: 2)

## Input Data

Place your herb data in `data/input/main_name_synonyms.json`:

```json
[
  {
    "main_name": "Terminalia chebula",
    "synonyms": ["Terminalia chebula Retz", "Myrobalan"]
  },
  {
    "main_name": "Ocimum sanctum",
    "synonyms": ["Ocimum tenuiflorum", "Holy Basil"]
  }
]
```

## Output Format

### JSON Output (Default)
Each query generates a separate JSON file in `data/output/json/`:

**Filename**: `{normalized_query_name}.json`

**Structure**:
```json
[
  {
    "Indian medicinal plant": "Terminalia chebula",
    "Plant part": "bark",
    "IMPPAT Phytochemical identifier": "IMPHY001187",
    "Phytochemical name": "Compound Name",
    "References": "Source details",
    "query_used": "terminalia chebula"
  }
]
```

### CSV Output (Legacy)
Single CSV file with aggregated data:

**Filename**: `data/output/output.csv`

**Structure**:
```
Herb,Phytochemical Associations
Terminalia chebula,"Terminalia chebula | bark | IMPHY001187 | Compound1 || Terminalia chebula | fruit | IMPHY002419 | Compound2"
```

## Usage

Run the scraper:
```bash
python main.py
```

## Project Structure

```
.
├── config/           # Configuration settings
├── data/
│   ├── input/        # Input herb data
│   └── output/       # Generated output files
├── models/           # Data models
├── processor/        # Data processing logic
├── scraper/          # Web scraping logic
├── storage/          # Data storage handlers
└── utils/            # Utility functions
```

## Key Components

- **main.py**: Orchestrates the entire scraping pipeline
- **scraper/scraper.py**: Core scraping logic with pagination
- **processor/data_processor.py**: Data validation and cleaning
- **storage/data_writer.py**: Handles JSON and CSV output
- **models/herb_model.py**: Data structures for herbs and associations

## Error Handling

The scraper includes comprehensive error handling:
- Network timeouts and connection failures
- Invalid selectors and page structure changes
- File I/O errors
- Data validation and cleaning

Check `logs/` directory for detailed error logs.

## Development

### Testing
Run individual components for testing:
```bash
python test_browser.py      # Test browser initialization
python test_selectors.py    # Test page selectors
```

### Adding New Features
1. Update data models in `models/`
2. Modify scraping logic in `scraper/`
3. Update processing in `processor/`
4. Add storage handlers in `storage/`

## License

This project is for educational and research purposes. Please respect the terms of service of the IMPPAT database.