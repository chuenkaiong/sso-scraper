import datetime
import requests
from bs4 import BeautifulSoup

from scraper_lib import filemgr
from scraper_lib import settings
from scraper_lib.items import LegisItem
from scraper_lib.download import get_body, write_to_file
from scraper_lib.subsid import get_subsid


def scrape_main(retrieve="ALL", sl=False, date=datetime.date.today().strftime("%Y%m%d"), saveTo="./data"):
    if not filemgr.check_save_location(saveTo):
        return

    if retrieve == "ALL":
        # if user does not specify which Act to retrieve, start from the contents page.
        # TODO: handle date
        scrape_all(sl, saveTo)

    else:
        # if user specifies the Act to retrieve by shorthand, scrape it directly
        url = f"https://sso.agc.gov.sg/Act/{retrieve}"
        item = LegisItem(url, retrieve)
        scrape_one(item, sl, saveTo)


def scrape_all(sl, saveTo):
    # generate list of LegisItem objects representing each Act, then scrape each one individually
    legis_items = []
    contents_url = 'https://sso.agc.gov.sg/Browse/Act/Current/All?PageSize=500&SortBy=Title&SortOrder=ASC'

    r = requests.get(contents_url, headers=settings.headers)
    if r.status_code != 200:
        print('Failed to load main url:', contents_url)
        return
    soup = BeautifulSoup(r.text, 'lxml')
    page_count = int(soup.find("div", class_="page-count").string.split()[-2])

    for i in range(page_count):
        pg_str = "" if i == 0 else "/" + str(i)
        url = f'https://sso.agc.gov.sg/Browse/Act/Current/All{pg_str}?PageSize=500&SortBy=Title&SortOrder=ASC'

        r = requests.get(url, headers=settings.headers)
        if r.status_code != 200:
            print('Failed to get page:', url)
            continue

        soup = BeautifulSoup(r.text, "lxml")
        browse_list = soup.find("table", class_="browse-list").find("tbody")
        rows = browse_list.find_all("tr")[:10]
        for row in rows:
            link = f"https://sso.agc.gov.sg{row.find('a')['href']}"
            shorthand = link.split("/")[-1]
            item = LegisItem(link, shorthand)
            legis_items.append(item)

    for item in legis_items:
        scrape_one(item, sl, saveTo)


def scrape_one(item, sl, saveTo):
    # get main body of Act
    print("Retrieving", item.shorthand)
    r = requests.get(item.url, headers=settings.headers)
    if r.status_code != 200:
        print('Failed:', item.url, f"status: {r.status_code}")
        return
    item.set_html(get_body(r.text))

    write_to_file(saveTo, item)
    
    # get subsidiary legislation
    if sl:
        get_subsid(item, saveTo)
