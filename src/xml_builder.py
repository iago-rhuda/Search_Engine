import os
from lxml import etree

class XMLBuilder:
    """Utility to build the structured XML corpus from dictionary data."""
    def __init__(self):
        self.corpus = etree.Element('corpus')

    def add_document(self, data: dict):
        """Creates a <document> entry in the XML tree with metadata and images."""
        doc_node = etree.SubElement(self.corpus, 'document')
        
        # Define basic metadata fields expected in the XML
        basic_fields = ['article', 'bulletin', 'date', 'rubric', 'title', 'author', 'text', 'contact']
        
        for field in basic_fields:
            if field in data:
                child_node = etree.SubElement(doc_node, field)
                child_node.text = str(data[field]) if data[field] else ""

        # Process images specifically
        images_node = etree.SubElement(doc_node, 'images')
        image_indices = sorted(set([k.split('_')[1] for k in data.keys() if k.startswith('image_')]))
        
        for idx in image_indices:
            url_key = f'image_{idx}_url'
            desc_key = f'image_{idx}_desc'
            
            if url_key in data or desc_key in data:
                image_node = etree.SubElement(images_node, 'image')
                etree.SubElement(image_node, 'urlImage').text = data.get(url_key, '')
                etree.SubElement(image_node, 'legendeImage').text = data.get(desc_key, '')

    def save(self, filepath: str):
        """Saves the generated XML tree to the specified file path."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        tree = etree.ElementTree(self.corpus)
        tree.write(filepath, encoding="utf-8", xml_declaration=True, pretty_print=True)
