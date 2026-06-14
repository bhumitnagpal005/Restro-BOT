"""
Scrapes all tracked Roorkee restaurants from Zomato and saves menu JSON files.
Run from the backend/ directory: python -m data.runner
"""

from data.scraper import scrape_zomato

RESTAURANTS = {
    "prakash_hotel": "https://www.zomato.com/roorkee/hotel-prakash-restaurant-roorkee-locality/order",
    "dominos": "https://www.zomato.com/roorkee/dominos-pizza-roorkee-locality/order",
    "pizza_hut": "https://www.zomato.com/roorkee/pizza-hut-roorkee-locality/order",
    "foodbay": "https://www.zomato.com/roorkee/foodbay-roorkee-locality/order",
    "kfc": "https://www.zomato.com/roorkee/kfc-1-roorkee-locality/order",
    "waffle_by_nature": "https://www.zomato.com/roorkee/waffle-by-nature-roorkee-locality/order",
    "patiala_lassi": "https://www.zomato.com/roorkee/patiala-lassi-roorkee-locality/order",
    "desi_tadka": "https://www.zomato.com/roorkee/desi-tadka-2-roorkee-locality/order",
    "baap_of_rolls": "https://www.zomato.com/roorkee/baap-of-rolls-roorkee-locality/order",
}


def main() -> None:
    for name, url in RESTAURANTS.items():
        print(f"\n==> Scraping {name}")
        try:
            scrape_zomato(url, f"{name}_menu.json")
        except Exception as e:
            print(f"Failed to scrape {name}: {e}")


if __name__ == "__main__":
    main()
