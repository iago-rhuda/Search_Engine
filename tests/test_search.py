import os
import sys
import pytest
from unittest.mock import MagicMock

# Add src/ directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tokenizer import Tokenizer
from stemmer import Stemmer
from spell_checker import SpellChecker, calculate_levenshtein
from query_processing import extract_metadata, process_request
from search_engine import BinarySearchTree, SearchEngine

def test_tokenizer_basic():
    # Simple regex test for Tokenizer.tokenize
    # Mocking standard ET.parse to avoid loading XML during __init__
    original_parse = Tokenizer.__init__
    try:
        # Patch __init__ to avoid file operations
        def mock_init(self, xml_filepath, output_dir):
            import re
            self.tokenizer_pattern = re.compile(r"\b\w{3,}[']\w+\b|\b\w+(?:-\w+)+\b|\b\w+\b")
        Tokenizer.__init__ = mock_init
        
        t = Tokenizer("dummy.xml", "dummy_out")
        tokens = t.tokenize("L'innovation et le développement d'applications.")
        # 'L'innovation' has "L'" (less than 3 letters/part of apostrophe pattern doesn't match since it starts with L')
        # tokenizer pattern: r"\b\w{3,}[']\w+\b|\b\w+(?:-\w+)+\b|\b\w+\b"
        # "L'innovation" splits into "l'innovation" if lowercase? No, L' is 1 letter, so it matches "l" (ignored) and "innovation".
        # Let's verify:
        assert "innovation" in tokens
        assert "développement" in tokens
        assert "applications" in tokens
    finally:
        Tokenizer.__init__ = original_parse

def test_stemmer_french():
    # Verify Snowball stemming for French
    s = Stemmer(input_xml=None)
    assert s.stemmer.stem("recherche") == "recherch"
    assert s.stemmer.stem("recherches") == "recherch"
    assert s.stemmer.stem("innovante") == "innov"
    assert s.stemmer.stem("innovation") == "innov"

def test_levenshtein_distance():
    # Test edit distance algorithm
    assert calculate_levenshtein("chat", "chat") == 0
    assert calculate_levenshtein("chat", "chats") == 1
    assert calculate_levenshtein("machine", "machyne") == 1
    assert calculate_levenshtein("innovation", "inovatyon") == 2
    assert calculate_levenshtein("abc", "") == 3

def test_spellchecker_mocked_lexicon():
    # Test spell checker candidate matching with mocked lexicon
    original_init = SpellChecker.__init__
    try:
        def mock_init(self, lexicon_file):
            self.lexicon = {
                "chimie": "chim",
                "chimiste": "chim",
                "russe": "russ",
                "russie": "russ",
                "innovation": "innov"
            }
            self.min_prefix = 3
            self.max_length = 20
            self.proximity_threshold = 2
            # Create a mock tokenizer
            self.tokenizer = MagicMock()
            self.tokenizer.tokenize = lambda text: text.lower().split()
            
        SpellChecker.__init__ = mock_init
        
        sc = SpellChecker("dummy_lexicon.txt")
        
        # Test candidate search and matching
        assert sc.process_query("chimie") == ["chim"]
        # 'chimi' should correct to 'chimie' (dist 1)
        assert sc.process_query("chimi") == ["chim"]
        # 'innov' -> 'innovation' (len difference is 5, proximity threshold is 2, so it won't match, return 'innov')
        assert sc.process_query("innov") == ["innov"]
        
    finally:
        SpellChecker.__init__ = original_init

def test_metadata_extraction_queries():
    # Test metadata parser for various French query structures
    
    # 1. Rubrics
    m, q = extract_metadata("Je veux les articles de la rubrique Focus parlant d'innovation")
    assert m['rubric'] == "focus"
    assert "innovation" in q
    
    # 2. Image filters
    m, q = extract_metadata("Articles contenant une image de chimie")
    assert m['image'] is True
    assert "chimie" in q
    
    m, q = extract_metadata("Je veux les articles sans image de 2013")
    assert m['image'] is False
    
    # 3. Date expressions
    m, q = extract_metadata("Je voudrais les articles de 2011 sur l’enseignement")
    assert m['date_min'] == "01/01/2011"
    assert m['date_max'] == "31/12/2011"
    
    m, q = extract_metadata("Articles en mars 2013")
    assert m['date_min'] == "01/03/2013"
    assert m['date_max'] == "31/03/2013"
    
    m, q = extract_metadata("Articles entre le 03/03/2013 et le 04/05/2013")
    assert m['date_min'] == "03/03/2013"
    assert m['date_max'] == "04/05/2013"
    
    # 4. Search field target
    m, q = extract_metadata("Articles dont le titre contient le mot chimie")
    assert m['search_field'] == "title"
    
    m, q = extract_metadata("Articles dont le contenu parle de robotique")
    assert m['search_field'] == "text"

def test_boolean_expression_resolver():
    # Test metadata/boolean query normalization
    m, q = extract_metadata("CNRS ou grandes écoles mais pas Centrale Paris")
    # 'ou' -> ' OR ', 'mais pas' -> ' AND_NOT '
    assert "OR" in q
    assert "AND_NOT" in q
    
    m, q = extract_metadata("systèmes embarqués et non pas la robotique")
    assert "AND_NOT" in q

def test_binary_search_tree():
    # Verify balanced BST construction and lookup
    bst = BinarySearchTree()
    # Build list of sorted tuples
    items = [("focus", {"1", "2"}), ("teaching", {"3"}), ("innovation", {"2", "4"})]
    bst.build_balanced(items)
    
    assert bst.search_exact("focus") == {"1", "2"}
    assert bst.search_exact("teaching") == {"3"}
    assert bst.search_exact("innovation") == {"2", "4"}
    assert bst.search_exact("missing") == set()
