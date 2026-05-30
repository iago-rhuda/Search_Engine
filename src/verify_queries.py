import os

from search_engine import SearchEngine
from query_processing import process_request
from spell_checker import SpellChecker
from tokenizer import Tokenizer


QUERIES = [
    "CNRS",
    "grandes écoles",
    "Centrale Paris",
    "CNRS ou grandes écoles",
    "CNRS ou grandes écoles mais pas Centrale Paris",
    "systèmes embarqués",
    "robotique",
    "systèmes embarqués et non pas robotique",
    "chimie",
    "Je voudrais les articles dont le titre contient le mot chimie.",
]


class _SimpleTokenizer:
    @staticmethod
    def tokenize(text):
        return [t for t in text.lower().replace("'", " ").split() if t]


class _SimpleSpellChecker:
    def __init__(self):
        self.tokenizer = _SimpleTokenizer()

    @staticmethod
    def process_query(token, logger=None):
        return [token]


def _load_runtime_components(base_dir):
    xml_phase1 = os.path.join(base_dir, "data", "outputs", "phase_1_xml", "xml.xml")
    phase2_dir = os.path.join(base_dir, "data", "outputs", "phase_2_filtered")
    stop_words_file = os.path.join(phase2_dir, "stop_words.txt")
    phase3_dir = os.path.join(base_dir, "data", "outputs", "phase_3_indexed")
    stem_lexicon = os.path.join(phase3_dir, "stems_nltk.txt")

    required = [xml_phase1, stop_words_file, stem_lexicon, phase3_dir]
    inverse_files = [
        os.path.join(phase3_dir, "inverse_title.txt"),
        os.path.join(phase3_dir, "inverse_text.txt"),
    ]

    if all(os.path.exists(p) for p in required) and all(os.path.exists(p) for p in inverse_files):
        tokenizer = Tokenizer(xml_filepath=xml_phase1, output_dir=phase2_dir)
        spell_checker = SpellChecker(lexicon_file=stem_lexicon)
        stop_words = tokenizer.load_dictionary(stop_words_file)
        mode = "real"
    else:
        spell_checker = _SimpleSpellChecker()
        stop_words = set()
        mode = "fallback"

    return {
        "mode": mode,
        "xml_phase1": xml_phase1,
        "phase3_dir": phase3_dir,
        "spell_checker": spell_checker,
        "stop_words": stop_words,
    }


def main():
    print("=== Structured query checks ===")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    runtime = _load_runtime_components(base_dir)
    spell_checker = runtime["spell_checker"]
    stop_words = runtime["stop_words"]
    print(f"Component mode : {runtime['mode']}")

    for q in QUERIES:
        structured = process_request(q, stemmer=None, spell_checker=spell_checker, stop_words=stop_words)
        print(f"\nOriginal query : {q}")
        print(f"  keywords     : {structured.get('keywords')}")
        print(f"  equation     : {structured.get('equation')}")
        print(f"  operators    : {structured.get('operateur')}")
        print(f"  search_field : {structured.get('search_field')}")

    index_dir = runtime["phase3_dir"]
    xml_path = runtime["xml_phase1"]

    if not (os.path.isdir(index_dir) and os.path.isfile(xml_path)):
        print("\n=== Result counts ===")
        for q in QUERIES:
            print(f"- {q}\n  results_count: N/A (index/xml not available)")
        print("\n[INFO] Index/XML outputs not found; skipping engine verification.")
        print("Expected:")
        print(f"  - {index_dir}")
        print(f"  - {xml_path}")
        return

    print("\n=== Result counts ===")
    engine = SearchEngine(index_dir=index_dir, xml_path=xml_path)
    for q in QUERIES:
        structured = process_request(q, stemmer=None, spell_checker=spell_checker, stop_words=stop_words)
        results = engine.search(structured)
        print(f"\n- query        : {q}")
        print(f"  keywords     : {structured.get('keywords')}" )
        print(f"  equation     : {structured.get('equation')}" )
        print(f"  operators    : {structured.get('operateur')}" )
        print(f"  search_field : {structured.get('search_field')}" )
        print(f"  results_count: {len(results)}")

        title_index = engine.indexes.get('title', {})
        text_index = engine.indexes.get('text', {})
        for term in structured.get('keywords', []):
            title_docs = set(title_index.get(term, {}).keys())
            text_docs = set(text_index.get(term, {}).keys())
            total_docs = title_docs | text_docs
            print(f"  term: {term}")
            print(f"    title_docs: {len(title_docs)}")
            print(f"    text_docs : {len(text_docs)}")
            print(f"    total_docs: {len(total_docs)}")


if __name__ == "__main__":
    main()
