from datetime import date, datetime, timedelta
from typing import Any

MIN_BIRTH_YEAR = 1920
MAX_BIRTH_YEAR = datetime.now().year - 18


def str_to_date(date_of_birth: str) -> datetime.date:
    date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    return date_of_birth


def get_age_from_date_of_birth(date_of_birth: Any) -> int:
    if isinstance(date_of_birth, str):
        date_of_birth = str_to_date(date_of_birth)
    if not isinstance(date_of_birth, date):
        raise ValueError("Invalid date of type")

    today = date.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


def is_over_18_years_old(day_of_birth: datetime.date) -> bool:
    today = date.today()
    age = today.year - day_of_birth.year
    if age < 18:
        return False
    elif age > 18:
        return True

    elif today.month > day_of_birth.month:
        return True
    elif today.month < day_of_birth.month:
        return False

    elif today.day >= day_of_birth.day:
        return True
    else:
        return False


def calculate_expiration_time(from_time: datetime, timedelta: timedelta) -> datetime:
    return from_time + timedelta
