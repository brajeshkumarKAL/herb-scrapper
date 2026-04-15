import asyncio
from config.settings import settings

from processor.data_loader import load_herb_data
from scraper.browser import init_browser, close_browser
from scraper.scraper import scrape_all_herbs
from processor.data_processor import process_data
from storage.data_writer import save_all_queries_to_json, save_to_csv


async def main():
    try:
        herbs = load_herb_data("data/input/main_name_synonyms.json")
        if not herbs:
            print("No herbs found in input file.")
            return
        
        print(f"Loaded {len(herbs)} herbs.")
        
        browser = await init_browser()
        try:
            scraped_data = await scrape_all_herbs(browser, herbs)
            processed_data = process_data(scraped_data)
            
            if settings.output_format == "json":
                created_files = save_all_queries_to_json(processed_data)
                print(f"Created {len(created_files)} JSON files in {settings.json_output_dir}")
                if created_files:
                    print(f"Sample file: {created_files[0]}")
            elif settings.output_format == "csv":
                # Convert processed_data back to old format for CSV compatibility
                csv_data = []
                for query, associations in processed_data.items():
                    associations_str = " || ".join(
                        " | ".join([assoc["herb"], assoc["part"], assoc["imphy_id"], assoc["phytochemical"]])
                        for assoc in associations
                    )
                    csv_data.append({"Herb": query, "Phytochemical Associations": associations_str})
                output_path = save_to_csv(csv_data)
                print(f"Output saved to: {output_path}")
            else:
                print(f"Unknown output format: {settings.output_format}")
        finally:
            await close_browser(browser)
    except FileNotFoundError as error:
        print(f"Error: {error}")
    except ValueError as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    asyncio.run(main())
