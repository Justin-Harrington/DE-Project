
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
    for side in sides:
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
    if value is None:
        return None
    else:
        return value.strip()



# def parse_pct(value):
#     if value is None:
#         return None
#     value = value.strip("%")
#     return float(value) / 100.0

