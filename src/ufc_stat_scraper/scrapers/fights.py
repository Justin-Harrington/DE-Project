import requests
from bs4 import BeautifulSoup

def fights_scraper():
    url = "http://ufcstats.com/event-details/bd92cf5da5413d2a" #url to a events page of ufcstats.com for testing

    HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),

    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    } #default headers for web scraping requests

    session = requests.Session() 
    session.headers.update(HEADERS) #update session with headers
    response = session.get(url, timeout=10) #get request to url
    response.raise_for_status() #checks for good connection and stops if not
    html = response.text #assign response text to variable
    
    fight_soup = BeautifulSoup(html, "html.parser") #parse html with BS4 - turning it into a soup object which can be searched
    fight_list = fight_soup.find_all("tr", class_=["b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click"]) #creates a list of all tr tags with a link to a specific fight page
    hrefs = [tr["data-link"] for tr in fight_list] #rips out just the hrefs from the tr tags and puts them in a list
    event_name = fight_soup.find("span", class_=["b-content__title-highlight"]).get_text(strip=True) #gets event name and cleans it up
    header_tags = fight_soup.find_all("li", class_=["b-list__box-list-item"]) #finds the li tags that contain event date and location
    event_date = ( #grabs and cleans up event date
        header_tags[0]
        .get_text(strip=True)
        .replace("Date:","")
        ) 
    event_location = ( #grabs and cleans up event location
        header_tags[1]
        .get_text(strip=True)
        .replace("Location:", "")
    ) 

    event_info = { #dictionary to hold event info
    "event_name": event_name,
    "event_date_parsed": event_date,
    "location_raw": event_location,
    } 

    print(event_info) #prints event info for testing


    return



if __name__ == "__main__":
    fights_scraper()

# def scrape_fight_stats(session, fight_items):
#     for item in fight_items:
#         fight_url = item["fight_url"]
#         event_context = {
#             "event_name": item["event_name"],
#             "event_date": item["event_date"],
#             "event_location": item["event_location"],
#         }

#         fight_data = scrape_single_fight(session, fight_url)
#         fight_data.update(event_context)

#         write_jsonl(fight_data)
