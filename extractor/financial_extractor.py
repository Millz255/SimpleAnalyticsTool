import re
import json
import os
import sys
from typing import Optional, Dict, Any


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


with open(resource_path('app/data/tanzania_locations.json'), 'r', encoding='utf-8') as f:
    TANZANIA_LOCATIONS = json.load(f)


def extract_full_name(text: str) -> Optional[str]:
    # Look for common name introductions
    patterns = [
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}) is (?:a|an)",  # e.g. "John Doe is a..."
        r"My name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})",
        r"Name[:\s]*([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def extract_phone_numbers(text: str) -> Optional[list]:
    pattern = re.compile(r'(\+255|0)(7|6|5|4|2)\d{7,8}')
    return list(set([m.group() for m in pattern.finditer(text)]))


def extract_nida_number(text: str) -> Optional[str]:
    pattern = re.compile(r'(?:NIDA\s*Number[:\s]*)?([A-Z]?\d{15,17})', re.IGNORECASE)
    for match in pattern.findall(text):
        cleaned = match.replace(' ', '').replace('-', '')
        if len(cleaned) in (16, 17):
            return cleaned.upper()
    return None


def extract_age(text: str) -> Optional[int]:
    age_match = re.search(r'Age[:\s]+(\d{1,2})', text)
    if age_match:
        return int(age_match.group(1))

    birth_match = re.search(r'Born(?: in)?[:\s]*(\d{4})', text, re.IGNORECASE)
    if birth_match:
        from datetime import datetime
        birth_year = int(birth_match.group(1))
        age = datetime.now().year - birth_year
        if 0 < age < 120:
            return age
    return None


def extract_income(text: str) -> Optional[float]:
    patterns = [
        r'income of\s*([\d,]+)',
        r'earns\s*an\s*income\s*of\s*([\d,]+)',
        r'Income[:\s]*([\d,]+)'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                continue
    return None


def extract_bank_balance(text: str) -> Optional[float]:
    pattern = re.compile(r'(?:Bank\s*Balance|Balance)[:\s]*([\d,]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def extract_loan_limit(text: str) -> Optional[float]:
    patterns = [
        r'loan limit of\s*([\d,]+)',
        r'applied for (?:a )?loan.*?([\d,]+)',
        r'(?:Loan\s*limit|Borrowing\s*limit)[:\s]*([\d,]+)'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                continue
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


def extract_job_and_work(text: str) -> Dict[str, Optional[str]]:
    job_keywords = [
        "software developer", "engineer", "teacher", "manager", "consultant",
        "accountant", "driver", "nurse", "farmer", "mechanic", "worker",
        "developer", "technician", "officer", "supervisor", "assistant",
        "clerk", "operator", "analyst", "security", "doctor"
    ]
    job_pattern = re.compile(r'\b(' + '|'.join(job_keywords) + r')\b', re.IGNORECASE)
    job_match = job_pattern.search(text)
    job_title = job_match.group(1).title() if job_match else None

    workplace_patterns = [
        r'works at ([A-Z][\w&\s\-]+)',
        r'employed by ([A-Z][\w&\s\-]+)',
        r'working at ([A-Z][\w&\s\-]+)',
        r'employee of ([A-Z][\w&\s\-]+)',
    ]
    for pattern in workplace_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {"job_title": job_title, "workplace": match.group(1).strip()}
    return {"job_title": job_title, "workplace": None}


def extract_all_financial_data(text: str) -> Dict[str, Any]:
    return {
        "full_name": extract_full_name(text),
        "phone_numbers": extract_phone_numbers(text),
        "nida_number": extract_nida_number(text),
        "age": extract_age(text),
        "location": extract_location(text),
        "income_tzs": extract_income(text),
        "bank_balance_tzs": extract_bank_balance(text),
        "loan_limit_tzs": extract_loan_limit(text),
        **extract_job_and_work(text),
    }
