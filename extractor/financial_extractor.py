import re
from typing import Optional, Dict


def extract_email(text: str) -> Optional[str]:
    pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    match = pattern.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    # Tanzanian phone numbers typically start with +255 or 0 followed by 9 digits
    pattern = re.compile(r'(\+255|0)\d{9}')
    match = pattern.search(text)
    return match.group(0) if match else None


def extract_nida(text: str) -> Optional[str]:
    # Assuming NIDA number format: 9 alphanumeric characters (can be adjusted)
    pattern = re.compile(r'\b[A-Z0-9]{9}\b')
    # You might want to make this more specific with a prefix if known
    match = pattern.search(text)
    return match.group(0) if match else None


def extract_age(text: str) -> Optional[int]:
    # look for patterns like 'Age: 32' or 'aged 32'
    pattern = re.compile(r'Age[:\s]+(\d{1,3})|aged[:\s]+(\d{1,3})', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        age_str = match.group(1) or match.group(2)
        return int(age_str)
    return None


def extract_income(text: str) -> Optional[float]:
    # Basic pattern to capture monthly income e.g. "Income: 500000 TZS"
    pattern = re.compile(r'Income[:\s]+([\d,\.]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        # Remove commas and parse float
        income_str = match.group(1).replace(',', '')
        try:
            return float(income_str)
        except ValueError:
            return None
    return None


def extract_location(text: str) -> Optional[str]:
    # You can improve this by importing your detailed location extractor
    # For demo, just return first matching region from a list
    regions = ["Dar es Salaam", "Arusha", "Mbeya", "Njombe", "Mwanza", "Dodoma", "Moshi"]
    for region in regions:
        if region.lower() in text.lower():
            return region
    return None


def extract_all_financial_data(text: str) -> Dict[str, Optional[str]]:
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "nida_number": extract_nida(text),
        "age": extract_age(text),
        "income": extract_income(text),
        "location": extract_location(text),
        # Add more fields here as needed
    }
