import os
from extractor.text_extractor import extract_text, UnsupportedFileTypeError


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
        print(text[:500].strip())  # First 500 characters
        print("-" * 60)

        # Placeholder for next step
        print("\n🚧 Analysis module coming up next...")

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
