import requests
from bs4 import BeautifulSoup

def fights_scraper():
    url = "http://ufcstats.com/fight-details/10cca6f437922b6c" #url to a events page of ufcstats.com for testing

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
    #print(html)  # For debugging: print the raw HTML content
    fight_soup = BeautifulSoup(html, "html.parser") #parse html with BS4 - turning it into a soup object which can be searched
    print(type(fight_soup))  # For debugging: print the raw HTML content
    nickname = fight_soup.find("p", class_=["b-fight-details__person-title"]).get_text(strip=True) 
    print(nickname)
    return
fights_scraper()