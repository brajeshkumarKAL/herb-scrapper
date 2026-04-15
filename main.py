import asyncio

from processor.data_loader import load_herb_data
from scraper.browser import init_browser, close_browser
from scraper.scraper import scrape_all_herbs
from processor.data_processor import process_data
from storage.csv_writer import save_to_csv


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
            output_path = save_to_csv(processed_data)
            print(f"Output saved to: {output_path}")
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
