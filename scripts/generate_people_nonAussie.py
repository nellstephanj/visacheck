#!/usr/bin/env python3
"""Generate synthetic person JSON files for res/people based on country.

Usage:
    python3 scripts/generate_people_nonAussie.py --count 200 --country USA
    python3 scripts/generate_people_nonAussie.py --count 100 --country Germany

This script writes files person_001.json .. person_NNN.json in res/people.
"""
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "res" / "people"
TEMPLATE_PATH = OUTPUT_DIR / "person_template.json"


def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Country-specific data configuration
COUNTRY_DATA = {
    "USA": {
        "first_names": ["John", "Mary", "James", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
                       "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen"],
        "last_names": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                      "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"],
        "city_state_mapping": {
            "New York": "NY",
            "Los Angeles": "CA",
            "San Diego": "CA",
            "San Jose": "CA",
            "Chicago": "IL",
            "Houston": "TX",
            "Dallas": "TX",
            "San Antonio": "TX",
            "Austin": "TX",
            "Fort Worth": "TX",
            "Phoenix": "AZ",
            "Philadelphia": "PA",
            "Jacksonville": "FL",
            "Columbus": "OH",
            "Charlotte": "NC"
        },
        "address_format": {
            "street_types": ["St", "Ave", "Blvd", "Rd", "Dr", "Ln", "Way", "Ct"],
            "unit_types": ["Apt", "Suite", "Unit", "#"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["New York FO", "Los Angeles FO", "Chicago FO", "Houston FO", "Miami FO"],
        "nationality": "United States"
    },
    "Germany": {
        "first_names": ["Hans", "Anna", "Klaus", "Maria", "Peter", "Elisabeth", "Wolfgang", "Ursula", "Jürgen", "Ingrid",
                       "Günter", "Christa", "Stefan", "Petra", "Michael", "Andrea", "Thomas", "Sabine", "Frank", "Gabriele"],
        "last_names": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
                      "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann"],
        "city_state_mapping": {
            "Berlin": "Berlin",
            "Hamburg": "Hamburg",
            "Bremen": "Bremen",
            "München": "Bayern",
            "Nürnberg": "Bayern",
            "Stuttgart": "Baden-Württemberg",
            "Köln": "Nordrhein-Westfalen",
            "Düsseldorf": "Nordrhein-Westfalen",
            "Dortmund": "Nordrhein-Westfalen",
            "Essen": "Nordrhein-Westfalen",
            "Duisburg": "Nordrhein-Westfalen",
            "Frankfurt am Main": "Hessen",
            "Leipzig": "Sachsen",
            "Dresden": "Sachsen",
            "Hannover": "Niedersachsen"
        },
        "address_format": {
            "street_types": ["Straße", "Weg", "Platz", "Allee", "Gasse"],
            "unit_types": ["Wohnung", "App.", "Zi."],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Berlin FO", "München FO", "Hamburg FO", "Frankfurt FO", "Düsseldorf FO"],
        "nationality": "Germany"
    },
    "France": {
        "first_names": ["Pierre", "Marie", "Jean", "Françoise", "Michel", "Monique", "Philippe", "Catherine", "Alain", "Nathalie",
                       "Bernard", "Isabelle", "Christian", "Sylvie", "Daniel", "Martine", "André", "Nicole", "Henri", "Chantal"],
        "last_names": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau",
                      "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier"],
        "city_state_mapping": {
            "Paris": "Île-de-France",
            "Marseille": "Provence-Alpes-Côte d'Azur",
            "Nice": "Provence-Alpes-Côte d'Azur",
            "Toulon": "Provence-Alpes-Côte d'Azur",
            "Lyon": "Auvergne-Rhône-Alpes",
            "Saint-Étienne": "Auvergne-Rhône-Alpes",
            "Toulouse": "Occitanie",
            "Montpellier": "Occitanie",
            "Lille": "Hauts-de-France",
            "Le Havre": "Normandie",
            "Strasbourg": "Grand Est",
            "Reims": "Grand Est",
            "Nantes": "Pays de la Loire",
            "Rennes": "Bretagne",
            "Bordeaux": "Nouvelle-Aquitaine"
        },
        "address_format": {
            "street_types": ["Rue", "Avenue", "Boulevard", "Place", "Chemin", "Impasse"],
            "unit_types": ["Apt", "Bât", "Esc"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Paris FO", "Lyon FO", "Marseille FO", "Strasbourg FO", "Bordeaux FO"],
        "nationality": "France"
    },
    "India": {
        "first_names": ["Raj", "Priya", "Amit", "Atul", "Sunita", "Vikash", "Anita", "Suresh", "Kavita", "Ramesh", "Geeta",
                       "Ajay", "Sita", "Manoj", "Radha", "Deepak", "Meera", "Rakesh", "Lata", "Ashok", "Usha"],
        "last_names": ["Sharma", "Verma", "Singh", "Chhotray", "Choudhary", "Kumar", "Gupta", "Agarwal", "Tiwari", "Mishra", "Jain", "Bansal",
                      "Sinha", "Pandey", "Yadav", "Arora", "Malhotra", "Chopra", "Shah", "Patel", "Mehta", "Khanna"],
        "city_state_mapping": {
            "Mumbai": "Maharashtra",
            "Thane": "Maharashtra", 
            "Pune": "Maharashtra",
            "Nagpur": "Maharashtra",
            "Delhi": "Delhi",
            "Bangalore": "Karnataka",
            "Hyderabad": "Telangana",
            "Ahmedabad": "Gujarat",
            "Surat": "Gujarat",
            "Chennai": "Tamil Nadu",
            "Kolkata": "West Bengal",
            "Jaipur": "Rajasthan",
            "Bhubaneshwar": "Odisha",
            "Lucknow": "Uttar Pradesh",
            "Kanpur": "Uttar Pradesh",
            "Indore": "Madhya Pradesh",
            "Nainital": "Uttarakhand",
            "Chandigarh": "Punjab"
        },
        "address_format": {
            "street_types": ["Road", "Lane", "Marg", "Cross", "Main Road"],
            "unit_types": ["Flat", "Apartment", "Block"],
            "postal_code_format": "999999"
        },
        "intake_locations": ["Mumbai FO", "Delhi FO", "Chennai FO", "Kolkata FO", "Bangalore FO"],
        "nationality": "India"
    },
    "UK": {
        "first_names": ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
                       "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen"],
        "last_names": ["Smith", "Jones", "Taylor", "Williams", "Brown", "Davies", "Evans", "Wilson", "Thomas", "Roberts",
                      "Johnson", "Lewis", "Walker", "Robinson", "Wood", "Thompson", "White", "Watson", "Jackson", "Wright"],
        "city_state_mapping": {
            "London": "England",
            "Birmingham": "England",
            "Manchester": "England",
            "Liverpool": "England",
            "Leeds": "England",
            "Sheffield": "England",
            "Bristol": "England",
            "Leicester": "England",
            "Coventry": "England",
            "Bradford": "England",
            "Nottingham": "England",
            "Glasgow": "Scotland",
            "Edinburgh": "Scotland",
            "Cardiff": "Wales",
            "Belfast": "Northern Ireland"
        },
        "address_format": {
            "street_types": ["Road", "Street", "Lane", "Avenue", "Close", "Drive", "Place", "Way"],
            "unit_types": ["Flat", "Apt", "Unit"],
            "postal_code_format": "A99 9AA"  # UK postcode format
        },
        "intake_locations": ["London FO", "Manchester FO", "Edinburgh FO", "Belfast FO", "Cardiff FO"],
        "nationality": "United Kingdom"
    },
    "Canada": {
        "first_names": ["Liam", "Emma", "Noah", "Olivia", "William", "Ava", "James", "Isabella", "Benjamin", "Sophia",
                       "Lucas", "Charlotte", "Henry", "Mia", "Alexander", "Amelia", "Mason", "Harper", "Michael", "Evelyn"],
        "last_names": ["Smith", "Brown", "Tremblay", "Martin", "Roy", "Wilson", "MacDonald", "Johnson", "Taylor", "Anderson",
                      "Clark", "Thompson", "Lee", "White", "Harris", "Lewis", "Walker", "Hall", "Young", "Allen"],
        "city_state_mapping": {
            "Toronto": "Ontario",
            "Ottawa": "Ontario",
            "Hamilton": "Ontario",
            "Kitchener": "Ontario",
            "London": "Ontario",
            "Montreal": "Quebec",
            "Quebec City": "Quebec",
            "Vancouver": "British Columbia",
            "Victoria": "British Columbia",
            "Calgary": "Alberta",
            "Edmonton": "Alberta",
            "Winnipeg": "Manitoba",
            "Regina": "Saskatchewan",
            "Saskatoon": "Saskatchewan",
            "Halifax": "Nova Scotia"
        },
        "address_format": {
            "street_types": ["Street", "Avenue", "Road", "Drive", "Boulevard", "Lane", "Way", "Circle"],
            "unit_types": ["Apt", "Suite", "Unit"],
            "postal_code_format": "A9A 9A9"  # Canadian postal code format
        },
        "intake_locations": ["Toronto FO", "Vancouver FO", "Montreal FO", "Calgary FO", "Ottawa FO"],
        "nationality": "Canada"
    },
    "Algeria": {
        "first_names": ["Mohammed", "Fatima", "Ahmed", "Aicha", "Ali", "Khadija", "Omar", "Amina", "Youssef", "Zahra",
                       "Abdelkader", "Rachida", "Karim", "Nadia", "Hassan", "Samira", "Samir", "Leila", "Tayeb", "Malika"],
        "last_names": ["Benaissa", "Boumediene", "Cherif", "Djamel", "Hamidi", "Kaci", "Larbi", "Mahmoudi", "Naceur", "Ouali",
                      "Rahmani", "Slimani", "Touati", "Yahi", "Zerrouki", "Benali", "Chabane", "Ferhat", "Mansouri", "Saidi"],
        "city_state_mapping": {
            "Algiers": "Algiers Province",
            "Oran": "Oran Province",
            "Constantine": "Constantine Province",
            "Annaba": "Annaba Province",
            "Blida": "Blida Province",
            "Batna": "Batna Province",
            "Djelfa": "Djelfa Province",
            "Sétif": "Sétif Province",
            "Sidi Bel Abbès": "Sidi Bel Abbès Province",
            "Biskra": "Biskra Province",
            "Tebessa": "Tebessa Province",
            "Tlemcen": "Tlemcen Province",
            "Béchar": "Béchar Province",
            "Tiaret": "Tiaret Province",
            "Bordj Bou Arréridj": "Bordj Bou Arréridj Province"
        },
        "address_format": {
            "street_types": ["Rue", "Avenue", "Boulevard", "Place", "Chemin"],
            "unit_types": ["App", "Apt", "Bloc"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Algiers FO", "Oran FO", "Constantine FO", "Annaba FO", "Blida FO"],
        "nationality": "Algeria"
    },
    "Egypt": {
        "first_names": ["Mohamed", "Fatma", "Ahmed", "Aisha", "Omar", "Khadija", "Hassan", "Amira", "Ali", "Nour",
                       "Mahmoud", "Salma", "Youssef", "Mariam", "Khaled", "Dina", "Tamer", "Yasmin", "Amr", "Rana"],
        "last_names": ["Hassan", "Mohamed", "Ahmed", "Ali", "Ibrahim", "Mahmoud", "Abdel Rahman", "Omar", "Youssef", "Khalil",
                      "Farouk", "Mostafa", "Gamal", "Said", "Nasser", "Abdel Aziz", "Mansour", "Rashid", "Fouad", "Saleh"],
        "city_state_mapping": {
            "Cairo": "Cairo Governorate",
            "Alexandria": "Alexandria Governorate",
            "Giza": "Giza Governorate",
            "Shubra El Kheima": "Qalyubia Governorate",
            "Port Said": "Port Said Governorate",
            "Suez": "Suez Governorate",
            "Luxor": "Luxor Governorate",
            "Mansoura": "Dakahlia Governorate",
            "El Mahalla El Kubra": "Gharbia Governorate",
            "Tanta": "Gharbia Governorate",
            "Asyut": "Asyut Governorate",
            "Ismailia": "Ismailia Governorate",
            "Fayyum": "Fayyum Governorate",
            "Zagazig": "Sharqia Governorate",
            "Aswan": "Aswan Governorate"
        },
        "address_format": {
            "street_types": ["شارع", "طريق", "ميدان", "حي", "منطقة"],
            "unit_types": ["شقة", "دور", "عمارة"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Cairo FO", "Alexandria FO", "Giza FO", "Port Said FO", "Luxor FO"],
        "nationality": "Egypt"
    },
    "Malaysia": {
        "first_names": ["Ahmad", "Siti", "Muhammad", "Nur", "Ali", "Fatimah", "Hassan", "Aishah", "Ibrahim", "Khadijah",
                       "Wei Ming", "Li Hua", "Raj", "Priya", "Kumar", "Devi", "Muthu", "Kamala", "Bala", "Shanti"],
        "last_names": ["Abdullah", "Ahmad", "Ibrahim", "Ismail", "Omar", "Rahman", "Hassan", "Ali", "Mohamed", "Yaacob",
                      "Lim", "Tan", "Lee", "Wong", "Ng", "Singh", "Kumar", "Raj", "Nair", "Pillai"],
        "city_state_mapping": {
            "Kuala Lumpur": "Federal Territory of Kuala Lumpur",
            "George Town": "Penang",
            "Ipoh": "Perak",
            "Shah Alam": "Selangor",
            "Petaling Jaya": "Selangor",
            "Klang": "Selangor",
            "Johor Bahru": "Johor",
            "Kuching": "Sarawak",
            "Kota Kinabalu": "Sabah",
            "Malacca City": "Malacca",
            "Alor Setar": "Kedah",
            "Miri": "Sarawak",
            "Kuala Terengganu": "Terengganu",
            "Kota Bharu": "Kelantan",
            "Kuantan": "Pahang"
        },
        "address_format": {
            "street_types": ["Jalan", "Lorong", "Persiaran", "Lebuh", "Tingkat"],
            "unit_types": ["Unit", "Tingkat", "Blok"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Kuala Lumpur FO", "George Town FO", "Johor Bahru FO", "Kuching FO", "Kota Kinabalu FO"],
        "nationality": "Malaysia"
    },
    "Bolivia": {
        "first_names": ["Carlos", "María", "Luis", "Ana", "José", "Carmen", "Juan", "Rosa", "Miguel", "Elena",
                       "Diego", "Patricia", "Fernando", "Luz", "Roberto", "Gloria", "Pedro", "Isabel", "Antonio", "Esperanza"],
        "last_names": ["Mamani", "Quispe", "Condori", "Huanca", "Apaza", "Choque", "Flores", "García", "López", "Martínez",
                      "Rodríguez", "Pérez", "Sánchez", "Morales", "Vargas", "Herrera", "Castro", "Jiménez", "Ruiz", "Díaz"],
        "city_state_mapping": {
            "Santa Cruz": "Santa Cruz Department",
            "La Paz": "La Paz Department",
            "Cochabamba": "Cochabamba Department",
            "Sucre": "Chuquisaca Department",
            "Oruro": "Oruro Department",
            "Tarija": "Tarija Department",
            "Potosí": "Potosí Department",
            "Trinidad": "Beni Department",
            "Cobija": "Pando Department",
            "Riberalta": "Beni Department",
            "Montero": "Santa Cruz Department",
            "Yacuiba": "Tarija Department",
            "Warnes": "Santa Cruz Department",
            "Llallagua": "Potosí Department",
            "Quillacollo": "Cochabamba Department"
        },
        "address_format": {
            "street_types": ["Calle", "Avenida", "Plaza", "Barrio", "Zona"],
            "unit_types": ["Casa", "Depto", "Piso"],
            "postal_code_format": "9999"
        },
        "intake_locations": ["La Paz FO", "Santa Cruz FO", "Cochabamba FO", "Sucre FO", "Tarija FO"],
        "nationality": "Bolivia"
    },
    "Mexico": {
        "first_names": ["José", "María", "Juan", "Ana", "Carlos", "Carmen", "Luis", "Rosa", "Miguel", "Elena",
                       "Francisco", "Patricia", "Antonio", "Laura", "Alejandro", "Isabel", "Fernando", "Guadalupe", "Roberto", "Leticia"],
        "last_names": ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez", "Cruz", "Flores",
                      "Gómez", "Morales", "Vásquez", "Jiménez", "Reyes", "Díaz", "Torres", "Gutiérrez", "Ruiz", "Hernández"],
        "city_state_mapping": {
            "Mexico City": "Mexico City",
            "Guadalajara": "Jalisco",
            "Monterrey": "Nuevo León",
            "Puebla": "Puebla",
            "Tijuana": "Baja California",
            "León": "Guanajuato",
            "Juárez": "Chihuahua",
            "Torreón": "Coahuila",
            "Querétaro": "Querétaro",
            "San Luis Potosí": "San Luis Potosí",
            "Mérida": "Yucatán",
            "Mexicali": "Baja California",
            "Aguascalientes": "Aguascalientes",
            "Tampico": "Tamaulipas",
            "Cuernavaca": "Morelos"
        },
        "address_format": {
            "street_types": ["Calle", "Avenida", "Boulevard", "Privada", "Callejón"],
            "unit_types": ["Casa", "Depto", "Piso", "Local"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Mexico City FO", "Guadalajara FO", "Monterrey FO", "Tijuana FO", "Mérida FO"],
        "nationality": "Mexico"
    },
    "Guatemala": {
        "first_names": ["José", "María", "Juan", "Ana", "Carlos", "Carmen", "Luis", "Rosa", "Miguel", "Elena",
                       "Francisco", "Patricia", "Antonio", "Laura", "Manuel", "Isabel", "Pedro", "Gloria", "Diego", "Esperanza"],
        "last_names": ["López", "García", "Martínez", "Pérez", "González", "Rodríguez", "Morales", "Hernández", "Jiménez", "Cruz",
                      "Flores", "Castillo", "Reyes", "Sánchez", "Ramírez", "Torres", "Vásquez", "Gutiérrez", "Ruiz", "Díaz"],
        "city_state_mapping": {
            "Guatemala City": "Guatemala Department",
            "Mixco": "Guatemala Department",
            "Villa Nueva": "Guatemala Department",
            "Petapa": "Guatemala Department",
            "San Juan Sacatepéquez": "Guatemala Department",
            "Quetzaltenango": "Quetzaltenango Department",
            "Escuintla": "Escuintla Department",
            "Villa Canales": "Guatemala Department",
            "Cobán": "Alta Verapaz Department",
            "Chimaltenango": "Chimaltenango Department",
            "Huehuetenango": "Huehuetenango Department",
            "Amatitlán": "Guatemala Department",
            "Totonicapán": "Totonicapán Department",
            "Santa Catarina Pinula": "Guatemala Department",
            "Puerto Barrios": "Izabal Department"
        },
        "address_format": {
            "street_types": ["Calle", "Avenida", "Boulevard", "Callejón", "Diagonal"],
            "unit_types": ["Casa", "Apartamento", "Nivel"],
            "postal_code_format": "99999"
        },
        "intake_locations": ["Guatemala City FO", "Quetzaltenango FO", "Escuintla FO", "Cobán FO", "Huehuetenango FO"],
        "nationality": "Guatemala"
    }
}

OCCUPATIONS = ["Unemployed", "Student", "Engineer", "Teacher", "Nurse", "Developer", "Chef", "Retail Worker", "Manager", "Consultant", "Scientist"]


def get_available_countries():
    """Get list of available countries for generation."""
    return list(COUNTRY_DATA.keys())


def get_country_data(country: str) -> Dict:
    """Get country-specific data configuration."""
    if country not in COUNTRY_DATA:
        raise ValueError(f"Country '{country}' not supported. Available countries: {get_available_countries()}")
    return COUNTRY_DATA[country]


def generate_postal_code(format_pattern: str) -> str:
    """Generate postal code based on country format pattern.
    
    Format patterns:
    - 9: Random digit (0-9)
    - A: Random uppercase letter (A-Z)
    - a: Random lowercase letter (a-z)
    - Other chars: Literal characters (spaces, hyphens, etc.)
    """
    result = ""
    for char in format_pattern:
        if char == '9':
            result += str(random.randint(0, 9))
        elif char == 'A':
            result += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        elif char == 'a':
            result += random.choice('abcdefghijklmnopqrstuvwxyz')
        else:
            result += char
    return result


def generate_address(country_data: Dict, city: str, state: str, country: str) -> Dict:
    """Generate address based on country-specific format."""
    address_format = country_data["address_format"]
    street_number = random.randint(1, 9999)
    street_name = random.choice(["Oak", "Main", "First", "Second", "Park", "Washington", "Lincoln", "Jefferson"])
    street_type = random.choice(address_format["street_types"])
    
    # Generate unit number (30% chance)
    unit_number = ""
    if random.random() < 0.3:
        unit_type = random.choice(address_format["unit_types"])
        unit_num = random.randint(1, 50)
        unit_number = f"{unit_type} {unit_num}"
    
    postal_code = generate_postal_code(address_format["postal_code_format"])
    
    return {
        "street_number": f"{street_number} {street_name} {street_type}",
        "unit_number": unit_number,
        "postal_code": postal_code,
        "city": city,
        "state": state,
        "country": country
    }


def random_date(start_year=1940, end_year=2001):
    """Generate random valid date."""
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    
    # Handle February in leap years
    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            day = random.randint(1, 29)  # Leap year
        else:
            day = random.randint(1, 28)  # Non-leap year
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)  # Months with 30 days
    else:
        day = random.randint(1, 31)  # Months with 31 days
    
    return {"year": year, "month": month, "day": day}


def make_person(i: int, template: Dict, country: str) -> Dict:
    """Generate a person with country-specific data."""
    country_data = get_country_data(country)
    
    # Select random data from country-specific lists
    first = random.choice(country_data["first_names"])
    last = random.choice(country_data["last_names"])
    
    # Handle city-state selection using mapping for geographic accuracy
    # All countries now have city_state_mapping
    city = random.choice(list(country_data["city_state_mapping"].keys()))
    state = country_data["city_state_mapping"][city]
    
    dob = random_date()

    person = template.copy()
    person["visa_application_number"] = f"AUTO{i:06d}"
    person["case_type"] = random.choice(["Schengen Short Stay", "Tourist", "Student Visa"])[:30]
    person["visa_type_requested"] = random.choice(["Short Stay 30 Days", "Short Stay 60 Days"])[:30]
    person["application_type"] = random.choice(["Initial", "Renewal"])[:10]
    person["submission_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    person["intake_location"] = random.choice(country_data["intake_locations"])
    person["applicant_is_minor"] = random.random() < 0.15
    person["urgent"] = random.random() < 0.1
    person["given_names"] = first
    person["surname"] = last
    person["variation_in_birth_certificate"] = random.random() < 0.05
    person["gender"] = random.choice(["Female", "Male", "Other"])
    person["country_of_nationality"] = country_data["nationality"]
    
    # Generate country-specific address
    person["address"] = generate_address(country_data, city, state, country_data["nationality"])
    
    person["date_of_birth"] = dob
    
    # Generate place of birth using city-state mapping
    birth_city = random.choice(list(country_data["city_state_mapping"].keys()))
    birth_state = country_data["city_state_mapping"][birth_city]
    
    person["place_of_birth"] = {
        "city": birth_city, 
        "state": birth_state, 
        "country": country_data["nationality"]
    }
    
    # Set residency status in their country of residence (home country)
    # Use standard residency statuses for all countries, weighted towards citizenship
    person["residency_status_in_country_of_residence"] = random.choices(
        ["Citizen", "Permanent Resident", "Temporary Resident"],
        weights=[0.7, 0.2, 0.1]  # 70% Citizen, 20% Permanent Resident, 10% Temporary Resident
    )[0]
    
    person["civil_status"] = random.choice(["Single", "Married", "Divorced"])
    
    # EU membership logic
    eu_countries = ["Germany", "France"]  # Add more EU countries as needed
    person["packaged_member_of_eu"] = country in eu_countries
    
    person["occupation"] = random.choice(OCCUPATIONS)
    return person


def main(count: int = 200, start: int = 1000, country: str = "USA", out_dir=OUTPUT_DIR):
    """Generate synthetic person data for specified country."""
    # Validate country
    if country not in COUNTRY_DATA:
        print(f"Error: Country '{country}' not supported.")
        print(f"Available countries: {', '.join(get_available_countries())}")
        return
    
    out_dir.mkdir(parents=True, exist_ok=True)
    template = load_template()
    
    print(f"Generating {count} persons from {country}...")
    
    for i in range(start, start + count):
        p = make_person(i, template, country)
        out_path = out_dir / f"person_{i:03d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    
    print(f"Wrote {count} person files from {country} to {out_dir}")
    print(f"Files: person_{start:03d}.json to person_{start + count - 1:03d}.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic person data for visa applications by country"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=200, 
        help="Number of person records to generate (default: 200)"
    )
    parser.add_argument(
        "--start", 
        type=int, 
        default=1000, 
        help="Starting index for person numbering (default: 1000)"
    )
    parser.add_argument(
        "--country", 
        type=str, 
        default="USA", 
        choices=get_available_countries(),
        help=f"Country to generate data for. Available: {', '.join(get_available_countries())}"
    )
    parser.add_argument(
        "--list-countries", 
        action="store_true", 
        help="List available countries and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_countries:
        print("Available countries:")
        for country in get_available_countries():
            print(f"  - {country}")
        print("\nExample usage:")
        print(f"  python {Path(__file__).name} --country USA --count 100")
        print(f"  python {Path(__file__).name} --country Germany --count 50 --start 2000")
        exit(0)
    
    main(count=args.count, start=args.start, country=args.country)
