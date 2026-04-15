import asyncio
from scraper.browser import init_browser, close_browser, get_new_page
from config.settings import settings

async def test():
    browser = await init_browser()
    
    page = None
    try:
        page = await get_new_page(browser)
        await page.goto("https://cb.imsc.res.in/imppat/basicsearch/phytochemical", timeout=30000)
        print("Page loaded")
        
        search_input = page.locator("#edit-combine")
        print(f"Search input found: {await search_input.count()}")
        
        await search_input.fill("Terminalia chebula")
        print("Filled search input")
        
        submit_button = page.locator("input[value=Search]")
        print(f"Submit button found: {await submit_button.count()}")
        
        await submit_button.click()
        print("Clicked search button")
        
        await page.wait_for_timeout(3000)
        print("Waited 3 seconds")
        
        table_rows = page.locator("table tbody tr")
        print(f"Table rows found: {await table_rows.count()}")
        
        if await table_rows.count() > 0:
            first_row = table_rows.nth(0)
            cells = first_row.locator("td")
            for i in range(4):
                text = await cells.nth(i).inner_text()
                print(f"  Cell {i}: {text}")
        else:
            print("No table rows found.")
            all_tables = page.locator("table")
            print(f"Total tables on page: {await all_tables.count()}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if page:
            await page.close()
        await close_browser(browser)

asyncio.run(test())
