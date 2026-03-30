"""
Country reference data for tagging.
Maps country names, demonyms, cities, and abbreviations to ISO-3166 alpha-2 codes.

Includes humanitarian-priority countries (Somalia, Sudan, DRC, Yemen, etc.)
with expanded REGION_KEYWORDS and HUMANITARIAN_REGIONS for dashboard filtering.
"""

from typing import Dict, List, Set

# ---------------------------------------------------------------------------
# Country mappings: ISO code -> list of keywords
# (unchanged from original except additions marked with # NEW)
# ---------------------------------------------------------------------------

COUNTRY_KEYWORDS: Dict[str, List[str]] = {
    "US": [
        "united states", "usa", "u.s.", "u.s.a", "america", "american", "americans",
        "washington dc", "new york", "california", "texas", "florida",
    ],
    "GB": [
        "united kingdom", "uk", "u.k.", "britain", "great britain", "british",
        "england", "english", "scotland", "scottish", "wales", "welsh",
        "northern ireland", "london", "manchester", "birmingham",
        "fcdo", "foreign commonwealth development office",  # NEW: FCDO = UK
    ],
    "DE": [
        "germany", "german", "germans", "deutschland",
        "berlin", "munich", "hamburg", "frankfurt",
    ],
    "FR": [
        "france", "french", "paris", "lyon", "marseille",
    ],
    "CN": [
        "china", "chinese", "beijing", "shanghai", "guangzhou", "shenzhen",
        "prc", "people's republic of china",
    ],
    "IN": [
        "india", "indian", "indians", "new delhi", "delhi", "mumbai",
        "bangalore", "bengaluru", "hyderabad",
    ],
    "JP": [
        "japan", "japanese", "tokyo", "osaka", "kyoto",
    ],
    "KR": [
        "south korea", "korea", "korean", "koreans", "seoul", "busan",
        "republic of korea", "rok",
    ],
    "KP": [
        "north korea", "dprk", "pyongyang", "democratic people's republic of korea",
    ],
    "AU": [
        "australia", "australian", "australians", "sydney", "melbourne",
        "brisbane", "perth", "canberra",
    ],
    "CA": [
        "canada", "canadian", "canadians", "toronto", "montreal", "vancouver",
        "ottawa", "calgary",
    ],
    "ES": [
        "spain", "spanish", "madrid", "barcelona", "seville",
    ],
    "IT": [
        "italy", "italian", "italians", "rome", "milan", "naples",
        "florence", "venice",
    ],
    "NL": [
        "netherlands", "dutch", "holland", "amsterdam", "rotterdam",
        "the hague",
    ],
    "BE": [
        "belgium", "belgian", "belgians", "brussels", "antwerp",
    ],
    "PL": [
        "poland", "polish", "poles", "warsaw", "krakow", "gdansk",
    ],
    "SE": [
        "sweden", "swedish", "swedes", "stockholm", "gothenburg",
    ],
    "NO": [
        "norway", "norwegian", "norwegians", "oslo", "bergen",
    ],
    "DK": [
        "denmark", "danish", "danes", "copenhagen",
    ],
    "BR": [
        "brazil", "brazilian", "brazilians", "brasilia", "sao paulo",
        "rio de janeiro", "rio",
    ],
    "MX": [
        "mexico", "mexican", "mexicans", "mexico city", "guadalajara",
    ],
    "AR": [
        "argentina", "argentinian", "argentinians", "buenos aires",
    ],
    "CL": [
        "chile", "chilean", "chileans", "santiago",
    ],
    "ZA": [
        "south africa", "south african", "south africans",
        "johannesburg", "cape town", "pretoria", "durban",
    ],
    "SA": [
        "saudi arabia", "saudi", "saudis", "riyadh", "jeddah",
    ],
    "AE": [
        "united arab emirates", "uae", "u.a.e", "emirates", "dubai", "abu dhabi",
    ],
    "IL": [
        "israel", "israeli", "israelis", "jerusalem", "tel aviv",
    ],
    "TR": [
        "turkey", "turkish", "turks", "ankara", "istanbul",
    ],
    "RU": [
        "russia", "russian", "russians", "moscow", "st petersburg",
        "petersburg", "soviet", "ussr",
    ],
    "UA": [
        "ukraine", "ukrainian", "ukrainians", "kyiv", "kiev", "odessa",
        "kharkiv", "zaporizhzhia", "kherson", "mariupol",  # NEW: conflict cities
    ],
    "EG": [
        "egypt", "egyptian", "egyptians", "cairo",
    ],
    "NG": [
        "nigeria", "nigerian", "nigerians", "lagos", "abuja",
        "borno", "northeast nigeria",  # NEW: conflict zones
    ],
    "KE": [
        "kenya", "kenyan", "kenyans", "nairobi",
    ],
    "ID": [
        "indonesia", "indonesian", "indonesians", "jakarta",
    ],
    "MY": [
        "malaysia", "malaysian", "malaysians", "kuala lumpur",
    ],
    "SG": [
        "singapore", "singaporean", "singaporeans",
    ],
    "VN": [
        "vietnam", "vietnamese", "hanoi", "ho chi minh",
    ],
    "TH": [
        "thailand", "thai", "bangkok",
    ],
    "PH": [
        "philippines", "filipino", "filipinos", "manila",
    ],
    "NZ": [
        "new zealand", "new zealander", "new zealanders", "kiwi", "kiwis",
        "wellington", "auckland",
    ],
    "IE": [
        "ireland", "irish", "dublin",
    ],
    "PT": [
        "portugal", "portuguese", "lisbon", "porto",
    ],
    "GR": [
        "greece", "greek", "greeks", "athens",
    ],
    "AT": [
        "austria", "austrian", "austrians", "vienna",
    ],
    "CH": [
        "switzerland", "swiss", "zurich", "geneva", "bern",
    ],
    "FI": [
        "finland", "finnish", "finns", "helsinki",
    ],
    "CZ": [
        "czech republic", "czech", "czechs", "czechia", "prague",
    ],
    "HU": [
        "hungary", "hungarian", "hungarians", "budapest",
    ],
    "RO": [
        "romania", "romanian", "romanians", "bucharest",
    ],

    # ------------------------------------------------------------------
    # NEW: Humanitarian-priority countries
    # ------------------------------------------------------------------

    # East Africa / Horn
    "SO": [
        "somalia", "somali", "mogadishu", "puntland", "somaliland",
        "jubaland", "al-shabaab",
    ],
    "SD": [
        "sudan", "sudanese", "khartoum", "darfur", "kordofan",
        "blue nile", "rapid support forces", "rsf", "saf",
        "sudanese armed forces",
    ],
    "SS": [
        "south sudan", "south sudanese", "juba", "jonglei",
        "unity state", "upper nile",
    ],
    "ET": [
        "ethiopia", "ethiopian", "addis ababa", "tigray", "amhara",
        "oromia", "afar", "tplf",
    ],
    "ER": [
        "eritrea", "eritrean", "asmara",
    ],
    "DJ": [
        "djibouti", "djiboutian",
    ],
    "UG": [
        "uganda", "ugandan", "kampala",
    ],
    "RW": [
        "rwanda", "rwandan", "kigali",
    ],
    "BI": [
        "burundi", "burundian", "bujumbura",
    ],
    "TZ": [
        "tanzania", "tanzanian", "dar es salaam",
    ],

    # Central Africa
    "CD": [
        "democratic republic of congo", "drc", "dr congo", "congo",
        "kinshasa", "goma", "north kivu", "south kivu",
        "ituri", "kasai", "m23", "adf",
    ],
    "CF": [
        "central african republic", "car", "c.a.r.", "bangui",
        "seleka", "anti-balaka",
    ],
    "CM": [
        "cameroon", "cameroonian", "yaounde", "douala",
        "anglophone crisis", "northwest cameroon", "southwest cameroon",
    ],
    "TD": [
        "chad", "chadian", "n'djamena", "lake chad",
    ],

    # West Africa / Sahel
    "ML": [
        "mali", "malian", "bamako", "mopti", "segou", "kidal",
        "wagner", "jnim",
    ],
    "BF": [
        "burkina faso", "burkinabe", "ouagadougou",
        "sahel region", "est region",
    ],
    "NE": [
        "niger", "nigerien", "niamey",
    ],
    "GN": [
        "guinea", "guinean", "conakry",
    ],
    "SL": [
        "sierra leone", "sierra leonean", "freetown",
    ],
    "LR": [
        "liberia", "liberian", "monrovia",
    ],

    # Middle East
    "YE": [
        "yemen", "yemeni", "sanaa", "aden", "hodeidah", "houthi",
        "ansarallah", "marib",
    ],
    "SY": [
        "syria", "syrian", "damascus", "aleppo", "idlib",
        "deir ez-zor", "northeast syria",
    ],
    "IQ": [
        "iraq", "iraqi", "baghdad", "mosul", "basra", "erbil",
    ],
    "PS": [
        "palestine", "palestinian", "gaza", "west bank", "rafah",
        "khan younis", "ramallah", "unrwa",
    ],
    "LB": [
        "lebanon", "lebanese", "beirut", "south lebanon",
    ],
    "AF": [
        "afghanistan", "afghan", "kabul", "kandahar", "herat",
        "taliban", "islamic emirate",
    ],

    # South / Southeast Asia
    "MM": [
        "myanmar", "burmese", "naypyidaw", "yangon", "rakhine",
        "rohingya", "chin state", "tatmadaw", "sac",
    ],
    "BD": [
        "bangladesh", "bangladeshi", "dhaka", "cox's bazar",
    ],
    "PK": [
        "pakistan", "pakistani", "islamabad", "karachi", "lahore",
        "khyber pakhtunkhwa", "balochistan",
    ],
    "NP": [
        "nepal", "nepali", "kathmandu",
    ],

    # Caribbean / Latin America
    "HT": [
        "haiti", "haitian", "port-au-prince", "cite soleil",
        "martissant", "gang violence haiti",
    ],
    "VE": [
        "venezuela", "venezuelan", "caracas", "maracaibo",
    ],
    "CO": [
        "colombia", "colombian", "bogota", "medellin",
    ],
    "HN": [
        "honduras", "honduran", "tegucigalpa",
    ],
    "GT": [
        "guatemala", "guatemalan", "guatemala city",
    ],

    # Southern Africa
    "MZ": [
        "mozambique", "mozambican", "maputo", "cabo delgado",
        "ansar al-sunna",
    ],
    "ZW": [
        "zimbabwe", "zimbabwean", "harare",
    ],
    "MW": [
        "malawi", "malawian", "lilongwe",
    ],
    "MG": [
        "madagascar", "malagasy", "antananarivo",
    ],
}


# ---------------------------------------------------------------------------
# Ambiguous terms (unchanged)
# ---------------------------------------------------------------------------

AMBIGUOUS_KEYWORDS: Dict[str, str] = {
    "georgia": "GE",
}


# ---------------------------------------------------------------------------
# Region keywords — EXPANDED for humanitarian geographic groupings
#
# These are used two ways:
#   1. The CountryTagger engine detects them and stores in metadata["regions"]
#   2. The API uses them for the "region" filter on the dashboard
# ---------------------------------------------------------------------------

REGION_KEYWORDS: Dict[str, List[str]] = {
    # Original
    "EU": [
        "european union", "eu", "e.u.", "brussels", "european commission",
        "european parliament", "eurozone",
    ],

    # NEW: Humanitarian geographic groupings
    # These match how OCHA, ReliefWeb and FCDO refer to regions

    "East Africa": [
        "east africa", "horn of africa", "greater horn",
        "east african", "eastern africa",
    ],
    "West Africa": [
        "west africa", "west african", "western africa",
        "sahel", "sahelian", "lake chad basin",
        "ecowas",
    ],
    "Central Africa": [
        "central africa", "central african", "great lakes",
        "great lakes region", "central african region",
    ],
    "Southern Africa": [
        "southern africa", "southern african", "sadc",
    ],
    "Middle East": [
        "middle east", "middle eastern", "mena",
        "near east", "levant", "gulf region",
        "occupied territory", "occupied palestinian territory", "opt",
    ],
    "South Asia": [
        "south asia", "south asian",
    ],
    "Southeast Asia": [
        "southeast asia", "southeast asian", "asean",
    ],
    "Ukraine / Eastern Europe": [
        "eastern europe", "eastern european",
    ],
    "Latin America": [
        "latin america", "latin american", "central america",
        "caribbean", "northern triangle",
    ],
    "Global": [
        "global", "worldwide", "international", "cross-border",
    ],
}


# ---------------------------------------------------------------------------
# Humanitarian region grouping
# Maps ISO country codes to their humanitarian region label.
# Used by the API to populate the "region" field on each article.
# ---------------------------------------------------------------------------

COUNTRY_TO_REGION: Dict[str, str] = {
    # East Africa / Horn
    "SO": "East Africa", "SD": "East Africa", "SS": "East Africa",
    "ET": "East Africa", "KE": "East Africa", "UG": "East Africa",
    "ER": "East Africa", "DJ": "East Africa", "RW": "East Africa",
    "BI": "East Africa", "TZ": "East Africa",
    # West Africa / Sahel
    "NG": "West Africa", "ML": "West Africa", "BF": "West Africa",
    "NE": "West Africa", "TD": "West Africa", "GN": "West Africa",
    "SL": "West Africa", "LR": "West Africa",
    # Central Africa
    "CD": "Central Africa", "CF": "Central Africa",
    "CM": "Central Africa",
    # Southern Africa
    "MZ": "Southern Africa", "ZW": "Southern Africa",
    "MW": "Southern Africa", "MG": "Southern Africa",
    "ZA": "Southern Africa",
    # Middle East
    "YE": "Middle East", "SY": "Middle East", "IQ": "Middle East",
    "PS": "Middle East", "LB": "Middle East", "AF": "Middle East",
    "IL": "Middle East",
    # South Asia
    "MM": "South Asia", "BD": "South Asia", "PK": "South Asia",
    "IN": "South Asia", "NP": "South Asia",
    # Southeast Asia
    "ID": "Southeast Asia", "PH": "Southeast Asia", "VN": "Southeast Asia",
    "TH": "Southeast Asia", "MY": "Southeast Asia",
    # Ukraine / Eastern Europe
    "UA": "Ukraine / Eastern Europe",
    # Latin America
    "HT": "Latin America", "VE": "Latin America", "CO": "Latin America",
    "HN": "Latin America", "GT": "Latin America",
    # Europe / Other donors
    "GB": "Europe", "DE": "Europe", "FR": "Europe",
}


def get_region_for_country(iso_code: str) -> str:
    """
    Return the humanitarian region label for a country ISO code.

    Args:
        iso_code: ISO 3166-1 alpha-2 code e.g. "SD"

    Returns:
        Region label string, or "Global / Other" if not mapped
    """
    return COUNTRY_TO_REGION.get(iso_code.upper(), "Global / Other")


# ---------------------------------------------------------------------------
# Utility functions (unchanged from original)
# ---------------------------------------------------------------------------

def detect_countries_in_text(text: str) -> List[str]:
    """Detect country codes in text based on keyword mentions."""
    if not text:
        return []
    text_lower = text.lower()
    detected = set()
    for code, keywords in COUNTRY_KEYWORDS.items():
        for keyword in keywords:
            import re
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                detected.add(code)
                break
    return sorted(list(detected))


def get_all_keywords() -> Set[str]:
    """Get set of all country keywords for validation."""
    all_keywords = set()
    for keywords in COUNTRY_KEYWORDS.values():
        all_keywords.update(keywords)
    return all_keywords


def get_country_for_keyword(keyword: str) -> str:
    """Get ISO country code for a keyword."""
    keyword = keyword.lower().strip()
    for code, keywords in COUNTRY_KEYWORDS.items():
        if keyword in keywords:
            return code
    if keyword in AMBIGUOUS_KEYWORDS:
        return AMBIGUOUS_KEYWORDS[keyword]
    return ""