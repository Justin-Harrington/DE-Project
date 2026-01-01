from time import time
import requests
from bs4 import BeautifulSoup
from helper_functions import generate_fight_schema, parse_int, parse_of, parse_pct, parse_time

def fights_scraper():

    #url = "http://ufcstats.com/fight-details/b2218930b982d9b6" #url to belal bs ian cuck garry fight page for testing
    url = "http://ufcstats.com/fight-details/4a0db214d9721d6e" #url to merab vs yan - 5 0f 5 rnds 
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

    method = fight_soup.find("i", class_=["b-fight-details__text-item_first"]).get_text(strip=True) #finds type of victory and stores it in dictionary
    data["method"] = method[7:]

    fight_time = fight_soup.find_all("i", class_=["b-fight-details__text-item"]) #finds fight time details, referee name and stores them in dictionary
    data["total_rounds"] = int(fight_time[0].get_text(strip=True)[-1])
    data["total_fight_time"] = fight_time[1].get_text(strip=True)[5:]
    data['total_rounds'] = fight_time[2].get_text(strip=True)[12]
    data["referee"] = fight_time[3].get_text(strip=True)[8:]
    
    method_details = fight_soup.find_all("p", class_=["b-fight-details__text"]) #finds method of victory and stores it in dictionary         
    data["method_details"] = method_details[1].get_text(strip=True)[8:]

    schema = generate_fight_schema() # generate schema for fight data 
    data.update(schema) # adds the schema to the data dictionary

    stats_table = fight_soup.find_all("p", class_=["b-fight-details__table-text"]) #finds number of knockdowns for each fighter and stores them in dictionary

    ROUND_STRUCTURE_PART_1 = [
    {
        "parser": "int",
        "fields": ["knockdowns"],
    },
    {
        "parser": "of",
        "fields": ["sig_strikes_landed", "sig_strikes_attempted"],
    },
    {
        "parser": "pct",
        "fields": ["sig_strike_pct"],
    },
        {
        "parser": "of",
        "fields": ["strikes_landed", "strikes_attempted"],
    },
    {
        "parser": "of",
        "fields": ["takedowns_landed", "takedowns_attempted"],
    },
    {
        "parser": "pct",
        "fields": ["takedowns_pct"],
    },
    {
        "parser": "int",
        "fields": ["sub_attempted"],
    },
    {
        "parser": "int",
        "fields": ["reversals"],
    },
    {
        "parser": "time",
        "fields": ["control_time"],
    }
    ]

    ROUND_STRUCTURE_PART_2 = [
        {
        "parser": "of",
        "fields": ["sig_strikes_head_landed", "sig_strikes_head_attempted"],
    },
        {
        "parser": "of",
        "fields": ["sig_strikes_body_landed", "sig_strikes_body_attempted"],
    },
        {
        "parser": "of",
        "fields": ["sig_strikes_leg_landed", "sig_strikes_leg_attempted"],
    },
        {
        "parser": "of",
        "fields": ["sig_strikes_distance_landed", "sig_strikes_distance_attempted"],
    },
        {
        "parser": "of",
        "fields": ["sig_strikes_clinch_landed", "sig_strikes_clinch_attempted"],
    },
        {
        "parser": "of",
        "fields": ["sig_strikes_ground_landed", "sig_strikes_ground_attempted"],
    }
    ]

    round_order = ["total"] + [str(i) for i in range(1, int(data["total_rounds"]) + 1)]
    index = 2
    sides=["red", "blue"]
    #print(stats_table[19].get_text(strip=True))
    for round in round_order:
        for x in ROUND_STRUCTURE_PART_1:
                for side in sides:
                    if len(x["fields"]) == 1:
                        if x["parser"] == "int":
                            for y in x['fields']:
                                #print(stats_table[index].get_text(strip=True))
                                data[f"{side}_{y}_{round}"] = parse_int((stats_table[index].get_text(strip=True)))
                                #print([f"{side}_{y}_{round}",data[f"{side}_{y}_{round}"], f"{index}", 'int'])
                                index += 1 
                        elif x["parser"] == "pct":
                            for y in x['fields']:
                                data[f"{side}_{y}_{round}"] = parse_pct(stats_table[index].get_text(strip=True))
                                #print([f"{side}_{y}_{round}", data[f"{side}_{y}_{round}"], f"{index}", 'pct'])
                                index += 1
                        elif x["parser"] == "time":
                            #print('in time parser')
                            for y in x['fields']:
                                data[f"{side}_{y}_{round}"] = parse_time(stats_table[index].get_text(strip=True))
                                #print([f"{side}_{y}_{round}", data[f"{side}_{y}_{round}"], f"{index}", 'time'])
                                index += 1

                    elif len(x["fields"]) == 2:
                        #print([stats_table[index].get_text(strip=True), f"{index}", 'before_split'])
                        holder = parse_of(stats_table[index].get_text(strip=True))
                        landed = holder[0]
                        attempted = holder[1]
                        data[f"{side}_{x['fields'][0]}_{round}"] = landed
                        data[f"{side}_{x['fields'][1]}_{round}"] = attempted
                        #print([f"{side}_{x['fields'][0]}_{round}", data[f"{side}_{x['fields'][0]}_{round}"],f"{index}", 'of'])
                        #print([f"{side}_{x['fields'][1]}_{round}", data[f"{side}_{x['fields'][1]}_{round}"],f"{index}", 'of'])
                        index += 1
        index += 2
    
    index += 4

    for round in round_order: #second pass part for significant strikes stats
        for x in ROUND_STRUCTURE_PART_2:
                for side in sides:
                    if len(x["fields"]) == 1:
                        if x["parser"] == "int":
                            for y in x['fields']:
                                #print(stats_table[index].get_text(strip=True))
                                data[f"{side}_{y}_{round}"] = parse_int((stats_table[index].get_text(strip=True)))
                                #print([f"{side}_{y}_{round}",data[f"{side}_{y}_{round}"], f"{index}", 'int'])
                                index += 1 
                        elif x["parser"] == "pct":
                            for y in x['fields']:
                                data[f"{side}_{y}_{round}"] = parse_pct(stats_table[index].get_text(strip=True))
                                #print([f"{side}_{y}_{round}", data[f"{side}_{y}_{round}"], f"{index}", 'pct'])
                                index += 1
                        elif x["parser"] == "time":
                            #print('in time parser')
                            for y in x['fields']:
                                data[f"{side}_{y}_{round}"] = parse_time(stats_table[index].get_text(strip=True))
                                #print([f"{side}_{y}_{round}", data[f"{side}_{y}_{round}"], f"{index}", 'time'])
                                index += 1

                    elif len(x["fields"]) == 2:
                        #print([stats_table[index].get_text(strip=True), f"{index}", 'before_split'])
                        holder = parse_of(stats_table[index].get_text(strip=True))
                        landed = holder[0]
                        attempted = holder[1]
                        data[f"{side}_{x['fields'][0]}_{round}"] = landed
                        data[f"{side}_{x['fields'][1]}_{round}"] = attempted
                        #print([f"{side}_{x['fields'][0]}_{round}", data[f"{side}_{x['fields'][0]}_{round}"],f"{index}", 'of'])
                        #print([f"{side}_{x['fields'][1]}_{round}", data[f"{side}_{x['fields'][1]}_{round}"],f"{index}", 'of'])
                        index += 1
        index += 6


    for key, value in data.items():
        if value is not None:
            print(f"{key}: {value}")
    #print(ROUND_STRUCTURE_PART_1[1]['fields'][0])
    
    #print(stats_table[22].get_text(strip=True))
    #print(stats_table[39].get_text(strip=True))
    return

fights_scraper()