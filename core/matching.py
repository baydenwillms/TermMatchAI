def normalized_match(normalized_template_terms, normalized_user_terms):
    """
    Find normalized exact matches based on terms only.
    """
    normalized_matches = {}
    for user_term in normalized_user_terms:
        if user_term in normalized_template_terms:
            normalized_matches[user_term] = user_term
    return normalized_matches

def exact_match(noaa_template_terms, user_terms):
    """
    Find exact matches based on terms only.
    """
    exact_matches = {}
    for user_term in user_terms:
        if user_term in noaa_template_terms:
            exact_matches[user_term] = user_term
    return exact_matches