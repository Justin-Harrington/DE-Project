import requests
from bs4 import BeautifulSoup


def main():
    url = "http://ufcstats.com/statistics/events/completed"
    
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
}


    response = requests.get(url, headers=headers)
    print(response)
    #print(response.status_code)
    #print(response.headers["Content-Type"])


if __name__ == "__main__":
    main()