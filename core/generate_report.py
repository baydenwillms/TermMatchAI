from core.id_checker import get_id_terms
from core.date_checker import get_date_terms
import csv
from core.normalization import normalize

def generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, output_file, user_terms_w_data, noaa_terms_w_data, bert_threshold=0.3, num_matches=5):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Perfect Matches Section
        writer.writerow(['Perfect Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example'])
        
		# Also this section seems unnecessarily repetetive and complex. will change soon
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

        # ID Terms Section
        writer.writerow(['ID Terms'])
        writer.writerow(['User Term', 'User Data Example', 'NOAA ID Term', 'NOAA Data Example'])

        user_id_terms, user_compound_key = get_id_terms(user_terms_w_data)
        print(f'user compound key: {user_compound_key}')
    
        noaa_id_terms, noaa_compound_key = get_id_terms(noaa_terms_w_data)
        print(f'NOAA compound key: {noaa_compound_key}')

        # Prepare items, putting compound key first for NOAA terms
        user_items = [(term, str(user_terms_w_data.get(term, ''))) for term in user_id_terms]
        noaa_items = []
        if noaa_compound_key:
            noaa_items.append((noaa_compound_key, str(noaa_terms_w_data.get(noaa_compound_key, ''))))
        noaa_items.extend([(term, str(noaa_terms_w_data.get(term, ''))) for term in noaa_id_terms if term != noaa_compound_key])

        # Calculate the max length to ensure we don't miss terms
        max_len = max(len(user_items), len(noaa_items))

        # Iterate and write each term side by side
        for i in range(max_len):
            user_term, user_data = user_items[i] if i < len(user_items) else ('', '')
            noaa_term, noaa_data = noaa_items[i] if i < len(noaa_items) else ('', '')
            writer.writerow([user_term, user_data, noaa_term, noaa_data])

        writer.writerow([])
        


		# Date / Time Terms Section
        writer.writerow(['Date and Time Terms'])
        writer.writerow(['User Term', 'User Data Example', 'NOAA Term', 'NOAA Data Example'])
		
        user_date_terms = get_date_terms(user_terms_w_data)
        noaa_date_terms = get_date_terms(noaa_terms_w_data)

		# Prepare items
        user_items = [(term, str(user_terms_w_data.get(term, ''))) for term in user_date_terms]
        noaa_items = [(term, str(noaa_terms_w_data.get(term, ''))) for term in noaa_date_terms]

		# Calculate the max length to ensure we don't miss terms
        max_len = max(len(user_items), len(noaa_items))

		# Iterate and write each term side by side
        for i in range(max_len):
            user_term, user_data = user_items[i] if i < len(user_items) else ('', '')
            noaa_term, noaa_data = noaa_items[i] if i < len(noaa_items) else ('', '')
            writer.writerow([user_term, user_data, noaa_term, noaa_data])

        writer.writerow([])



        # AI Powered Matches Section
        writer.writerow(['AI Powered Matches'])
        writer.writerow(['User Term', 'User Data Example', 'Matched Term', 'Matched Data Example', 'Score'])
        perfect_match_terms = set(exact_matches.keys()) | set(normalized_matches.keys())
        id_terms = set(user_id_terms) | set(noaa_id_terms)
        for term, matches in semantic_matches_scibert.items():
            if term not in perfect_match_terms and term not in id_terms:
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

		# I will probably remove this very soon
        # New Terms Section
        writer.writerow(['New Terms'])
        writer.writerow(['User Term', 'User Data Example'])
        for term in new_terms:
            if term not in id_terms:
                writer.writerow([term, str(user_terms_w_data.get(term, ''))])

        # Additional information for clarity
        writer.writerow([])
        writer.writerow(['Note: Scores indicate the similarity confidence. Higher scores imply better matches.'])

# Usage:
# generate_report(normalized_matches, exact_matches, semantic_matches_scibert, new_terms, 
#                 'term_matching_report.csv', user_terms_w_data, noaa_terms_w_data,
#                 bert_threshold=0.3, num_matches=5)