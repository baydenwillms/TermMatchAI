import csv
from .normalization import normalize

def generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, output_file, user_terms_w_data, noaa_terms_w_data, bert_threshold=0.3, num_matches=5):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Perfect Matches Section
        writer.writerow(['Perfect Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example'])
        
        # Process exact matches first
        for user_term, template_term in exact_matches.items():
            user_data = str(user_terms_w_data.get(user_term, ''))
            template_data = str(noaa_terms_w_data.get(template_term, ''))
            writer.writerow([user_term, user_data, template_term, template_data])
        
        # Process normalized matches that aren't in exact matches
        for norm_user_term, norm_template_term in normalized_matches.items():
            if norm_user_term not in [normalize(term) for term in exact_matches]:
                user_term = next((term for term in user_terms_w_data if normalize(term) == norm_user_term), norm_user_term)
                template_term = next((term for term in noaa_terms_w_data if normalize(term) == norm_template_term), norm_template_term)
                user_data = str(user_terms_w_data.get(user_term, ''))
                template_data = str(noaa_terms_w_data.get(template_term, ''))
                writer.writerow([user_term, user_data, template_term, template_data])
        
        writer.writerow([])

        # AI Powered Matches Section
        writer.writerow(['AI Powered Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example', 'Score'])
        perfect_match_terms = set(exact_matches.keys()) | set(normalized_matches.keys())
        for term, matches in semantic_matches_scibert.items():
            if term not in perfect_match_terms:
                first_row = True
                for match, score, _, _ in matches[:num_matches]:
                    if score >= bert_threshold:
                        user_data = str(user_terms_w_data.get(term, ''))
                        template_data = str(noaa_terms_w_data.get(match, ''))
                        if first_row:
                            writer.writerow([term, user_data, match, template_data, score])
                            first_row = False
                        else:
                            writer.writerow(['', '', match, template_data, score])
        writer.writerow([])

        # Low-confidence Matches and New Terms Section
        writer.writerow(['Low-confidence Matches and New Terms'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example', 'Score'])
        for term, matches in semantic_matches_scibert.items():
            if matches[0][1] < bert_threshold and term not in perfect_match_terms:
                first_row = True
                for match, score, _, _ in matches[:num_matches]:
                    user_data = str(user_terms_w_data.get(term, ''))
                    template_data = str(noaa_terms_w_data.get(match, ''))
                    if first_row:
                        writer.writerow([term, user_data, match, template_data, score])
                        first_row = False
                    else:
                        writer.writerow(['', '', match, template_data, score])
        
        for term in new_terms:
            writer.writerow([term, str(user_terms_w_data.get(term, '')), '', '', ''])

        # Additional information for clarity
        writer.writerow([])
        writer.writerow(['Note: Scores indicate the similarity confidence. Higher scores imply better matches.'])