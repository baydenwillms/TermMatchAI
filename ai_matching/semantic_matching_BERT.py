from sentence_transformers import SentenceTransformer, util

# Load SentenceBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text, model):
    return model.encode(text, convert_to_tensor=True)

def combine_term_and_data(term, data):
    return f"{term}: {data}"

def semantic_match_sentencebert(term, term_data, template_terms_with_data, model):
    combined_term = combine_term_and_data(term, term_data)
    term_embedding = get_embedding(combined_term, model)
    similarities = {}
    for template_term, template_data in template_terms_with_data.items():
        combined_template = combine_term_and_data(template_term, template_data)
        template_embedding = get_embedding(combined_template, model)
        similarity = util.pytorch_cos_sim(term_embedding, template_embedding).item()
        similarities[template_term] = similarity
    best_match = max(similarities, key=similarities.get)
    return best_match, similarities[best_match]

def find_semantic_matches_sentencebert(user_terms_with_data, template_terms_with_data):
    matches = {}
    for term, user_data in user_terms_with_data.items():
        match, score = semantic_match_sentencebert(term, user_data, template_terms_with_data, model)
        matched_data = template_terms_with_data.get(match, '')  # Get the data example from the matched term
        matches[term] = (match, score, user_data, matched_data)  # Return 4 elements
    return matches
