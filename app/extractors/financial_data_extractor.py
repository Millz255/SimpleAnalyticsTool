import re
from typing import Optional, Dict, Union
from datetime import datetime


def extract_name(text: str) -> Optional[str]:
    """
    A heuristic approach to extract full names:
    - Look for lines with capitalized words (2 or 3 words)
    - Could be improved with NLP or named entity recognition in future
    """
    # Simplistic regex looking for 2 or 3 consecutive capitalized words
    pattern = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})\b')
    matches = pattern.findall(text)
    return matches[0] if matches else None


def extract_age(text: str) -> Optional[int]:
    """
    Extract age from text.
    Looks for patterns like:
    - Age: 30
    - Born: 1994 (calculate age)
    """
    # First try Age: <number>
    age_match = re.search(r'Age[:\s]+(\d{1,3})', text, re.I)
    if age_match:
        return int(age_match.group(1))

    # Try to find birth year and calculate age
    birth_year_match = re.search(r'(Born|Birth Year|DOB)[:\s]+(\d{4})', text, re.I)
    if birth_year_match:
        birth_year = int(birth_year_match.group(2))
        current_year = datetime.now().year
        return current_year - birth_year

    return None


def extract_nida(text: str) -> Optional[str]:
    """
    Extract Tanzanian NIDA number.
    Format: 14 digit number, may contain spaces.
    Example: 1234 5678 9012 34 or 12345678901234
    """
    # Remove non-digit chars and then look for 14 digit number
    digits_only = re.sub(r'\D', '', text)
    nida_match = re.search(r'(\d{14})', digits_only)
    if nida_match:
        return nida_match.group(1)
    return None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract Tanzanian phone numbers.
    Formats:
    - +2557XXXXXXXX
    - 07XXXXXXXX
    """
    # Regex for phone number variants
    phone_pattern = re.compile(
        r'(\+2557\d{8}|07\d{8})'
    )
    match = phone_pattern.search(text)
    if match:
        return match.group(0)
    return None


def extract_email(text: str) -> Optional[str]:
    # Keep extraction same, but allow None
    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    match = email_pattern.search(text)
    return match.group(0) if match else None


def extract_amount(text: str, keywords: list) -> Optional[float]:
    """
    Generic function to extract amount of money after keywords.
    Supports Tsh, TSh, TZS, etc.
    Examples: "Income: Tsh 500,000", "Salary 1,200,000 TZS"
    """
    pattern = re.compile(
        rf"(?:{'|'.join(keywords)})[:\s]*T?h?s?\.?\s?([\d,]+)", re.I)
    match = pattern.search(text)
    if match:
        amount_str = match.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            return None
    return None


def extract_income(text: str) -> Optional[float]:
    return extract_amount(text, ['income', 'salary', 'monthly income'])


def extract_bank_balance(text: str) -> Optional[float]:
    return extract_amount(text, ['bank balance', 'account balance', 'balance'])


def extract_loan_limit(text: str) -> Optional[float]:
    return extract_amount(text, ['loan limit', 'borrowing capacity', 'loan capacity'])


def extract_all_financial_data(text: str) -> Dict[str, Union[str, int, float, None]]:
    """
    Aggregate function to extract all financial relevant data.
    """
    return {
        "name": extract_name(text),
        "age": extract_age(text),
        "nida": extract_nida(text),
        "phone": extract_phone(text),
        "email": extract_email(text),
        "income": extract_income(text),
        "bank_balance": extract_bank_balance(text),
        "loan_limit": extract_loan_limit(text)
    }
