import asyncio
from pyppeteer import launch
from motor.motor_asyncio import AsyncIOMotorClient
from config import *


async def run():
    # URL Define
    url = "https://bye-lemon.github.io"
    connection = AsyncIOMotorClient(HOST, PORT)
    site_info = connection["siteInfo"]
    raw_site_info = site_info["rawSiteInfo"]
    # Initialization
    browser = await launch(headless=False)
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(0)

    async def click(selector):
        await asyncio.gather(
            page.waitForNavigation(),
            page.click(selector),
        )

    await page.goto(url)
    links = []
    while True:
        articles = await page.JJ('article.index-post > a')
        for article in articles:
            links.append(await page.evaluate('(elem) => elem.href', article))
        if (next_btn := await page.J('a.next')) is None:
            break
        await click('a.next')

    for link in links:
        await page.goto(link)
        while not (license_ := await page.J("div.license-wrapper")):
            continue
        title = await page.Jeval("h1.intro-title.intro-fade-in", "node => node.innerText")
        update_time = await license_.Jeval("p:nth-child(4) > a", "node => node.innerText")
        html_ = await page.Jeval("article.article-entry", "node => node.innerText")
        await raw_site_info.insert_one({
            "title": title,
            "update_time": update_time,
            "url": link,
            "content": html_
        })

    await browser.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
