import argparse
import requests
from bs4 import BeautifulSoup
import json

# URL of the Criminal Minds episodes wiki page
EPISODE_URL = "https://criminalminds.fandom.com/wiki/Criminal_Minds_Episodes"
DEFAULT_EXPORT_PATH = "../data/episodes.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Criminal Minds wiki for episode information"
        + "and export data as JSON."
    )
    parser.add_argument(
        "--export_path",
        help="Path to save the JSON file",
        required=False,
        default=DEFAULT_EXPORT_PATH,
    )
    args = parser.parse_args()

    # Request episodes page and get BeautifulSoup object
    response = requests.get(EPISODE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Need series, season, episode title, and other infor
    episodes = []
    divs = soup.find_all("div", class_="wikia-gallery-item")
    for div in divs:
        series = div.find_previous("h2").get_text()
        season = div.find_previous("h3").get_text()
        gallery_item = div.find("div", class_="lightbox-caption").find("a")
        if gallery_item is None:
            continue
        href = gallery_item["href"]
        title = gallery_item["title"]
        link = f"https://criminalminds.fandom.com{href}"
        number = gallery_item.text.split(".")[0]
        episode = {
            "series": series,
            "title": title,
            "season": season,
            "number": number,
            "link": link,
        }
        episodes.append(episode)
    with open(args.export_path, "w") as json_file:
        json.dump(episodes, json_file, indent=4)
