from __future__ import annotations
import time
import random
import requests
import logging
from datetime import date, datetime
from typing import Union

# def extract_judges_scores(text: str) -> list[str]:


def trim_words(text: str, remove_start: int, remove_end: int) -> str:
    """
    Removes `remove_start` words from the beginning and
    `remove_end` words from the end of a string.

    Words are defined as whitespace-separated tokens.

    Returns an empty string if nothing remains.
    """
    if not text:
        return ""

    if remove_start < 0 or remove_end < 0:
        raise ValueError("remove_start and remove_end must be >= 0")

    words = text.split()

    if remove_start + remove_end >= len(words):
        return ""

    return " ".join(words[remove_start:len(words) - remove_end])


def is_today_after(date_str: str, fmt: str = "%B %d, %Y") -> bool: 
    """
    Return True if today's date is strictly AFTER the given date string.

    Example input: "December 13, 2025"
    Default format: "%B %d, %Y"
    """
    target = datetime.strptime(date_str.strip(), fmt).date()
    return date.today() > target


def polite_sleep(): # will sleep between requests to avoid overloading server
    wait = random.uniform(1.5, 3.5)
    time.sleep(wait)

def get_page(session, url, max_retries=3): #robust page retrieval with retries and error handling
    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(url, timeout=15)

            if response.status_code == 200:
                logging.info(f"200 OK | {url}")
                return response.text

            elif response.status_code in (429, 503):
                wait = random.uniform(10, 30)
                logging.warning(
                    f"{response.status_code} rate-limited | {url} | sleeping {wait:.1f}s"
                )
                time.sleep(wait)

            elif response.status_code == 403:
                logging.error(f"403 FORBIDDEN | {url} | stopping scrape")
                raise RuntimeError("Blocked by server")

            else:
                logging.warning(
                    f"{response.status_code} unexpected status | {url}"
                )

        except requests.RequestException as e:
            wait = random.uniform(5, 15)
            logging.error(
                f"Request error | {url} | {e} | retry {attempt}/{max_retries} | sleeping {wait:.1f}s"
            )
            time.sleep(wait)

    logging.error(f"FAILED after {max_retries} retries | {url}")
    return None

def generate_fight_schema(
    sides=("red", "blue"),
    rounds=5,
):
    base_metrics = [
        "knockdowns",

        "sig_strikes_landed",
        "sig_strikes_attempted",
        "sig_strike_pct",

        "strikes_landed",
        "strikes_attempted",

        "takedowns_landed",
        "takedowns_attempted",
        "takedown_pct",

        "sub_attempted",
        "reversals",
        "control_time",

        # Sig strike breakdowns
        "sig_strikes_head_landed",
        "sig_strikes_head_attempted",
        "sig_strikes_body_landed",
        "sig_strikes_body_attempted",
        "sig_strikes_leg_landed",
        "sig_strikes_leg_attempted",

        "sig_strikes_distance_landed",
        "sig_strikes_distance_attempted",
        "sig_strikes_clinch_landed",
        "sig_strikes_clinch_attempted",
        "sig_strikes_ground_landed",
        "sig_strikes_ground_attempted",
    ]

    schema = {}
    rounds = int(rounds)
    schema["validation_status"] = None
    schema["validation_errors"] = None
    schema["parser_version"] = None
    schema["scraped_at_utc"] = None
    schema["url"] = None
    schema["event_name"] = None
    schema["event_date_parsed"] = None
    schema["location_raw"] = None
    schema["weightclass"] = None
    schema["method"] = None
    schema["ending_round"] = None
    schema["total_fight_time"] = None
    schema["total_rounds"] = None
    schema["referee"] = None
    schema["method_details"] = None
    schema["title_fight"] = None
    schema["sex"] = None
    schema["judge_1"] = None
    schema["judge_2"] = None
    schema["judge_3"] = None
    schema["judge_1_score_red"] = None
    schema["judge_1_score_blue"] = None
    schema["judge_2_score_red"] = None
    schema["judge_2_score_blue"] = None
    schema["judge_3_score_red"] = None
    schema["judge_3_score_blue"] = None
    for side in sides:
        schema[f"{side}_nickname"] = None
        schema[f"{side}_outcome"] = None
        for metric in base_metrics:
            for r in range(1, rounds + 1):
                schema[f"{side}_{metric}_round_{r}"] = None
            schema[f"{side}_{metric}_total"] = None
    return schema


def index_setup(rounds):
    SECTION_1_PATTERN = {
    "skip": 2,
    "take": 18,
}
    SECTION_2_PATTERN = {
    "skip": 6,
    "take": 12,
}

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
    return
#index_setup(3)

def parse_int(value):
    try:
        return int(value)
    except (AttributeError, ValueError):
        return None

def parse_of(value):
    if value is None:
        return [None, None]
    landed, attempted = value.split("of")
    return [int(landed.strip()), int(attempted.strip())]

def parse_pct(value):
    try:
        return float(value.strip().strip("%")) / 100.0
    except (AttributeError, ValueError):
        return None

def parse_time(value):
    """
    Parse a time string in 'm:ss' format and return total seconds as int.
    Returns None if value is None or empty.
    Raises ValueError for invalid formats.
    """
    if value is None:
        return None

    value = value.strip()
    if not value:
        return None

    try:
        minutes_str, seconds_str = value.split(":")
        minutes = int(minutes_str)
        seconds = int(seconds_str)

        if seconds < 0 or seconds >= 60:
            raise ValueError("Seconds must be between 0 and 59")

        return minutes * 60 + seconds

    except Exception as e:
        raise ValueError(f"Invalid time format '{value}', expected m:ss") from e




# def parse_pct(value):
#     if value is None:
#         return None
#     value = value.strip("%")
#     return float(value) / 100.0

