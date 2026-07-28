# from sentence_transformers import SentenceTransformer, util
from sentence_transformers import SentenceTransformer
import hashlib
import os
import re
import torch
from data_loading.data_loading import get_term_value, get_term_description


# Load SentenceBERT model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# Proper sentence-embedding model (contrastive ST). Mean-pooled SciBERT is a language model,
# not a similarity model — that made near-identical descriptions rank below shared "*id" names.
MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'

# Previous SciBERT encoder (kept for reference; weak for description matching)
# MODEL_NAME = 'allenai/scibert_scivocab_uncased'

# Use custom trained eDNA SciBERT model
# MODEL_NAME = './ai_matching/eDNA_scibert_model'

# Lazy-loaded so main.py can print prompts before the model download/load
_model = None

BATCH_SIZE = 32

# Descriptions dominate. Name tokens are only a light tie-breaker (and ignore generic id/name noise).
WEIGHT_DESCRIPTION = 0.9
WEIGHT_NAME = 0.1

# Generic abbreviation expansions for field-name token matching (any metadata standard).
# Note: do NOT map id -> identifier here; both are treated as stopwords below.
_NAME_ABBREVS = {
    'samp': 'sample',
    'temp': 'temperature',
    'lat': 'latitude',
    'lon': 'longitude',
    'long': 'longitude',
    'lng': 'longitude',
    'env': 'environment',
    'vol': 'volume',
    'conc': 'concentration',
    'num': 'number',
    'qty': 'quantity',
    'desc': 'description',
    'loc': 'location',
    'geo': 'geographic',
    'elev': 'elevation',
    'alt': 'altitude',
    'dur': 'duration',
    'meth': 'method',
    'mat': 'material',
    'org': 'organism',
    'biol': 'biological',
    'chem': 'chemical',
    'seq': 'sequence',
    'nucl': 'nucleic',
    'ext': 'extraction',
    'amp': 'amplification',
    'rep': 'replicate',
    'cont': 'control',
    'pos': 'positive',
    'neg': 'negative',
    'fwd': 'forward',
    'rev': 'reverse',
    'primer': 'primer',
    'lib': 'library',
    'run': 'run',
    'proj': 'project',
    'inst': 'institution',
    'depth': 'depth',
    'ph': 'ph',
}

# Tokens that appear on almost every key/ID field — sharing them must NOT boost the score.
_NAME_STOPWORDS = {
    'id', 'identifier', 'identifiers', 'name', 'names', 'code', 'codes',
    'value', 'values', 'type', 'types', 'num', 'number', 'no', 'flag',
    'label', 'labels', 'info', 'data', 'field', 'fields', 'key', 'keys',
    'the', 'a', 'an', 'of', 'for', 'to', 'and', 'or', 'in', 'on', 'by',
}


def _get_model(quiet=False):
    global _model
    if _model is None:
        if not quiet:
            print(
                "Loading sentence embedding model (all-mpnet-base-v2) for description matching. "
                "First time only: downloads from HuggingFace and caches on disk.",
                flush=True,
            )
        _model = SentenceTransformer(MODEL_NAME)
        if not quiet:
            print("Model ready.", flush=True)
    return _model


def humanize_field_name(term):
    """sample_id / decimalLatitude -> 'sample id' / 'decimal latitude'."""
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', str(term))
    s = s.replace('_', ' ').replace('-', ' ')
    return re.sub(r'\s+', ' ', s).strip().lower()


def field_name_tokens(term):
    """Content tokens only (abbrevs expanded; generic id/name/code tokens dropped)."""
    tokens = set()
    for raw in humanize_field_name(term).split():
        if raw in _NAME_STOPWORDS:
            continue
        tokens.add(raw)
        expanded = _NAME_ABBREVS.get(raw)
        if expanded and expanded not in _NAME_STOPWORDS:
            tokens.add(expanded)
    return tokens


def name_similarity(term_a, term_b):
    """Dice coefficient on content name tokens (0-1). Returns 0 if either side has no content tokens."""
    a = field_name_tokens(term_a)
    b = field_name_tokens(term_b)
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return (2.0 * inter) / (len(a) + len(b))


# Old version of combine_term_and_data, accounts for when data example is 'None' to help avoid matching other terms with 'None'
# def combine_term_and_data(term, data):
#     return f"{term}: {data}"

def description_text(term, entry):
    """
    Text embedded for meaning: the field description alone.
    Field names and example values are NOT included (names share noisy tokens like 'id';
    examples make unrelated ID fields look alike).
    """
    description = (get_term_description(entry) or '').strip()
    if description:
        return description
    # Fallback only when a description is missing
    return f"Metadata field: {humanize_field_name(term)}"


# Kept for any callers that still expect the old combine helper
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


def _cache_dir():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, '.cache', 'embeddings')
    os.makedirs(path, exist_ok=True)
    return path


def _texts_cache_path(label, texts):
    h = hashlib.sha256()
    h.update(MODEL_NAME.encode('utf-8'))
    h.update(b'\0')
    h.update(label.encode('utf-8'))
    for t in texts:
        h.update(t.encode('utf-8'))
        h.update(b'\n')
    return os.path.join(_cache_dir(), h.hexdigest() + '.pt')


def embed_texts(texts, model, label='texts', use_cache=False, quiet=False):
    """Embed strings with sentence-transformers. Optionally cache by content hash."""
    if not texts:
        return torch.empty((0, 0))

    cache_path = _texts_cache_path(label, texts) if use_cache else None
    if cache_path and os.path.isfile(cache_path):
        if not quiet:
            print(f"  using cached embeddings ({label}, {len(texts)} texts)", flush=True)
        return torch.load(cache_path, map_location='cpu')

    if not quiet:
        print(f"  embedding {len(texts)} texts ({label})...", flush=True)
    emb = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        convert_to_tensor=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    if cache_path:
        torch.save(emb, cache_path)
        if not quiet:
            print(f"  cached embeddings -> {cache_path}", flush=True)
    return emb


def find_semantic_matches_scibert(
    user_terms_with_data, template_terms_with_data, num_matches=5, quiet=False
):
    """
    Semantic match: embed field descriptions with a sentence-transformer, lightly blend
    contentful field-name token overlap (ignoring generic id/name/code tokens).
    Template embeddings are cached on disk so re-runs against the same standard are fast.
    """
    model = _get_model(quiet=quiet)

    user_terms = list(user_terms_with_data.keys())
    template_terms = list(template_terms_with_data.keys())

    if not user_terms or not template_terms:
        return {}

    if not quiet:
        print(
            f"Semantic matching: {len(user_terms)} user fields x {len(template_terms)} template fields "
            f"(score = {int(WEIGHT_DESCRIPTION * 100)}% description + {int(WEIGHT_NAME * 100)}% name tokens)",
            flush=True,
        )

    user_texts = [description_text(t, user_terms_with_data[t]) for t in user_terms]
    template_texts = [description_text(t, template_terms_with_data[t]) for t in template_terms]

    # User side is usually small / changes often; template (e.g. FAIRe) is large and stable -> cache
    user_emb = embed_texts(user_texts, model, label='user', use_cache=False, quiet=quiet)
    template_emb = embed_texts(
        template_texts, model, label='template', use_cache=True, quiet=quiet
    )

    if not quiet:
        print("Scoring (description cosine + content name tokens)...", flush=True)
    # encode(..., normalize_embeddings=True) => cosine = dot product
    desc_sim = torch.mm(user_emb, template_emb.T)

    # Name token similarity matrix (CPU, cheap)
    name_sims = torch.zeros((len(user_terms), len(template_terms)), dtype=desc_sim.dtype)
    for i, ut in enumerate(user_terms):
        for j, tt in enumerate(template_terms):
            name_sims[i, j] = name_similarity(ut, tt)

    if name_sims.device != desc_sim.device:
        name_sims = name_sims.to(desc_sim.device)

    sim_matrix = (WEIGHT_DESCRIPTION * desc_sim) + (WEIGHT_NAME * name_sims)

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

    if not quiet:
        print("Semantic matching done.", flush=True)
    return matches
