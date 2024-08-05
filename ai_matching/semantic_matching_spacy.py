"""
Perform semantic matching using SpaCy.
Args:
	term (str): The term to match.
	template_terms (list): List of template terms.
Returns:
	tuple: Best matching term and its similarity score.
"""

# You can now load the package via spacy.load('en_core_web_md')

import spacy

# Load SpaCy model
nlp = spacy.load('en_core_web_md')

def semantic_match_spacy(term, template_terms):
    term_doc = nlp(term)
    similarities = {}
    for template_term in template_terms:
        template_doc = nlp(template_term)
        similarity = term_doc.similarity(template_doc)
        similarities[template_term] = similarity
    best_match = max(similarities, key=similarities.get)
    return best_match, similarities[best_match]

def find_semantic_matches_spacy(user_terms, template_terms):
    matches = {}
    for term in user_terms:
        match, score = semantic_match_spacy(term, template_terms)
        matches[term] = (match, score)
    return matches