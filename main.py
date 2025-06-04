import os
import traceback
import time
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"⚠️  File not found: {file_path}")
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


def generate_pdf_report(file_path: str, extracted_data: dict, analysis: dict):
    pdf_path = "analysis_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 40, 50
    y = height - y_margin

    def draw_line(text, offset=14, font="Helvetica", size=10):
        nonlocal y
        if y < y_margin:
            c.showPage()
            y = height - y_margin
        c.setFont(font, size)
        c.drawString(x_margin, y, text)
        y -= offset

    draw_line("📄 Document Analysis Report", offset=20, font="Helvetica-Bold", size=14)
    draw_line(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    draw_line(f"Source File: {os.path.basename(file_path)}")
    draw_line("")

    draw_line("💰 Financial Data Extracted:", font="Helvetica-Bold")
    draw_line(f"- Full Name: {extracted_data.get('full_name', 'Not found')}")
    phones = extracted_data.get("phone_numbers", [])
    draw_line(f"- Phone Number(s): {', '.join(phones) if phones else 'Not found'}")
    draw_line(f"- NIDA Number: {extracted_data.get('nida_number', 'Not found')}")
    draw_line(f"- Age: {extracted_data.get('age', 'Not found')}")
    loc = extracted_data.get("location", {})
    for level in ["region", "district", "ward"]:
        val = loc.get(level)
        if val:
            draw_line(f"- {level.capitalize()}: {val}")
    draw_line(f"- Income (TZS): {extracted_data.get('income_tzs', 'Not found')}")
    draw_line(f"- Bank Balance (TZS): {extracted_data.get('bank_balance_tzs', 'Not found')}")
    draw_line(f"- Loan Limit (TZS): {extracted_data.get('loan_limit_tzs', 'Not found')}")

    draw_line("")
    draw_line("📧 Email: " + extracted_data.get("email", "Not found"))

    draw_line("")
    draw_line("📝 Summary:", font="Helvetica-Bold")
    summary = analysis.get("summary", "No summary available.")
    for line in summary.split("\n"):
        draw_line(line)

    draw_line("")
    draw_line("🔑 Key Phrases:", font="Helvetica-Bold")
    key_phrases = analysis.get("key_phrases", [])
    if key_phrases:
        for phrase in key_phrases:
            draw_line(f"• {phrase}")
    else:
        draw_line("No key phrases found.")

    draw_line("")
    draw_line("🧩 Named Entities:", font="Helvetica-Bold")
    named_entities = analysis.get("named_entities", [])
    if named_entities:
        for ent in named_entities:
            draw_line(f"• {ent['text']} [{ent['label']}]")
    else:
        draw_line("No named entities found.")

    c.save()
    print(f"\n📁 PDF report generated: {pdf_path}")


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

        # Handle email if extracted, otherwise notify
        email = data.get("email")
        if email:
            print(f"\n📧 Email: {email}")
        else:
            print("\n⚠️ Email not found; many Tanzanians may not have one.")

        display_financial_data(data)

        print("\n🔎 Analyzing text...\n")
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze(text)

        print("📝 Summary:")
        print(analysis.get('summary', 'No summary available.'))
        print("\n🔑 Key Phrases:")
        key_phrases = analysis.get('key_phrases', [])
        print(", ".join(key_phrases) if key_phrases else "No key phrases found.")
        print("\n🧩 Named Entities:")
        named_entities = analysis.get('named_entities', [])
        if named_entities:
            for ent in named_entities:
                print(f" - {ent['text']} [{ent['label']}]")
        else:
            print("No named entities found.")

        # Generate the PDF
        generate_pdf_report(file_path, data, analysis)

    except FileNotFoundError as fnf:
        print(str(fnf))
    except UnsupportedFileTypeError as uft:
        print(str(uft))
    except ValueError as ve:
        print(f"⚠️  {ve}")

    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(f"❌ Unexpected error occurred: {e}\n")
            traceback.print_exc(file=f)
        print("❌ Unexpected error occurred. Check 'error_log.txt' for details.")
        time.sleep(20)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
