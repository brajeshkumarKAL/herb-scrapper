import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

from config.settings import settings
from processor.data_loader import load_herb_data
from scraper.browser import init_browser, close_browser, get_new_page
from scraper.scraper import scrape_herb
from processor.data_processor import process_data
from storage.data_writer import save_all_queries_to_json, save_query_to_json, save_to_csv


def load_progress(progress_file: str) -> dict:
    progress_path = Path(progress_file)
    if not progress_path.exists():
        return {"completed_herbs": []}
    try:
        with progress_path.open("r", encoding="utf-8") as source:
            progress_data = json.load(source)
        return {
            "completed_herbs": progress_data.get("completed_herbs", []),
        }
    except Exception:
        return {"completed_herbs": []}


def save_progress(progress_file: str, completed_herbs: list[str]) -> None:
    progress_path = Path(progress_file)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_data = {
        "completed_herbs": completed_herbs,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    with progress_path.open("w", encoding="utf-8") as destination:
        json.dump(progress_data, destination, indent=2, ensure_ascii=False)


def select_herb_batch(herbs, completed_herbs: set[str], max_batch: int) -> list:
    pending = [herb for herb in herbs if herb.main_name not in completed_herbs]
    if max_batch and max_batch > 0:
        return pending[:max_batch]
    return pending


async def main():
    # Set up logging
    log_file = Path("logs/herb_processing.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logger = logging.getLogger(__name__)
    
    try:
        herbs = load_herb_data("data/input/main_name_synonyms.json")
        if not herbs:
            logger.warning("No herbs found in input file.")
            return

        logger.info(f"Loaded {len(herbs)} herbs.")

        progress = load_progress(settings.query_progress_file)
        completed_herbs = set(progress.get("completed_herbs", []))
        batch = select_herb_batch(herbs, completed_herbs, settings.max_queries_per_run)

        if not batch:
            logger.info("No pending herbs to process. All herbs are complete.")
            return

        logger.info(f"Processing {len(batch)} herb(s) this run.")
        pending_total = len([herb for herb in herbs if herb.main_name not in completed_herbs])
        logger.info(f"{pending_total} herb(s) pending in total.")

        browser = await init_browser()
        page = None
        try:
            page = await get_new_page(browser)
            completed_this_run = []
            for herb in batch:
                logger.info(f"Starting herb: {herb.main_name}")
                try:
                    query_results = await scrape_herb(page, herb)
                    processed_data = process_data(query_results)
                    if settings.output_format == "json":
                        if not processed_data:
                            empty_file = save_query_to_json(herb.main_name, [], settings.json_output_dir)
                            logger.info(f"  Saved empty file for herb {herb.main_name}: {empty_file}")
                        else:
                            created_files = save_all_queries_to_json(processed_data)
                            logger.info(f"  Saved {len(created_files)} file(s) for herb {herb.main_name}: {', '.join(created_files)}")
                    elif settings.output_format == "csv":
                        csv_data = []
                        for query, associations in processed_data.items():
                            association_strings = []
                            for assoc in associations:
                                herb_name = assoc.get("Indian medicinal plant") or assoc.get("herb") or ""
                                plant_part = assoc.get("Plant part") or assoc.get("part") or ""
                                imphy_id = assoc.get("IMPPAT Phytochemical identifier") or assoc.get("imphy_id") or ""
                                phytochemical_name = assoc.get("Phytochemical name") or assoc.get("phytochemical") or ""
                                association_strings.append(" | ".join([herb_name, plant_part, imphy_id, phytochemical_name]))
                            associations_str = " || ".join(association_strings)
                            csv_data.append({"Herb": query, "Phytochemical Associations": associations_str})
                        output_path = save_to_csv(csv_data)
                        logger.info(f"  Saved CSV output for herb {herb.main_name} to {output_path}")
                    else:
                        logger.warning(f"Unknown output format: {settings.output_format}")

                    completed_herbs.add(herb.main_name)
                    completed_this_run.append(herb.main_name)
                    save_progress(settings.query_progress_file, sorted(completed_herbs))
                except Exception as error:
                    logger.error(f"  Failed herb {herb.main_name}: {error}")
                    continue
        finally:
            if page:
                await page.close()
            await close_browser(browser)

        logger.info(f"Completed {len(completed_this_run)} herb(s) this run.")
        if completed_this_run:
            logger.info(f"Last completed herb: {completed_this_run[-1]}")
    except FileNotFoundError as error:
        logger.error(f"Error: {error}")
    except ValueError as error:
        logger.error(f"Error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}")


if __name__ == "__main__":
    asyncio.run(main())
