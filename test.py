import requests
from bs4 import BeautifulSoup
from scraper_lib import filemgr, settings
from scraper import scrape_one
from scraper_lib.items import LegisItem


def test_scrape():
    # test with a sample of various pieces of legislation
    if not filemgr.check_save_location("./data"):
        return
    
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
        rows = browse_list.find_all("tr")[::20]
        for row in rows:
            link = f"https://sso.agc.gov.sg{row.find('a')['href']}"
            shorthand = link.split("/")[-1]
            item = LegisItem(link, shorthand)
            legis_items.append(item)

    print("Items to scrape:", [item.shorthand for item in legis_items])

    for item in legis_items:
        scrape_one(item=item, sl=True, saveTo="./data")

if __name__ == "__main__":
    test_scrape()