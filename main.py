import os
from extractor.text_extractor import extract_text, UnsupportedFileTypeError
from analyzer.text_analyzer import TextAnalyzer
from extractor.financial_extractor import extract_all_financial_data


def print_header():
    print("=" * 60)
    print("🧠  Simple Analytics Tool".center(60))
    print("=" * 60)


def prompt_file_path() -> str:
    file_path = input("📄 Enter the full path to your document (.txt, .pdf, .docx): ").strip()
    if not file_path:
        raise ValueError("⚠️  File path cannot be empty.")
    return file_path


def display_financial_data(data: dict):
    print("\n💰 Extracted Financial Data:")

    full_name = data.get("full_name")
    print(f" - Full Name: {full_name if full_name else 'Not found'}")

    phones = data.get("phone_numbers")
    print(f" - Phone Number(s): {', '.join(phones) if phones else 'Not found'}")

    nida = data.get("nida_number")
    print(f" - NIDA Number: {nida if nida else 'Not found'}")

    age = data.get("age")
    print(f" - Age: {age if age is not None else 'Not found'}")

    location = data.get("location")
    if location:
        print("\n📍 Location Information:")
        for level in ["region", "district", "ward"]:
            val = location.get(level)
            if val:
                print(f"  {level.capitalize()}: {val}")

    income = data.get("income_tzs")
    print(f" - Income (TZS): {income:,.0f}" if income is not None else " - Income (TZS): Not found")

    balance = data.get("bank_balance_tzs")
    print(f" - Bank Balance (TZS): {balance:,.0f}" if balance is not None else " - Bank Balance (TZS): Not found")

    loan_limit = data.get("loan_limit_tzs")
    print(f" - Loan Limit (TZS): {loan_limit:,.0f}" if loan_limit is not None else " - Loan Limit (TZS): Not found")


def main():
    print_header()

    try:
        file_path = prompt_file_path()
        print("\n🔍 Extracting text...\n")
        text = extract_text(file_path)

        if not text.strip():
            print("⚠️  No readable text was extracted from the document.")
            return

        print("✅ Extraction successful! Here's a preview:\n")
        print("-" * 60)
        print(text[:500].strip())
        print("-" * 60)

        data = extract_all_financial_data(text)

        # If you want to handle email extraction and it's not implemented in extractor,
        # just note here:
        if data.get("email") is None:
            print("\n⚠️ Email not found; many Tanzanians may not have one.")
        else:
            print(f"\nEmail: {data['email']}")

        display_financial_data(data)

        print("\n🔎 Analyzing text...\n")
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze(text)

        print("📝 Summary:")
        print(analysis['summary'])
        print("\n🔑 Key Phrases:")
        print(", ".join(analysis['key_phrases']))
        print("\n🧩 Named Entities:")
        for ent in analysis['named_entities']:
            print(f" - {ent['text']} [{ent['label']}]")

    except FileNotFoundError as fnf:
        print(str(fnf))
    except UnsupportedFileTypeError as uft:
        print(str(uft))
    except ValueError as ve:
        print(f"⚠️  {ve}")
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
