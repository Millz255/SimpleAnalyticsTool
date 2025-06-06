import os
import sys
import traceback
import time
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from extractor.text_extractor import extract_text, UnsupportedFileTypeError
from analyzer.text_analyzer import TextAnalyzer
from extractor.financial_extractor import extract_all_financial_data


def safe_input(prompt=""):
    """Robust input handling that works in both dev and compiled environments"""
    try:
        # First try standard input
        return input(prompt)
    except (EOFError, RuntimeError) as e:
        # Fallback for when stdin is lost
        try:
            if sys.platform == "win32":
                import msvcrt
                print(prompt, end='', flush=True)
                buffer = []
                while True:
                    ch = msvcrt.getwch()
                    if ch in ('\r', '\n'):
                        print()
                        break
                    if ch == '\x03':
                        raise KeyboardInterrupt
                    buffer.append(ch)
                    print(ch, end='', flush=True)
                return ''.join(buffer).strip()
            else:
                # Linux/Mac fallback
                with open('/dev/tty', 'r') as tty:
                    print(prompt, end='', flush=True)
                    return tty.readline().strip()
        except Exception:
            # Final fallback
            print("Could not get input. Please run in a proper console.")
            raise


def print_header():
    """Print header with Unicode emoji support"""
    try:
        header = "🧠  Simple Analytics Tool".center(60)
        print("=" * 60)
        print(header)
        print("=" * 60)
    except UnicodeEncodeError:
        # Fallback for systems without Unicode support
        print("=" * 60)
        print("Simple Analytics Tool".center(60))
        print("=" * 60)


def prompt_file_path() -> str:
    """Get valid file path from user with error handling"""
    while True:
        try:
            file_path = safe_input("📄 Enter the full path to your document (.txt, .pdf, .docx): ").strip()
            if not file_path:
                raise ValueError("⚠️ File path cannot be empty.")
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"⚠️ File not found: {file_path}")
            return file_path
        except (ValueError, FileNotFoundError) as e:
            print(str(e))
            if not sys.stdin.isatty():  # Don't loop infinitely in non-interactive mode
                raise


def display_financial_data(data: dict):
    """Display extracted financial data with proper formatting"""
    print("\n💰 Extracted Financial Data:")

    # Display basic info
    full_name = data.get("full_name")
    print(f" - Full Name: {full_name if full_name else 'Not found'}")

    phones = data.get("phone_numbers")
    print(f" - Phone Number(s): {', '.join(phones) if phones else 'Not found'}")

    nida = data.get("nida_number")
    print(f" - NIDA Number: {nida if nida else 'Not found'}")

    age = data.get("age")
    print(f" - Age: {age if age is not None else 'Not found'}")

    # Display location info if available
    location = data.get("location")
    if location:
        print("\n📍 Location Information:")
        for level in ["region", "district", "ward"]:
            val = location.get(level)
            if val:
                print(f"  {level.capitalize()}: {val}")

    # Display financial numbers
    income = data.get("income_tzs")
    print(f" - Income (TZS): {income:,.0f}" if income is not None else " - Income (TZS): Not found")

    balance = data.get("bank_balance_tzs")
    print(f" - Bank Balance (TZS): {balance:,.0f}" if balance is not None else " - Bank Balance (TZS): Not found")

    loan_limit = data.get("loan_limit_tzs")
    print(f" - Loan Limit (TZS): {loan_limit:,.0f}" if loan_limit is not None else " - Loan Limit (TZS): Not found")


def generate_pdf_report(file_path: str, extracted_data: dict, analysis: dict):
    """Generate PDF report with all analysis results"""
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

    # Report header
    draw_line("Document Analysis Report", offset=20, font="Helvetica-Bold", size=14)
    draw_line(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    draw_line(f"Source File: {os.path.basename(file_path)}")
    draw_line("")

    # Financial data section
    draw_line("Financial Data Extracted:", font="Helvetica-Bold")
    draw_line(f"- Full Name: {extracted_data.get('full_name', 'Not found')}")

    phones = extracted_data.get("phone_numbers", [])
    draw_line(f"- Phone Number(s): {', '.join(phones) if phones else 'Not found'}")

    draw_line(f"- NIDA Number: {extracted_data.get('nida_number', 'Not found')}")
    draw_line(f"- Age: {extracted_data.get('age', 'Not found')}")

    # Location data
    loc = extracted_data.get("location", {})
    for level in ["region", "district", "ward"]:
        val = loc.get(level)
        if val:
            draw_line(f"- {level.capitalize()}: {val}")

    # Financial numbers
    draw_line(f"- Income (TZS): {extracted_data.get('income_tzs', 'Not found')}")
    draw_line(f"- Bank Balance (TZS): {extracted_data.get('bank_balance_tzs', 'Not found')}")
    draw_line(f"- Loan Limit (TZS): {extracted_data.get('loan_limit_tzs', 'Not found')}")

    # Email
    draw_line("")
    draw_line(f"Email: {extracted_data.get('email', 'Not found')}")

    # Analysis sections
    draw_line("")
    draw_line("Summary:", font="Helvetica-Bold")
    summary = analysis.get("summary", "No summary available.")
    for line in summary.split("\n"):
        draw_line(line)

    draw_line("")
    draw_line("Key Phrases:", font="Helvetica-Bold")
    key_phrases = analysis.get("key_phrases", [])
    if key_phrases:
        for phrase in key_phrases:
            draw_line(f"• {phrase}")
    else:
        draw_line("No key phrases found.")

    draw_line("")
    draw_line("Named Entities:", font="Helvetica-Bold")
    named_entities = analysis.get("named_entities", [])
    if named_entities:
        for ent in named_entities:
            draw_line(f"• {ent['text']} [{ent['label']}]")
    else:
        draw_line("No named entities found.")

    c.save()
    print(f"\n📁 PDF report generated: {pdf_path}")


def main():
    """Main program execution"""
    try:
        # Initialize console encoding (especially for Windows)
        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

        print_header()

        # Get and process document
        file_path = prompt_file_path()
        print("\n🔍 Extracting text...\n")
        text = extract_text(file_path)

        if not text.strip():
            print("⚠️ No readable text was extracted from the document.")
            return

        # Show preview
        print("✅ Extraction successful! Here's a preview:\n")
        print("-" * 60)
        print(text[:500].strip())
        print("-" * 60)

        # Extract financial data
        data = extract_all_financial_data(text)

        # Display results
        email = data.get("email")
        if email:
            print(f"\n📧 Email: {email}")
        else:
            print("\n⚠️ Email not found")

        display_financial_data(data)

        # Analyze text
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

        # Generate PDF report
        generate_pdf_report(file_path, data, analysis)

    except (FileNotFoundError, UnsupportedFileTypeError, ValueError) as e:
        print(f"\n❌ Error: {str(e)}")
    except Exception as e:
        # Log full error details
        with open("error_log.txt", "w", encoding='utf-8') as f:
            f.write(f"❌ Unexpected error occurred at {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            traceback.print_exc(file=f)

        print("\n❌ An unexpected error occurred. Details saved to error_log.txt")
        traceback.print_exc()
    finally:
        # Keep window open in interactive mode
        if sys.stdin.isatty():
            try:
                safe_input("\nPress Enter to exit...")
            except:
                pass
        time.sleep(1)  # Ensure messages are visible


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        traceback.print_exc()
        try:
            safe_input("Press Enter to exit...")
        except:
            pass
        time.sleep(5)