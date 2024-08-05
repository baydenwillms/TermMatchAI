'''
Performs semantic term matching using SentenceBERT AI model, a sentence vector based model
'''

from sentence_transformers import SentenceTransformer, util

# Load SentenceBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(term, model):
    return model.encode(term, convert_to_tensor=True)

def semantic_match_sentencebert(term, template_terms, model):
    term_embedding = get_embedding(term, model)
    similarities = {}
    for template_term in template_terms:
        template_embedding = get_embedding(template_term, model)
        similarity = util.pytorch_cos_sim(term_embedding, template_embedding).item()
        similarities[template_term] = similarity
    best_match = max(similarities, key=similarities.get)
    return best_match, similarities[best_match]

def find_semantic_matches_sentencebert(user_terms, template_terms):
    matches = {}
    for term in user_terms:
        match, score = semantic_match_sentencebert(term, template_terms, model)
        matches[term] = (match, score)
    return matches