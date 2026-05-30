import xml.etree.ElementTree as ET
import re
import sys
import os

try:
    from nltk.stem.snowball import SnowballStemmer
except ImportError:
    import subprocess
    print("Installing NLTK library for stemming...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    from nltk.stem.snowball import SnowballStemmer

class Stemmer:
    """Class to handle word stemming using NLTK's Snowball algorithm."""
    def __init__(self, input_xml=None, output_file=None):
        self.input_xml = input_xml
        self.output_file = output_file
        self.stemmer = SnowballStemmer("french")
        
        if self.input_xml:
            self.tree = ET.parse(self.input_xml)
            self.root = self.tree.getroot()
        else:
            self.tree = None
            self.root = None
        
        # Pattern to match words with at least 3 characters, including those with hyphens or apostrophes
        self.tokenizer_pattern = re.compile(r"\b\w{3,}[']\w+\b|\b\w+\b")

    def _extract_texts(self):
        """Generator to extract lowercase text from all documents in the XML."""
        for doc in self.root.findall('document'):
            title = doc.find('title')
            text = doc.find('text')
            
            content = ""
            if title is not None and title.text:
                content += title.text + " "
            if text is not None and text.text:
                content += text.text
                
            if content.strip():
                yield content.lower()

    def stem_text(self, text):
        """Stems all words in a given text string."""
        words = self.tokenizer_pattern.findall(text)
        return " ".join([self.stemmer.stem(word.lower()) for word in words])

    def run(self):
        """Processes the XML and saves the word-to-stem mapping to a file."""
        print("Starting stemming process using NLTK Snowball...")
        stem_dict = {}
        
        for text in self._extract_texts():
            words = self.tokenizer_pattern.findall(text)
            for word in words:
                word_lower = word.lower()
                stem_dict[word_lower] = self.stemmer.stem(word_lower)
                    
        # Write Word and Stem columns (tab-separated)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for word, stem in sorted(stem_dict.items()):
                f.write(f"{word}\t{stem}\n")
                
        print(f"File '{self.output_file}' generated successfully. {len(stem_dict)} pairs saved.")
