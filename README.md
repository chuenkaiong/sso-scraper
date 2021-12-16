# SSO Scraper
## Description
Scraper for legislation from sso.agc.gov.sg (adapted from old SSO scraper to remove dependency on Scrapy)


## Usage 

```
usage: sso-scrape.py [-h] [--retrieve retrieve] [--save_to saveTo] [--include-subsid]

Scrape legislation from AGC SSO website


optional arguments:
  -h, --help            show this help message and exit
  --retrieve retrieve, -r retrieve
                        Shorthand of legislation to scrape (default: Scraper will scrape all legislation)      
  --save_to saveTo, -s saveTo
                        Location to dump scraped files (default: ./data
  --include-subsid, -sl
                        Include subsidiary legislation (default: False)
```


## TODOs
### Date filtering 
* Where retrieving all legislation – only legislation in force at the time should be returned, AND each piece of legislation should be the version in force at that date.
* Where retrieving single legislation by shorthand – legislation returned should be the version in force at that date.