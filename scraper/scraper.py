import asyncio
from config.settings import settings
from models.herb_model import Herb
from .browser import get_new_page

URL = "https://cb.imsc.res.in/imppat/basicsearch/phytochemical"


async def _extract_rows(page, query: str):
    try:
        await page.wait_for_selector("table tbody tr", timeout=10000)
    except Exception:
        return []
    rows = page.locator("table tbody tr")
    result = []
    total = await rows.count()
    for index in range(total):
        cells = rows.nth(index).locator("td")
        plant = (await cells.nth(0).inner_text()).strip()
        part = (await cells.nth(1).inner_text()).strip()
        identifier = (await cells.nth(2).inner_text()).strip()
        compound = (await cells.nth(3).inner_text()).strip()
        result.append(
            {
                "herb": plant,
                "part": part,
                "imphy_id": identifier,
                "phytochemical": compound,
                "query_used": query,
            }
        )
    return result


async def scrape_single_query(page, query: str):
    try:
        await page.goto(URL, timeout=settings.browser_timeout)
    except Exception:
        return []
    
    search_input = page.locator("#edit-combine")
    if await search_input.count() == 0:
        return []
    
    try:
        await search_input.fill(query)
    except Exception:
        return []
    
    try:
        submit_button = page.locator("input[value=Search]")
        await submit_button.click()
    except Exception:
        return []
    
    await page.wait_for_timeout(1500)
    result = []
    result.extend(await _extract_rows(page, query))
    while True:
        next_button = page.locator("a.paginate_button.next")
        if await next_button.count() == 0:
            break
        button = next_button.nth(0)
        classes = (await button.get_attribute("class")) or ""
        if "disabled" in classes:
            break
        try:
            await button.click()
            await page.wait_for_timeout(2500)
            page_results = await _extract_rows(page, query)
            result.extend(page_results)
        except Exception:
            break
    return result


async def scrape_herb(page, herb: Herb):
    query_results = {}
    
    # Scrape main name
    main_records = await scrape_single_query(page, herb.main_name)
    if main_records:
        query_results[herb.main_name] = main_records
    
    # Scrape synonyms if main query returned few results or none
    if len(main_records) < 20:
        for synonym in herb.synonyms:
            records = await scrape_single_query(page, synonym)
            if records:
                query_results[synonym] = records
    
    return query_results


async def _process_herb(browser, herb: Herb, semaphore):
    async with semaphore:
        page = await get_new_page(browser)
        try:
            query_results = await scrape_herb(page, herb)
            return query_results
        except Exception as error:
            return {herb.main_name: str(error)}
        finally:
            await page.close()


async def scrape_all_herbs(browser, herbs: list[Herb]):
    semaphore = asyncio.Semaphore(3)
    tasks = [_process_herb(browser, herb, semaphore) for herb in herbs]
    results = await asyncio.gather(*tasks)
    
    # Merge all query results into a single dict
    all_query_results = {}
    for result in results:
        all_query_results.update(result)
    return all_query_results
