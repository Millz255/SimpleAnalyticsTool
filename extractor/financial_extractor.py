import re
import json
from typing import Optional, Dict, Any


with open('app/data/tanzania_locations.json', 'r', encoding='utf-8') as f:
    TANZANIA_LOCATIONS = json.load(f)

def extract_full_name(text: str) -> Optional[str]:
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})$', line):
            return line

        if line.isupper() and 2 <= len(line.split()) <= 4:
            return line.title()
    return None

def extract_phone_numbers(text: str) -> Optional[list]:
    pattern = re.compile(r'(\+255|0)(7|6|5|4|2)\d{7,8}')
    phones = pattern.findall(text)
    if phones:
        phones_full = [m.group() for m in pattern.finditer(text)]
        return list(set(phones_full))
    return None

def extract_nida_number(text: str) -> Optional[str]:
    pattern = re.compile(r'(?:NIDA\s*Number[:\s]*)?([A-Z]?\d{15,16})', re.IGNORECASE)
    matches = pattern.findall(text)
    for match in matches:
        candidate = match.replace(' ', '').replace('-', '')
        if len(candidate) in (16, 17):
            return candidate.upper()
    return None

def extract_age(text: str) -> Optional[int]:
    age_pattern = re.compile(r'Age[:\s]+(\d{1,2})')
    dob_pattern = re.compile(r'Date of Birth[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', re.IGNORECASE)
    year_pattern = re.compile(r'Born[:\s]+(\d{4})', re.IGNORECASE)

    age_match = age_pattern.search(text)
    if age_match:
        try:
            age = int(age_match.group(1))
            if 0 < age < 120:
                return age
        except ValueError:
            pass

    dob_match = dob_pattern.search(text)
    if dob_match:
        dob_str = dob_match.group(1)
        year_match = re.search(r'\d{4}', dob_str)
        if year_match:
            birth_year = int(year_match.group(0))
            from datetime import datetime
            current_year = datetime.now().year
            age = current_year - birth_year
            if 0 < age < 120:
                return age

    year_match = year_pattern.search(text)
    if year_match:
        birth_year = int(year_match.group(1))
        from datetime import datetime
        current_year = datetime.now().year
        age = current_year - birth_year
        if 0 < age < 120:
            return age

    return None

def extract_income(text: str) -> Optional[float]:
    pattern = re.compile(r'Income[:\s]*([\d,]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str)
        except ValueError:
            pass
    return None

def extract_bank_balance(text: str) -> Optional[float]:
    pattern = re.compile(r'(?:Bank\s*Balance|Balance)[:\s]*([\d,]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str)
        except ValueError:
            pass
    return None

def extract_loan_limit(text: str) -> Optional[float]:
    pattern = re.compile(r'(?:Loan\s*limit|Borrowing\s*limit)[:\s]*([\d,]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str)
        except ValueError:
            pass
    return None

def extract_location(text: str) -> Dict[str, Optional[str]]:

    text_lower = text.lower()

    for region, districts in TANZANIA_LOCATIONS.items():
        if region.lower() in text_lower:
            for district, wards in districts.items():
                if district.lower() in text_lower:
                    for ward in wards:
                        if ward.lower() in text_lower:
                            return {"region": region, "district": district, "ward": ward}
                    return {"region": region, "district": district, "ward": None}
            return {"region": region, "district": None, "ward": None}

    return {"region": None, "district": None, "ward": None}

def extract_all_financial_data(text: str) -> Dict[str, Any]:
    """
    Extract all relevant financial data from text into a structured dictionary.
    """
    return {
        "full_name": extract_full_name(text),
        "phone_numbers": extract_phone_numbers(text),
        "nida_number": extract_nida_number(text),
        "age": extract_age(text),
        "location": extract_location(text),
        "income_tzs": extract_income(text),
        "bank_balance_tzs": extract_bank_balance(text),
        "loan_limit_tzs": extract_loan_limit(text),
    }
