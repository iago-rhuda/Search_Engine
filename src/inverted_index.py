"""Inverted index generation and export for LO17 corpus fields."""

import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import os

class InvertedIndexGenerator:
    """Generates inverted indexes for various document fields from a processed XML corpus."""
    def __init__(self, xml_filepath: str, output_dir: str):
        self.xml_filepath = xml_filepath
        self.output_dir = output_dir.rstrip('/')
        os.makedirs(self.output_dir, exist_ok=True)
        self.fields = ['date', 'rubric', 'title', 'author', 'contact', 'text', 'images']
        
        # Structure: indexes[field][term][doc_id] = frequency
        self.indexes = {field: defaultdict(lambda: defaultdict(int)) for field in self.fields}
        self.tokenizer_pattern = re.compile(r"\b\w{3,}[']\w+\b|\b\w+(?:-\w+)+\b|\b\w+\b")

    def _tokenize(self, text: str) -> list:
        """Tokenizes text into lowercase alphanumeric words."""
        if not text:
            return []
        return self.tokenizer_pattern.findall(text.lower())

    def _process_images(self, images_node) -> list:
        """Extracts text metadata from images (URLs and descriptions)."""
        text_content = []
        if images_node is not None:
            for img in images_node.findall('image'):
                url_node = img.find('urlImage')
                if url_node is not None and url_node.text:
                    text_content.append(url_node.text)
                desc_node = img.find('legendeImage')
                if desc_node is not None and desc_node.text:
                    text_content.append(desc_node.text)
        return text_content
        
    def generate(self):
        """Parses the XML corpus and populates the inverted index data structure."""
        print(f"Reading XML for indexing: {self.xml_filepath}")
        tree = ET.parse(self.xml_filepath)
        root = tree.getroot()
        
        for doc in root.findall('document'):
            doc_id_node = doc.find('article')
            if doc_id_node is None or not doc_id_node.text:
                continue
            doc_id = doc_id_node.text
            
            for field in self.fields:
                if field == 'images':
                    images_node = doc.find('images')
                    tokens = [t.strip().lower() for t in self._process_images(images_node) if t.strip()]
                elif field in ['title', 'text']:
                    node = doc.find(field)
                    raw_text = node.text if node is not None else ""
                    tokens = self._tokenize(raw_text)
                else:
                    node = doc.find(field)
                    raw_text = node.text if node is not None else ""
                    # Exact match fields (date, author, etc.) are indexed as a single token
                    tokens = [raw_text.strip().lower()] if raw_text.strip() else []
                    
                for token in tokens:
                    self.indexes[field][token][doc_id] += 1
                    
        print("In-memory index generation complete.")

    def export(self):
        """Saves the generated inverted indexes to text files."""
        for field in self.fields:
            filename = os.path.join(self.output_dir, f"inverse_{field}.txt")
            terms = sorted(self.indexes[field].keys())
            
            with open(filename, 'w', encoding='utf-8') as f:
                for term in terms:
                    # Sort document IDs numerically if possible, otherwise alphabetically
                    def sort_key(doc_pair):
                        try:
                            return int(doc_pair[0])
                        except ValueError:
                            return doc_pair[0]
                            
                    docs = sorted(self.indexes[field][term].items(), key=sort_key)
                    docs_str = " ".join([f"({doc_id}, {freq})" for doc_id, freq in docs])
                    f.write(f"{term}\t{docs_str}\n")
                    
        print(f"Index files exported to: {self.output_dir}")
