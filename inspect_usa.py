from playwright.sync_api import sync_playwright
from job_scraper_bot.config import USER_AGENT
from bs4 import BeautifulSoup
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=USER_AGENT)
    page = context.new_page()
    page.goto('https://www.usajobs.gov/Search/Results?keyword=meteorologist', timeout=60000)
    page.wait_for_timeout(5000)
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select('a[href^="/job/"]')
    for link in links[:2]:
        h2 = link.find_parent('h2')
        card = h2
        while card and card.name != 'div':
            card = card.parent
        print('LINK', link['href'], 'TEXT', link.get_text(strip=True))
        if card:
            # print the first 1200 chars of the card's HTML
            print(card.prettify()[:1200].replace('\n',' '))
        else:
            print('NO CARD')
        print('---')
    browser.close()
