import requests
from bs4 import BeautifulSoup
from stats import scraper
from helper_functions import get_page, polite_sleep
import json
def fights_scraper(session, url, f):
    #url = "http://ufcstats.com/event-details/bd92cf5da5413d2a" #url to a events page of ufcstats.com for testing
    print("entered fights scraper")
    response = session.get(url, timeout=10) #get request to url
    response.raise_for_status() #checks for good connection and stops if not
    html = response.text #assign response text to variable
    print("fights page -got html")
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
    
    for href in hrefs:
        html = get_page(session, href)
        if html is None:
            continue
        print (href)
        scraper(session, event_info, href, f) #calls fights_scraper function for each event link found
        polite_sleep() #polite sleep between requests

    #print(event_info) #prints event info for testing


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
