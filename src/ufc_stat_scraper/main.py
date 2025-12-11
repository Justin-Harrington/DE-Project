import requests
from bs4 import BeautifulSoup


def main():
    url = "http://ufcstats.com/statistics/events/completed"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    print(response)
    #print(response.status_code)
    #print(response.headers["Content-Type"])


if __name__ == "__main__":
    main()