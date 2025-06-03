import re
from typing import Dict, Optional


def analyze_financial_data(text: str) -> Dict[str, Optional[str]]:
    """Analyzes financial document text and extracts structured customer data."""

    data = {
        "full_name": extract_full_name(text),
        "nida_number": extract_nida(text),
        "phone_number": extract_phone(text),
        "email": extract_email(text),
        "age": extract_age(text),
        "location": extract_location(text),
        "employment_status": extract_employment(text),
        "monthly_income_tzs": extract_income(text),
        "bank_balance_tzs": extract_balance(text),
        "loan_purpose": extract_loan_purpose(text),
        "requested_loan_amount": extract_requested_loan(text),
        "estimated_max_loan_limit": None  # calculated below
    }

    # Calculate loan capacity (up to 5× income if income exists)
    try:
        income = clean_tzs_to_number(data["monthly_income_tzs"])
        if income:
            data["estimated_max_loan_limit"] = f"TZS {income * 5:,.0f}"
    except Exception:
        pass

    return data


# Individual extraction functions below

def extract_full_name(text: str) -> Optional[str]:
    lines = text.strip().split("\n")
    for line in lines[:5]:
        if re.match(r"^[A-Z][a-z]+\s[A-Z][a-z]+(\s[A-Z][a-z]+)?$", line.strip()):
            return line.strip()
    return None


def extract_nida(text: str) -> Optional[str]:
    match = re.search(r'\b[1-9]\d{19}\b', text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    match = re.search(r'\b(?:\+255|0)[67][0-9]{8}\b', text)
    return match.group(0) if match else None


def extract_email(text: str) -> Optional[str]:
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    return match.group(0) if match else None


def extract_age(text: str) -> Optional[str]:
    match = re.search(r'Age[:\s]*([1-9][0-9]?)\b', text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_location(text: str) -> Optional[str]:
    keywords = ["Dar es Salaam", "Arusha", "Mbeya", "Njombe", "Mwanza", "Dodoma", "Moshi"]
    for place in keywords:
        if place.lower() in text.lower():
            return place
    return None


def extract_employment(text: str) -> Optional[str]:
    options = ["self-employed", "unemployed", "employed", "business owner", "farmer"]
    for status in options:
        if status in text.lower():
            return status.capitalize()
    return None


def extract_income(text: str) -> Optional[str]:
    match = re.search(r'(?i)(?:monthly income|income)[:\s]*TZS[\s,]*([\d,]+)', text)
    return f"TZS {match.group(1).replace(',', '')}" if match else None


def extract_balance(text: str) -> Optional[str]:
    match = re.search(r'(?i)(?:bank balance|savings)[:\s]*TZS[\s,]*([\d,]+)', text)
    return f"TZS {match.group(1).replace(',', '')}" if match else None


def extract_requested_loan(text: str) -> Optional[str]:
    match = re.search(r'(?i)(?:requested loan|loan amount)[:\s]*TZS[\s,]*([\d,]+)', text)
    return f"TZS {match.group(1).replace(',', '')}" if match else None


def extract_loan_purpose(text: str) -> Optional[str]:
    purposes = [
        "business", "school fees", "health", "agriculture", "home improvement", "wedding"
    ]
    for purpose in purposes:
        if purpose in text.lower():
            return purpose.capitalize()
    return None


def clean_tzs_to_number(tzs_string: Optional[str]) -> Optional[int]:
    """Convert 'TZS 500,000' → 500000"""
    if not tzs_string:
        return None
    return int("".join(re.findall(r'\d+', tzs_string)))
