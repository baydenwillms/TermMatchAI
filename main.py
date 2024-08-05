from core.data_loading import get_term_lists
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
from ai_matching.semantic_matching_BERT import find_semantic_matches_sentencebert
from core.generate_report import generate_report

def main():
    # Get the lists of term names
    template_terms, user_terms = get_term_lists()
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in template_terms]
    normalized_user_terms = [normalize(term) for term in user_terms]
    
    # Normalized and Exact matching
    normalized_matches = normalized_match(normalized_template_terms, normalized_user_terms)
    print(f"Normalized Matches: {normalized_matches}")
    
    exact_matches = exact_match(template_terms, user_terms)
    print(f"Exact Matches: {exact_matches}")
    
    # Fuzzy matching
    fuzzy_matches = fuzzy_match(normalized_template_terms, normalized_user_terms)
    print(f"Fuzzy Matches: {fuzzy_matches}")
    
    # Semantic matching using SpaCy
    semantic_matches_spacy = find_semantic_matches_spacy(normalized_user_terms, normalized_template_terms)
    print(f"SpaCy Semantic Matches: {semantic_matches_spacy}")
    
    # Semantic matching using SentenceBERT
    semantic_matches_sentencebert = find_semantic_matches_sentencebert(normalized_user_terms, normalized_template_terms)
    print(f"SentenceBERT Semantic Matches: {semantic_matches_sentencebert}")
    
    # Identify new terms
    all_exact_matches = set(normalized_matches.values()).union(set(exact_matches.values()), set(match[0] for match in fuzzy_matches.values()))
    new_terms = [term for term in normalized_user_terms if term not in all_exact_matches]
    print(f"New Terms: {new_terms}")
    
    # Generate report
    generate_report(normalized_matches, exact_matches, fuzzy_matches, semantic_matches_spacy, semantic_matches_sentencebert, new_terms, 'term_matching_report.csv')

if __name__ == '__main__':
    main()