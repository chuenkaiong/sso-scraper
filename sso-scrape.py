import argparse

from scraper import scrape_main


if __name__ == "__main__":
    # TODO - implement CLI
    parser = argparse.ArgumentParser(description="Scrape legislation from AGC SSO website")
    
    parser.add_argument("--retrieve", "-r", 
    type=str,
    default="ALL",
    help="Shorthand of legislation to scrape (default: Scraper will scrape all legislation)")

    parser.add_argument("--save_to", "-s", 
    type=str,
    default="./data", 
    help="Location to dump scraped files (default: ./data)")

    parser.add_argument("--include_subsid", "-sl",
    action="store_true",
    default="False",
    help="Include subsidiary legislation (default: False)"
    )

    args = parser.parse_args()
    scrape_main(retrieve=args.retrieve, saveTo=args.save_to, sl=args.include_subsid)