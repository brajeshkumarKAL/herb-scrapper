import asyncio
from scraper.browser import init_browser, close_browser, get_new_page

async def test():
    browser = await init_browser()
    
    page = None
    try:
        page = await get_new_page(browser)
        await page.goto("https://cb.imsc.res.in/imppat/basicsearch/phytochemical", timeout=30000)
        print("Page loaded\n")
        
        inputs = page.locator("input")
        input_count = await inputs.count()
        print(f"Found {input_count} input fields:")
        for i in range(input_count):
            input_elem = inputs.nth(i)
            id_attr = await input_elem.get_attribute("id") or "N/A"
            name_attr = await input_elem.get_attribute("name") or "N/A"
            placeholder = await input_elem.get_attribute("placeholder") or "N/A"
            type_attr = await input_elem.get_attribute("type") or "text"
            print(f"  [{i}] id={id_attr}, name={name_attr}, type={type_attr}, placeholder={placeholder}")
        
        print(f"\nFound 2 buttons:")
        buttons = page.locator("button")
        button_count = await buttons.count()
        for i in range(button_count):
            button = buttons.nth(i)
            text = await button.inner_text()
            id_attr = await button.get_attribute("id") or "N/A"
            class_attr = await button.get_attribute("class") or "N/A"
            print(f"  [{i}] id={id_attr}, class={class_attr}, text={text}")
        
        print(f"\nFound 1 submit input:")
        submit = page.locator("input[type=submit]")
        submit_count = await submit.count()
        for i in range(submit_count):
            elem = submit.nth(i)
            value = await elem.get_attribute("value") or "N/A"
            print(f"  [{i}] value={value}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if page:
            await page.close()
        await close_browser(browser)

asyncio.run(test())
