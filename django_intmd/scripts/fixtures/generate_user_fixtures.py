import json
import random
from datetime import datetime

MAX_USERS = 50
USER_FIXTURE_FILE_PATH = "matching_app/fixtures/user_fixtures.json"

min_date_of_birth = datetime.now().year - 50
max_date_of_birth = datetime.now().year - 18

user_ids = list(range(1, MAX_USERS + 1))
addresses = ["Tokyo", "Osaka", "Fukuoka", "Sapporo", "Nagoya", "Hiroshima", "Sendai", "Yokohama", "Saitama", "Chiba"]
occupations = [
    "Engineer",
    "Designer",
    "Manager",
    "Sales",
    "Marketing",
    "Accounting",
    "HR",
    "Legal",
    "Customer Support",
    "Other",
]
biographies = [
    "I'm a software engineer.",
    "I'm a designer.",
    "I'm a manager.",
    "I'm a sales.",
    "I'm a marketing.",
    "I'm an accountant.",
    "I'm an HR.",
    "I'm a legal.",
    "I'm a customer support.",
    "I'm a legal.",
]

base_date = datetime(2025, 1, 1)


def get_age_from_date_of_birth(date_of_birth: datetime) -> int:
    today = datetime.now()
    if date_of_birth.month < today.month:
        return today.year - date_of_birth.year
    elif date_of_birth.month == today.month and date_of_birth.day <= today.day:
        return today.year - date_of_birth.year
    else:
        return today.year - date_of_birth.year - 1


def generate_user_fixtures() -> list[dict]:
    fixtures = []
    for i in range(1, MAX_USERS + 1):
        date_str = base_date.strftime("%Y-%m-%d %H:%M:%S")
        date_of_birth = datetime(random.randint(min_date_of_birth, max_date_of_birth), 1, 1)
        date_of_birth_str = date_of_birth.strftime("%Y-%m-%d")
        age = get_age_from_date_of_birth(date_of_birth)

        user = {
            "model": "matching_app.user",
            "pk": i,
            "fields": {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": f"password{i}",
                "date_of_birth": date_of_birth_str,
            },
        }
        user_profile = {
            "model": "matching_app.userprofile",
            "pk": i,
            "fields": {
                "user": i,
                "age": age,
                "address": random.choice(addresses),
                "occupation": random.choice(occupations),
                "biography": random.choice(biographies),
                "created_at": date_str,
                "updated_at": date_str,
            },
        }
        fixtures.append(user)
        fixtures.append(user_profile)
    return fixtures


def write_fixtures_to_file(fixtures: list[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    print("Generating user fixtures...")
    fixtures = generate_user_fixtures()
    write_fixtures_to_file(fixtures, USER_FIXTURE_FILE_PATH)
    print("User fixtures generated successfully.")
