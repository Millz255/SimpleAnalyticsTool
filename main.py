from extractor.text_extractor import extract_text, UnsupportedFileTypeError
from analyzer.text_analyzer import TextAnalyzer
from extractor.financial_data_extractor import extract_all_financial_data  # <-- import your extractor


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
        print(text[:500].strip())  # First 500 characters
        print("-" * 60)

        # Extract structured financial data
        data = extract_all_financial_data(text)

        if data.get("email") is None:
            print("⚠️ Email not found; many Tanzanians may not have one.")
        else:
            print(f"Email: {data['email']}")

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
