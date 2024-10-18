import re

date_related_words = {
    'date', 'time', 'day', 'month', 'year', 'hour', 'minute', 'second',
    'dt', 'tm', 'timestamp', 'datetime', 'created', 'modified', 'updated'
}

common_date_prefixes = {
    'start', 'end', 'begin', 'finish', 'initial', 'final', 'last', 'first',
    'event', 'log', 'record', 'entry'
}

def is_likely_date_field(term, data_example=''):
    term = term.lower()
    
    if term in date_related_words:
        return True

    if len(term) > 5:
        prefix = term[:-4]
        if prefix in common_date_prefixes:
            return True

    # Explicit check for patterns like 'yearCollected'
    if re.match(r'(year|month|day|date|time|hour|minute|second).*', term):
        return True

    date_patterns = [
        r'.*?(date|time|day|month|year|hour|minute|second)s?.*',  # Contains date-related word
        r'\b(dt|tm)\b',  # Common abbreviations
        r'_at$',  # Fields ending with '_at' (e.g., created_at)
        r'timestamp',  # Timestamp fields
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # Basic date format check in data
        r'\d{1,2}:\d{2}(:\d{2})?',  # Basic time format check in data
    ]
    
    if any(re.search(pattern, term) for pattern in date_patterns):
        return True

    # Check if the data example looks like a date/time
    if data_example:
        data_str = str(data_example)
        if re.search(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', data_str) or \
           re.search(r'\b\d{1,2}:\d{2}(:\d{2})?\b', data_str):
            return True

    return False

def get_date_terms(terms_with_data):
    date_terms = []
    
    for term, data in terms_with_data.items():
        if is_likely_date_field(term, data):
            date_terms.append(term)
    
    return date_terms

# Usage:
# your_data = {...}  # Your dictionary of terms and their data
# date_terms = get_date_terms(your_data)