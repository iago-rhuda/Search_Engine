"""Experimental evaluation pipeline for query accuracy and search performance.

Runs a fixed set of queries against the search engine,
loads ground-truth datasets, computes precision/recall/latency,
and exports results to CSV/JSON files.
"""

import matplotlib
matplotlib.use('Agg')

import argparse
import csv
import json
import os
import time

from search_engine import SearchEngine
from spell_checker import SpellChecker
from tokenizer import Tokenizer
from query_processing import process_request


QUERIES = [
    (1, "Je veux les articles de la rubrique Focus parlant d’innovation."),
    (2, "Afficher les articles de la rubrique en direct des laboratoires."),
    (3, "Je voudrais les articles de 2011 sur l’enseignement."),
    (4, "Quels sont les articles parlant de la Russie ou du Japon ?"),
    (5, "Liste des articles qui parlent soit du CNRS, soit des grandes écoles, mais pas de Centrale Paris."),
    (6, "Articles contenant une image."),
    (7, "Je veux les articles sans image."),
    (8, "Je voudrais les articles dont le titre contient le mot chimie."),
    (9, "Quels sont les articles parus entre le 3 mars 2013 et le 4 mai 2013 évoquant les Etats-Unis ?"),
    (10, "Je veux les articles qui parlent des systèmes embarqués et non pas la robotique."),
]

# Hardcoded fallback Ground Truth for evaluations (can be populated if external JSON not found)
GROUND_TRUTH = {
    1: set(),
    2: set(),
    3: set(),
    4: set(),
    5: set(),
    6: set(),
    7: set(),
    8: set(),
    9: set(),
    10: set(),
}

GROUND_TRUTH_EXTERNAL = os.path.join("data", "outputs", "evaluation", "ground_truth.json")
GROUND_TRUTH_TEMPLATE = os.path.join("data", "outputs", "evaluation", "ground_truth_template.json")


def safe_div(num, den):
    """Returns num/den with zero-division protection."""
    return (num / den) if den else 0.0


def ensure_runtime_paths(base_dir):
    """Builds required runtime paths and returns missing dependencies."""
    paths = {
        "xml": os.path.join(base_dir, "data", "outputs", "phase_1_xml", "xml.xml"),
        "phase2": os.path.join(base_dir, "data", "outputs", "phase_2_filtered"),
        "stop_words": os.path.join(base_dir, "data", "outputs", "phase_2_filtered", "stop_words.txt"),
        "phase3": os.path.join(base_dir, "data", "outputs", "phase_3_indexed"),
        "stem": os.path.join(base_dir, "data", "outputs", "phase_3_indexed", "stems_nltk.txt"),
        "inverse_title": os.path.join(base_dir, "data", "outputs", "phase_3_indexed", "inverse_title.txt"),
        "inverse_text": os.path.join(base_dir, "data", "outputs", "phase_3_indexed", "inverse_text.txt"),
    }
    required = [
        paths["xml"],
        paths["stop_words"],
        paths["stem"],
        paths["inverse_title"],
        paths["inverse_text"],
    ]
    missing = [p for p in required if not os.path.exists(p)]
    return paths, missing


def build_components(paths):
    """Initializes tokenizer, spell checker and search engine from pipeline outputs."""
    tokenizer = Tokenizer(xml_filepath=paths["xml"], output_dir=paths["phase2"])
    stop_words = tokenizer.load_dictionary(paths["stop_words"])
    spell_checker = SpellChecker(lexicon_file=paths["stem"])
    engine = SearchEngine(index_dir=paths["phase3"], xml_path=paths["xml"])
    return stop_words, spell_checker, engine


def _to_int_ids(values):
    """Converts iterable values to integer IDs when possible."""
    out = set()
    for v in values:
        s = str(v).strip()
        if s.isdigit():
            out.add(int(s))
    return out


def build_auto_ground_truth(engine, structured_queries):
    """Builds objective ground truth subsets for Q2/Q6/Q7/Q8.

    Criteria are structural and fully verifiable from XML/indexes.
    """
    auto_gt = {qid: set() for qid, _ in QUERIES}

    # Q2: exact rubric match
    q2 = structured_queries.get(2, {})
    rubric = q2.get("rubric")
    if rubric:
        for doc_id, rub in engine.doc_rubrics.items():
            if str(rub).strip().lower() == str(rubric).strip().lower() and str(doc_id).isdigit():
                auto_gt[2].add(int(doc_id))

    # Q6/Q7: image presence from images index
    image_docs = set()
    for term_map in engine.indexes.get("images", {}).values():
        image_docs.update(_to_int_ids(term_map.keys()))
    all_docs = _to_int_ids(engine.doc_titles.keys())
    auto_gt[6] = image_docs.copy()
    auto_gt[7] = all_docs - image_docs

    # Q8: title contains stem "chim" (derived from structured query)
    q8 = structured_queries.get(8, {})
    q8_terms = q8.get("keywords", [])
    title_index = engine.indexes.get("title", {})
    q8_docs = None
    for term in q8_terms:
        docs = _to_int_ids(title_index.get(term, {}).keys())
        q8_docs = docs if q8_docs is None else (q8_docs & docs)
    auto_gt[8] = q8_docs if q8_docs is not None else set()

    return auto_gt


def load_ground_truth(base_dir, auto_gt):
    """Loads ground truth from external JSON if present, else fallback map."""
    ext_path = os.path.join(base_dir, GROUND_TRUTH_EXTERNAL)
    if os.path.exists(ext_path):
        with open(ext_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        loaded = {}
        for qid, _ in QUERIES:
            key = f"Q{qid}"
            loaded[qid] = _to_int_ids(raw.get(key, []))
        return loaded, ext_path

    merged = {qid: set(GROUND_TRUTH.get(qid, set())) for qid, _ in QUERIES}
    for qid in [2, 6, 7, 8]:
        merged[qid] = set(auto_gt.get(qid, set()))
    return merged, None


def write_ground_truth_template(base_dir, auto_gt):
    """Writes a reusable JSON template for manual ground-truth curation."""
    out_path = os.path.join(base_dir, GROUND_TRUTH_TEMPLATE)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {}
    for qid, _ in QUERIES:
        key = f"Q{qid}"
        payload[key] = sorted(auto_gt.get(qid, set())) if qid in [2, 6, 7, 8] else []
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out_path


def detect_match_fields(engine, structured, result):
    """Heuristic field-level explanation for candidate inspection output."""
    fields = set()
    doc_id = str(result.get("id", ""))
    title = engine.doc_titles.get(doc_id, "").lower()
    text = engine.doc_texts.get(doc_id, "").lower()
    date = engine.doc_dates.get(doc_id, "").lower()
    rubric = engine.doc_rubrics.get(doc_id, "").lower()

    # keyword matches (literal + index-backed)
    for kw in structured.get("keywords", []):
        if doc_id in engine.indexes.get("title", {}).get(kw, {}):
            fields.add("title")
        if doc_id in engine.indexes.get("text", {}).get(kw, {}):
            fields.add("text")

    if structured.get("rubric") and structured["rubric"].lower() == rubric:
        fields.add("rubric")
    if structured.get("date") and structured["date"].lower() == date:
        fields.add("date")
    if structured.get("date_min") or structured.get("date_max"):
        fields.add("date")
    if structured.get("image") is not None:
        fields.add("images")

    # fallback if no field detected but literal appears
    if not fields:
        for tok in structured.get("highlight_keywords", []):
            t = str(tok).lower()
            if t and t in title:
                fields.add("title")
            if t and t in text:
                fields.add("text")

    return sorted(fields)


def evaluate_query(query_id, query_text, gt_ids, stop_words, spell_checker, engine, runs=100, top_k=20):
    """Evaluates one query and returns metrics + inspection metadata."""
    structured = process_request(query_text, stemmer=None, spell_checker=spell_checker, stop_words=stop_words)

    t0 = time.perf_counter()
    for _ in range(runs):
        engine.search(structured)
    avg_ms = ((time.perf_counter() - t0) * 1000.0) / runs

    results = engine.search(structured)
    returned_ids = {int(r["id"]) for r in results if str(r.get("id", "")).isdigit()}
    relevant_ids = set(gt_ids)

    tp = len(returned_ids & relevant_ids)
    fp = len(returned_ids - relevant_ids)
    fn = len(relevant_ids - returned_ids)

    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)

    return {
        "query_id": query_id,
        "query": query_text,
        "search_field": structured.get("search_field"),
        "keywords": structured.get("keywords", []),
        "equation": structured.get("equation", ""),
        "operators": structured.get("operateur", []),
        "returned_docs": sorted(returned_ids),
        "relevant_docs": sorted(relevant_ids),
        "nb_returned": len(returned_ids),
        "nb_relevant": len(relevant_ids),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "average_response_time_ms": avg_ms,
        "preview_results": [
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "date": r.get("date"),
                "rubric": r.get("rubric"),
                "score": r.get("score"),
                "snippet": r.get("snippet", "")[:180],
                "match_fields": detect_match_fields(engine, structured, r),
            }
            for r in results[:top_k]
        ],
        "structured": structured,
    }


def write_outputs(results, out_dir):
    """Exports aggregated evaluation outputs to CSV and JSON files."""
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "evaluation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(out_dir, "evaluation_results.csv")
    fields = [
        "query_id", "precision", "recall", "average_response_time_ms",
        "nb_returned", "nb_relevant", "true_positives", "false_positives", "false_negatives",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row[k] for k in fields})


def make_plot(results, value_key, title, ylabel, output_path):
    """Generates one bar chart if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[WARN] Could not import matplotlib ({exc}). Skipping plot: {output_path}")
        return False

    x = [r["query_id"] for r in results]
    y = [r[value_key] for r in results]
    plt.figure(figsize=(10, 4))
    plt.bar(x, y)
    plt.title(title)
    plt.xlabel("Query ID")
    plt.ylabel(ylabel)
    plt.xticks(x)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return True


def print_table(results):
    """Prints compact metric table in console."""
    print("\nquery_id | precision | recall | avg_time_ms | nb_returned | nb_relevant")
    print("-" * 72)
    for r in results:
        print(
            f"{r['query_id']:>8} | "
            f"{r['precision']:.4f}   | "
            f"{r['recall']:.4f} | "
            f"{r['average_response_time_ms']:.2f}      | "
            f"{r['nb_returned']:>11} | "
            f"{r['nb_relevant']:>11}"
        )


def print_inspection_help(results, out_dir):
    """Exports verbose candidate file used for manual ground-truth review."""
    inspect_path = os.path.join(out_dir, "ground_truth_candidates.txt")
    with open(inspect_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"\n=== Query {r['query_id']} ===\n")
            f.write(f"query: {r['query']}\n")
            f.write(f"structured: {json.dumps(r['structured'], ensure_ascii=False)}\n")
            f.write(f"keywords: {r['keywords']}\n")
            f.write(f"equation: {r['equation']}\n")
            f.write("Top candidates:\n")
            for item in r["preview_results"]:
                f.write(
                    f"- id={item['id']} | date={item['date']} | rubric={item['rubric']} | score={item['score']}\n"
                    f"  title: {item['title']}\n"
                    f"  match_fields: {', '.join(item.get('match_fields', [])) or 'unknown'}\n"
                    f"  snippet: {item['snippet']}\n"
                )
    print(f"\n[INFO] Ground-truth helper written to: {inspect_path}")


def run_evaluation_pipeline(base_dir=None, runs=100, inspect=True, top=50):
    """Programmatically runs the evaluation pipeline and generates results files."""
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(base_dir, "data", "outputs", "evaluation")

    paths, missing = ensure_runtime_paths(base_dir)
    if missing:
        print("[ERROR] Missing required files to run evaluation.")
        print("Generate corpus and indexes first (run web/app.py to bootstrap the pipeline).")
        print("Missing:")
        for p in missing:
            print(f"  - {p}")
        return False

    stop_words, spell_checker, engine = build_components(paths)
    structured_by_qid = {}
    for qid, qtext in QUERIES:
        structured_by_qid[qid] = process_request(qtext, stemmer=None, spell_checker=spell_checker, stop_words=stop_words)

    auto_gt = build_auto_ground_truth(engine, structured_by_qid)
    gt_template_path = write_ground_truth_template(base_dir, auto_gt)
    gt_map, gt_external_path = load_ground_truth(base_dir, auto_gt)

    if gt_external_path:
        print(f"[INFO] Loaded external ground truth: {gt_external_path}")
    else:
        print("[INFO] External ground truth not found; using internal + objective auto GT (Q2/Q6/Q7/Q8).")
    print(f"[INFO] Ground-truth template: {gt_template_path}")

    results = []
    for qid, qtext in QUERIES:
        gt = gt_map.get(qid, set())
        results.append(evaluate_query(qid, qtext, gt, stop_words, spell_checker, engine, runs=runs, top_k=top))

    write_outputs(results, out_dir)
    p1 = make_plot(results, "precision", "Precision by query", "Precision", os.path.join(out_dir, "precision.png"))
    p2 = make_plot(results, "recall", "Recall by query", "Recall", os.path.join(out_dir, "recall.png"))
    p3 = make_plot(results, "average_response_time_ms", "Average response time by query", "Milliseconds", os.path.join(out_dir, "response_time.png"))
    print_table(results)
    if inspect:
        print_inspection_help(results, out_dir)

    print("\n[OK] Evaluation completed.")
    print(f"- CSV : {os.path.join(out_dir, 'evaluation_results.csv')}")
    print(f"- JSON: {os.path.join(out_dir, 'evaluation_results.json')}")
    if p1:
        print(f"- PNG : {os.path.join(out_dir, 'precision.png')}")
    if p2:
        print(f"- PNG : {os.path.join(out_dir, 'recall.png')}")
    if p3:
        print(f"- PNG : {os.path.join(out_dir, 'response_time.png')}")
    return True


def main():
    """CLI entrypoint for evaluation execution."""
    parser = argparse.ArgumentParser(description="Experimental evaluation of the NLP search engine")
    parser.add_argument("--runs", type=int, default=100, help="Number of timed executions per query")
    parser.add_argument("--inspect", action="store_true", help="Generate extended candidate inspection output")
    parser.add_argument("--top", type=int, default=20, help="Number of top candidates to export per query")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_evaluation_pipeline(base_dir=base_dir, runs=args.runs, inspect=args.inspect, top=args.top)


if __name__ == "__main__":
    main()
