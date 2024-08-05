'''
This function gives near exact matches, after normalization.
Meaning: they mostly match, with a possibility of slight differences in syntax
'''

def normalized_match(normalized_template_terms, normalized_user_terms):
    """
    Find normalized exact matches.
    """
    normalized_matches = set(normalized_template_terms) & set(normalized_user_terms)
    return normalized_matches

def exact_match(noaa_template_terms, user_terms):
    """
    Find exact matches.
    """
    exact_matches = set(noaa_template_terms) & set(user_terms)
    return exact_matches