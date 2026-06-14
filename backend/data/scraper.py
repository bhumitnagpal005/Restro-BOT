"""
Zomato Menu Scraper — extracts restaurant info and full menu data via Selenium + BeautifulSoup.
"""

import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def scrape_zomato(url: str, filename: str = "zomato_menu.json") -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.get(url)
    time.sleep(4)

    # Expand all "Read More" buttons for full descriptions
    try:
        while True:
            buttons = driver.find_elements(
                By.XPATH,
                "//span[contains(translate(text(), 'READ MORE', 'read more'), 'read more')]",
            )
            if not buttons:
                break
            for btn in buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    pass
            time.sleep(0.5)
    except Exception:
        pass

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    # Restaurant info
    restaurant_info: dict[str, str] = {}
    h1 = soup.find("h1")
    restaurant_info["name"] = h1.get_text(strip=True) if h1 else ""

    loc_tag = soup.find("div", class_=re.compile("sc-clNaTc"))
    restaurant_info["location"] = loc_tag.get_text(strip=True) if loc_tag else ""

    phone_tag = soup.find("a", href=re.compile(r"tel:"))
    restaurant_info["contact"] = phone_tag.get_text(strip=True) if phone_tag else ""

    # Menu
    menu_data = []
    for section in soup.find_all("section", class_=re.compile("sc-bZVNgQ")):
        cat_tag = section.find("h4")
        category = cat_tag.get_text(strip=True) if cat_tag else ""
        items = []

        for item in section.find_all("div", class_=re.compile("sc-jhLVlY")):
            veg_type = "Unknown"
            veg_div = item.find("div", class_=re.compile("sc-gcpVEs"))
            if veg_div and veg_div.has_attr("type"):
                veg_type = "Veg" if veg_div["type"] == "veg" else "Non-Veg"

            name_tag = item.find("h4", class_=re.compile("sc-cGCqpu"))
            name = name_tag.get_text(strip=True) if name_tag else ""

            price_tag = item.find("span", class_=re.compile("sc-17hyc2s-1"))
            price = price_tag.get_text(strip=True) if price_tag else ""

            desc_tag = item.find("p", class_=re.compile("sc-gsxalj"))
            desc = ""
            if desc_tag:
                for rm in desc_tag.find_all("span", string=re.compile("read more", re.I)):
                    rm.extract()
                desc = desc_tag.get_text(" ", strip=True)

            spice_level = (
                "Spicy"
                if re.search(r"spicy|fiery|peri peri|chilli|hot", desc, re.I)
                else "Normal"
            )

            if name:
                items.append(
                    {
                        "name": name,
                        "price": price,
                        "description": desc,
                        "veg_nonveg": veg_type,
                        "spice_level": spice_level,
                    }
                )

        menu_data.append({"category": category, "items": items})

    print(f"Restaurant: {restaurant_info['name']}")
    print(f"Location:   {restaurant_info['location']}")
    print(f"Contact:    {restaurant_info['contact']}")

    os.makedirs("menu", exist_ok=True)
    filepath = os.path.join("menu", filename.replace(".csv", ".json"))
    with open(filepath, "w") as f:
        json.dump({"restaurant": restaurant_info, "menu": menu_data}, f, indent=4)
    print(f"Saved to {filepath}")
