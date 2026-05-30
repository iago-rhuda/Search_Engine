import os
import re
import xml.etree.ElementTree as ET
import math

class Tokenizer:
    """Handles text tokenization, TF-IDF statistical analysis, and stopword filtering."""
    def __init__(self, xml_filepath: str, output_dir: str):
        self.input_xml = xml_filepath
        self.output_dir = output_dir.rstrip('/')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.tree = ET.parse(self.input_xml)
        self.root = self.tree.getroot()
        
        # Regex to capture words >= 3 chars with apostrophes, or hyphenated words, or standard words.
        self.tokenizer_pattern = re.compile(r"\b\w{3,}[']\w+\b|\b\w+(?:-\w+)+\b|\b\w+\b")

    def tokenize(self, text: str) -> list:
        """Splits text into a list of lowercase tokens based on the defined regex pattern."""
        return self.tokenizer_pattern.findall(text.lower())

    def _extract_documents(self, xml_file=None):
        """Generator yielding (doc_id, title, text) for each document in the XML."""
        root = ET.parse(xml_file).getroot() if xml_file else self.root
        
        for doc in root.findall('document'):
            doc_id_node = doc.find('article')
            doc_id = doc_id_node.text if doc_id_node is not None else "0"
            
            title_node = doc.find('title')
            title = title_node.text if title_node is not None else ""
            
            text_node = doc.find('text')
            text_content = text_node.text if text_node is not None else ""
            
            yield doc_id, title, text_content

    def _compute_frequencies(self):
        """Calculates Term Frequency (TF) per document and Document Frequency (DF)."""
        tf_dict = {}
        df_dict = {}
        n_docs = 0

        for doc_id, title, text in self._extract_documents():
            n_docs += 1
            tf_dict[doc_id] = {}
            content = f"{title} {text}"
            tokens = self.tokenize(content)

            for token in tokens:
                if token not in tf_dict[doc_id]:
                    tf_dict[doc_id][token] = 1
                    df_dict[token] = df_dict.get(token, 0) + 1
                else:
                    tf_dict[doc_id][token] += 1
                    
        return n_docs, tf_dict, df_dict

    def export_stats(self):
        """Computes and exports TF-IDF statistics and generates the initial stopword list."""
        n_docs, tf_dict, df_dict = self._compute_frequencies()
        
        # 1. Export tokens and counts
        with open(f'{self.output_dir}/tokens.txt', 'w', encoding='utf-8') as f:
            for doc_id, tokens in tf_dict.items():
                for token, freq in tokens.items():
                    f.write(f"{doc_id}\t{token}\t{freq}\n")

        print(f"Tokenized {n_docs} articles.")

        # 2. Calculate IDF and overall coefficients
        coef_dict = {}
        with open(f'{self.output_dir}/idf.txt', 'w', encoding='utf-8') as f:
            for token, df in df_dict.items():
                idf = math.log((n_docs / df), 10)
                coef_dict[token] = df * idf
                f.write(f"{token}\t{idf}\n")

        # 3. Export sorted coefficients and stopword list (threshold < 2)
        sorted_tokens = sorted(coef_dict.items(), key=lambda x: x[1], reverse=True)
        stop_words_path = f'{self.output_dir}/stop_words.txt'
        
        with open(stop_words_path, 'w', encoding='utf-8') as f:
            for token, coef in sorted_tokens:
                if coef < 2:
                    f.write(f"{token}\t\n")

        self._create_filtered_xml(stop_words_path)

    def load_dictionary(self, dict_file: str) -> dict:
        """Loads a tab-separated mapping file into a dictionary."""
        mapping = {}
        if not os.path.exists(dict_file):
            return mapping
        with open(dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.rstrip('\n').split('\t')
                if parts:
                    mapping[parts[0]] = parts[1] if len(parts) > 1 else ""
        return mapping

    def _apply_substitution(self, text: str, substitutions: dict, stem_map=None) -> str:
        """Replaces tokens in text based on provided dictionary and optional stem mapping."""
        def _replace(match):
            word = match.group(0).lower()
            if not stem_map:
                return substitutions.get(word, word)
            stemmed = stem_map.get(word, word)
            return substitutions.get(stemmed, stemmed)

        filtered = self.tokenizer_pattern.sub(_replace, text)
        filtered = re.sub(r"[^\w\s'-]", " ", filtered)
        filtered = re.sub(r"(?<!\w)'|'(?!\w)", " ", filtered) # Stray apostrophes
        filtered = re.sub(r' +', ' ', filtered)
        return filtered.strip()

    def _create_filtered_xml(self, dict_file, input_xml=None, output_filename='corpus_filtered.xml', stem_dict_file=None):
        """Generates a new XML corpus file with stopwords removed."""
        substitutions = self.load_dictionary(dict_file)
        stem_map = self.load_dictionary(stem_dict_file) if stem_dict_file else None
            
        target_xml = input_xml if input_xml else self.input_xml
        tree = ET.parse(target_xml)
        root = tree.getroot()
        
        for doc in root.findall('document'):
            for node_name in ('title', 'text'):
                node = doc.find(node_name)
                if node is not None and node.text:
                    node.text = self._apply_substitution(node.text, substitutions, stem_map)
                
        tree.write(f'{self.output_dir}/{output_filename}', encoding='utf-8', xml_declaration=True)

    def export_stem_stats(self, stem_dict_file: str, target_xml: str, out_file: str, filter_again=False):
        """Recalculates TF-IDF scores for stemmed words and applies secondary filtering."""
        print("Recalculating TF-IDF scores for stems...")
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        
        stem_map = self.load_dictionary(stem_dict_file)
        tf_dict = {}
        df_dict = {}
        n_docs = 0

        for doc_id, title, text in self._extract_documents(target_xml):
            n_docs += 1
            tf_dict[doc_id] = {}
            content = f"{title} {text}"
            tokens = self.tokenize(content)
            
            doc_stems = set()
            for token in tokens:
                stem = stem_map.get(token, token)
                tf_dict[doc_id][stem] = tf_dict[doc_id].get(stem, 0) + 1
                doc_stems.add(stem)
                
            for stem in doc_stems:
                df_dict[stem] = df_dict.get(stem, 0) + 1
        
        coef_dict = {stem: df * math.log((n_docs / df), 10) for stem, df in df_dict.items() if df > 0}
        sorted_stems = sorted(coef_dict.items(), key=lambda x: x[1], reverse=True)
        
        with open(out_file, 'w', encoding='utf-8') as f:
            for stem, coef in sorted_stems:
                f.write(f"{stem}\t{coef}\n")
                
        if filter_again:
            out_dir = os.path.dirname(out_file)
            stop_words_2 = f'{out_dir}/stop_words_v2.txt'
            with open(stop_words_2, 'w', encoding='utf-8') as f:
                for stem, coef in sorted_stems:
                    if coef < 2:
                        f.write(f"{stem}\t\n")
            self._create_filtered_xml(stop_words_2, input_xml=target_xml, output_filename="../phase_3_indexed/corpus_filtered_v2.xml", stem_dict_file=stem_dict_file)
