from core.data_loading import get_term_lists, get_terms_with_data
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
# from ai_matching.semantic_matching_BERT import find_semantic_matches_sentencebert
from ai_matching.semantic_matching_BERT import find_semantic_matches_scibert
from core.generate_report import generate_report

def main():
    # Get the lists of term names
    template_terms, user_terms = get_term_lists()
    
    # Get the dictionaries of term names and a piece of sample data
    template_terms_w_data, user_terms_w_data = get_terms_with_data()
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in template_terms]
    normalized_user_terms = [normalize(term) for term in user_terms]
    
    # Convert outputs to dictionaries if they are sets
    def convert_to_dict(output, default_value=None):
        if isinstance(output, set):
            return {item: default_value for item in output}
        return output
    
    # Normalized and Exact matching against template terms
    normalized_matches = convert_to_dict(normalized_match(normalized_template_terms, normalized_user_terms))
    exact_matches = convert_to_dict(exact_match(template_terms, user_terms))
    
    # Fuzzy matching against template terms
    fuzzy_matches = convert_to_dict(fuzzy_match(normalized_template_terms, normalized_user_terms), default_value=(None, 100))
    
    # Semantic matching using SpaCy against template terms
    semantic_matches_spacy = convert_to_dict(find_semantic_matches_spacy(normalized_user_terms, normalized_template_terms), default_value=(None, 0.0))
    
    # Semantic matching using SentenceBERT against template terms with descriptions
    # semantic_matches_sentencebert = find_semantic_matches_sentencebert(user_terms_w_data, template_terms_w_data)
    semantic_matches_scibert = find_semantic_matches_scibert(user_terms_w_data, template_terms_w_data)

    # Identify new terms by combining all match keys
    all_matches = set()
    for matches_dict in [normalized_matches, exact_matches, fuzzy_matches, semantic_matches_spacy, semantic_matches_scibert]:
        all_matches.update(matches_dict.keys())

    new_terms = [term for term in user_terms if term not in all_matches]
    print(f"New Terms: {new_terms}")
    
    # Generate report
    generate_report(semantic_matches_spacy, semantic_matches_scibert, new_terms, 'term_matching_report.csv', bert_threshold=0.35)

if __name__ == '__main__':
    main()