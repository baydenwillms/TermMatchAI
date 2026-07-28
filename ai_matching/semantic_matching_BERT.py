# from sentence_transformers import SentenceTransformer, util
from transformers import AutoModel, AutoTokenizer
import torch
from data_loading.data_loading import get_term_value, get_term_description


# Load SentenceBERT model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# New SciBERT model. BERT model pre-trained with Scientific papers, vocabulary
MODEL_NAME = 'allenai/scibert_scivocab_uncased'

# Use custom trained eDNA SciBERT model
# MODEL_NAME = './ai_matching/eDNA_scibert_model'

# Lazy-loaded so main.py can print prompts before the model download/load
_tokenizer = None
_model = None

MAX_LENGTH = 512
BATCH_SIZE = 16


def _get_model():
    global _tokenizer, _model
    if _model is None:
        print("Loading SciBERT model (first run may download weights)...", flush=True)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _model.eval()
        print("SciBERT ready.", flush=True)
    return _model, _tokenizer


# Old version of combine_term_and_data, accounts for when data example is 'None' to help avoid matching other terms with 'None'
# def combine_term_and_data(term, data):
#     return f"{term}: {data}"

# Build the text SciBERT embeds: field name + description + example value.
# Description is the main signal for meaning; value helps disambiguate similar fields.
def combine_term_and_data(term, entry):
    description = get_term_description(entry)
    value = get_term_value(entry)

    parts = [str(term)]
    if description:
        parts.append(str(description))
    if value is not None and value != '':
        parts.append(f"Example: {value}")
    return ". ".join(parts)


# Legacy code version: sentenceBERT AI model. We have since switched to SciBERT, which is trained in scientific vocabulary and journals

# def get_embedding(text, model):
#     return model.encode(text, convert_to_tensor=True)

# def semantic_match_sentencebert(term, term_data, template_terms_with_data, model):
#     combined_term = combine_term_and_data(term, term_data)
#     term_embedding = get_embedding(combined_term, model)
#     similarities = {}
#     for template_term, template_data in template_terms_with_data.items():
#         combined_template = combine_term_and_data(template_term, template_data)
#         template_embedding = get_embedding(combined_template, model)
#         similarity = util.pytorch_cos_sim(term_embedding, template_embedding).item()
#         similarities[template_term] = similarity
#     best_match = max(similarities, key=similarities.get)
#     return best_match, similarities[best_match]

# def find_semantic_matches_sentencebert(user_terms_with_data, template_terms_with_data):
#     matches = {}
#     for term, user_data in user_terms_with_data.items():
#         match, score = semantic_match_sentencebert(term, user_data, template_terms_with_data, model)
#         matched_data = template_terms_with_data.get(match, '')  # Get the data example from the matched term
#         matches[term] = (match, score, user_data, matched_data)  # Return 4 elements
#     return matches

def _mean_pool(last_hidden_state, attention_mask):
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def embed_texts(texts, model, tokenizer, batch_size=BATCH_SIZE):
    """Embed a list of strings in batches. Returns (N, hidden) tensor."""
    chunks = []
    total = len(texts)
    for start in range(0, total, batch_size):
        batch = texts[start:start + batch_size]
        inputs = tokenizer(
            batch,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
        )
        with torch.no_grad():
            outputs = model(**inputs)
            emb = _mean_pool(outputs.last_hidden_state, inputs['attention_mask'])
        chunks.append(emb)
        done = min(start + batch_size, total)
        print(f"  embedded {done}/{total}", flush=True)
    return torch.cat(chunks, dim=0)


def get_scibert_embedding(text, model, tokenizer):
    return embed_texts([text], model, tokenizer, batch_size=1)


def semantic_match_scibert(term, term_data, template_terms_with_data, model, tokenizer, num_matches=5):
    # Kept for compatibility; prefer find_semantic_matches_scibert (batched).
    combined_term = combine_term_and_data(term, term_data)
    term_embedding = get_scibert_embedding(combined_term, model, tokenizer)
    template_terms = list(template_terms_with_data.keys())
    template_texts = [combine_term_and_data(t, template_terms_with_data[t]) for t in template_terms]
    template_embeddings = embed_texts(template_texts, model, tokenizer)
    sims = torch.nn.functional.cosine_similarity(
        term_embedding, template_embeddings
    )
    top = torch.topk(sims, k=min(num_matches, len(template_terms)))
    return [(template_terms[i], sims[i].item()) for i in top.indices.tolist()]


# def find_semantic_matches_scibert(user_terms_with_data, template_terms_with_data, num_matches=5):
#     matches = {}
#     for term, user_data in user_terms_with_data.items():
#         top_matches = semantic_match_scibert(term, user_data, template_terms_with_data, model, tokenizer, num_matches)
#         matches[term] = [(match, score, user_data, template_terms_with_data.get(match, '')) for match, score in top_matches]
#     return matches

def find_semantic_matches_scibert(user_terms_with_data, template_terms_with_data, num_matches=5):
    """
    Semantic match user terms to FAIRe terms.
    Embeds each side once (batched), then uses a similarity matrix.
    Old pairwise approach re-ran SciBERT ~user_count * faire_count times and froze on large checklists.
    """
    model, tokenizer = _get_model()

    user_terms = list(user_terms_with_data.keys())
    template_terms = list(template_terms_with_data.keys())

    if not user_terms or not template_terms:
        return {}

    print(f"Semantic matching: {len(user_terms)} user terms x {len(template_terms)} FAIRe terms", flush=True)

    print("Embedding user terms...", flush=True)
    user_texts = [combine_term_and_data(t, user_terms_with_data[t]) for t in user_terms]
    user_emb = embed_texts(user_texts, model, tokenizer)

    print("Embedding FAIRe terms (once)...", flush=True)
    template_texts = [combine_term_and_data(t, template_terms_with_data[t]) for t in template_terms]
    template_emb = embed_texts(template_texts, model, tokenizer)

    print("Scoring similarities...", flush=True)
    # Normalize then matrix multiply => cosine similarity for all pairs
    user_norm = torch.nn.functional.normalize(user_emb, p=2, dim=1)
    template_norm = torch.nn.functional.normalize(template_emb, p=2, dim=1)
    # (num_user, num_template)
    sim_matrix = torch.mm(user_norm, template_norm.T)

    k = min(num_matches, len(template_terms))
    matches = {}
    for i, term in enumerate(user_terms):
        scores, indices = torch.topk(sim_matrix[i], k=k)
        user_data = user_terms_with_data[term]
        matches[term] = [
            (
                template_terms[j],
                scores[rank].item(),
                user_data,
                template_terms_with_data.get(template_terms[j], ''),
            )
            for rank, j in enumerate(indices.tolist())
        ]

    print("Semantic matching done.", flush=True)
    return matches
