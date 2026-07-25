"""
Karnataka Master Reference Data.
All real administrative, legal, and demographic reference data for Karnataka.
"""

# ──────────────────────────────────────────────
# Karnataka Districts with real coordinates
# ──────────────────────────────────────────────
KARNATAKA_DISTRICTS = [
    {"name": "Bagalkot", "code": "BGK", "hq": "Bagalkot", "lat": 16.1691, "lon": 75.6615, "pop": 1890826, "area": 6575},
    {"name": "Ballari", "code": "BLR", "hq": "Ballari", "lat": 15.1394, "lon": 76.9214, "pop": 2532383, "area": 8450},
    {"name": "Belagavi", "code": "BGM", "hq": "Belagavi", "lat": 15.8497, "lon": 74.4977, "pop": 4778439, "area": 13415},
    {"name": "Bengaluru Rural", "code": "BRU", "hq": "Bengaluru", "lat": 13.2257, "lon": 77.5750, "pop": 990923, "area": 2259},
    {"name": "Bengaluru Urban", "code": "BLU", "hq": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "pop": 9621551, "area": 2196},
    {"name": "Bidar", "code": "BDR", "hq": "Bidar", "lat": 17.9104, "lon": 77.5199, "pop": 1703300, "area": 5448},
    {"name": "Chamarajanagar", "code": "CMR", "hq": "Chamarajanagar", "lat": 11.9236, "lon": 76.9398, "pop": 1020962, "area": 5101},
    {"name": "Chikkaballapur", "code": "CKB", "hq": "Chikkaballapur", "lat": 13.4355, "lon": 77.7315, "pop": 1254377, "area": 4210},
    {"name": "Chikkamagaluru", "code": "CKM", "hq": "Chikkamagaluru", "lat": 13.3153, "lon": 75.7754, "pop": 1137753, "area": 7201},
    {"name": "Chitradurga", "code": "CTR", "hq": "Chitradurga", "lat": 14.2226, "lon": 76.3980, "pop": 1660378, "area": 8388},
    {"name": "Dakshina Kannada", "code": "DKN", "hq": "Mangaluru", "lat": 12.8438, "lon": 75.0108, "pop": 2089649, "area": 4560},
    {"name": "Davanagere", "code": "DVG", "hq": "Davanagere", "lat": 14.4644, "lon": 75.9218, "pop": 1946905, "area": 5924},
    {"name": "Dharwad", "code": "DWD", "hq": "Dharwad", "lat": 15.4589, "lon": 75.0078, "pop": 1846993, "area": 4260},
    {"name": "Gadag", "code": "GDG", "hq": "Gadag", "lat": 15.4166, "lon": 75.6290, "pop": 1065235, "area": 4656},
    {"name": "Hassan", "code": "HSN", "hq": "Hassan", "lat": 13.0072, "lon": 76.0962, "pop": 1776421, "area": 6814},
    {"name": "Haveri", "code": "HVR", "hq": "Haveri", "lat": 14.7951, "lon": 75.4006, "pop": 1598506, "area": 4823},
    {"name": "Kalaburagi", "code": "KLB", "hq": "Kalaburagi", "lat": 17.3297, "lon": 76.8343, "pop": 2564892, "area": 10951},
    {"name": "Kodagu", "code": "KDG", "hq": "Madikeri", "lat": 12.4244, "lon": 75.7382, "pop": 554519, "area": 4102},
    {"name": "Kolar", "code": "KLR", "hq": "Kolar", "lat": 13.1360, "lon": 78.1292, "pop": 1540231, "area": 3969},
    {"name": "Koppal", "code": "KPL", "hq": "Koppal", "lat": 15.3547, "lon": 76.1548, "pop": 1391292, "area": 5548},
    {"name": "Mandya", "code": "MND", "hq": "Mandya", "lat": 12.5218, "lon": 76.8951, "pop": 1808680, "area": 4961},
    {"name": "Mysuru", "code": "MYS", "hq": "Mysuru", "lat": 12.2958, "lon": 76.6394, "pop": 3001127, "area": 6854},
    {"name": "Raichur", "code": "RCR", "hq": "Raichur", "lat": 16.2076, "lon": 77.3463, "pop": 1924773, "area": 8440},
    {"name": "Ramanagara", "code": "RMN", "hq": "Ramanagara", "lat": 12.7159, "lon": 77.2817, "pop": 1082739, "area": 3556},
    {"name": "Shivamogga", "code": "SMG", "hq": "Shivamogga", "lat": 13.9299, "lon": 75.5681, "pop": 1752753, "area": 8465},
    {"name": "Tumakuru", "code": "TMK", "hq": "Tumakuru", "lat": 13.3379, "lon": 77.1173, "pop": 2681449, "area": 10598},
    {"name": "Udupi", "code": "UDP", "hq": "Udupi", "lat": 13.3409, "lon": 74.7421, "pop": 1177908, "area": 3598},
    {"name": "Uttara Kannada", "code": "UKN", "hq": "Karwar", "lat": 14.8182, "lon": 74.1290, "pop": 1436847, "area": 10291},
    {"name": "Vijayapura", "code": "VJP", "hq": "Vijayapura", "lat": 16.8302, "lon": 75.7100, "pop": 2175102, "area": 10498},
    {"name": "Yadgir", "code": "YDG", "hq": "Yadgir", "lat": 16.7604, "lon": 77.1381, "pop": 1172985, "area": 5234},
    {"name": "Vijayanagara", "code": "VJN", "hq": "Hosapete", "lat": 15.2689, "lon": 76.3909, "pop": 1158852, "area": 3585},
]

# ──────────────────────────────────────────────
# Taluks per District (representative set)
# ──────────────────────────────────────────────
KARNATAKA_TALUKS = {
    "Bengaluru Urban": [
        {"name": "Bengaluru North", "code": "BLU-N", "lat": 13.0358, "lon": 77.5970},
        {"name": "Bengaluru South", "code": "BLU-S", "lat": 12.9121, "lon": 77.5868},
        {"name": "Bengaluru East", "code": "BLU-E", "lat": 12.9850, "lon": 77.6500},
        {"name": "Anekal", "code": "BLU-ANK", "lat": 12.7105, "lon": 77.6947},
        {"name": "Yelahanka", "code": "BLU-YLK", "lat": 13.1007, "lon": 77.5963},
    ],
    "Mysuru": [
        {"name": "Mysuru", "code": "MYS-MYS", "lat": 12.2958, "lon": 76.6394},
        {"name": "Nanjangud", "code": "MYS-NJD", "lat": 12.1166, "lon": 76.6836},
        {"name": "T. Narasipura", "code": "MYS-TNP", "lat": 12.2100, "lon": 76.9000},
        {"name": "Hunsur", "code": "MYS-HNR", "lat": 12.3037, "lon": 76.2928},
        {"name": "K.R. Nagar", "code": "MYS-KRN", "lat": 12.4333, "lon": 76.3833},
        {"name": "Periyapatna", "code": "MYS-PPT", "lat": 12.3380, "lon": 76.1000},
        {"name": "H.D. Kote", "code": "MYS-HDK", "lat": 12.0892, "lon": 76.3339},
    ],
    "Belagavi": [
        {"name": "Belagavi", "code": "BGM-BGM", "lat": 15.8497, "lon": 74.4977},
        {"name": "Athani", "code": "BGM-ATH", "lat": 16.7264, "lon": 75.0598},
        {"name": "Bailhongal", "code": "BGM-BHL", "lat": 15.8134, "lon": 74.8622},
        {"name": "Chikkodi", "code": "BGM-CKD", "lat": 16.4294, "lon": 74.5858},
        {"name": "Gokak", "code": "BGM-GKK", "lat": 16.1676, "lon": 74.8238},
        {"name": "Hukkeri", "code": "BGM-HKR", "lat": 16.2325, "lon": 74.6034},
        {"name": "Khanapur", "code": "BGM-KNP", "lat": 15.6388, "lon": 74.5134},
        {"name": "Ramdurg", "code": "BGM-RMD", "lat": 15.9480, "lon": 75.3006},
        {"name": "Raibag", "code": "BGM-RBG", "lat": 16.4895, "lon": 74.7780},
        {"name": "Savadatti", "code": "BGM-SVD", "lat": 15.7714, "lon": 75.1090},
    ],
    "Dakshina Kannada": [
        {"name": "Mangaluru", "code": "DKN-MNG", "lat": 12.9141, "lon": 74.8560},
        {"name": "Bantwal", "code": "DKN-BNT", "lat": 12.8914, "lon": 75.0343},
        {"name": "Belthangady", "code": "DKN-BLT", "lat": 12.9695, "lon": 75.2724},
        {"name": "Puttur", "code": "DKN-PTR", "lat": 12.7596, "lon": 75.2024},
        {"name": "Sullia", "code": "DKN-SUL", "lat": 12.5604, "lon": 75.3886},
        {"name": "Kadaba", "code": "DKN-KDB", "lat": 12.7538, "lon": 75.1187},
    ],
    "Kalaburagi": [
        {"name": "Kalaburagi", "code": "KLB-KLB", "lat": 17.3297, "lon": 76.8343},
        {"name": "Afzalpur", "code": "KLB-AFZ", "lat": 17.1995, "lon": 76.3584},
        {"name": "Aland", "code": "KLB-ALD", "lat": 17.5622, "lon": 76.5681},
        {"name": "Chincholi", "code": "KLB-CNC", "lat": 17.4678, "lon": 77.4186},
        {"name": "Chittapur", "code": "KLB-CTP", "lat": 17.1189, "lon": 77.0896},
        {"name": "Jevargi", "code": "KLB-JVR", "lat": 16.9074, "lon": 76.7735},
        {"name": "Sedam", "code": "KLB-SDM", "lat": 17.1793, "lon": 77.2771},
    ],
    "Ballari": [
        {"name": "Ballari", "code": "BLR-BLR", "lat": 15.1394, "lon": 76.9214},
        {"name": "Hadagali", "code": "BLR-HDG", "lat": 15.0208, "lon": 75.9336},
        {"name": "Hagaribommanahalli", "code": "BLR-HBM", "lat": 15.0496, "lon": 76.2041},
        {"name": "Kudligi", "code": "BLR-KDL", "lat": 14.9051, "lon": 76.3895},
        {"name": "Sandur", "code": "BLR-SDR", "lat": 15.0847, "lon": 76.5523},
        {"name": "Siruguppa", "code": "BLR-SRG", "lat": 15.6280, "lon": 76.8981},
    ],
    "Dharwad": [
        {"name": "Dharwad", "code": "DWD-DWD", "lat": 15.4589, "lon": 75.0078},
        {"name": "Hubli", "code": "DWD-HBL", "lat": 15.3647, "lon": 75.1240},
        {"name": "Kalghatgi", "code": "DWD-KLG", "lat": 15.1849, "lon": 74.9753},
        {"name": "Kundgol", "code": "DWD-KND", "lat": 15.2562, "lon": 75.2483},
        {"name": "Navalgund", "code": "DWD-NVG", "lat": 15.5587, "lon": 75.3589},
    ],
    "Tumakuru": [
        {"name": "Tumakuru", "code": "TMK-TMK", "lat": 13.3379, "lon": 77.1173},
        {"name": "Gubbi", "code": "TMK-GBI", "lat": 13.3121, "lon": 76.9411},
        {"name": "Kunigal", "code": "TMK-KNG", "lat": 13.0231, "lon": 77.0254},
        {"name": "Madhugiri", "code": "TMK-MDG", "lat": 13.6633, "lon": 77.2085},
        {"name": "Pavagada", "code": "TMK-PVG", "lat": 14.0999, "lon": 77.2813},
        {"name": "Sira", "code": "TMK-SRA", "lat": 13.7412, "lon": 76.9035},
        {"name": "Tiptur", "code": "TMK-TPR", "lat": 13.2556, "lon": 76.4733},
        {"name": "Turuvekere", "code": "TMK-TRV", "lat": 13.1611, "lon": 76.6656},
        {"name": "Koratagere", "code": "TMK-KRT", "lat": 13.5222, "lon": 77.2319},
        {"name": "C.N. Halli", "code": "TMK-CNH", "lat": 13.5761, "lon": 76.3932},
    ],
    "Hassan": [
        {"name": "Hassan", "code": "HSN-HSN", "lat": 13.0072, "lon": 76.0962},
        {"name": "Arsikere", "code": "HSN-ARK", "lat": 13.3148, "lon": 76.2541},
        {"name": "Belur", "code": "HSN-BLR", "lat": 13.1651, "lon": 75.8651},
        {"name": "Channarayapatna", "code": "HSN-CRP", "lat": 12.9018, "lon": 76.3875},
        {"name": "Holenarasipura", "code": "HSN-HNP", "lat": 12.7853, "lon": 76.2428},
        {"name": "Sakleshpur", "code": "HSN-SKP", "lat": 12.9439, "lon": 75.7853},
        {"name": "Alur", "code": "HSN-ALR", "lat": 12.9714, "lon": 75.9869},
        {"name": "Arkalgud", "code": "HSN-AKD", "lat": 12.7618, "lon": 76.0621},
    ],
    "Raichur": [
        {"name": "Raichur", "code": "RCR-RCR", "lat": 16.2076, "lon": 77.3463},
        {"name": "Devadurga", "code": "RCR-DVG", "lat": 16.4166, "lon": 76.9333},
        {"name": "Lingasugur", "code": "RCR-LNG", "lat": 16.1535, "lon": 76.5213},
        {"name": "Manvi", "code": "RCR-MNV", "lat": 15.9924, "lon": 77.0488},
        {"name": "Sindhanur", "code": "RCR-SDN", "lat": 15.7685, "lon": 76.7574},
    ],
}

# For remaining districts, generate minimal taluk data using district HQ
_REMAINING_DISTRICTS = [
    d["name"] for d in KARNATAKA_DISTRICTS if d["name"] not in KARNATAKA_TALUKS
]
for _dist_name in _REMAINING_DISTRICTS:
    _dist_data = next(d for d in KARNATAKA_DISTRICTS if d["name"] == _dist_name)
    KARNATAKA_TALUKS[_dist_name] = [
        {"name": _dist_data["hq"], "code": f"{_dist_data['code']}-HQ",
         "lat": _dist_data["lat"], "lon": _dist_data["lon"]},
        {"name": f"{_dist_data['hq']} Rural", "code": f"{_dist_data['code']}-RUR",
         "lat": _dist_data["lat"] + 0.05, "lon": _dist_data["lon"] + 0.05},
    ]


# ──────────────────────────────────────────────
# Police Ranks
# ──────────────────────────────────────────────
RANKS = [
    {"name": "Constable", "code": "PC", "level": 1, "grade": "Group D"},
    {"name": "Head Constable", "code": "HC", "level": 2, "grade": "Group D"},
    {"name": "Assistant Sub Inspector", "code": "ASI", "level": 3, "grade": "Group C"},
    {"name": "Sub Inspector", "code": "SI", "level": 4, "grade": "Group C"},
    {"name": "Inspector", "code": "INS", "level": 5, "grade": "Group B"},
    {"name": "Deputy Superintendent of Police", "code": "DYSP", "level": 6, "grade": "Group A"},
    {"name": "Assistant Commissioner of Police", "code": "ACP", "level": 7, "grade": "Group A"},
    {"name": "Deputy Commissioner of Police", "code": "DCP", "level": 8, "grade": "IPS"},
    {"name": "Superintendent of Police", "code": "SP", "level": 8, "grade": "IPS"},
    {"name": "Deputy Inspector General", "code": "DIG", "level": 9, "grade": "IPS"},
    {"name": "Inspector General", "code": "IG", "level": 10, "grade": "IPS"},
    {"name": "Additional Director General", "code": "ADGP", "level": 11, "grade": "IPS"},
    {"name": "Director General of Police", "code": "DGP", "level": 12, "grade": "IPS"},
]

# ──────────────────────────────────────────────
# Designations
# ──────────────────────────────────────────────
DESIGNATIONS = [
    {"name": "Station House Officer", "rank": "Inspector", "desc": "Head of a police station"},
    {"name": "Investigating Officer", "rank": "Sub Inspector", "desc": "Handles case investigations"},
    {"name": "Beat Constable", "rank": "Constable", "desc": "Patrol duty officer"},
    {"name": "Traffic Constable", "rank": "Constable", "desc": "Traffic management duty"},
    {"name": "Cyber Crime Inspector", "rank": "Inspector", "desc": "Cyber crime investigation"},
    {"name": "Women Protection Officer", "rank": "Sub Inspector", "desc": "Women and child protection"},
    {"name": "Circle Inspector", "rank": "Inspector", "desc": "In-charge of a police circle"},
    {"name": "Control Room Operator", "rank": "Head Constable", "desc": "Emergency control room"},
    {"name": "Crime Branch Inspector", "rank": "Inspector", "desc": "Special crime branch"},
    {"name": "Forensic Analyst", "rank": "Sub Inspector", "desc": "Forensic science support"},
]

# ──────────────────────────────────────────────
# Unit Types
# ──────────────────────────────────────────────
UNIT_TYPES = [
    {"name": "Police Station", "desc": "Regular law and order police station"},
    {"name": "Traffic Police Station", "desc": "Traffic enforcement"},
    {"name": "Cyber Crime Police Station", "desc": "Cyber crime investigation"},
    {"name": "Women Police Station", "desc": "Crimes against women and children"},
    {"name": "CEN Crime Police Station", "desc": "Central crime investigation unit"},
    {"name": "Rural Police Station", "desc": "Rural jurisdiction police station"},
    {"name": "Railway Police Station", "desc": "Railway Protection Force station"},
    {"name": "APMC Police Station", "desc": "Market yard area station"},
]

# ──────────────────────────────────────────────
# Occupations
# ──────────────────────────────────────────────
OCCUPATIONS = [
    {"name": "Farmer", "category": "Agriculture"},
    {"name": "Agricultural Labourer", "category": "Agriculture"},
    {"name": "Software Engineer", "category": "IT/Private"},
    {"name": "Teacher", "category": "Government"},
    {"name": "Government Employee", "category": "Government"},
    {"name": "Business Owner", "category": "Self-Employed"},
    {"name": "Shop Keeper", "category": "Self-Employed"},
    {"name": "Auto/Taxi Driver", "category": "Self-Employed"},
    {"name": "Truck Driver", "category": "Private"},
    {"name": "Daily Wage Worker", "category": "Labour"},
    {"name": "Construction Worker", "category": "Labour"},
    {"name": "Factory Worker", "category": "Private"},
    {"name": "Doctor", "category": "Professional"},
    {"name": "Lawyer", "category": "Professional"},
    {"name": "Student", "category": "Student"},
    {"name": "Homemaker", "category": "Homemaker"},
    {"name": "Retired", "category": "Retired"},
    {"name": "Unemployed", "category": "Unemployed"},
    {"name": "Politician", "category": "Political"},
    {"name": "Journalist", "category": "Media"},
    {"name": "Real Estate Agent", "category": "Self-Employed"},
    {"name": "Bank Employee", "category": "Private"},
    {"name": "Police (Retired)", "category": "Retired"},
    {"name": "Mechanic", "category": "Self-Employed"},
    {"name": "Electrician", "category": "Self-Employed"},
    {"name": "Plumber", "category": "Self-Employed"},
    {"name": "IT Support", "category": "IT/Private"},
    {"name": "Delivery Agent", "category": "Private"},
    {"name": "Security Guard", "category": "Private"},
    {"name": "Nurse", "category": "Professional"},
]

# ──────────────────────────────────────────────
# Religions
# ──────────────────────────────────────────────
RELIGIONS = [
    {"name": "Hindu"},
    {"name": "Muslim"},
    {"name": "Christian"},
    {"name": "Jain"},
    {"name": "Buddhist"},
    {"name": "Sikh"},
    {"name": "Other"},
]

RELIGION_DISTRIBUTION = [0.74, 0.13, 0.04, 0.04, 0.02, 0.01, 0.02]

# ──────────────────────────────────────────────
# Castes (representative set for Karnataka)
# ──────────────────────────────────────────────
CASTES = [
    {"name": "Lingayat", "category": "General"},
    {"name": "Vokkaliga", "category": "General"},
    {"name": "Brahmin", "category": "General"},
    {"name": "Kuruba", "category": "OBC"},
    {"name": "Scheduled Caste", "category": "SC"},
    {"name": "Scheduled Tribe", "category": "ST"},
    {"name": "Reddy", "category": "General"},
    {"name": "Muslim (OBC)", "category": "OBC"},
    {"name": "Christian (General)", "category": "General"},
    {"name": "Jain", "category": "General"},
    {"name": "Maratha", "category": "General"},
    {"name": "Devanga", "category": "OBC"},
    {"name": "Gowda", "category": "OBC"},
    {"name": "Bunt", "category": "General"},
    {"name": "Billava", "category": "OBC"},
    {"name": "Lambani", "category": "ST"},
    {"name": "Nayaka", "category": "ST"},
    {"name": "Madiga", "category": "SC"},
    {"name": "Holeya", "category": "SC"},
    {"name": "Other", "category": "General"},
]

CASTE_DISTRIBUTION = [
    0.14, 0.12, 0.04, 0.07, 0.10, 0.07, 0.03, 0.08,
    0.03, 0.03, 0.02, 0.03, 0.04, 0.02, 0.03,
    0.03, 0.02, 0.04, 0.03, 0.03,
]

# ──────────────────────────────────────────────
# Case Categories
# ──────────────────────────────────────────────
CASE_CATEGORIES = [
    {"name": "FIR", "desc": "First Information Report — cognizable offence"},
    {"name": "UDR", "desc": "Unnatural Death Report"},
    {"name": "ZeroFIR", "desc": "Zero FIR — filed at any station, transferred to jurisdiction"},
    {"name": "PAR", "desc": "Preliminary Action Report"},
]

# ──────────────────────────────────────────────
# Case Statuses
# ──────────────────────────────────────────────
CASE_STATUSES = [
    {"name": "Under Investigation", "code": "UI", "is_final": False},
    {"name": "Charge Sheeted", "code": "CS", "is_final": False},
    {"name": "Pending Trial", "code": "PT", "is_final": False},
    {"name": "Convicted", "code": "CV", "is_final": True},
    {"name": "Acquitted", "code": "AQ", "is_final": True},
    {"name": "Discharged", "code": "DC", "is_final": True},
    {"name": "Compounded", "code": "CM", "is_final": True},
    {"name": "Undetected", "code": "UD", "is_final": True},
    {"name": "Closed — Mistake of Fact", "code": "MF", "is_final": True},
    {"name": "Closed — Mistake of Law", "code": "ML", "is_final": True},
    {"name": "Referred", "code": "RF", "is_final": True},
    {"name": "Transferred", "code": "TR", "is_final": False},
]

# ──────────────────────────────────────────────
# Gravity of Offence
# ──────────────────────────────────────────────
GRAVITY_OFFENCES = [
    {"name": "Heinous", "level": 3, "desc": "Murder, Dacoity, Rape, Kidnapping for ransom"},
    {"name": "Less Heinous", "level": 2, "desc": "Robbery, Burglary, Grievous Hurt"},
    {"name": "Non-Heinous", "level": 1, "desc": "Theft, Cheating, Trespass"},
]

# ──────────────────────────────────────────────
# Crime Heads & Sub-Heads
# ──────────────────────────────────────────────
CRIME_HEADS = [
    {"name": "Murder", "code": "MUR", "gravity": "Heinous"},
    {"name": "Attempt to Murder", "code": "ATM", "gravity": "Heinous"},
    {"name": "Culpable Homicide", "code": "CHM", "gravity": "Heinous"},
    {"name": "Kidnapping & Abduction", "code": "KNA", "gravity": "Heinous"},
    {"name": "Robbery", "code": "ROB", "gravity": "Less Heinous"},
    {"name": "Dacoity", "code": "DAC", "gravity": "Heinous"},
    {"name": "Burglary", "code": "BRG", "gravity": "Less Heinous"},
    {"name": "Theft", "code": "THF", "gravity": "Non-Heinous"},
    {"name": "Vehicle Theft", "code": "VTH", "gravity": "Non-Heinous"},
    {"name": "Assault", "code": "AST", "gravity": "Less Heinous"},
    {"name": "Rioting", "code": "RIT", "gravity": "Less Heinous"},
    {"name": "Sexual Offences", "code": "SXO", "gravity": "Heinous"},
    {"name": "POCSO", "code": "POC", "gravity": "Heinous"},
    {"name": "Domestic Violence", "code": "DMV", "gravity": "Less Heinous"},
    {"name": "Dowry Death", "code": "DWD", "gravity": "Heinous"},
    {"name": "Cheating & Fraud", "code": "CHT", "gravity": "Non-Heinous"},
    {"name": "Cyber Crime", "code": "CYB", "gravity": "Non-Heinous"},
    {"name": "Forgery", "code": "FRG", "gravity": "Non-Heinous"},
    {"name": "Criminal Breach of Trust", "code": "CBT", "gravity": "Non-Heinous"},
    {"name": "NDPS (Narcotics)", "code": "NDP", "gravity": "Less Heinous"},
    {"name": "Arms Act", "code": "ARM", "gravity": "Less Heinous"},
    {"name": "Traffic Accident (Fatal)", "code": "TAF", "gravity": "Heinous"},
    {"name": "Traffic Accident (Non-Fatal)", "code": "TAN", "gravity": "Non-Heinous"},
    {"name": "Criminal Intimidation", "code": "CIN", "gravity": "Non-Heinous"},
    {"name": "Trespass", "code": "TRS", "gravity": "Non-Heinous"},
    {"name": "Mischief", "code": "MSC", "gravity": "Non-Heinous"},
    {"name": "Hurt", "code": "HRT", "gravity": "Non-Heinous"},
    {"name": "Grievous Hurt", "code": "GHR", "gravity": "Less Heinous"},
    {"name": "Missing Person", "code": "MSP", "gravity": "Non-Heinous"},
    {"name": "Unnatural Death", "code": "UND", "gravity": "Non-Heinous"},
]

CRIME_SUB_HEADS = {
    "Theft": [
        {"name": "Mobile Theft", "code": "THF-MOB"},
        {"name": "Jewellery Theft", "code": "THF-JWL"},
        {"name": "Cattle Theft", "code": "THF-CTL"},
        {"name": "Pickpocketing", "code": "THF-PKP"},
        {"name": "Shoplifting", "code": "THF-SHL"},
    ],
    "Vehicle Theft": [
        {"name": "Two Wheeler Theft", "code": "VTH-2W"},
        {"name": "Four Wheeler Theft", "code": "VTH-4W"},
        {"name": "Auto Theft", "code": "VTH-AT"},
    ],
    "Cyber Crime": [
        {"name": "UPI Fraud", "code": "CYB-UPI"},
        {"name": "Phishing", "code": "CYB-PHS"},
        {"name": "Identity Theft", "code": "CYB-IDT"},
        {"name": "Fake App Fraud", "code": "CYB-FAP"},
        {"name": "Cryptocurrency Fraud", "code": "CYB-CRY"},
        {"name": "SIM Swap Fraud", "code": "CYB-SIM"},
        {"name": "Online Harassment", "code": "CYB-HRS"},
        {"name": "Ransomware", "code": "CYB-RNS"},
        {"name": "Dark Web Crime", "code": "CYB-DRK"},
        {"name": "Social Media Fraud", "code": "CYB-SMF"},
        {"name": "OTP Fraud", "code": "CYB-OTP"},
        {"name": "Job Fraud", "code": "CYB-JOB"},
        {"name": "Loan App Fraud", "code": "CYB-LOA"},
        {"name": "Investment Fraud", "code": "CYB-INV"},
    ],
    "Sexual Offences": [
        {"name": "Rape", "code": "SXO-RPE"},
        {"name": "Attempt to Rape", "code": "SXO-ATR"},
        {"name": "Sexual Harassment", "code": "SXO-SHR"},
        {"name": "Stalking", "code": "SXO-STK"},
        {"name": "Voyeurism", "code": "SXO-VOY"},
    ],
    "Robbery": [
        {"name": "Highway Robbery", "code": "ROB-HWY"},
        {"name": "House Robbery", "code": "ROB-HSE"},
        {"name": "Chain Snatching", "code": "ROB-CHN"},
    ],
    "Burglary": [
        {"name": "House Break", "code": "BRG-HSE"},
        {"name": "Shop Break", "code": "BRG-SHP"},
        {"name": "Office Break", "code": "BRG-OFC"},
    ],
    "NDPS (Narcotics)": [
        {"name": "Ganja", "code": "NDP-GNJ"},
        {"name": "Cocaine", "code": "NDP-COC"},
        {"name": "Heroin", "code": "NDP-HRN"},
        {"name": "Synthetic Drugs", "code": "NDP-SYN"},
        {"name": "Drug Trafficking", "code": "NDP-TRF"},
    ],
    "Assault": [
        {"name": "Simple Assault", "code": "AST-SMP"},
        {"name": "Aggravated Assault", "code": "AST-AGG"},
        {"name": "Assault on Public Servant", "code": "AST-PUB"},
    ],
    "Murder": [
        {"name": "Premeditated Murder", "code": "MUR-PRE"},
        {"name": "Murder in Quarrel", "code": "MUR-QRL"},
        {"name": "Honour Killing", "code": "MUR-HNR"},
        {"name": "Contract Killing", "code": "MUR-CON"},
        {"name": "Gang Murder", "code": "MUR-GNG"},
    ],
}

# ──────────────────────────────────────────────
# Acts and Sections
# ──────────────────────────────────────────────
ACTS = [
    {"name": "Indian Penal Code", "code": "IPC", "year": 1860, "active": False, "replaced_by": "BNS"},
    {"name": "Bharatiya Nyaya Sanhita", "code": "BNS", "year": 2023, "active": True, "replaced_by": None},
    {"name": "Code of Criminal Procedure", "code": "CrPC", "year": 1973, "active": False, "replaced_by": "BNSS"},
    {"name": "Bharatiya Nagarik Suraksha Sanhita", "code": "BNSS", "year": 2023, "active": True, "replaced_by": None},
    {"name": "Indian Evidence Act", "code": "IEA", "year": 1872, "active": False, "replaced_by": "BSA"},
    {"name": "Bharatiya Sakshya Adhiniyam", "code": "BSA", "year": 2023, "active": True, "replaced_by": None},
    {"name": "Protection of Children from Sexual Offences Act", "code": "POCSO", "year": 2012, "active": True, "replaced_by": None},
    {"name": "Narcotic Drugs and Psychotropic Substances Act", "code": "NDPS", "year": 1985, "active": True, "replaced_by": None},
    {"name": "Information Technology Act", "code": "ITA", "year": 2000, "active": True, "replaced_by": None},
    {"name": "Motor Vehicles Act", "code": "MVA", "year": 1988, "active": True, "replaced_by": None},
    {"name": "Arms Act", "code": "AA", "year": 1959, "active": True, "replaced_by": None},
    {"name": "Dowry Prohibition Act", "code": "DPA", "year": 1961, "active": True, "replaced_by": None},
    {"name": "SC/ST (Prevention of Atrocities) Act", "code": "SCST", "year": 1989, "active": True, "replaced_by": None},
    {"name": "Karnataka Police Act", "code": "KPA", "year": 1963, "active": True, "replaced_by": None},
    {"name": "Juvenile Justice Act", "code": "JJA", "year": 2015, "active": True, "replaced_by": None},
    {"name": "Explosive Substances Act", "code": "ESA", "year": 1908, "active": True, "replaced_by": None},
    {"name": "Prevention of Money Laundering Act", "code": "PMLA", "year": 2002, "active": True, "replaced_by": None},
]

# Key IPC/BNS Sections with mappings
SECTIONS = [
    # Murder
    {"number": "302", "title": "Murder", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Death or Life Imprisonment", "gravity": "Heinous", "bns": "101"},
    {"number": "101", "title": "Murder", "act": "BNS", "bailable": False, "cognizable": True, "max_punishment": "Death or Life Imprisonment", "gravity": "Heinous", "bns": None},
    # Attempt to Murder
    {"number": "307", "title": "Attempt to Murder", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": "109"},
    {"number": "109", "title": "Attempt to Murder", "act": "BNS", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": None},
    # Culpable Homicide
    {"number": "304", "title": "Culpable Homicide not amounting to Murder", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment or 10 years", "gravity": "Heinous", "bns": "105"},
    # Kidnapping
    {"number": "363", "title": "Kidnapping", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "7 years", "gravity": "Heinous", "bns": "137"},
    # Robbery
    {"number": "392", "title": "Robbery", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "10 years + fine", "gravity": "Less Heinous", "bns": "309"},
    # Dacoity
    {"number": "395", "title": "Dacoity", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": "310"},
    # Theft
    {"number": "379", "title": "Theft", "act": "IPC", "bailable": True, "cognizable": True, "max_punishment": "3 years", "gravity": "Non-Heinous", "bns": "303"},
    # Burglary / House Breaking
    {"number": "457", "title": "Lurking house-trespass or house-breaking by night", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "5 years", "gravity": "Less Heinous", "bns": "333"},
    # Cheating
    {"number": "420", "title": "Cheating and dishonestly inducing delivery of property", "act": "IPC", "bailable": True, "cognizable": True, "max_punishment": "7 years", "gravity": "Non-Heinous", "bns": "318"},
    # Assault / Hurt
    {"number": "323", "title": "Voluntarily causing hurt", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "1 year", "gravity": "Non-Heinous", "bns": "115"},
    {"number": "325", "title": "Voluntarily causing grievous hurt", "act": "IPC", "bailable": True, "cognizable": True, "max_punishment": "7 years", "gravity": "Less Heinous", "bns": "117"},
    # Criminal Intimidation
    {"number": "506", "title": "Criminal Intimidation", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "2 years", "gravity": "Non-Heinous", "bns": "351"},
    # Rape
    {"number": "376", "title": "Rape", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": "63"},
    # Dowry Death
    {"number": "304B", "title": "Dowry Death", "act": "IPC", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": "80"},
    # Rioting
    {"number": "147", "title": "Rioting", "act": "IPC", "bailable": True, "cognizable": True, "max_punishment": "2 years", "gravity": "Less Heinous", "bns": "189"},
    # Criminal Breach of Trust
    {"number": "406", "title": "Criminal breach of trust", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "3 years", "gravity": "Non-Heinous", "bns": "316"},
    # Forgery
    {"number": "465", "title": "Forgery", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "2 years", "gravity": "Non-Heinous", "bns": "336"},
    # Trespass
    {"number": "447", "title": "Criminal Trespass", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "3 months", "gravity": "Non-Heinous", "bns": "329"},
    # IT Act Sections
    {"number": "66", "title": "Computer related offences", "act": "ITA", "bailable": True, "cognizable": True, "max_punishment": "3 years", "gravity": "Non-Heinous", "bns": None},
    {"number": "66C", "title": "Identity theft", "act": "ITA", "bailable": True, "cognizable": True, "max_punishment": "3 years", "gravity": "Non-Heinous", "bns": None},
    {"number": "66D", "title": "Cheating by personation using computer resource", "act": "ITA", "bailable": True, "cognizable": True, "max_punishment": "3 years", "gravity": "Non-Heinous", "bns": None},
    {"number": "67", "title": "Publishing obscene material in electronic form", "act": "ITA", "bailable": True, "cognizable": True, "max_punishment": "3 years first conviction", "gravity": "Non-Heinous", "bns": None},
    # NDPS
    {"number": "20", "title": "Punishment for contravention in relation to cannabis plant and cannabis", "act": "NDPS", "bailable": False, "cognizable": True, "max_punishment": "20 years + fine", "gravity": "Less Heinous", "bns": None},
    {"number": "21", "title": "Punishment for contravention in relation to manufactured drugs", "act": "NDPS", "bailable": False, "cognizable": True, "max_punishment": "20 years + fine", "gravity": "Less Heinous", "bns": None},
    {"number": "22", "title": "Punishment for contravention in relation to psychotropic substances", "act": "NDPS", "bailable": False, "cognizable": True, "max_punishment": "20 years + fine", "gravity": "Less Heinous", "bns": None},
    # POCSO
    {"number": "4", "title": "Punishment for penetrative sexual assault", "act": "POCSO", "bailable": False, "cognizable": True, "max_punishment": "Life Imprisonment", "gravity": "Heinous", "bns": None},
    {"number": "6", "title": "Punishment for aggravated penetrative sexual assault", "act": "POCSO", "bailable": False, "cognizable": True, "max_punishment": "Death or Life Imprisonment", "gravity": "Heinous", "bns": None},
    # Arms Act
    {"number": "25", "title": "Punishment for certain offences", "act": "AA", "bailable": False, "cognizable": True, "max_punishment": "7 years", "gravity": "Less Heinous", "bns": None},
    # Motor Vehicles Act
    {"number": "184", "title": "Dangerous driving", "act": "MVA", "bailable": True, "cognizable": True, "max_punishment": "1 year or fine up to 5000", "gravity": "Non-Heinous", "bns": None},
    {"number": "185", "title": "Driving under influence of alcohol or drugs", "act": "MVA", "bailable": True, "cognizable": True, "max_punishment": "6 months or fine up to 10000", "gravity": "Non-Heinous", "bns": None},
    {"number": "304A", "title": "Causing death by negligence", "act": "IPC", "bailable": True, "cognizable": False, "max_punishment": "2 years", "gravity": "Heinous", "bns": "106"},
]

# Crime Head → Section mappings
CRIME_HEAD_TO_SECTIONS = {
    "Murder": ["302", "101"],
    "Attempt to Murder": ["307", "109"],
    "Culpable Homicide": ["304"],
    "Kidnapping & Abduction": ["363"],
    "Robbery": ["392"],
    "Dacoity": ["395"],
    "Theft": ["379", "303"],
    "Vehicle Theft": ["379"],
    "Burglary": ["457", "333"],
    "Assault": ["323", "325", "115", "117"],
    "Hurt": ["323", "115"],
    "Grievous Hurt": ["325", "117"],
    "Sexual Offences": ["376", "63"],
    "POCSO": ["4", "6"],
    "Domestic Violence": ["498A"],
    "Dowry Death": ["304B", "80"],
    "Cheating & Fraud": ["420", "318"],
    "Cyber Crime": ["66", "66C", "66D"],
    "Forgery": ["465", "336"],
    "Criminal Breach of Trust": ["406", "316"],
    "Rioting": ["147", "189"],
    "NDPS (Narcotics)": ["20", "21", "22"],
    "Arms Act": ["25"],
    "Criminal Intimidation": ["506", "351"],
    "Trespass": ["447", "329"],
    "Traffic Accident (Fatal)": ["304A", "184", "185"],
    "Traffic Accident (Non-Fatal)": ["184", "185"],
    "Mischief": ["425"],
    "Missing Person": [],
    "Unnatural Death": ["174"],
}

# Crime Head → Act mappings
CRIME_HEAD_TO_ACTS = {
    "Murder": ["IPC", "BNS"],
    "Attempt to Murder": ["IPC", "BNS"],
    "Culpable Homicide": ["IPC", "BNS"],
    "Kidnapping & Abduction": ["IPC", "BNS"],
    "Robbery": ["IPC", "BNS"],
    "Dacoity": ["IPC", "BNS"],
    "Theft": ["IPC", "BNS"],
    "Vehicle Theft": ["IPC", "BNS"],
    "Burglary": ["IPC", "BNS"],
    "Assault": ["IPC", "BNS"],
    "Hurt": ["IPC", "BNS"],
    "Grievous Hurt": ["IPC", "BNS"],
    "Sexual Offences": ["IPC", "BNS"],
    "POCSO": ["POCSO"],
    "Domestic Violence": ["IPC", "BNS"],
    "Dowry Death": ["IPC", "BNS", "DPA"],
    "Cheating & Fraud": ["IPC", "BNS"],
    "Cyber Crime": ["ITA", "IPC", "BNS"],
    "Forgery": ["IPC", "BNS"],
    "Criminal Breach of Trust": ["IPC", "BNS"],
    "Rioting": ["IPC", "BNS"],
    "NDPS (Narcotics)": ["NDPS"],
    "Arms Act": ["AA"],
    "Criminal Intimidation": ["IPC", "BNS"],
    "Trespass": ["IPC", "BNS"],
    "Traffic Accident (Fatal)": ["IPC", "BNS", "MVA"],
    "Traffic Accident (Non-Fatal)": ["MVA"],
    "Mischief": ["IPC", "BNS"],
    "Missing Person": ["BNSS"],
    "Unnatural Death": ["BNSS"],
}

# ──────────────────────────────────────────────
# Courts
# ──────────────────────────────────────────────
COURT_TYPES = [
    "JMFC",  # Judicial Magistrate First Class
    "CJM",   # Chief Judicial Magistrate
    "Sessions Court",
    "Additional Sessions Court",
    "Fast Track Court",
    "Family Court",
    "POCSO Special Court",
    "High Court of Karnataka",
    "Lok Adalat",
]

# ──────────────────────────────────────────────
# Indian Names for Faker augmentation (Kannada-region common names)
# ──────────────────────────────────────────────
MALE_FIRST_NAMES = [
    "Ravi", "Kumar", "Suresh", "Ramesh", "Basavaraju", "Shivaraj", "Manjunath",
    "Mahesh", "Ganesh", "Nagaraj", "Siddharth", "Arun", "Venkatesh", "Prasad",
    "Rajesh", "Deepak", "Vinay", "Santosh", "Manoj", "Prakash", "Anand",
    "Mohan", "Girish", "Harish", "Naveen", "Sachin", "Kiran", "Ashok",
    "Srinivas", "Vijay", "Chandrashekar", "Raghavendra", "Shivakumar",
    "Basavaraj", "Mallesh", "Hanumanthappa", "Ningaraju", "Thimmaiah",
    "Madhu", "Raju", "Manju", "Chethan", "Darshan", "Pavan", "Yogesh",
    "Pradeep", "Bharath", "Sagar", "Rakesh", "Rohan",
]

FEMALE_FIRST_NAMES = [
    "Lakshmi", "Suma", "Savitri", "Kavitha", "Rekha", "Asha", "Padma",
    "Geetha", "Shanthi", "Sunitha", "Priya", "Divya", "Anitha", "Meena",
    "Swathi", "Pooja", "Rashmi", "Nandini", "Mamatha", "Bhagyalakshmi",
    "Shobha", "Vidya", "Pushpa", "Renuka", "Indira", "Sudha", "Jayalakshmi",
    "Roopa", "Sindhu", "Deepa", "Ashwini", "Keerthana", "Lavanya",
    "Sahana", "Tejaswini", "Akshatha", "Chaitra", "Pallavi", "Neha",
    "Shruti", "Varsha", "Amrutha", "Bhavana", "Chaithra", "Spandana",
]

LAST_NAMES = [
    "Gowda", "Shetty", "Patil", "Naik", "Reddy", "Rao", "Swamy",
    "Murthy", "Hegde", "Bhat", "Acharya", "Kulkarni", "Joshi",
    "Desai", "Nayak", "Poojary", "Shenoy", "Pai", "Kamath",
    "Babu", "Nair", "Sharma", "Singh", "Khan", "Ahmed",
    "Hussain", "Patel", "Yadav", "Chauhan", "Gupta",
    "Basappa", "Hanumanthu", "Thimmegowda", "Siddaramaiah",
    "Shivanna", "Manjappa", "Rajanna", "Shekhar", "Prasanna",
    "Mallikarjun", "Basavaraju", "Channappa", "Veeranna",
]

# ──────────────────────────────────────────────
# Vehicle Data
# ──────────────────────────────────────────────
VEHICLE_MANUFACTURERS = {
    "Car": ["Maruti Suzuki", "Hyundai", "Tata", "Mahindra", "Toyota", "Honda", "Kia", "MG", "Renault", "Volkswagen"],
    "Bike": ["Hero", "Honda", "Bajaj", "TVS", "Royal Enfield", "Yamaha", "KTM", "Suzuki"],
    "Auto": ["Bajaj", "Piaggio", "TVS", "Mahindra"],
    "Truck": ["Tata", "Ashok Leyland", "BharatBenz", "Eicher", "Mahindra"],
    "Bus": ["Tata", "Ashok Leyland", "Eicher", "Volvo", "BharatBenz"],
    "Van": ["Maruti Suzuki", "Tata", "Mahindra", "Force"],
    "SUV": ["Mahindra", "Tata", "Hyundai", "Kia", "Toyota", "MG"],
}

VEHICLE_COLORS = [
    "White", "Silver", "Black", "Grey", "Red", "Blue",
    "Brown", "Green", "Yellow", "Orange", "Maroon",
]

# Karnataka RTO codes
KARNATAKA_RTO_CODES = [
    "KA-01", "KA-02", "KA-03", "KA-04", "KA-05", "KA-06", "KA-07", "KA-08",
    "KA-09", "KA-10", "KA-11", "KA-12", "KA-13", "KA-14", "KA-15", "KA-16",
    "KA-17", "KA-18", "KA-19", "KA-20", "KA-21", "KA-22", "KA-23", "KA-24",
    "KA-25", "KA-26", "KA-27", "KA-28", "KA-29", "KA-30", "KA-31", "KA-32",
    "KA-33", "KA-34", "KA-35", "KA-36", "KA-37", "KA-38", "KA-39", "KA-40",
    "KA-41", "KA-42", "KA-43", "KA-44", "KA-45", "KA-46", "KA-47", "KA-48",
    "KA-49", "KA-50", "KA-51", "KA-52", "KA-53", "KA-54", "KA-55", "KA-56",
    "KA-57", "KA-58", "KA-59", "KA-60", "KA-61", "KA-62", "KA-63", "KA-64",
    "KA-65", "KA-66", "KA-67", "KA-68", "KA-69", "KA-70", "KA-71",
]

# ──────────────────────────────────────────────
# Weapon Types
# ──────────────────────────────────────────────
WEAPON_TYPES = [
    {"type": "Knife", "sub_types": ["Kitchen Knife", "Pocket Knife", "Machete", "Cleaver"]},
    {"type": "Pistol", "sub_types": ["Country-made Pistol", "Semi-automatic Pistol", "Revolver"]},
    {"type": "Rifle", "sub_types": ["Bolt-action Rifle", "Air Rifle"]},
    {"type": "Blunt Object", "sub_types": ["Iron Rod", "Wooden Stick", "Cricket Bat", "Stone", "Brick", "Hammer"]},
    {"type": "Acid", "sub_types": ["Sulphuric Acid", "Hydrochloric Acid"]},
    {"type": "Explosives", "sub_types": ["Crude Bomb", "Firecracker Bomb", "Gelatin Stick"]},
    {"type": "Improvised", "sub_types": ["Glass Bottle", "Chain", "Belt", "Wire"]},
    {"type": "Vehicle (as weapon)", "sub_types": ["Car", "Truck", "Bike"]},
    {"type": "Poison", "sub_types": ["Pesticide", "Rat Poison", "Chemical"]},
    {"type": "Hands/Feet", "sub_types": ["Fist", "Kick", "Strangulation"]},
]

# ──────────────────────────────────────────────
# Banks (for financial engine)
# ──────────────────────────────────────────────
BANKS = [
    "State Bank of India", "Canara Bank", "Syndicate Bank",
    "Corporation Bank", "Vijaya Bank", "Karnataka Bank",
    "Bank of Baroda", "Punjab National Bank", "Union Bank of India",
    "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank",
    "Yes Bank", "IndusInd Bank", "Federal Bank",
    "Karnataka Grameena Bank", "Pragathi Krishna Grameena Bank",
]

UPI_APPS = ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay", "WhatsApp Pay"]

# ──────────────────────────────────────────────
# Education Levels
# ──────────────────────────────────────────────
EDUCATION_LEVELS = [
    "Illiterate", "Primary (1-5)", "Middle (6-8)", "Secondary (9-10)",
    "Higher Secondary (11-12)", "Diploma", "Graduate", "Post-Graduate",
    "Professional (Engineering/Medical/Law)", "PhD",
]

EDUCATION_DISTRIBUTION = [0.10, 0.12, 0.14, 0.18, 0.15, 0.06, 0.13, 0.06, 0.05, 0.01]

# ──────────────────────────────────────────────
# Income Brackets (monthly, INR)
# ──────────────────────────────────────────────
INCOME_BRACKETS = {
    "BPL": (0, 5000),
    "Lower": (5001, 15000),
    "Middle": (15001, 40000),
    "Upper-Middle": (40001, 100000),
    "Upper": (100001, 500000),
}

INCOME_DISTRIBUTION = [0.15, 0.25, 0.35, 0.18, 0.07]
