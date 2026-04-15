class Settings:
    # Browser settings
    headless: bool = True
    browser_timeout: int = 300000
    
    # Output settings
    output_format: str = "json"  # "json" or "csv"
    json_output_dir: str = "data/output/json/"
    json_indent: int = 2


settings = Settings()
