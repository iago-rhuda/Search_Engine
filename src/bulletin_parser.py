from lxml import html

class BulletinParser:
    """Parses individual HTM bulletin files and returns a structured dictionary."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        try:
            with open(self.filepath, 'r', encoding='UTF-8') as f:
                self.tree = html.fromstring(f.read())
        except Exception as e:
            print(f'Error reading file {self.filepath}: [{e}]')

    def _extract_metadata(self) -> dict:
        """Extracts general metadata like bulletin number, date, author, etc."""
        xpaths = {
            "bulletin": "//span[@class='style32']",
            "article": "//p[@class='style23']//a/span[@class='style95']",
            "date": "//span[contains(@class, 'style42') and contains(text(), '/')]",
            "rubric": "//p[@class='style96']/span[@class='style42']",
            "title": "//p[@class='style96']/span[@class='style17']",
            "author": "//td[p/span[contains(text(), 'dacteur')]]/following-sibling::td/p/span",
            "contact": "//td[p/span[contains(text(), 'contacts')]]/following-sibling::td/p/span"
        }

        data = {}
        for key, xpath_str in xpaths.items():
            elements = self.tree.xpath(xpath_str)
            data[key] = elements[0].text_content().strip() if elements else None

        # Clean specific fields
        if data.get('bulletin'):
            data['bulletin'] = data['bulletin'].replace('BE France', '').strip()
        if data.get('author') and '- ' in data['author']:
            data['author'] = data['author'].split('- ')[1].strip()

        return data

    def _extract_body_text(self) -> str:
        """Extracts the main body text of the article."""
        xpath_text_blocks = "//td[contains(@class, 'FWExtra2')]//span[@class='style95']"
        elements = self.tree.xpath(xpath_text_blocks)
        if not elements:
            return None
        text_parts = [el.text_content().strip() for el in elements if el.text_content().strip()]
        return "\n\n".join(text_parts)

    def _extract_images(self) -> dict:
        """Extracts article images with their URLs and descriptions."""
        xpath_images = "//td[contains(@class, 'FWExtra2')]//div[contains(@style, 'text-align: center')]//img"
        elements = self.tree.xpath(xpath_images)
        images = {}
        for i, img in enumerate(elements, 1):
            images[f'image_{i}_url'] = img.get('src')
            
            parent = img.getparent()
            # Try to find a caption/legend in specific child nodes
            desc_nodes = parent.xpath(".//span[contains(@class, 'style21')] | .//strong")
            description = ""
            for node in desc_nodes:
                text = node.text_content().strip()
                if text:
                    description = text
                    break
            
            if not description:
                description = img.get('alt', '').strip()
                
            images[f'image_{i}_desc'] = description
            
        return images

    def parse(self) -> dict:
        """Main parsing method to aggregate all extracted components."""
        parsed_data = self._extract_metadata()
        body_text = self._extract_body_text()
        
        if body_text:
            # Clean up the footer content if present
            footer_index = body_text.find('Partager cette')
            if footer_index != -1:
                body_text = body_text[:footer_index]
            parsed_data['text'] = body_text
        else:
            parsed_data['text'] = ""

        parsed_data.update(self._extract_images())
        return parsed_data
