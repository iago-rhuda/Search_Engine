"""Natural-language query normalization for search.

Extracts metadata (rubric/date/image/field), normalizes boolean
operators, and produces a structured query consumed by `SearchEngine`.
"""

import re
import calendar
from spell_checker import SpellChecker
from stemmer import Stemmer

MONTH_MAP = {
    "janvier": "01", "février": "02", "fevrier": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08", "aout": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12", "decembre": "12"
}

# Common query filler words that should not be indexed as keywords (in French)
QUERY_NOISE_WORDS = {
    "afficher", "donner", "chercher", "rechercher", "trouver", "retourner", "retournez", "lister", "listez", "liste",
    "aimerais", "j'aimerais", "je", "j", "voudrais", "veux", "souhaite", "souhaites", "souhaitons", 
    "cherche", "obtenir", "voir", "avoir", "quel", "quels", "quelle", "quelles", "sont", 
    "tout", "tous", "toutes", "la", "les", "le", "un", "une", "des", "du", "de", "d", "l", "à", "a", "au", "aux", "en", "sur", "dans", "avec", 
    "article", "articles", "bulletin", "bulletins", "qui", "que", "dont", "où", "fait", "faire", "être",
    "parle", "parlent", "parlant", "traite", "traitent", "traitant", "porte", "portent", "portant",
    "évoque", "évoquent", "évoquant", "mentionne", "mentionnent", "mentionnant", "concerne", "concernent",
    "contient", "contiennent", "contenant", "possède", "possédant", "implique", "impliquant",
    "titre", "contenu", "mot", "mots", "terme", "termes", "propos", "lié", "liés", "liées",
    "domaine", "sujet", "cité", "ville", "pays", "moi", "nous", "mais", "ceux", "celles", "parue", "parues", "paru", "parus",
    "rubrique", "rubriques", "publié", "publiés", "publiée", "publiées", "écrit", "écrits", "écrite", "écrites",
    "provenant", "concernant", "liste", "afficher", "donner", "chercher", "rechercher", "veux", "voudrais", "souhaite",
    "soit", "mais", "pas", "non", "sans", "projet", "recherche"
}


def _normalize_year_to_range(year: int):
    return f"01/01/{year}", f"31/12/{year}"


def _normalize_month_year_to_range(month: int, year: int):
    last_day = calendar.monthrange(year, month)[1]
    return f"01/{month:02d}/{year}", f"{last_day:02d}/{month:02d}/{year}"


def _parse_date_expression(raw: str):
    s = raw.strip().lower()

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{day:02d}/{month:02d}/{year}", f"{day:02d}/{month:02d}/{year}"

    m = re.fullmatch(r"(?:(?:le)\s+)?(\d{1,2})\s+([a-zéûôîàèùç]+)\s+(\d{4})", s)
    if m:
        day, month_name, year = int(m.group(1)), m.group(2), int(m.group(3))
        if month_name in MONTH_MAP:
            month = int(MONTH_MAP[month_name])
            return f"{day:02d}/{month:02d}/{year}", f"{day:02d}/{month:02d}/{year}"

    m = re.fullmatch(r"(?:(?:au\s+mois\s+de|au\s+mois\s+d'|en|de)\s+)?([a-zéûôîàèùç]+)\s+(\d{4})", s)
    if m:
        month_name, year = m.group(1), int(m.group(2))
        if month_name in MONTH_MAP:
            month = int(MONTH_MAP[month_name])
            return _normalize_month_year_to_range(month, year)

    m = re.fullmatch(r"(?:en|de|de\s+l'année|de\s+l'annee|l'année|l'annee|année|annee|à\s+partir\s+de|a\s+partir\s+de)?\s*(\d{4})", s)
    if m:
        return _normalize_year_to_range(int(m.group(1)))

    return None, None

def extract_metadata(query: str, logger=None):
    """
    Extracts metadata (dates, rubrics, image filters) using regex patterns.
    Returns a metadata dictionary and the remaining cleaned query string.
    """
    phrase = query.lower()
    
    metadata = {
        'rubric': None,
        'search_field': None,
        'date_min': None,
        'date_max': None,
        'mois_inclus': [],
        'mois_exclus': [],
        'image': None,
        'operateur': []
    }
    
    # 1. Structural Filters (Images)
    no_image_pattern = r'\b(sans image|sans images|pas d\'image|pas d\'images)\b'
    has_image_pattern = r'\b(avec des images|avec image|avec images|contenant une image|des images)\b'
    
    if re.search(no_image_pattern, phrase):
        metadata['image'] = False
        phrase = re.sub(no_image_pattern, '', phrase)
        if logger:
            logger.log("METADATA", "Image filter detected: No images")
    elif re.search(has_image_pattern, phrase):
        metadata['image'] = True
        phrase = re.sub(has_image_pattern, '', phrase)
        if logger:
            logger.log("METADATA", "Image filter detected: With images")

    # 2. ADIT Specific Rubrics (French corpus)
    rubrics = [
        "en direct des laboratoires", "horizons enseignement", "horizon enseignement",
        "actualités innovations", "actualites innovations", "actualité innovation",
        "focus", "a lire", "événement", "evenement"
    ]

    for rub in sorted(rubrics, key=len, reverse=True):
        rub_pattern = re.escape(rub)
        context_patterns = [
            rf"\b(?:de\s+la|de\s+l[ae]|dans\s+la|provenant\s+de\s+la|dont\s+la|dont\s+les)\s+rubriques?\s+(?:est\s+|sont\s+)?({rub_pattern})\b",
            rf"\brubriques?\s+(?:est\s+|sont\s+)?({rub_pattern})\b",
            rf"\b({rub_pattern})\b"
        ]

        matched = False
        for pattern in context_patterns:
            m = re.search(pattern, phrase)
            if m:
                metadata['rubric'] = m.group(1).strip()
                phrase = phrase[:m.start()] + " " + phrase[m.end():]
                matched = True
                if logger:
                    logger.log("METADATA", f"Rubric detected: {metadata['rubric']}")
                break
        if matched:
            break

    # 3. Specific Months (Inclusions/Exclusions in French queries)
    month_names = "|".join(MONTH_MAP.keys())
    
    exclude_pattern = rf'\b(?:mais pas|pas|non|sauf)(?:\s+(?:au mois de|en|le|au mois d\'|d\'))?\s+({month_names}|[0-9]{{4}})\b'
    for match in re.finditer(exclude_pattern, phrase):
        m = match.group(1).lower()
        if m.isdigit() and len(m) == 4:
            metadata['mois_exclus'].append(m)
            if logger:
                logger.log("METADATA", f"Year exclusion detected: {m}")
        elif m in MONTH_MAP:
            metadata['mois_exclus'].append(MONTH_MAP[m])
            if logger:
                logger.log("METADATA", f"Month exclusion detected: {m}")
    phrase = re.sub(exclude_pattern, '', phrase)

    include_pattern = rf'\b(?:au mois de|au mois d\'|en|le)\s+({month_names})\b(?!\s+[0-9]{{4}})'
    for match in re.finditer(include_pattern, phrase):
        m = match.group(1).lower()
        metadata['mois_inclus'].append(MONTH_MAP[m])
        if logger:
            logger.log("METADATA", f"Month inclusion detected: {m}")
    phrase = re.sub(include_pattern, '', phrase)

    # 4. Temporal Constraints (Years and specific dates in French)
    months_regex = r"(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)"
    date_regex = rf"(?:[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}|(?:le\s+)?[0-9]{{1,2}}\s+{months_regex}\s+[0-9]{{4}}|(?:au\s+mois\s+de\s+|au\s+mois\s+d'|en\s+|de\s+)?{months_regex}\s+[0-9]{{4}}|[0-9]{{4}})"

    between_match = re.search(rf"\bentre\s+(?:le\s+)?({date_regex})\s+et\s+(?:le\s+)?({date_regex})\b", phrase)
    after_match = re.search(rf"\b(?:après|apres|à\s+partir\s+de|a\s+partir\s+de)\s+(?:le\s+)?({date_regex})\b", phrase)

    day_month_year_match = re.search(
        rf"\b(?:en|de|de\s+l'année|de\s+l'annee|l'année|l'annee|année|annee|au\s+mois\s+de|au\s+mois\s+d')\s+((?:le\s+)?[0-9]{{1,2}}\s+{months_regex}\s+[0-9]{{4}}|[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}})\b",
        phrase
    )
    month_year_match = re.search(
        rf"\b(?:en|de|de\s+l'année|de\s+l'annee|l'année|l'annee|année|annee|au\s+mois\s+de|au\s+mois\s+d')\s+({months_regex}\s+[0-9]{{4}})\b",
        phrase
    )
    month_year_fallback_match = re.search(rf"\b({months_regex}\s+(?:19\d{{2}}|20\d{{2}}))\b", phrase)
    single_match = re.search(rf"\b(?:en|de|de\s+l'année|de\s+l'annee|l'année|l'annee|année|annee|au\s+mois\s+de|au\s+mois\s+d')\s+([0-9]{{4}})\b", phrase)
    standalone_year_match = re.search(r"\b(19\d{2}|20\d{2})\b", phrase)

    if between_match:
        left_min, _ = _parse_date_expression(between_match.group(1))
        _, right_max = _parse_date_expression(between_match.group(2))
        metadata['date_min'] = left_min
        metadata['date_max'] = right_max
        phrase = phrase[:between_match.start()] + ' ' + phrase[between_match.end():]
    elif after_match:
        parsed_min, _ = _parse_date_expression(after_match.group(1))
        metadata['date_min'] = parsed_min
        phrase = phrase[:after_match.start()] + ' ' + phrase[after_match.end():]
    elif day_month_year_match:
        parsed_min, parsed_max = _parse_date_expression(day_month_year_match.group(1))
        metadata['date_min'] = parsed_min
        metadata['date_max'] = parsed_max
        phrase = phrase[:day_month_year_match.start()] + ' ' + phrase[day_month_year_match.end():]
    elif month_year_match:
        parsed_min, parsed_max = _parse_date_expression(month_year_match.group(1))
        metadata['date_min'] = parsed_min
        metadata['date_max'] = parsed_max
        phrase = phrase[:month_year_match.start()] + ' ' + phrase[month_year_match.end():]
    elif month_year_fallback_match:
        parsed_min, parsed_max = _parse_date_expression(month_year_fallback_match.group(1))
        metadata['date_min'] = parsed_min
        metadata['date_max'] = parsed_max
        phrase = phrase[:month_year_fallback_match.start()] + ' ' + phrase[month_year_fallback_match.end():]
    elif single_match:
        parsed_min, parsed_max = _parse_date_expression(single_match.group(1))
        metadata['date_min'] = parsed_min
        metadata['date_max'] = parsed_max
        phrase = phrase[:single_match.start()] + ' ' + phrase[single_match.end():]
    elif standalone_year_match:
        y = int(standalone_year_match.group(1))
        metadata['date_min'], metadata['date_max'] = _normalize_year_to_range(y)
        phrase = phrase[:standalone_year_match.start()] + ' ' + phrase[standalone_year_match.end():]

    cleaned_query = re.sub(r'\s+', ' ', phrase).strip()

    # 5. Field-specific intent (French queries)
    title_field_pattern = r"\b(?:dont\s+le\s+)?titre\s+(?:contient|évoque|evoque|parle\s+de)\b"
    text_field_pattern = r"\b(?:contenu|texte)\s+(?:contient|évoque|evoque|parle\s+de)\b"
    if re.search(title_field_pattern, cleaned_query):
        metadata['search_field'] = 'title'
        cleaned_query = re.sub(title_field_pattern, ' ', cleaned_query)
    elif re.search(text_field_pattern, cleaned_query):
        metadata['search_field'] = 'text'
        cleaned_query = re.sub(text_field_pattern, ' ', cleaned_query)
    
    # 6. Boolean Operator Normalization
    boolean_patterns = [
        (r",\s*soit\b", " OR "),
        (r"\bsoit\b", " OR "),
        (r"\bmais\s+pas\b", " AND_NOT "),
        (r"\bet\s+non\s+pas\b", " AND_NOT "),
        (r"\bsans\b", " AND_NOT "),
        (r"\b(?:mais\s+qui\s+)?ne\s+parl(?:e|ent)?\s+pas\s+de\b", " AND_NOT "),
        (r"\b(?:mais\s+qui\s+)?n'\s*parl(?:e|ent)?\s+pas\s+de\b", " AND_NOT "),
        (r"\b(?:mais\s+)?(?:qui\s+)?ne\s+\w+\s+pas\b", " AND_NOT "),
        (r"\b(?:mais\s+)?(?:qui\s+)?n'\s*\w+\s+pas\b", " AND_NOT "),
        (r"\bou\b", " OR "),
        (r"\bet\b", " AND "),
    ]

    for pattern, replacement in boolean_patterns:
        cleaned_query = re.sub(pattern, replacement, cleaned_query)

    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
    cleaned_query = re.sub(r'^OR\s+', '', cleaned_query)
    cleaned_query = re.sub(r'\s+OR$', '', cleaned_query)
    metadata['operateur'] = re.findall(r'\b(?:AND_NOT|AND|OR)\b', cleaned_query)
        
    return metadata, re.sub(r'\s+', ' ', cleaned_query).strip()

def process_request(query_text: str, stemmer, spell_checker, stop_words, logger=None):
    """Processes natural language query into a structured object."""
    def _clean_token(token: str) -> str:
        if not token:
            return ""
        cleaned = token.strip().strip(",.!?;:\"()[]{}")
        return cleaned

    if logger:
        logger.log("QUERY", "Starting metadata extraction...")
    metadata, remaining_text = extract_metadata(query_text, logger)
    if logger:
        logger.log("QUERY", f"Remaining query after extraction: '{remaining_text}'")
    
    tokens = spell_checker.tokenizer.tokenize(remaining_text)
    formal_operators = {"AND", "OR", "AND_NOT"}
    
    keywords = []
    highlight_keywords = []
    equation_parts = []
    
    for token in tokens:
        token = _clean_token(token)
        if not token:
            continue

        op_token = token.upper()
        if op_token in formal_operators:
            equation_parts.append(op_token)
            continue
            
        if token in stop_words or token in QUERY_NOISE_WORDS:
            if logger:
                logger.log("FILTER", f"Token ignored (noise/stopword): '{token}'")
            continue
            
        corrected = spell_checker.process_query(token, logger=logger)
        if corrected:
            word = _clean_token(corrected[0])
            if not word:
                continue
            keywords.append(word)
            highlight_keywords.append(token)
            equation_parts.append(word)

    cleaned_parts = []
    for part in equation_parts:
        if part in formal_operators:
            if not cleaned_parts:
                continue
            if cleaned_parts[-1] in formal_operators:
                cleaned_parts[-1] = part
                continue
        cleaned_parts.append(part)

    while cleaned_parts and cleaned_parts[-1] in formal_operators:
        cleaned_parts.pop()

    metadata['keywords'] = keywords
    metadata['highlight_keywords'] = highlight_keywords
    metadata['equation'] = " ".join(cleaned_parts)
    metadata['operateur'] = [t for t in cleaned_parts if t in formal_operators]
    return metadata
