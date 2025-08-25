import json
import random
from datetime import datetime

from generate_user_fixtures import MAX_USERS

MAX_RECRUITMENTS = 50
RECRUITMENT_FIXTURE_FILE_PATH = "matching_app/fixtures/recruitment_fixtures.json"

user_ids = list(range(1, MAX_USERS + 1))
titles = ["event", "party", "study", "hobby", "game", "other"]
contents = [
    "Let's have fun together!",
    "We can enjoy together!",
    "I want have a good time!",
    "I want to learn something new!",
    "I want to play something!",
    "I want to do other things!",
]

base_date = datetime(2025, 1, 1)


def generate_recruitment_fixtures() -> list[dict]:
    fixtures = []
    for i in range(1, MAX_RECRUITMENTS + 1):
        date_str = base_date.strftime("%Y-%m-%d %H:%M:%S")

        recruitment = {
            "model": "matching_app.recruitment",
            "pk": i,
            "fields": {
                "created_at": date_str,
                "updated_at": date_str,
                "user": random.choice(user_ids),
                "title": random.choice(titles),
                "content": random.choice(contents),
            },
        }
        fixtures.append(recruitment)

    return fixtures


def write_fixtures_to_file(fixtures: list[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    print("Generating recruitment fixtures...")
    fixtures = generate_recruitment_fixtures()
    write_fixtures_to_file(fixtures, RECRUITMENT_FIXTURE_FILE_PATH)
    print("Recruitment fixtures generated successfully.")
