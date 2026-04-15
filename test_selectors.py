import asyncio
from scraper.browser import init_browser, close_browser, get_new_page

async def test():
    print("Initializing browser...")
    browser = await init_browser()
    
    page = None
    try:
        page = await get_new_page(browser)
        print("Navigating to URL...")
        await page.goto("https://cb.imsc.res.in/imppat/basicsearch/phytochemical", timeout=30000)
        print("Page loaded")
        
        search_input_count = await page.locator("input[placeholder*='Indian medicinal plant']").count()
        print(f"Search input found: {search_input_count}")
        
        if search_input_count == 0:
            xpath_count = await page.locator("xpath=//input[@name='toSearch']").count()
            print(f"Input with name 'toSearch': {xpath_count}")
            
            all_inputs = await page.locator("input").count()
            print(f"Total inputs on page: {all_inputs}")
            
            text_inputs = await page.locator("input[type=text]").count()
            print(f"Text inputs: {text_inputs}")
        
        search_button_count = await page.locator("button:has-text('Search')").count()
        print(f"Search button found: {search_button_count}")
        
        if search_button_count == 0:
            submit_buttons = await page.locator("input[type=submit]").count()
            print(f"Submit buttons: {submit_buttons}")
            
            all_buttons = await page.locator("button").count()
            print(f"Total buttons: {all_buttons}")
        
        table_count = await page.locator("table tbody tr").count()
        print(f"Table rows found: {table_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if page:
            await page.close()
        await close_browser(browser)

asyncio.run(test())
