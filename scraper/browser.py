from playwright.async_api import async_playwright

from config.settings import settings

_browser = None
_browser_context = None
_playwright = None


async def init_browser():
    global _browser, _browser_context, _playwright
    if _browser is not None:
        return _browser

    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch(headless=settings.headless)
    _browser_context = await _browser.new_context()
    return _browser


async def get_new_page(browser):
    if browser is None:
        raise ValueError("Browser instance is required")
    global _browser_context
    if _browser_context is None:
        _browser_context = await browser.new_context()
    page = await _browser_context.new_page()
    page.set_default_timeout(settings.browser_timeout)
    return page


async def close_browser(browser):
    global _browser, _browser_context, _playwright
    if browser is None:
        return
    if _browser_context is not None:
        await _browser_context.close()
        _browser_context = None
    await browser.close()
    _browser = None
    if _playwright is not None:
        await _playwright.stop()
        _playwright = None
