import csv

def generate_report(semantic_matches_spacy, semantic_matches_sentencebert, new_terms, output_file, bert_threshold=0.35):
    """
    Generate a report summarizing the term matches and new terms.
    Args:
        semantic_matches_spacy (dict): Dictionary of semantic matches using SpaCy.
        semantic_matches_sentencebert (dict): Dictionary of semantic matches using SentenceBERT.
        new_terms (list): List of new terms.
        output_file (str): Path to the output CSV file.
        bert_threshold (float): Minimum BERT score to consider a match as confident.
    """
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write header for the main matches section
        writer.writerow(['Main Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example', 'Score'])

        # Exact matches (SpaCy score of 1.0)
        for term, (match, score) in semantic_matches_spacy.items():
            if score == 1.0:
                bert_match = semantic_matches_sentencebert.get(term, (match, score, '', ''))
                user_data = bert_match[2]
                matched_data = bert_match[3]
                writer.writerow([term, user_data, match, matched_data, score])
        
        # Confident BERT matches (above the threshold)
        for term, (match, score, user_data, matched_data) in semantic_matches_sentencebert.items():
            if score >= bert_threshold:
                writer.writerow([term, user_data, match, matched_data, score])

        # Low-confidence matches (below the threshold)
        writer.writerow([])
        writer.writerow(['Low-Confidence Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example', 'Score'])
        
        for term, (match, score, user_data, matched_data) in semantic_matches_sentencebert.items():
            if score < bert_threshold:
                writer.writerow([term, user_data, match, matched_data, score])

        # New terms section
        writer.writerow([])
        writer.writerow(['New Terms'])
        for term in new_terms:
            writer.writerow([term])

        # Additional information for clarity
        writer.writerow([])
        writer.writerow(['Note: Scores indicate the similarity confidence. Higher scores imply better matches.'])