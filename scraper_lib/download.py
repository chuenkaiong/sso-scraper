from bs4 import BeautifulSoup
import requests
import json

from scraper_lib import settings


def get_body(response):
    headers = settings.headers

    # Gets non-lazy loaded content
    soup = BeautifulSoup(response, "lxml")
    data = soup.find_all("div", {"class": "prov1"})

    non_lazy_load = ''
    for prov in data:
        non_lazy_load += "".join(str(x) for x in prov.contents)

    # Get the parameters with which to request lazyload content
    lazyload_data = json.loads(soup.find_all(
        "div", {"class": "global-vars"}, limit=2)[1]["data-json"])
    # print(json.dumps(lazyload_data, sort_keys=True, indent=4))
    if "tocsysId" not in lazyload_data or "fragments" not in lazyload_data:
        print("Unable to find lazyload data.")
        return ""
    toc_sys_id = lazyload_data["tocSysId"]

    series_ids = [div["data-term"]
                  for div in soup.find_all("div", {"class": "dms"})]

    parts = [non_lazy_load]

    # Request content in parts
    for series_id in series_ids:
        frag_sys_id = lazyload_data["fragments"][series_id]["Item1"]
        dt_id = lazyload_data["fragments"][series_id]["Item2"]
        url = "https://sso.agc.gov.sg/Details/GetLazyLoadContent?TocSysId={}&SeriesId={}".format(toc_sys_id, series_id) + \
            "&ValidTime=&TransactionTime=&ViewType=&V=25&Phrase=&Exact=&Any=&Without=&WiAl=&WiPr=&WiLT=&WiSc=" + \
            "&WiDT=&WiDH=&WiES=&WiPH=&RefinePhrase=&RefineWithin=&CustomSearchId=&FragSysId={}&_={}".format(
              frag_sys_id, dt_id)

        parts.append(download_part(url, headers))

    # ensures no missing spaces
    return stitch_parts(parts).replace(u'\xa0', u' ')


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
    with open(f"{saveTo}/{item.shorthand}.html", "w", encoding="utf-8") as f:
        # prints subsid link at the top of .html file
        if item.sl_urls:
            f.write(f"Subsidiary Legislation Link: {item.sl_urls}")

        f.write(item.html)
