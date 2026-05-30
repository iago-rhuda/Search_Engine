"""Lightweight delivery checklist for search system state."""

import os


def _exists(path):
    return os.path.exists(path)


def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    checks = {
        "requirements.txt exists": _exists(os.path.join(base, "requirements.txt")),
        "requirements.txt non-empty": os.path.getsize(os.path.join(base, "requirements.txt")) > 0 if _exists(os.path.join(base, "requirements.txt")) else False,
        "README.md exists": _exists(os.path.join(base, "README.md")),
        "Phase 1 XML exists": _exists(os.path.join(base, "data", "outputs", "phase_1_xml", "xml.xml")),
        "inverse_title exists": _exists(os.path.join(base, "data", "outputs", "phase_3_indexed", "inverse_title.txt")),
        "inverse_text exists": _exists(os.path.join(base, "data", "outputs", "phase_3_indexed", "inverse_text.txt")),
        "ground_truth.json exists": _exists(os.path.join(base, "data", "outputs", "evaluation", "ground_truth.json")),
        "evaluation_results.csv exists": _exists(os.path.join(base, "data", "outputs", "evaluation", "evaluation_results.csv")),
        "evaluation_results.json exists": _exists(os.path.join(base, "data", "outputs", "evaluation", "evaluation_results.json")),
    }

    print("PySearchNLP project check")
    print("-------------------------")
    for label, ok in checks.items():
        print(f"- {label}: {'OK' if ok else 'MISSING'}")

    try:
        from search_engine import SearchEngine
        from query_processing import process_request
        from evaluation import QUERIES
        from tokenizer import Tokenizer
        from spell_checker import SpellChecker

        phase1_xml = os.path.join(base, "data", "outputs", "phase_1_xml", "xml.xml")
        phase2_dir = os.path.join(base, "data", "outputs", "phase_2_filtered")
        phase3_dir = os.path.join(base, "data", "outputs", "phase_3_indexed")
        stop_words_file = os.path.join(phase2_dir, "stop_words.txt")
        stem_file = os.path.join(phase3_dir, "stems_nltk.txt")

        engine = SearchEngine(index_dir=phase3_dir, xml_path=phase1_xml)
        tokenizer = Tokenizer(xml_filepath=phase1_xml, output_dir=phase2_dir)
        stop_words = tokenizer.load_dictionary(stop_words_file)
        spell_checker = SpellChecker(lexicon_file=stem_file)
        structured = process_request(QUERIES[0][1], stemmer=None, spell_checker=spell_checker, stop_words=stop_words)
        results = engine.search(structured)
        print(f"- backend import/search smoke test: OK ({len(results)} result(s))")
    except Exception as exc:
        print(f"- backend import/search smoke test: FAILED ({exc})")


if __name__ == "__main__":
    main()
