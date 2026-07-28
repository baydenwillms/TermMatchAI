from data_loading.data_loading import (
    get_terms_with_data,
    FAIRE_STANDARD_PATH,
    USER_STANDARD_EXAMPLE_PATH,
)
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
# from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
from ai_matching.semantic_matching_BERT import find_semantic_matches_scibert
from core.generate_report import generate_report
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

    # FAIRe = standard you match TO. User file = your lab's standard to map FROM.
    print()
    print("TermMatchAI maps YOUR data standard onto the FAIRe eDNA standard.")
    print("  1) FAIRe JSON   (match TO)   default: inputs/FAIRe_standard.json")
    print("  2) Your JSON    (match FROM) default: inputs/user_standard_example.json")
    print()
    print(f"Default FAIRe: {FAIRE_STANDARD_PATH}")
    print(f"Default user:  {USER_STANDARD_EXAMPLE_PATH}")
    faire_path = input("Path to FAIRe JSON (ENTER for default): ").strip()
    user_path = input("Path to YOUR standard JSON (ENTER for example): ").strip()

    if not faire_path and not user_path:
        print("Using inputs/FAIRe_standard.json and inputs/user_standard_example.json")
        template_terms_w_data, user_terms_w_data = get_terms_with_data()
    else:
        template_terms_w_data, user_terms_w_data = get_terms_with_data(
            faire_path=faire_path or FAIRE_STANDARD_PATH,
            user_path=user_path or USER_STANDARD_EXAMPLE_PATH
        )
    
    # Get the lists of term names
    template_terms = list(template_terms_w_data.keys())
    user_terms = list(user_terms_w_data.keys())
    
    # DATE / TIME TERMS SECTION 
    # Identify DATE terms
    user_date_terms = get_date_terms(user_terms_w_data)
    noaa_date_terms = get_date_terms(template_terms_w_data)
    
    # Remove DATE terms from consideration for other matching methods
    remaining_user_terms = {term: data for term, data in user_terms_w_data.items() if term not in user_date_terms}
    remaining_template_terms = {term: data for term, data in template_terms_w_data.items() if term not in noaa_date_terms}
    
    # Exact matching against template terms
    print("Running exact matching...", flush=True)
    exact_matches = exact_match(list(remaining_template_terms.keys()), list(remaining_user_terms.keys()))
    
    # Remove exact matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if term not in exact_matches}
    
    # Normalize terms
    normalized_template_terms = [normalize(term) for term in remaining_template_terms.keys()]
    normalized_user_terms = [normalize(term) for term in remaining_user_terms.keys()]
    
    # Normalized matching against template terms
    print("Running normalized matching...", flush=True)
    normalized_matches = normalized_match(normalized_template_terms, normalized_user_terms)
    
    # Remove normalized matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if normalize(term) not in normalized_matches}
    
    # Fuzzy matching against template terms
    print("Running fuzzy matching...", flush=True)
    fuzzy_matches = fuzzy_match(normalized_template_terms, [normalize(term) for term in remaining_user_terms])
    
    # Remove fuzzy matched terms from further consideration
    remaining_user_terms = {term: data for term, data in remaining_user_terms.items() 
                            if normalize(term) not in fuzzy_matches}
    
    # Semantic matching using SciBERT (field name + description + example value)
    print("Running semantic (SciBERT) matching...", flush=True)
    semantic_matches_scibert = find_semantic_matches_scibert(
        remaining_user_terms, remaining_template_terms, num_matches=num_matches
    )

    # Identify new terms
    new_terms = list(remaining_user_terms.keys())
    
    # Generate report
    print("Writing report...", flush=True)
    generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, 
                    'term_matching_report.csv', user_terms_w_data, template_terms_w_data,
                    bert_threshold=0.3, num_matches=num_matches)
    print("Done. Wrote term_matching_report.csv", flush=True)

if __name__ == '__main__':
    main()
