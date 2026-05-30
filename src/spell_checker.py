"""Spelling correction and lexical normalization for query terms.

Uses prefix-based candidate retrieval and Levenshtein distance to map user
input words to known lexicon forms/stems.
"""

import sys
import re
import os
from tokenizer import Tokenizer

def calculate_levenshtein(s1: str, s2: str) -> int:
    """Calculates the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return calculate_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class SpellChecker:
    """Provides spell correction and normalization using a prefix search and Levenshtein distance."""
    def __init__(self, lexicon_file: str, min_prefix=3, max_length=20, proximity_threshold=2):
        # Using a default path for the dummy xml needed by Tokenizer
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dummy_xml = os.path.join(current_dir, "../data/outputs/phase_1_xml/xml.xml")
        self.tokenizer = Tokenizer(dummy_xml, os.path.join(current_dir, "../data/outputs/phase_2_filtered"))
        self.lexicon = self.tokenizer.load_dictionary(lexicon_file)
        self.min_prefix = min_prefix
        self.max_length = max_length
        self.proximity_threshold = proximity_threshold
        print(f"Lexicon loaded: {len(self.lexicon)} words.")

    def _get_candidates(self, term: str) -> list:
        """Finds candidate words in the lexicon based on shared prefix and length proximity."""
        prefix_len = min(len(term), self.min_prefix)
        prefix = term[:prefix_len]

        candidates = []
        for word in self.lexicon.keys():
            if word.startswith(prefix) and abs(len(word) - len(term)) <= self.proximity_threshold and len(word) <= self.max_length:
                candidates.append(word)
        return candidates

    def process_query(self, query: str, logger=None) -> list:
        """Tokenizes the query and returns a list of corrected stems/lemmas."""
        tokens = self.tokenizer.tokenize(query)
        corrected_stems = []
        
        for term in tokens:
            # Skip numbers or entities
            if re.match(r'^\d+$', term):
                corrected_stems.append(term)
                continue
                
            # Perfect match in lexicon
            if term in self.lexicon:
                corrected_stems.append(self.lexicon[term])
                continue
                
            # Generate candidates via prefix search
            candidates = self._get_candidates(term)
            
            if not candidates:
                if logger: logger.log("SPELL", f"'{term}' -> No candidates found. Kept as is.")
                corrected_stems.append(term)
                continue
                
            # Single candidate: direct correction
            if len(candidates) == 1:
                best_word = candidates[0]
                best_stem = self.lexicon[best_word]
                if logger: logger.log("SPELL", f"'{term}' -> Corrected to '{best_word}' (stem: {best_stem})")
                corrected_stems.append(best_stem)
                continue
                
            # Multiple candidates: resolve with Levenshtein
            best_word = min(candidates, key=lambda c: calculate_levenshtein(term, c))
            best_stem = self.lexicon[best_word]
            if logger: logger.log("SPELL", f"'{term}' -> Multi-candidate tie-break: '{best_word}' (stem: {best_stem})")
            corrected_stems.append(best_stem)
            
        return corrected_stems
