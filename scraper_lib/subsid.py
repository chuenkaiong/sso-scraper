from os import write
from bs4 import BeautifulSoup
import requests
from scraper_lib import settings
from scraper_lib.download import get_body, write_to_file

from scraper_lib.items import LegisItem


def get_subsid(main_item, saveTo):
    # generate list of SL items 
    subsid_url = f"https://sso.agc.gov.sg/Act/{main_item.shorthand}?DocType=Act&ViewType=Sl&PageIndex=0&PageSize=500"
    r = requests.get(subsid_url, headers=settings.headers)
    if r.status_code != requests.status_codes.codes.ok:
        print('URL not found: ' + subsid_url)
    soup = BeautifulSoup(r.text, "lxml")
    
    # (assume only one page of SL for now)
    subsid_items = []
    rows = soup.find("table", class_="browse-list").find("tbody").find_all("tr")
    for row in rows: 
        sl = row.find("a")
        sl_url = "https://sso.agc.gov.sg/" + sl["href"]
        sl_shorthand = sl_url.split("/")[-1].split("?")[0]
        subsid_items.append(LegisItem(sl_url, sl_shorthand))

    # scrape each SL item
    for subsid_item in subsid_items:
        sl_scrape_one(subsid_item, saveTo)
    
def sl_scrape_one(sl_item, saveTo):
    print("Retrieving SL", sl_item.shorthand)
    r = requests.get(sl_item.url, headers=settings.headers)
    if r.status_code != requests.status_codes.codes.ok:
        print(f"SL not found: {sl_item.shorthand}")
    soup = BeautifulSoup(r.text, "lxml")
    openWd = soup.find("td", class_="openWd")
    non_lazy = "".join([str(x) for x in openWd.contents]) if openWd else ""
    # Assume that there is only one openWd table in SL. 
    # TODO - check if some SL contains multple openWd tables, or non-lazy content in other formats
    lazy = get_body(r.text)
    body = non_lazy + lazy
    sl_item.set_html(body)
    
    write_to_file(saveTo, sl_item)