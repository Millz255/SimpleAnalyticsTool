from extractor.financial_extractor import extract_all_financial_data
from analyzer.text_analyzer import TextAnalyzer

def main():
    with open('sample.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    print("=== Extracted Financial Data ===")
    data = extract_all_financial_data(text)
    for key, val in data.items():
        print(f"{key}: {val}")

    print("\n=== Text Analysis ===")
    analyzer = TextAnalyzer()
    analysis = analyzer.analyze(text)

    print("Summary:")
    print(analysis['summary'])
    print("\nKey Phrases:")
    print(", ".join(analysis['key_phrases']))
    print("\nNamed Entities:")
    for ent in analysis['named_entities']:
        print(f" - {ent['text']} [{ent['label']}]")

if __name__ == "__main__":
    main()
