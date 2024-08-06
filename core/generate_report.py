import csv

def generate_report(normalized_matches, exact_matches, fuzzy_matches, semantic_matches_spacy, semantic_matches_sentencebert, new_terms, output_file):
    """
    Generate a report summarizing the term matches and new terms.
    Args:
        normalized_matches (dict): Dictionary of normalized matches.
        exact_matches (dict): Dictionary of exact matches.
        fuzzy_matches (dict): Dictionary of fuzzy matches.
        semantic_matches_spacy (dict): Dictionary of semantic matches using SpaCy.
        semantic_matches_sentencebert (dict): Dictionary of semantic matches using SentenceBERT.
        new_terms (list): List of new terms.
        output_file (str): Path to the output CSV file.
    """
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers, rearranging so matches and scores are last
        writer.writerow([
            'User Term',
            'Exact Match', 
            'Normalized Match', 
            'Fuzzy Match', 
            'Fuzzy Score', 
            'SpaCy Semantic Match', 
            'SpaCy Score', 
            'SentenceBERT Semantic Match', 
            'SentenceBERT Score'
        ])

        # Collect all terms from various match types
        all_user_terms = set(normalized_matches.keys()).union(
            exact_matches.keys(),
            fuzzy_matches.keys(),
            semantic_matches_spacy.keys(),
            semantic_matches_sentencebert.keys()
        )

        # Iterate through each term to compile their respective match information
        for term in all_user_terms:
            exact_match = exact_matches.get(term, '')
            normalized_match = normalized_matches.get(term, '')
            fuzzy_match, fuzzy_score = fuzzy_matches.get(term, (None, None))
            spacy_match, spacy_score = semantic_matches_spacy.get(term, (None, None))
            sentencebert_match, sentencebert_score = semantic_matches_sentencebert.get(term, (None, None))
            
            # Write each term's information as a new row in the CSV
            writer.writerow([
                term, 
                exact_match, 
                normalized_match, 
                fuzzy_match, 
                fuzzy_score, 
                spacy_match, 
                spacy_score, 
                sentencebert_match, 
                sentencebert_score
            ])

        # Write a new section for new terms
        writer.writerow([])
        writer.writerow(['New Terms'])
        for term in new_terms:
            writer.writerow([term])

