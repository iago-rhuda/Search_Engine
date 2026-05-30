"""Flask entrypoint for the search engine web interface and background indexing pipeline."""

import os
import sys
import threading
import json
from flask import Flask, request, jsonify, send_from_directory

# Configure system paths and current working directory for relative imports
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(SRC_DIR)
sys.path.append(SRC_DIR)

from bulletin_parser import BulletinParser
from xml_builder import XMLBuilder
from tokenizer import Tokenizer
from inverted_index import InvertedIndexGenerator
from spell_checker import SpellChecker
from query_processing import process_request
from search_engine import SearchEngine, BinarySearchTree
from stemmer import Stemmer
from logger import RequestLogger

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=WEB_DIR, static_url_path='')

# Robust Path Configuration
BASE_DIR = os.path.abspath(os.path.join(WEB_DIR, "../.."))
# Fallback check: if data/ isn't found in BASE_DIR, try current working directory or relative parent directory
if not os.path.exists(os.path.join(BASE_DIR, "data")):
    cwd = os.path.abspath(os.getcwd())
    if os.path.exists(os.path.join(cwd, "data")):
        BASE_DIR = cwd
    elif os.path.exists(os.path.join(cwd, "..", "data")):
        BASE_DIR = os.path.abspath(os.path.join(cwd, ".."))

OUTPUTS_DIR = os.path.join(BASE_DIR, "data", "outputs")

# Global engine components
spell_checker = None
stemmer_engine = None
search_engine = None
stop_words_list = None
is_pipeline_ready = False
pipeline_status = "Starting pipeline..."


def run_indexing_pipeline():
    """Executes the full document processing and indexing pipeline on startup."""
    global spell_checker, stemmer_engine, search_engine, stop_words_list, is_pipeline_ready, pipeline_status
    print("\n" + "="*50)
    print("      Initializing NLP Search Pipeline (PySearchNLP)      ")
    print("="*50)
    
    try:
        # Phase 1: Corpus XML Generation
        pipeline_status = "Phase 1: XML Corpus Generation"
        print("\n--- [Phase 1] XML Corpus Generation ---")
        phase1_dir = os.path.join(OUTPUTS_DIR, "phase_1_xml")
        os.makedirs(phase1_dir, exist_ok=True)
        xml_raw_path = os.path.join(phase1_dir, "xml.xml")
        
        builder = XMLBuilder()
        bulletin_dir = "../data/BULLETINS"
        if not os.path.exists(bulletin_dir):
            # Try path from workspace root
            bulletin_dir = "data/BULLETINS"
        
        bulletin_files = [f for f in os.listdir(bulletin_dir) if f.endswith(".htm")]
        for filename in bulletin_files:
            try:
                parser = BulletinParser(os.path.join(bulletin_dir, filename))
                data = parser.parse()
                if data:
                    builder.add_document(data)
            except Exception:
                continue
        builder.save(xml_raw_path)
        print(f"Raw XML corpus generated at: {xml_raw_path}")

        # Phase 2: Tokenization and Stopword Filtering
        pipeline_status = "Phase 2: Tokenization & Stopword Filtering"
        print("\n--- [Phase 2] Tokenization & Stopword Filtering ---")
        phase2_dir = os.path.join(OUTPUTS_DIR, "phase_2_filtered")
        tokenizer = Tokenizer(xml_filepath=xml_raw_path, output_dir=phase2_dir)
        tokenizer.export_stats()
        
        # Phase 3: Stemming and Inverted Indexing
        pipeline_status = "Phase 3: Stemming & Inverted Indexing"
        print("\n--- [Phase 3] Stemming & Inverted Indexing ---")
        phase3_dir = os.path.join(OUTPUTS_DIR, "phase_3_indexed")
        xml_filtered_path = os.path.join(phase2_dir, "corpus_filtered.xml")
        stem_mapping_path = os.path.join(phase3_dir, "stems_nltk.txt")
        tfidf_path = os.path.join(phase3_dir, "tfidf_coefficients.txt")
        xml_final_path = os.path.join(phase3_dir, "corpus_filtered_v2.xml")
        
        os.makedirs(phase3_dir, exist_ok=True)
        
        # Initialize Stemmer and generate word-to-stem mapping
        stemmer_engine = Stemmer(xml_filtered_path, stem_mapping_path)
        stemmer_engine.run()
        
        # Recalculate stats on stems and generate final filtered XML
        tokenizer.export_stem_stats(stem_dict_file=stem_mapping_path, target_xml=xml_filtered_path, out_file=tfidf_path, filter_again=True)
        
        print("Generating inverted index files...")
        index_gen = InvertedIndexGenerator(xml_filepath=xml_final_path, output_dir=phase3_dir)
        index_gen.generate()
        index_gen.export()
        
        # Phase 4: Component Initialization
        pipeline_status = "Phase 4: Loading Search Components"
        print("\n--- [Phase 4] Loading Search Components ---")
        stop_words_path = os.path.join(phase2_dir, "stop_words.txt")
        
        spell_checker = SpellChecker(lexicon_file=stem_mapping_path)
        search_engine = SearchEngine(index_dir=phase3_dir, xml_path=xml_raw_path)
        stop_words_list = tokenizer.load_dictionary(stop_words_path)
        
        # Phase 5: Auto-run Evaluation Benchmark
        pipeline_status = "Phase 5: Running Evaluation Auto-Benchmark"
        print("\n--- [Phase 5] Running Evaluation Auto-Benchmark ---")
        try:
            from evaluation import run_evaluation_pipeline
            run_evaluation_pipeline(base_dir=BASE_DIR, runs=100, inspect=True, top=50)
            print("[OK] Auto-Benchmark completed successfully.")
        except Exception as e:
            print(f"[WARN] Failed to run auto-benchmark: {e}")
            
        is_pipeline_ready = True
        pipeline_status = "Ready"
        print("\n[OK] Pipeline ready. Server listening for requests.")
        
    except Exception as e:
        print(f"CRITICAL ERROR in pipeline: {e}")
        import traceback
        traceback.print_exc()

# Start the indexing pipeline in a background thread to avoid blocking server startup
if not os.environ.get("PYSEARCH_SKIP_PIPELINE_THREAD"):
    threading.Thread(target=run_indexing_pipeline, daemon=True).start()



@app.route('/')
def serve_index():
    return send_from_directory(WEB_DIR, 'main.html')


@app.route('/data/BULLETINS/<filename>')
def serve_bulletin(filename):
    bulletins_path = os.path.abspath(os.path.join(SRC_DIR, "../data/BULLETINS"))
    if not os.path.exists(bulletins_path):
        bulletins_path = os.path.abspath(os.path.join(SRC_DIR, "data/BULLETINS"))
    return send_from_directory(bulletins_path, filename)


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(WEB_DIR, path)


@app.route('/api/status', methods=['GET'])
def handle_status():
    return jsonify({
        "ready": is_pipeline_ready,
        "status": pipeline_status
    })


@app.route('/config', methods=['GET'])
def serve_config():
    bulletins_path = os.path.abspath(os.path.join(SRC_DIR, "../data/BULLETINS"))
    if not os.path.exists(bulletins_path):
        bulletins_path = os.path.abspath(os.path.join(SRC_DIR, "data/BULLETINS"))
    return jsonify({
        "bulletinsPath": bulletins_path.replace('\\', '/')
    })


@app.route('/search', methods=['GET'])
def handle_search():
    if not is_pipeline_ready:
        return jsonify({"error": "Search pipeline is still initializing. Please wait a few seconds."}), 503

    query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'relevance')
    
    if not query:
        return jsonify({"results": [], "structured": {}})

    try:
        import time
        start_request = time.time()
        
        logger = RequestLogger()
        logger.log("SYSTEM", f"New search request: '{query}' (Sort: {sort_by})")
        
        # 1. Parse and Correct Query
        structured_query = process_request(query, stemmer_engine, spell_checker, stop_words_list, logger)
        
        # 2. Execute Search
        results = search_engine.search(structured_query, sort_by, logger)
        
        execution_time = (time.time() - start_request) * 1000
        logger.log("SYSTEM", f"Search completed in {execution_time:.2f}ms with {len(results)} results.")
        
        return jsonify({
            "results": results,
            "structured": structured_query,
            "logs": logger.logs,
            "time_ms": round(execution_time, 2)
        })
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def handle_analytics():
    """Returns general corpus and vocabulary statistical analytics."""
    if not is_pipeline_ready:
        return jsonify({"error": "Pipeline initializing"}), 503
        
    try:
        # 1. Total documents
        total_docs = len(search_engine.doc_titles)
        
        # 2. Vocabulary size (lexicon size)
        vocab_size = len(spell_checker.lexicon) if spell_checker else 0
        
        # 3. Rubrics distribution
        rubric_counts = {}
        for rubric in search_engine.doc_rubrics.values():
            r_name = rubric.strip() if rubric else "General/Unspecified"
            # Normalize display name
            r_name = r_name.title()
            rubric_counts[r_name] = rubric_counts.get(r_name, 0) + 1
            
        # Sort rubrics by count descending
        sorted_rubrics = sorted(rubric_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 4. Image stats
        image_docs = set()
        for term_matches in search_engine.indexes.get('images', {}).values():
            image_docs.update(term_matches.keys())
        docs_with_images = len(image_docs)
        
        # 5. Top 10 vocabulary terms based on TF-IDF coefficients
        top_terms = []
        tfidf_path = os.path.join(OUTPUTS_DIR, "phase_3_indexed", "tfidf_coefficients.txt")
        if os.path.exists(tfidf_path):
            with open(tfidf_path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    if idx >= 10:
                        break
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        top_terms.append({
                            "term": parts[0],
                            "score": round(float(parts[1]), 2)
                        })
                        
        return jsonify({
            "total_documents": total_docs,
            "vocabulary_size": vocab_size,
            "rubrics_distribution": sorted_rubrics,
            "documents_with_images": docs_with_images,
            "documents_without_images": total_docs - docs_with_images,
            "top_terms": top_terms
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/index-lookup', methods=['GET'])
def handle_index_lookup():
    """Allows direct query into the inverted index for inspection."""
    if not is_pipeline_ready:
        return jsonify({"error": "Pipeline initializing"}), 503
        
    term = request.args.get('term', '').strip().lower()
    field = request.args.get('field', 'text').strip().lower()
    
    if not term:
        return jsonify({"results": []})
        
    try:
        idx = search_engine.indexes.get(field)
        if not idx:
            return jsonify({"error": f"Index field '{field}' not found"}), 404
            
        if isinstance(idx, BinarySearchTree):
            # For BST exact match fields, search_exact returns a set of doc_ids
            doc_ids = idx.search_exact(term)
            results = [{"doc_id": doc_id, "frequency": 1} for doc_id in sorted(doc_ids)]
        else:
            # Hash map index yields: term -> {doc_id: frequency}
            doc_freqs = idx.get(term, {})
            results = [{"doc_id": doc_id, "frequency": freq} for doc_id, freq in sorted(doc_freqs.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])]
            
        return jsonify({
            "term": term,
            "field": field,
            "postings_count": len(results),
            "postings": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/benchmark-results', methods=['GET'])
def handle_benchmark_results():
    """Returns pre-computed evaluation benchmark metrics."""
    candidates = [
        os.path.join(OUTPUTS_DIR, "evaluation", "evaluation_results.json"),
        os.path.abspath(os.path.join(BASE_DIR, "data/outputs/evaluation/evaluation_results.json")),
        os.path.abspath("data/outputs/evaluation/evaluation_results.json"),
        os.path.abspath("../data/outputs/evaluation/evaluation_results.json"),
    ]
    
    results_path = None
    for c in candidates:
        if os.path.exists(c):
            results_path = c
            break
            
    if not results_path:
        return jsonify({
            "error": "Evaluation results not found. Run evaluation script first.",
            "searched_paths": candidates
        }), 404
        
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract a lean representation for the frontend
        summary = []
        for q in data:
            summary.append({
                "query_id": q.get("query_id"),
                "query": q.get("query"),
                "precision": q.get("precision"),
                "recall": q.get("recall"),
                "average_response_time_ms": round(q.get("average_response_time_ms"), 3),
                "nb_returned": q.get("nb_returned")
            })
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/run-benchmark', methods=['POST'])
def handle_run_benchmark():
    """Runs a live performance benchmark by executing queries in real time."""
    if not is_pipeline_ready:
        return jsonify({"error": "Pipeline initializing"}), 503
        
    try:
        import time
        from evaluation import QUERIES
        
        runs = 10
        benchmark_results = []
        
        for qid, qtext in QUERIES:
            structured = process_request(qtext, stemmer_engine, spell_checker, stop_words_list)
            
            # Warmup
            search_engine.search(structured)
            
            # Benchmark run
            t0 = time.perf_counter()
            for _ in range(runs):
                search_engine.search(structured)
            elapsed_ms = ((time.perf_counter() - t0) * 1000.0) / runs
            
            # Simple single run for count
            res = search_engine.search(structured)
            
            benchmark_results.append({
                "query_id": qid,
                "query": qtext,
                "returned_count": len(res),
                "live_time_ms": round(elapsed_ms, 3)
            })
            
        return jsonify({
            "runs_per_query": runs,
            "results": benchmark_results,
            "average_system_latency_ms": round(sum(q["live_time_ms"] for q in benchmark_results) / len(benchmark_results), 3)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n* PySearchNLP Server starting at http://localhost:5000")
    # Disable reloader to prevent duplicate pipeline execution in debug mode
    app.run(debug=True, use_reloader=False, port=5000)

