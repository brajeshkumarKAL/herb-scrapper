class Settings:
    # Browser settings
    headless: bool = True
    browser_timeout: int = 300000
    
    # Output settings
    output_format: str = "json"  # "json" or "csv"
    json_output_dir: str = "data/output/json/"
    json_indent: int = 2

    # Batch processing settings
    max_queries_per_run: int = 50  # 0 means process all pending herbs in one run
    query_progress_file: str = "data/output/query_progress.json"


settings = Settings()
