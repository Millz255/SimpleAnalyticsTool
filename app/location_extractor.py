import json
import os
from typing import Dict, Optional

# Load location data once when module is imported
LOCATION_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'tanzania_locations.json')

def load_location_data() -> Dict[str, Dict[str, list]]:

    with open(LOCATION_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

LOCATION_DATA = load_location_data()

def extract_location(text: str) -> Dict[str, Optional[str]]:

    text_lower = text.lower()
    result = {
        "region": None,
        "district": None,
        "ward": None
    }

    for region, districts in LOCATION_DATA.items():
        if region.lower() in text_lower:
            result["region"] = region
            for district, wards in districts.items():
                if district.lower() in text_lower:
                    result["district"] = district
                    for ward in wards:
                        if ward.lower() in text_lower:
                            result["ward"] = ward
                            return result
                    return result
            return result
    return result

# For quick testing when running this file directly
if __name__ == "__main__":
    test_text = (
        "The client is located in Dar es Salaam, in the Kinondoni district, "
        "specifically in the Mikocheni ward."
    )
    location = extract_location(test_text)
    print(location)
