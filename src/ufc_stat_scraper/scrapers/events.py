import requests
from bs4 import BeautifulSoup
from fights import fights_scraper
from helper_functions import get_page, polite_sleep, is_today_after
import json
def events_scraper():

    url = "http://ufcstats.com/statistics/events/completed?page=all" #url to all events page of ufcstats.com

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

    with requests.Session() as session: #start a session 
        session.headers.update(HEADERS) #update session with headers

        response = session.get(url, timeout=10) #get request to url
        response.raise_for_status() #checks for good connection and stops if not
        html = response.text #assign response text to variable

        event_soup = BeautifulSoup(html, "html.parser") #parse html with BS4 - turning it into a soup object which can be searched
        
        event_list = event_soup.find_all("a", class_=["b-link", "b-link_style_white"], href=True) #creates a list of all a tags with a link to a specific event page
        hrefs = [a["href"] for a in event_list] #rips out just the hrefs from the a tags and puts them in a list
        test = event_soup.find("span", class_="b-statistics__date").get_text(strip=True)
        if is_today_after(test) == False:
            hrefs = hrefs[1:]
        hrefs = hrefs[:-30] #removes last 30 hrefs which are not under the unified MMA ruleset
        print("step 1")
        
        #print(hrefs)
        with open("data.jsonl", "a", encoding="utf-8") as f:
            print("opened file")
            for href in hrefs:
                html = get_page(session, href)
                if html is None:
                    continue
                print("step 2")
                fights_scraper(session, href, f) #calls fights_scraper function for each event link found
                polite_sleep() #polite sleep between requests
       
    return 


if __name__ == "__main__":
    events_scraper()
