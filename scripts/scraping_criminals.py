import argparse
import requests
from bs4 import BeautifulSoup
import json

#TODO: Grab aliases, also make sure I'm not doubling up anywhere

# URL of the Criminal Minds criminals wiki page
CRIMINAL_URL = "https://criminalminds.fandom.com/wiki/List_of_major_criminals"
DEFAULT_EXPORT_PATH = "../data/criminals.json"


def get_season_url(section):
    season_link = None
    next_sibling = section.find_next_sibling()
    if next_sibling and next_sibling.name == "p" and next_sibling.find("a"):
        season_link = next_sibling.find("a")["href"]

        # Create the URL of the major criminals page for the season
        return f"https://criminalminds.fandom.com{season_link}"
    return None


def get_criminal_url(div):
    link = div.find_all("a")[-1]
    if link:
        # Create the URL of the criminal page
        criminal_link = link["href"]
        return f"https://criminalminds.fandom.com{criminal_link}"
    else:
        return None


def parse_criminal_soup(criminal_soup):
    # Find the aside of interest
    aside = criminal_soup.find("aside", class_="portable-infobox")

    if aside is None:
        return None

    def _parse_element(data_source):
        element = aside.find("div", {"data-source": data_source})
        if element:
            value = element.find("div", class_="pi-data-value").get_text(
                separator="\n"
            )
            return value
        return None

    name = _parse_element("name")
    pathologies = _parse_element("path")
    mo = _parse_element("mo")
    victims = _parse_element("victims")

    criminal = {}

    if name:
        criminal["name"] = name
    if pathologies:
        criminal["pathologies"] = pathologies
    if mo:
        criminal["modus_operandi"] = mo
    if victims:
        criminal["victims"] = victims

    # Add appearances
    h2s = criminal_soup.find_all("h2")
    appearances_ul = None
    for h2 in h2s:
        if h2.find("span", id="Appearances"):
            appearances_ul = h2.find_next_sibling("ul")
            break
    if appearances_ul:
        criminal["appearances"] = [
            li.text.strip().split("\n")[0]
            for li in appearances_ul.find_all("li")
        ]
    return criminal if criminal != {} else None


if __name__ == "__main__":

    # Parsing arguments
    parser = argparse.ArgumentParser(
        description="Scrape Criminal Minds wiki for criminal information and export data as JSON."
    )
    parser.add_argument(
        "--export_path",
        help="Path to save the JSON file",
        required=False,
        default=DEFAULT_EXPORT_PATH,
    )
    args = parser.parse_args()

    # Request criminals page and get BeautifulSoup object
    response = requests.get(CRIMINAL_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find sections for each major season
    major_criminal_sections = soup.find_all("h2")

    # Initialize a list to store the criminals' data
    major_criminals = []

    for section in major_criminal_sections[1:-4]:
        # Get season link, move on if this fails
        season_url = get_season_url(section)
        if season_url is None:
            continue

        # Send a GET request and create BeautifulSoup object response
        season_response = requests.get(season_url)
        season_soup = BeautifulSoup(season_response.text, "html.parser")

        # Parse season criminals
        gallery_divs = season_soup.find_all("div", class_="wikia-gallery-item")
        for div in gallery_divs:
            # Get link to criminal page, move on if this fails
            criminal_url = get_criminal_url(div)
            if criminal_url is None:
                continue

            # Send a GET request and create BeautifulSoup object response
            criminal_response = requests.get(criminal_url)
            criminal_soup = BeautifulSoup(
                criminal_response.text, "html.parser"
            )

            # Parse criminal soup
            criminal = parse_criminal_soup(criminal_soup)
            major_criminals.append(criminal)

    # Create a JSON file and write the criminals' data to it
    with open(args.export_path, "w") as json_file:
        json.dump(major_criminals, json_file, indent=4)
