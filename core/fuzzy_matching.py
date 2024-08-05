"""
Perform fuzzy matching between normalized template terms and normalized user terms.
Args:
	normalized_template_terms (list): List of normalized template terms.
	normalized_user_terms (list): List of normalized user terms.
	threshold (int): Threshold for fuzzy matching score (default is 80).
Returns:
	dict: Dictionary with template terms as keys and tuples (matched term, score) as values.
"""

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def fuzzy_match(normalized_template_terms, normalized_user_terms, threshold=80):
    matches = {}
    for term in normalized_template_terms:
        match, score = process.extractOne(term, normalized_user_terms, scorer=fuzz.ratio)
        if score >= threshold:
            matches[term] = (match, score)
    return matches