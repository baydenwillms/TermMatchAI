from core.data_loading import get_term_lists
from core.normalization import normalize
from core.exact_matching import exact_match
from core.fuzzy_matching import fuzzy_match
from ai_matching.semantic_matching import find_semantic_matches
from core.generate_report import generate_report

def main():
    # Get the lists of term names
    template_terms, user_terms = get_term_lists()
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in template_terms]
    normalized_user_terms = [normalize(term) for term in user_terms]
    
    # Exact matching
    exact_matches = exact_match(normalized_template_terms, normalized_user_terms)
    print(f"Exact Matches: {exact_matches}")
    
    # Fuzzy matching
    fuzzy_matches = fuzzy_match(normalized_template_terms, normalized_user_terms)
    print(f"Fuzzy Matches: {fuzzy_matches}")
    
    # Semantic matching
    semantic_matches = find_semantic_matches(normalized_user_terms, normalized_template_terms)
    print(f"Semantic Matches: {semantic_matches}")
    
    # Identify new terms
    new_terms = [term for term in normalized_user_terms if term not in exact_matches and term not in fuzzy_matches and term not in semantic_matches]
    print(f"New Terms: {new_terms}")
    
    # Generate report
    generate_report(exact_matches, fuzzy_matches, semantic_matches, new_terms, 'term_matching_report.csv')

if __name__ == '__main__':
    main()