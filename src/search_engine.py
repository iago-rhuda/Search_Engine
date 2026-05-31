"""Search engine core for boolean and metadata-driven retrieval.

Loads exported inverted indexes, evaluates structured queries, applies filters,
computes relevance scores, and formats UI-facing results.
"""

import os
import re
import xml.etree.ElementTree as ET

class BSTNode:
    """A node in the Binary Search Tree."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    """A balanced Binary Search Tree for exact metadata matching."""
    def __init__(self):
        self.root = None

    def build_balanced(self, items: list):
        """Builds a balanced BST from a list of (key, value) tuples."""
        items.sort(key=lambda x: x[0])
        self.root = self._build_balanced_recursive(items, 0, len(items) - 1)

    def _build_balanced_recursive(self, items, start, end):
        if start > end:
            return None
        mid = (start + end) // 2
        node = BSTNode(items[mid][0], items[mid][1])
        node.left = self._build_balanced_recursive(items, start, mid - 1)
        node.right = self._build_balanced_recursive(items, mid + 1, end)
        return node

    def search_exact(self, key):
        """Performs an exact search for a key in the BST."""
        node = self.root
        while node is not None:
            if key == node.key:
                return node.value
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return set()

class SearchEngine:
    """Core engine for boolean search and metadata filtering."""
    def __init__(self, index_dir: str, xml_path: str, status_callback=None):
        self.index_dir = index_dir
        self.xml_path = xml_path
        self.status_callback = status_callback
        self.indexes = {}
        self.doc_titles = {}
        self.doc_dates = {}
        self.doc_rubrics = {}
        self.doc_texts = {}
        
        self._load_doc_metadata()
        self._load_all_indexes()

    def _load_doc_metadata(self):
        """Loads basic document info (title, date) from the XML corpus for display."""
        if self.status_callback:
            self.status_callback("Phase 4: Loading Search Components", "Parsing XML corpus metadata...")
        if not os.path.exists(self.xml_path):
            print(f"Warning: XML corpus not found at {self.xml_path}")
            return
            
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        for doc in root.findall('document'):
            doc_id_node = doc.find('article')
            if doc_id_node is None:
                continue
            doc_id = doc_id_node.text
            
            title_node = doc.find('title')
            title = title_node.text if title_node is not None else "Untitled"
            date_node = doc.find('date')
            date = date_node.text if date_node is not None else ""
            rubric_node = doc.find('rubric')
            rubric = rubric_node.text if rubric_node is not None else ""
            text_node = doc.find('text')
            text = text_node.text if text_node is not None else ""
            
            self.doc_titles[doc_id] = title
            self.doc_dates[doc_id] = date
            self.doc_rubrics[doc_id] = rubric
            self.doc_texts[doc_id] = text

    def _load_all_indexes(self):
        """Loads all exported inverted index files into memory."""
        metadata_fields = {'date', 'author', 'rubric', 'contact'}
        if not os.path.exists(self.index_dir):
            return
            
        for filename in os.listdir(self.index_dir):
            if filename.startswith("inverse_") and filename.endswith(".txt"):
                field = filename.replace("inverse_", "").replace(".txt", "")
                filepath = os.path.join(self.index_dir, filename)
                
                if self.status_callback:
                    self.status_callback("Phase 4: Loading Search Components", f"Loading index: {field}...")
                
                # Metadata fields use BST for performance, content fields use hash maps
                if field in metadata_fields:
                    self.indexes[field] = self._read_inverse_file_bst(filepath)
                else:
                    self.indexes[field] = self._read_inverse_file(filepath)
        
        print(f"Indexes loaded: {list(self.indexes.keys())}")

    def _read_inverse_file_bst(self, filepath: str) -> BinarySearchTree:
        """Parses an index file and constructs a Binary Search Tree."""
        items = []
        import time
        line_count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                if line_count % 500 == 0:
                    time.sleep(0.002) # Yield GIL to prevent starving web thread
                line = line.strip()
                if not line:
                    continue

                if '\t' in line:
                    term, _ = line.split('\t', 1)
                else:
                    term = line.split(' ', 1)[0]
                doc_ids = set(re.findall(r'\((\d+),', line))
                items.append((term, doc_ids))
        
        bst = BinarySearchTree()
        bst.build_balanced(items)
        return bst

    def _read_inverse_file(self, filepath: str) -> dict:
        """Parses an index file into a mapping: term -> {doc_id: frequency}."""
        index = {}
        import time
        line_count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                if line_count % 500 == 0:
                    time.sleep(0.002) # Yield GIL to prevent starving web thread
                line = line.strip()
                if not line:
                    continue

                if '\t' in line:
                    term, _ = line.split('\t', 1)
                else:
                    term = line.split(' ', 1)[0]
                doc_freq = {
                    doc_id: int(freq)
                    for doc_id, freq in re.findall(r'\((\d+),\s*(\d+)\)', line)
                }
                index[term] = doc_freq
        return index

    def search(self, structured_query: dict, sort_by: str = "relevance", logger=None):
        """Executes the complete search pipeline based on a structured query."""
        if logger:
            logger.log("SEARCH", f"Starting boolean search for equation: {structured_query.get('equation')} (Sort: {sort_by})")
        
        # 1. Resolve Boolean Keyword Logic
        final_results = self._evaluate_boolean_query(structured_query, logger)
        
        # If no keywords are provided, start with all documents to allow metadata-only filtering
        if final_results is None:
            final_results = set(self.doc_titles.keys())
            if logger:
                logger.log("SEARCH", "No keywords provided, applying filters to full corpus.")
        else:
            if logger:
                logger.log("SEARCH", f"Initial boolean matches: {len(final_results)} documents.")

        # 2. Apply Metadata Equality Filters
        for field in ['rubric', 'author', 'contact', 'date']:
            if structured_query.get(field):
                val = str(structured_query[field]).lower()
                idx = self.indexes.get(field)
                
                if isinstance(idx, BinarySearchTree):
                    matches = idx.search_exact(val)
                else:
                    matches = idx.get(val, set()) if idx else set()
                
                final_results &= matches
                if logger:
                    logger.log("SEARCH", f"Metadata filter ({field}='{val}'): {len(final_results)} docs remaining.")

        # 3. Apply Range-based Date and Month Filters
        if any(structured_query.get(k) for k in ['date_min', 'date_max', 'mois_inclus', 'mois_exclus']):
            final_results = self._filter_by_date_range(
                final_results, 
                structured_query.get('date_min'), 
                structured_query.get('date_max'),
                structured_query.get('mois_inclus', []),
                structured_query.get('mois_exclus', [])
            )
            if logger:
                logger.log("SEARCH", f"Temporal filters applied: {len(final_results)} docs remaining.")

        # 4. Image Availability Filter
        if structured_query.get('image') is not None:
            image_docs = set()
            for term_matches in self.indexes.get('images', {}).values():
                image_docs.update(term_matches.keys())
            
            if structured_query['image']:
                final_results &= image_docs
            else:
                final_results -= image_docs
            if logger:
                logger.log("SEARCH", f"Image filter applied: {len(final_results)} docs remaining.")

        # 5. Calculate Scores and Sort
        keywords = structured_query.get('keywords', [])
        highlight_keywords = structured_query.get('highlight_keywords', keywords)
        scored_results = []
        for doc_id in final_results:
            score = self._calculate_score(doc_id, keywords)
            scored_results.append((doc_id, score))
            
        if sort_by == "newest":
            scored_results.sort(key=lambda x: self._parse_date(self.doc_dates.get(x[0], "")), reverse=True)
        elif sort_by == "oldest":
            scored_results.sort(key=lambda x: self._parse_date(self.doc_dates.get(x[0], "")))
        else: # relevance
            scored_results.sort(key=lambda x: x[1], reverse=True)

        # 6. Format Output
        output = []
        for doc_id, score in scored_results:
            output.append({
                'id': doc_id,
                'title': self.doc_titles.get(doc_id, "Untitled"),
                'date': self.doc_dates.get(doc_id, ""),
                'rubric': self.doc_rubrics.get(doc_id, "General"),
                'snippet': self._get_snippet(doc_id, highlight_keywords),
                'score': score
            })
        return output

    def _parse_date(self, date_str):
        """Helper to parse various date formats into a sortable tuple (YYYY, MM, DD)."""
        if not date_str:
            return (0, 0, 0)
        
        # DD/MM/YYYY
        match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
        if match:
            return (int(match.group(3)), int(match.group(2)), int(match.group(1)))
            
        # Month YYYY (from query)
        from query_processing import MONTH_MAP
        for m_name, m_num in MONTH_MAP.items():
            if m_name in date_str.lower():
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    return (int(year_match.group(1)), int(m_num), 1)
        
        # Just YYYY
        match_y = re.search(r'(\d{4})', date_str)
        if match_y:
            return (int(match_y.group(1)), 1, 1)
            
        return (0, 0, 0)

    def _calculate_score(self, doc_id, keywords):
        """Simple relevance scoring: 3*title_freq + 1*text_freq."""
        if not keywords:
            return 1.0
        score = 0
        title_index = self.indexes.get('title', {})
        text_index = self.indexes.get('text', {})
        for kw in keywords:
            title_freq = title_index.get(kw, {}).get(doc_id, 0)
            text_freq = text_index.get(kw, {}).get(doc_id, 0)
            score += (3 * title_freq) + text_freq
        return score

    def _get_snippet(self, doc_id, highlight_keywords):
        """Generates a contextual snippet around keywords."""
        text = self.doc_texts.get(doc_id, "")
        if not text:
            return ""
        
        text_clean = text.replace('\n', ' ').strip()
        text_lower = text_clean.lower()
        
        first_pos = -1
        for kw in highlight_keywords:
            if not kw:
                continue
            pos = text_lower.find(kw.lower())
            if pos != -1 and (first_pos == -1 or pos < first_pos):
                first_pos = pos
        
        if first_pos == -1:
            return text_clean[:150] + "..." if len(text_clean) > 150 else text_clean
            
        start = max(0, first_pos - 60)
        end = min(len(text_clean), first_pos + 90)
        snippet = text_clean[start:end].strip()
        
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text_clean) else ""
        return prefix + snippet + suffix

    def _evaluate_boolean_query(self, query: dict, logger=None):
        """Resolves boolean equation with implicit AND inside term groups."""
        keywords = query.get('keywords', [])
        equation = query.get('equation', "")
        search_field = query.get('search_field')
        
        if not keywords:
            return None
            
        postings = {}
        for word in keywords:
            title_docs = set(self.indexes.get('title', {}).get(word, {}).keys())
            text_docs = set(self.indexes.get('text', {}).get(word, {}).keys())

            if search_field == 'title':
                docs = title_docs
            elif search_field == 'text':
                docs = text_docs
            else:
                docs = title_docs | text_docs

            postings[word] = docs
            if logger:
                logger.log("SEARCH", f"Index hit for '{word}': {len(docs)} documents.")

        if not equation:
            # Default to intersection (AND) if no equation provided
            result = None
            for docs in postings.values():
                result = docs.copy() if result is None else result & docs
            return result

        tokens = equation.split()
        groups = []
        current_terms = []
        pending_op = None

        for token in tokens:
            if token in ["AND", "OR", "AND_NOT"]:
                if current_terms:
                    groups.append((pending_op, current_terms))
                    current_terms = []
                pending_op = token
            else:
                current_terms.append(token)

        if current_terms:
            groups.append((pending_op, current_terms))

        if not groups:
            return None

        def _group_docs(terms):
            group_result = None
            for term in terms:
                docs = postings.get(term, set())
                group_result = docs.copy() if group_result is None else (group_result & docs)
            return group_result if group_result is not None else set()

        result = None
        for idx, (op, terms) in enumerate(groups):
            g_docs = _group_docs(terms)
            if idx == 0:
                result = g_docs
                continue

            if op == "OR":
                result |= g_docs
            elif op == "AND_NOT":
                result -= g_docs
            else:
                result &= g_docs

        return result

    def _filter_by_date_range(self, doc_ids, min_date, max_date, inc_months, exc_months):
        """Filters documents based on date ranges and month/year exclusions."""
        filtered = set()
        
        # Pre-parse range boundaries
        start_bound = self._parse_date(min_date) if min_date else (0, 0, 0)
        end_bound = self._parse_date(max_date) if max_date else (9999, 12, 31)
        
        # Separate year exclusions from month exclusions
        year_exclusions = [int(m) for m in exc_months if len(m) == 4]
        month_exclusions = [m for m in exc_months if len(m) == 2]

        for doc_id in doc_ids:
            raw_date = self.doc_dates.get(doc_id, "")
            if not raw_date:
                continue
            
            doc_d = self._parse_date(raw_date)
            year, month, day = doc_d
            
            if year == 0:
                continue
            
            # 1. Year/Month Exclusions
            if year in year_exclusions:
                continue
            if f"{month:02d}" in month_exclusions:
                continue
            
            # 2. Month Inclusions
            if inc_months and f"{month:02d}" not in inc_months:
                continue
            
            # 3. Range check
            if start_bound <= doc_d <= end_bound:
                filtered.add(doc_id)
                
        return filtered

    def display_results(self, results: list):
        """Utility for console display of results."""
        if not results:
            print("\n[!] No articles found.")
            return
            
        print(f"\n[+] {len(results)} articles found:")
        print("=" * 80)
        for i, res in enumerate(results, 1):
            print(f"{i}. [{res['id']}] {res['title']} ({res['date']})")
        print("=" * 80)
