'''
Load term dictionaries for TermMatchAI.

Expected JSON format (one file per data standard):
{
  "field_name": {
    "value": "example data value",
    "description": "What this field means"
  }
}

Typical pair:
  inputs/FAIRe_standard.json     — FAIR eDNA data standard (match TO this)
  inputs/user_standard_example.json — your / another lab's standard (match FROM this)

Regenerate FAIR eDNA JSON after checklist updates:
  python data_loading/parse_faire_checklist.py
'''

import json
import os

# Default inputs shipped with the repo
INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs')
FAIRE_STANDARD_PATH = os.path.join(INPUTS_DIR, 'FAIRe_standard.json')
USER_STANDARD_EXAMPLE_PATH = os.path.join(INPUTS_DIR, 'user_standard_example.json')


def get_term_value(entry):
    """Return the example value from a term entry."""
    if isinstance(entry, dict):
        return entry.get('value')
    return entry


def get_term_description(entry):
    """Return the description from a term entry (empty string if missing)."""
    if isinstance(entry, dict):
        return entry.get('description') or ''
    return ''


def make_term_entry(value=None, description=''):
    """Build a term entry in the standard format."""
    return {
        'value': value,
        'description': description or ''
    }


def load_terms_json(path):
    """
    Load a terms JSON file.
    Returns dict: field_name -> {value, description}
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Normalize so every entry is {value, description}
    normalized = {}
    for term, entry in data.items():
        if isinstance(entry, dict) and ('value' in entry or 'description' in entry):
            normalized[term] = make_term_entry(
                value=entry.get('value'),
                description=entry.get('description', '')
            )
        else:
            # Plain "field": "value" fallback
            normalized[term] = make_term_entry(value=entry, description='')
    return normalized


def get_terms_with_data(faire_path=None, user_path=None):
    """
    Load FAIR eDNA (template) + user (incoming) term dictionaries from JSON.
    Defaults to inputs/FAIRe_standard.json and inputs/user_standard_example.json.
    """
    faire_path = faire_path or FAIRE_STANDARD_PATH
    user_path = user_path or USER_STANDARD_EXAMPLE_PATH
    return load_terms_json(faire_path), load_terms_json(user_path)
