from extractor.text_extractor import extract_text, UnsupportedFileTypeError
from analyzer.text_analyzer import TextAnalyzer
from extractor.financial_extractor import extract_all_financial_data  # corrected import name


def print_header():
    print("=" * 60)
    print("🧠  Simple Analytics Tool".center(60))
    print("=" * 60)


def prompt_file_path() -> str:
    file_path = input("📄 Enter the full path to your document (.txt, .pdf, .docx): ").strip()
    if not file_path:
        raise ValueError("⚠️  File path cannot be empty.")
    return file_path


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
        print(text[:500].strip())  # Show first 500 characters
        print("-" * 60)

        # Extract structured financial data
        data = extract_all_financial_data(text)

        if data.get("email") is None:
            print("⚠️ Email not found; many Tanzanians may not have one.")
        else:
            print(f"Email: {data['email']}")

        print(f"Phone: {data.get('phone', 'N/A')}")
        print(f"NIDA Number: {data.get('nida_number', 'N/A')}")
        print(f"Age: {data.get('age', 'N/A')}")
        print(f"Income: {data.get('income', 'N/A')}")
        print(f"Location: {data.get('location', 'N/A')}")

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
