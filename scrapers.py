import datetime
import requests
import json
from bs4 import BeautifulSoup

from lib import filemgr
from lib import settings
from lib.items import LegisItem


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
            link = row.find("a")["href"]
            print(link)
            shorthand = link.split("/")[-1]
            item = LegisItem(link, shorthand)
            legis_items.append(item)
        
        # CONTINUE HERE
        
    return

    
    for item in legis_items:
        scrape_one(item, sl, saveTo)

def scrape_one(item, sl, saveTo):
    # get main body of Act 
    r = requests.get(item.url, headers=settings.headers)
    if r.status_code != 200:
        print('Failed:', item.url, f"status: {r.status_code}")
        return
    item.set_html(get_body(r.text))

    write_to_file(saveTo, item)

    # get subsidiary legislation
    # TODO

def get_body(response):
    headers = settings.headers  

    # Gets non-lazy loaded content
    soup = BeautifulSoup(response, "lxml")
    data = soup.find_all("div", {"class": "prov1"})

    non_lazy_load =''
    for prov in data:
      non_lazy_load += "".join(str(x) for x in prov.contents)

    # Get the parameters with which to request lazyload content
    lazyload_data = json.loads(soup.find_all("div", {"class": "global-vars"}, limit=2)[1]["data-json"])
    # print(json.dumps(lazyload_data, sort_keys=True, indent=4))
    toc_sys_id = lazyload_data["tocSysId"]
    
    series_ids = [div["data-term"] for div in soup.find_all("div", {"class": "dms"})]

    parts = [non_lazy_load]

    # Request content in parts
    for series_id in series_ids:
      frag_sys_id = lazyload_data["fragments"][series_id]["Item1"]
      dt_id = lazyload_data["fragments"][series_id]["Item2"]
      url = "https://sso.agc.gov.sg/Details/GetLazyLoadContent?TocSysId={}&SeriesId={}".format(toc_sys_id, series_id) + \
        "&ValidTime=&TransactionTime=&ViewType=&V=25&Phrase=&Exact=&Any=&Without=&WiAl=&WiPr=&WiLT=&WiSc=" + \
        "&WiDT=&WiDH=&WiES=&WiPH=&RefinePhrase=&RefineWithin=&CustomSearchId=&FragSysId={}&_={}".format(frag_sys_id, dt_id)
      
      parts.append(download_part(url, headers))
    
    return stitch_parts(parts).replace(u'\xa0', u' ') #ensures no missing spaces

def download_part(url, headers):
# Downloads additional HTML parts
    r = requests.get(url, headers=headers)
    if r.status_code != requests.status_codes.codes.ok:
        print('URL not found: ' + url)
        return ''
    return r.text

def stitch_parts(parts):
# Takes a list of HTML parts and joins them into a single string
    first, *remaining = parts
    insert_idx = first.find('<div class="dms"')
    return first[:insert_idx] + ''.join(remaining) + first[insert_idx:]


def write_to_file(saveTo, item):
    with open(f"{saveTo}/{item.shorthand}.html", "w") as f:
        # prints subsid link at the top of .html file
        if item.sl_urls:
            f.write(f"Subsidiary Legislation Link: {item.sl_urls}")
        # handles unicode encode error
        f.write(item.html.encode(
            'ascii', errors='ignore').decode('unicode-escape'))
