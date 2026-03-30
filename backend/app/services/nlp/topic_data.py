"""
Topic taxonomy data for humanitarian crisis news tagging.
 
Each entry follows the same format as the original:
    topic_id -> (positive_keywords, negative_keywords)
 
Scoring note: the TopicTagger engine already gives higher weight to:
  - Title matches (3x)
  - Longer phrases (phrase_length multiplier)
So compound phrases like "acute food insecurity" score higher than
single words like "food", which helps precision.
"""
 
from typing import Dict, List, Tuple
 
TOPIC_KEYWORDS: Dict[str, Tuple[List[str], List[str]]] = {
 
    # ------------------------------------------------------------------ #
    #  CONFLICT                                                            #
    # ------------------------------------------------------------------ #
    "conflict": (
        [
            # Armed violence
            "conflict", "armed conflict", "war", "warfare", "civil war",
            "fighting", "clashes", "armed clashes", "skirmish",
            # Actors
            "militia", "armed group", "rebel", "insurgent", "insurgency",
            "armed faction", "non-state actor", "paramilitary",
            # Military actions
            "airstrike", "air strike", "bombardment", "shelling",
            "artillery", "offensive", "counteroffensive", "assault",
            "siege", "blockade", "troops", "military operation",
            "ceasefire", "peace deal", "peace talks", "peace agreement",
            # Casualties / impact
            "killed", "casualties", "civilian deaths", "civilian harm",
            "massacre", "atrocity", "war crime", "gender-based violence",
            "sexual violence", "explosive ordnance", "landmine", "iед",
            # Specific contexts
            "coup", "coup attempt", "political violence", "communal violence",
            "intercommunal", "ethnic violence", "sectarian",
            # Additional violence terms
            "attack", "violence", "bombing", "bomb", "gunfire", "sniper", "drone strike",
            "military", "army", "forces", "armed forces", "combatant", "fighter",
            "hostilities", "hostage", "prisoner of war", "pow", "detention",
            "occupied territory", "occupation", "annexation", "territorial dispute",
            "front line", "frontline", "battleground", "war zone", "warzone",
            "negotiation", "mediation", "peace process", "peacekeeping", "un peacekeeping",
            "sanctions", "arms embargo", "weapons", "ammunition",
            "displacement", "civilian", "population movement",
            # Specific contexts
            "sudan", "sudan conflict", "rsf", "rapid support forces", "saf",
            "myanmar", "junta", "tatmadaw", "arsa",
            "ukraine", "russia", "gaza", "hamas", "hezbollah", "houthis",
            "isis", "isil", "al-shabaab", "boko haram", "al-qaeda",
        ],
        # Negative: reduce score if purely diplomatic/historical
        ["peace conference", "historical", "anniversary", "museum"],
    ),
 
    # ------------------------------------------------------------------ #
    #  DISPLACEMENT                                                        #
    # ------------------------------------------------------------------ #
    "displacement": (
        [
            # People on the move
            "refugee", "refugees", "internally displaced", "idp", "idps",
            "displaced person", "displaced people", "displaced population",
            "forced displacement", "forced migration", "mass displacement",
            "fleeing", "fled", "exodus",
            # Status / process
            "asylum seeker", "asylum claim", "stateless", "statelessness",
            "resettlement", "repatriation", "voluntary return", "returnee",
            "durable solution",
            # Locations
            "refugee camp", "displacement camp", "transit camp",
            "informal settlement", "collective shelter", "reception centre",
            # Agencies / frameworks
            "unhcr", "refugee agency", "refugee convention",
            "non-refoulement", "protection", "refugee protection",
            # Scale indicators
            "million displaced", "thousand displaced", "new displacement",
            # Additional displacement terms
            "displaced", "displacement crisis", "cross-border", "border crossing",
            "host community", "host country", "burden sharing",
            "protection space", "temporary protection", "complementary protection",
            "mixed migration", "mixed movement", "smuggling", "trafficking",
            "rohingya", "south sudanese refugees", "sudanese refugees",
            "afghan refugees", "syrian refugees", "venezuelan refugees",
            "regional displacement", "internal displacement",
            "camp management", "camp coordination", "cccm",
            "shelter", "emergency shelter", "transitional shelter",
        ],
        ["economic migrant", "labour migration", "tourism"],
    ),
 
    # ------------------------------------------------------------------ #
    #  FAMINE / FOOD INSECURITY                                            #
    # ------------------------------------------------------------------ #
    "famine": (
        [
            # IPC / severity framework terms (high value — use long phrases)
            "famine", "ipc phase 5", "ipc phase 4", "ipc phase 3",
            "acute food insecurity", "acute malnutrition",
            "integrated food security phase classification",
            "emergency food", "food emergency",
            # Nutrition
            "malnutrition", "severe acute malnutrition", "sam",
            "moderate acute malnutrition", "mam",
            "global acute malnutrition", "gam",
            "wasting", "stunting", "undernutrition",
            "therapeutic feeding", "therapeutic food",
            "ready to use therapeutic food", "rutf",
            # Food access
            "food insecurity", "food crisis", "food shortage",
            "food access", "food assistance", "food aid",
            "hunger", "starvation", "food ration",
            "wfp", "world food programme", "food distribution",
            # Agricultural
            "crop failure", "harvest failure", "poor harvest",
            "livestock loss", "livelihood loss",
            "food production", "agricultural disruption",
            # Additional famine/food terms
            "food security", "food insecure", "food insecure population",
            "nutrition crisis", "nutrition emergency",
            "cash transfer", "cash assistance", "social protection",
            "livelihood", "livelihoods", "income support",
            "aid suspension", "aid cut", "usaid", "pepfar",
            "funding cut", "humanitarian funding cut",
            "price spike", "food price", "market disruption",
            "drought", "failed rains", "below average rainfall",
            "pastoral", "agropastoral", "arid", "semi-arid",
        ],
        ["food festival", "restaurant", "cuisine", "recipe"],
    ),
 
    # ------------------------------------------------------------------ #
    #  DISEASE OUTBREAK                                                    #
    # ------------------------------------------------------------------ #
    "disease_outbreak": (
        [
            # General outbreak language
            "outbreak", "epidemic", "disease outbreak", "health emergency",
            "public health emergency", "pheic",
            # Specific diseases relevant to humanitarian contexts
            "cholera", "ebola", "marburg", "mpox", "monkeypox",
            "malaria", "measles", "meningitis", "typhoid",
            "tuberculosis", "tb", "hepatitis", "dengue",
            "yellow fever", "plague", "diphtheria",
            # Response
            "vaccination", "vaccine", "immunisation", "immunization",
            "health response", "disease surveillance",
            "contact tracing", "quarantine", "isolation",
            "treatment centre", "health facility",
            # Agencies
            "who alert", "who declaration", "health cluster",
            "médecins sans frontières", "msf",
            # Rates
            "case fatality", "mortality rate", "morbidity",
            "infection rate", "transmission",
            # Additional disease/health terms
            "health", "health crisis", "health system", "health worker",
            "hospital", "clinic", "medical", "medicine", "drug",
            "hiv", "aids", "pepfar", "antiretroviral", "art",
            "polio", "leprosy", "sleeping sickness", "trypanosomiasis",
            "scabies", "acute watery diarrhoea", "awd",
            "respiratory", "pneumonia", "ari",
            "maternal health", "child health", "under-five mortality",
            "health funding", "health programme", "global health",
            "pandemic", "pandemic preparedness",
        ],
        ["chronic disease", "lifestyle", "cancer research", "pharmaceutical profit"],
    ),
 
    # ------------------------------------------------------------------ #
    #  FLOOD / CYCLONE / NATURAL DISASTER                                  #
    # ------------------------------------------------------------------ #
    "natural_disaster": (
        [
            # Floods
            "flood", "flooding", "flash flood", "river flood",
            "inundation", "dam burst", "riverine flooding",
            # Storms
            "cyclone", "hurricane", "typhoon", "tropical storm",
            "storm surge", "monsoon flooding",
            # Other disasters
            "landslide", "mudslide", "avalanche",
            "drought", "flash drought",
            # Impact language
            "disaster response", "disaster relief",
            "emergency response", "rapid onset",
            "affected population", "disaster affected",
            # Agencies / frameworks
            "ocha", "humanitarian response plan",
            "emergency declaration", "state of emergency",
            "ndma", "national disaster",
        ],
        ["flood risk modelling", "historical flood", "flood insurance market"],
    ),
 
    # ------------------------------------------------------------------ #
    #  EARTHQUAKE                                                          #
    # ------------------------------------------------------------------ #
    "earthquake": (
        [
            "earthquake", "tremor", "seismic", "seismic event",
            "magnitude", "epicentre", "epicenter",
            "aftershock", "fault line", "tectonic",
            "tsunami", "liquefaction",
            "collapsed building", "building collapse", "rubble",
            "search and rescue", "urban search and rescue", "usar",
        ],
        [],
    ),
 
    # ------------------------------------------------------------------ #
    #  HUMANITARIAN RESPONSE / AID OPERATIONS                             #
    # ------------------------------------------------------------------ #
    "humanitarian_response": (
        [
            # Operations
            "humanitarian response", "humanitarian operation",
            "humanitarian aid", "humanitarian assistance",
            "relief operation", "aid delivery", "aid access",
            "humanitarian corridor", "aid convoy",
            "humanitarian worker", "aid worker",
            # Funding
            "humanitarian funding", "humanitarian appeal",
            "flash appeal", "cap", "consolidated appeal",
            "underfunded", "funding gap", "donor",
            "ocha", "unocha",
            # Coordination
            "cluster coordination", "inter-agency",
            "humanitarian coordinator", "resident coordinator",
            "humanitarian country team", "hct",
            # Access
            "humanitarian access", "access constraints",
            "aid blockade", "aid obstruction",
            "humanitarian law", "ihl", "international humanitarian law",
            # Key NGOs / agencies
            "icrc", "red cross", "red crescent",
            "world food programme", "wfp", "unicef", "unhcr",
            "iom", "international organization for migration",
            "oxfam", "save the children", "care international",
            "international rescue committee", "irc",
            # Additional humanitarian response terms
            "aid", "assistance", "relief", "support",
            "ngo", "non-governmental", "civil society",
            "response plan", "response strategy",
            "operational", "field operations",
            "beneficiary", "beneficiaries",
            "distribution", "distribution point",
            "needs", "humanitarian needs",
            "crisis response", "emergency assistance",
            "devex", "reliefweb",
            "usaid", "dfid", "fcdo", "echo", "cerf",
            "bureau for humanitarian assistance", "bha",
            "bilateral aid", "multilateral",
            "cut", "cuts", "reduction", "suspend", "suspended", "halt", "halted",
            "freeze", "frozen", "withdraw", "withdrawal",
            "trump", "doge", "foreign aid",
        ],
        ["development aid", "development finance", "oda statistics"],
    ),
 
    # ------------------------------------------------------------------ #
    #  PROTECTION / HUMAN RIGHTS                                           #
    # ------------------------------------------------------------------ #
    "protection": (
        [
            "protection", "civilian protection", "civilian harm",
            "human rights", "human rights violation", "human rights abuse",
            "accountability", "impunity",
            "child protection", "child soldier", "recruitment of children",
            "gender based violence", "gbv", "sexual exploitation",
            "protection monitoring", "protection cluster",
            "detention", "arbitrary detention", "torture",
            "enforced disappearance", "extrajudicial killing",
            "rule of law", "transitional justice",
            "humanitarian principles", "neutrality", "impartiality",
            # Additional protection terms
            "rights", "fundamental rights", "civil rights",
            "vulnerable", "vulnerability", "marginalised", "marginalized",
            "women", "gender", "gender equality", "gender-based",
            "children", "child", "minors", "youth",
            "elderly", "older people", "persons with disabilities",
            "minority", "minorities", "ethnic minority",
            "persecution", "discriminat", "exclusion",
            "access to justice", "legal aid",
            "witness protection", "protection of civilians", "poc",
        ],
        [],
    ),
 
    # ------------------------------------------------------------------ #
    #  EARLY WARNING / ANALYSIS                                            #
    # ------------------------------------------------------------------ #
    "early_warning": (
        [
            # Early warning systems and frameworks
            "early warning", "early warning system", "risk analysis",
            "crisis analysis", "situation analysis", "needs assessment",
            "humanitarian needs overview", "hno",
            "inform score", "inform risk",
            "fews net", "famine early warning",
            "ipc", "ipc analysis", "ipc classification",
            # Monitoring
            "sentinel surveillance", "monitoring and evaluation",
            "situation report", "sitrep", "flash update",
            "crisis monitoring", "conflict monitoring",
            "displacement tracking", "dtm",
            # Indicators
            "leading indicator", "risk indicator", "trigger",
            "escalation", "deterioration", "deteriorating situation",
            "crisis trajectory",
            # Additional early warning terms
            "analysis", "assessment", "report", "briefing",
            "situation", "update", "monitoring",
            "risk", "risks", "risk factors",
            "forecast", "projection", "scenario",
            "watchlist", "watch list", "crisis watch",
            "tension", "tensions", "instability",
            "fragile", "fragility", "fragile state",
            "indicator", "indicators", "evidence",
            "icg", "crisis group", "international crisis group",
            "acled", "violence data",
        ],
        [],
    ),
}
 
 
# Display names shown in the dashboard UI
TOPIC_NAMES: Dict[str, str] = {
    "conflict":               "Conflict & Violence",
    "displacement":           "Displacement & Refugees",
    "famine":                 "Food Insecurity & Famine",
    "disease_outbreak":       "Disease Outbreak",
    "natural_disaster":       "Natural Disaster",
    "earthquake":             "Earthquake",
    "humanitarian_response":  "Humanitarian Response",
    "protection":             "Protection & Human Rights",
    "early_warning":          "Early Warning & Analysis",
}
 
# Severity escalation rules:
# If an article matches these COMBINATIONS of topics, escalate severity.
# Used in the API layer, not here — kept here for reference.
SEVERITY_ESCALATION_RULES = [
    ({"conflict", "famine"},            "CRITICAL"),
    ({"conflict", "disease_outbreak"},  "CRITICAL"),
    ({"displacement", "famine"},        "CRITICAL"),
    ({"displacement", "disease_outbreak"}, "CRITICAL"),
    ({"famine", "disease_outbreak"},    "CRITICAL"),
]
 
# Single-topic default severities
TOPIC_DEFAULT_SEVERITY: Dict[str, str] = {
    "conflict":              "HIGH",
    "displacement":          "HIGH",
    "famine":                "HIGH",
    "disease_outbreak":      "MEDIUM",
    "natural_disaster":      "MEDIUM",
    "earthquake":            "HIGH",
    "humanitarian_response": "MEDIUM",
    "protection":            "MEDIUM",
    "early_warning":         "LOW",
}
 
 
def get_all_topics() -> List[str]:
    """Get list of all topic IDs."""
    return list(TOPIC_KEYWORDS.keys())
 
 
def get_topic_name(topic_id: str) -> str:
    """Get display name for topic."""
    return TOPIC_NAMES.get(topic_id, topic_id)
 
 
def compute_severity(topic_ids: List[str]) -> str:
    """
    Compute article severity from matched topic IDs.
 
    Checks compound escalation rules first, then falls back
    to the highest single-topic default.
 
    Args:
        topic_ids: List of matched topic IDs
 
    Returns:
        Severity string: CRITICAL | HIGH | MEDIUM | LOW
    """
    topic_set = set(topic_ids)
 
    # Check compound escalation rules
    for rule_topics, severity in SEVERITY_ESCALATION_RULES:
        if rule_topics.issubset(topic_set):
            return severity
 
    # Fall back to highest single-topic severity
    order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    for level in order:
        for topic in topic_ids:
            if TOPIC_DEFAULT_SEVERITY.get(topic) == level:
                return level
 
    return "LOW"