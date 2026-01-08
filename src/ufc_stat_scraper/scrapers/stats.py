from time import time
import requests
from bs4 import BeautifulSoup
from helper_functions import generate_fight_schema, parse_int, parse_of, parse_pct, parse_time, get_page, polite_sleep, trim_words
import json

def scraper(session, event_info, url, f):

    #url = "http://ufcstats.com/fight-details/b2218930b982d9b6" #url to belal bs ian cuck garry fight page for testing
    #url = "http://ufcstats.com/fight-details/4a0db214d9721d6e" #url to merab vs yan - 5 0f 5 rnds 
    #url = "http://ufcstats.com/fight-details/dfa692db6d39330c" # url to pantoja vs van

    response = session.get(url, timeout=10) #get request to url
    response.raise_for_status() #checks for good connection and stops if not
    html = response.text #assign response text to variable
    
    data = generate_fight_schema()
    fight_soup = BeautifulSoup(html, "html.parser") #parse html with BS4 - turning it into a soup object which can be searched
    data["url"] = url
    data["event_name"] = event_info["event_name"]
    data["event_date_parsed"] = event_info["event_date_parsed"]
    data["location_raw"] = event_info["location_raw"]

    nickname = fight_soup.find_all("p", class_=["b-fight-details__person-title"]) #finds nicknames of fighters and stores them in dictionary
    data["red_nickname"] = nickname[0].get_text(strip=True).strip('"\'').strip() or None
    data["blue_nickname"] = nickname[1].get_text(strip=True).strip('"\'').strip() or None

    outcome = fight_soup.find_all("i", class_=["b-fight-details__person-status", "b-fight-details__person-status_style_green"]) #finds outcome for each fighter and stores them in dictionary
    data["red_outcome"] = outcome[0].get_text(strip=True)
    data["blue_outcome"] = outcome[1].get_text(strip=True)

    weightclass = fight_soup.find("i", class_=["b-fight-details__fight-title"]).get_text(strip=True) #finds weightclass of fight and stores it in dictionary
    if "Women" in weightclass:
        data["sex"] = 'W'
        if "Title" in weightclass:
            data["weightclass"] = trim_words(weightclass, 2, 2)
            data["title_fight"] = True
        else:
            data["weightclass"] = trim_words(weightclass, 1, 1)
            data["title_fight"] = False
        
    elif "Title" in weightclass:
        data["weightclass"] = trim_words(weightclass, 1, 2)
        data["title_fight"] = True
        data["sex"] = "M"
    else:
        data["weightclass"] = trim_words(weightclass,0,1)
        data["title_fight"] = False
        data["sex"] = "M"


    method = fight_soup.find("i", class_=["b-fight-details__text-item_first"]).get_text(strip=True) #finds type of victory and stores it in dictionary
    if "Decision" in data["method"]:     
        decision_list = method_details[1].get_text().strip("/n").replace(".","").replace("-","").split()
        data["judge_1"] = decision_list[1] + " " + decision_list[2]
        data["judge_2"] = decision_list[5] + " " + decision_list[6]
        data["judge_3"] = decision_list[9] + " " + decision_list[10]
        data["judge_1_score_red"] = decision_list[3]
        data["judge_1_score_blue"] = decision_list[4]
        data["judge_2_score_red"] = decision_list[7]
        data["judge_2_score_blue"] = decision_list[8]
        data["judge_3_score_red"] = decision_list[11]
        data["judge_3_score_blue"] = decision_list[12]

    else:
        data["method_details"] = method_details[1].get_text(strip=True).strip()[8:]

    fight_time = fight_soup.find_all("i", class_=["b-fight-details__text-item"]) #finds fight time details, referee name and stores them in dictionary
    data["ending_round"] = int(fight_time[0].get_text(strip=True)[-1])
    #print(data["ending_round"])
    data["total_fight_time"] = fight_time[1].get_text(strip=True)[5:]
    data['total_rounds'] = fight_time[2].get_text(strip=True)[12]
    data["referee"] = fight_time[3].get_text(strip=True)[8:]
    
    method_details = fight_soup.find_all("p", class_=["b-fight-details__text"]) #finds method of victory and stores it in dictionary         
    data["method_details"] = method_details[1].get_text(strip=True)[8:]

    # generate schema for fight data 
    #print(data)

    stats_table = fight_soup.find_all("p", class_=["b-fight-details__table-text"]) #finds number of knockdowns for each fighter and stores them in dictionary

    ROUND_STRUCTURE_PART_1 = [ #first part of structure for parsing and using correct parsers
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

    print(data["ending_round"])
    round_order = ["total"] + [
    f"round_{i}" for i in range(1, int(data["ending_round"]) + 1)
    ]

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
    
    f.write(json.dumps(data) + "\n")
    print("write to file")
    # for key, value in data.items():
    #     if value is not None:
    #         print(f"{key}: {value}")

    # for key, value in data.items():
    #     print(f"{key}: {value}   _type_{type(value)}")   

    # return

