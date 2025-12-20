import requests
from bs4 import BeautifulSoup

def fights_scraper():
    #url = "http://ufcstats.com/fight-details/a5a81a39ccf9b680" #url to royval vs kape fight page for testing
    url = "http://ufcstats.com/fight-details/b3d2ac2244e4f791" #url to terrance mckinney vs chris duncan fight page for testing
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
    data = {}
    session = requests.Session() 
    session.headers.update(HEADERS) #update session with headers
    response = session.get(url, timeout=10) #get request to url
    response.raise_for_status() #checks for good connection and stops if not
    html = response.text #assign response text to variable
   
    fight_soup = BeautifulSoup(html, "html.parser") #parse html with BS4 - turning it into a soup object which can be searched
    
    nickname = fight_soup.find_all("p", class_=["b-fight-details__person-title"]) #finds nicknames of fighters and stores them in dictionary
    data["r_nickname"] = nickname[0].get_text(strip=True).strip('"\'')
    data["b_nickname"] = nickname[1].get_text(strip=True).strip('"\'')

    outcome = fight_soup.find_all("i", class_=["b-fight-details__person-status", "b-fight-details__person-status_style_green"]) #finds outcome for each fighter and stores them in dictionary
    data["r_outcome"] = outcome[0].get_text(strip=True)
    data["b_outcome"] = outcome[1].get_text(strip=True)

    weightclass = fight_soup.find("i", class_=["b-fight-details__fight-title"]).get_text(strip=True) #finds weightclass of fight and stores it in dictionary
    weightclass = weightclass.join(weightclass.split()[:-1])
    data["weightclass"] = weightclass

    method = fight_soup.find("i", class_=["b-fight-details__text-item_first"]).get_text(strip=False) #finds type of victory and stores it in dictionary
    method = method.join(method.split()[1:]).strip()
    data["method"] = method

    fight_time = fight_soup.find_all("i", class_=["b-fight-details__text-item"]) #finds fight time details, referee name and stores them in dictionary
    data["total_rounds"] = fight_time[0].get_text(strip=True)[-1]
    data["total_fight_time"] = fight_time[1].get_text(strip=True)[5:]
    data['total_rounds'] = fight_time[2].get_text(strip=True)[12]
    data["referee"] = fight_time[3].get_text(strip=True)[8:]
    
    method_details = fight_soup.find_all("p", class_=["b-fight-details__text"]) #finds method of victory and stores it in dictionary         
    data["method_details"] = method_details[1].get_text(strip=True)[8:]
    #print(data) #prints event info for testing


    
    return 


fights_scraper()