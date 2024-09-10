from core.data_loading import get_term_lists, get_terms_with_data
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
from ai_matching.semantic_matching_BERT import find_semantic_matches_scibert
from core.generate_report import generate_report

def main():
    # Get user input for number of matches
    while True:
        try:
            num_matches = int(input("Enter the number of matches to display per term (1-5): "))
            if 1 <= num_matches <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get the dictionaries of term names and a piece of sample data
    template_terms_w_data, user_terms_w_data = get_terms_with_data()
    
    # Get the lists of term names
    template_terms = list(template_terms_w_data.keys())
    user_terms = list(user_terms_w_data.keys())
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in template_terms]
    normalized_user_terms = [normalize(term) for term in user_terms]
    
    # Normalized and Exact matching against template terms
    normalized_matches = normalized_match(normalized_template_terms, normalized_user_terms)
    exact_matches = exact_match(template_terms, user_terms)
    
    # Fuzzy matching against template terms
    fuzzy_matches = fuzzy_match(normalized_template_terms, normalized_user_terms)
    
    # Semantic matching using SpaCy against template terms
    semantic_matches_spacy = find_semantic_matches_spacy(normalized_user_terms, normalized_template_terms)
    
    # Semantic matching using SciBERT against template terms with descriptions
    semantic_matches_scibert = find_semantic_matches_scibert(user_terms_w_data, template_terms_w_data)

    # Identify new terms by combining all match keys
    all_matches = set()
    for matches_dict in [normalized_matches, exact_matches, fuzzy_matches, semantic_matches_spacy, semantic_matches_scibert]:
        all_matches.update(matches_dict.keys())

    new_terms = [term for term in user_terms if term not in all_matches]
    print(f"New Terms: {new_terms}")
    
    # Generate report
    generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, 
                    'term_matching_report.csv', user_terms_w_data, template_terms_w_data,
                    bert_threshold=0.3, num_matches=num_matches)

if __name__ == '__main__':
    main()