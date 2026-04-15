import asyncio
from scraper.browser import init_browser, close_browser

async def test():
    print("Initializing browser...")
    browser = await init_browser()
    print(f"Browser initialized: {browser}")
    
    page = None
    try:
        from scraper.browser import get_new_page
        page = await get_new_page(browser)
        print("Page created successfully")
        
        print("Navigating to URL...")
        await page.goto("https://cb.imsc.res.in/imppat/basicsearch/phytochemical", timeout=30000)
        print("Page loaded successfully")
        
        title = await page.title()
        print(f"Page title: {title}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if page:
            await page.close()
        await close_browser(browser)
        print("Browser closed")

asyncio.run(test())
