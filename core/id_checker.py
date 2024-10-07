import re

english_words = {
    'acid', 'amid', 'lipid', 'void', 'valid', 'humid', 'lucid', 'rigid', 'timid', 'vivid',
    'fluid', 'solid', 'rabid', 'tepid', 'candid', 'sordid', 'splendid', 'squalid', 'torrid',
    'arid', 'avid', 'fetid', 'frigid', 'hybrid', 'livid', 'morbid', 'putrid', 'rancid'
}

common_id_prefixes = {'user', 'employee', 'account', 'session', 'device', 'cruise', 'line',
                      'location', 'material', 'event', 'recordedBy', 'project', 'study',
                      'sample'}

def is_hyperlink(text):
    if not text:
        return False
    return bool(re.match(r'(https?://\S+|www\.\S+|\S+\.\S+/\S+)', text))

def is_likely_id_field(term, data_example=''):
    term = term.lower()
    
    if is_hyperlink(data_example):
        return True, True

    if term in english_words or term in ['county', 'island']:
        return False, False

    if len(term) > 4:
        prefix = term[:-2]
        if prefix in common_id_prefixes:
            return True, False

    id_patterns = [
        r'_id$',
        r'^id_',
        r'_id_',
        r'\d+id$',
        r'^id\d+$',
        r'guid',
        r'uuid',
        r'[a-z]+_id$',
        r'^id_[a-z]+$',
        r'[a-z]+id\d*$',
        r'^[a-z]+_?id_?\d*$',
        r'id[_-]?[a-z]*\d*$',
        r'\bid\b',
        r'ident(ifier)?',
        r'doi',
        r'bcid',
        r'uri',
        r'code$',
    ]
    
    if any(re.search(pattern, term, re.IGNORECASE) for pattern in id_patterns):
        return True, False

    if len(term) <= 6 and not term.isalpha():
        return True, False

    return False, False

def get_id_terms(terms_with_data):
    regular_ids = []
    hyperlink_ids = []
    
    for term, data in terms_with_data.items():
        data_str = str(data) if data is not None else ''
        is_id, is_hyperlink = is_likely_id_field(term, data_str)
        if is_id:
            if is_hyperlink:
                hyperlink_ids.append(term)
            else:
                regular_ids.append(term)
    
    # Identify compound keys
    all_ids = regular_ids + hyperlink_ids
    compound_keys = []
    for i, term in enumerate(all_ids):
        for other_term in all_ids[i+1:]:
            if term in other_term or other_term in term:
                compound_keys.extend([term, other_term])
    compound_keys = list(set(compound_keys))  # Remove duplicates
    
    # Identify the main compound key (longest one among compound keys)
    main_compound_key = max(compound_keys, key=len) if compound_keys else None
    
    # If no compound key is identified, use the longest non-hyperlink ID as a fallback
    if not main_compound_key:
        non_hyperlink_ids = [term for term in all_ids if term not in hyperlink_ids]
        if non_hyperlink_ids:
            main_compound_key = max(non_hyperlink_ids, key=len)
    
    # Remove compound keys and main_compound_key from regular_ids and hyperlink_ids
    regular_ids = [term for term in regular_ids if term not in compound_keys and term != main_compound_key]
    hyperlink_ids = [term for term in hyperlink_ids if term not in compound_keys and term != main_compound_key]
    
    # Ensure the main compound key is first in the list
    final_id_list = [main_compound_key] if main_compound_key else []
    final_id_list.extend([key for key in compound_keys if key != main_compound_key])
    final_id_list.extend(regular_ids + hyperlink_ids)
    
    return final_id_list, main_compound_key

# Usage:
# your_data = {...}  # Your dictionary of terms and their data
# id_terms, compound_key = get_id_terms(your_data)