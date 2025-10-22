#!/usr/bin/env python3
"""Generate synthetic person JSON files for res/people.

Usage:
    python3 scripts/generate_people.py --count 200

This script writes files person_001.json .. person_NNN.json in res/people.
"""
import json
import random
import argparse
from pathlib import Path
from datetime import datetime


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "res" / "people"
TEMPLATE_PATH = OUTPUT_DIR / "person_template.json"


def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


FIRST_NAMES = ["Alex", "Sam", "Taylor", "Jordan", "Casey", "Jamie", "Morgan", "Riley", "Cameron", "Drew", "Avery", "Charlie", "Quinn", "Parker", " Rowan", "Lee", "Robin", "Skyler", "Blake", "Sasha"]
LAST_NAMES = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Lee", "Martin", "Clark", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Torres", "Nguyen", "Adams", "Baker"]
CITIES = ["Sydney", "Melbourne", "Brisbane", "Adelaide", "Perth", "Hobart", "Canberra", "Darwin", "Mount Reaper", "Snowy Plain"]
STATES = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "ACT", "NT"]
OCCUPATIONS = ["Unemployed", "Student", "Engineer", "Teacher", "Nurse", "Developer", "Chef", "Retail Worker", "Manager", "Consultant"]


def random_date(start_year=1940, end_year=2023):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    # ensure valid day count
    day = random.randint(1, 28)
    return {"year": year, "month": month, "day": day}


def make_person(i, template):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    city = random.choice(CITIES)
    state = random.choice(STATES)
    dob = random_date()

    person = template.copy()
    person["visa_application_number"] = f"AUTO{i:06d}"
    person["case_type"] = random.choice(["Schengen Short Stay", "Work Visa", "Student Visa"])[:30]
    person["visa_type_requested"] = random.choice(["Short Stay", "Long Stay"])[:30]
    person["application_type"] = random.choice(["Initial", "Renewal"])[:10]
    # random recent submission date
    person["submission_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    person["intake_location"] = random.choice(["Sydney FO", "Melbourne FO", "Brisbane FO"]) 
    person["applicant_is_minor"] = random.random() < 0.15
    person["urgent"] = random.random() < 0.1
    person["given_names"] = first
    person["surname"] = last
    person["variation_in_birth_certificate"] = random.random() < 0.05
    person["gender"] = random.choice(["Female", "Male", "Other"]) 
    person["country_of_nationality"] = "Australia"
    person["address"] = {
        "street_number": f"{random.randint(1,999)} {random.choice(['Eagles Road','Main St','Station Rd','High St'])}",
        "unit_number": random.choice(["", "A", "1", "2", "3"]),
        "postal_code": f"{random.randint(1000,9999):04d}",
        "city": city,
        "state": state,
        "country": "Australia"
    }
    person["date_of_birth"] = dob
    person["place_of_birth"] = {"city": random.choice(CITIES), "state": state, "country": "Australia"}
    person["residency_status_in_country_of_residence"] = random.choice(["Permanent Resident", "Citizen", "Temporary Resident"]) 
    person["civil_status"] = random.choice(["Single", "Married", "Divorced"]) 
    person["packaged_member_of_eu"] = False
    person["occupation"] = random.choice(OCCUPATIONS)
    return person


def main(count=200, out_dir=OUTPUT_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    template = load_template()
    for i in range(1, count + 1):
        p = make_person(i, template)
        out_path = out_dir / f"person_{i:03d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    print(f"Wrote {count} person files to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=200)
    args = parser.parse_args()
    main(count=args.count)
