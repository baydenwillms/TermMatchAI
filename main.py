from data_loading.data_loading import get_terms_with_data
from data_loading.excel_loading import load_from_excel
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
# from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
from ai_matching.semantic_matching_BERT import find_semantic_matches_scibert
from core.generate_report import generate_report
from core.id_checker import get_id_terms
from core.date_checker import get_date_terms

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

    # Ask for Excel paths or use defaults
    template_path = input("Enter path to template Excel file (or press ENTER to use default dictionaries): ").strip()
    
    if template_path:
        # Excel file mode
        data_path = input("Enter path to your data Excel file: ").strip()
        row_num = int(input("Which row contains the term names? "))
        include_data = input("Include data examples for each term? This is HIGHLY RECOMMENDED (y/n): ").lower()
        
        if include_data == 'y' or 'yes':
            template_terms_w_data, user_terms_w_data = load_from_excel(template_path, data_path, row_num, include_examples=True)
        else:
            print("Warning: Matching accuracy will be reduced without data examples!")
            template_terms_w_data, user_terms_w_data = load_from_excel(template_path, data_path, row_num, include_examples=False)
    else:
        # Default dictionary mode
        print("Using default dictionaries from data_loading.py")
        template_terms_w_data, user_terms_w_data = get_terms_with_data()
    
    # Get the lists of term names
    template_terms = list(template_terms_w_data.keys())
    user_terms = list(user_terms_w_data.keys())
    
    # ID TERMS SECTION 
    # Identify ID terms
    user_id_terms, _ = get_id_terms(user_terms_w_data)
    noaa_id_terms, _ = get_id_terms(template_terms_w_data)
    
    # Remove ID terms from consideration for other matching methods
    remaining_user_terms = {term: data for term, data in user_terms_w_data.items() if term not in user_id_terms}
    remaining_template_terms = {term: data for term, data in template_terms_w_data.items() if term not in noaa_id_terms}
    
    # DATE / TIME TERMS SECTION 
    # Identify DATE terms
    user_date_terms = get_date_terms(user_terms_w_data)
    noaa_date_terms = get_date_terms(template_terms_w_data)
    
    # Remove DATE terms from consideration for other matching methods
    remaining_user_terms = {term: data for term, data in user_terms_w_data.items() if term not in user_date_terms}
    remaining_template_terms = {term: data for term, data in template_terms_w_data.items() if term not in noaa_date_terms}
    
    # Exact matching against template terms
    exact_matches = exact_match(list(remaining_template_terms.keys()), list(remaining_user_terms.keys()))
    
    # Remove exact matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if term not in exact_matches}
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in remaining_template_terms.keys()]
    normalized_user_terms = [normalize(term) for term in remaining_user_terms.keys()]
    
    # Normalized matching against template terms
    normalized_matches = normalized_match(normalized_template_terms, normalized_user_terms)
    
    # Remove normalized matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if normalize(term) not in normalized_matches}
    
    # Fuzzy matching against template terms
    fuzzy_matches = fuzzy_match(normalized_template_terms, [normalize(term) for term in remaining_user_terms])
    
    # Remove fuzzy matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if normalize(term) not in fuzzy_matches}
    
    # Semantic matching using SciBERT against template terms with descriptions
    semantic_matches_scibert = find_semantic_matches_scibert(remaining_user_terms, remaining_template_terms)

    # Identify new terms
    new_terms = list(remaining_user_terms.keys())
    
    # Generate report
    generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, 
                    'term_matching_report.csv', user_terms_w_data, template_terms_w_data,
                    bert_threshold=0.3, num_matches=num_matches)

if __name__ == '__main__':
    main()