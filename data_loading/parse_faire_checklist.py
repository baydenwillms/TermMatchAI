"""
Parse the FAIR eDNA checklist Excel into TermMatchAI JSON.

Checklist layout (stable; new terms may be appended at the bottom):
  Column C — term_name
  Column D — description
  Column L — example

Usage:
  python data_loading/parse_faire_checklist.py
  python data_loading/parse_faire_checklist.py path/to/FAIRe_checklist.xlsx
"""

import json
import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CHECKLIST_PATH = os.path.join(
    REPO_ROOT, 'script_dependencies', 'FAIRe_checklist_v1.0.2.xlsx'
)
DEFAULT_OUTPUT_PATH = os.path.join(REPO_ROOT, 'inputs', 'FAIRe_standard.json')

# 0-based column indexes matching Excel C, D, L
COL_TERM = 2
COL_DESCRIPTION = 3
COL_EXAMPLE = 11


def make_term_entry(value=None, description=''):
    return {
        'value': value,
        'description': description or ''
    }


def _json_safe(value):
    """Convert pandas/numpy values into plain JSON types."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if hasattr(value, 'item') and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def parse_faire_checklist(checklist_path):
    """
    Read the FAIR eDNA checklist and return field_name -> {value, description}.
    Skips rows with no term_name. Empty examples become null.
    """
    # Terms live on the 'checklist' sheet (not the README sheet)
    df = pd.read_excel(checklist_path, sheet_name='checklist', header=0)

    # Prefer header names if present; fall back to column positions C/D/L
    columns = [str(c).strip().lower() for c in df.columns]
    if 'term_name' in columns:
        term_col = df.columns[columns.index('term_name')]
        desc_col = df.columns[columns.index('description')] if 'description' in columns else df.columns[COL_DESCRIPTION]
        example_col = None
        for name in ('example', 'examples', 'example_value'):
            if name in columns:
                example_col = df.columns[columns.index(name)]
                break
        if example_col is None:
            example_col = df.columns[COL_EXAMPLE]
    else:
        term_col = df.columns[COL_TERM]
        desc_col = df.columns[COL_DESCRIPTION]
        example_col = df.columns[COL_EXAMPLE]

    terms = {}
    for _, row in df.iterrows():
        term = row[term_col]
        if pd.isna(term) or str(term).strip() == '':
            continue

        term = str(term).strip()
        description = row[desc_col]
        example = row[example_col]

        if pd.isna(description):
            description = ''
        else:
            description = str(description).strip()

        if pd.isna(example):
            value = None
        else:
            value = _json_safe(example)
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    value = None

        terms[term] = make_term_entry(value=value, description=description)

    return terms


def write_faire_json(terms, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(terms, f, indent=2, ensure_ascii=False)
        f.write('\n')


def main():
    checklist_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHECKLIST_PATH
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_PATH

    if not os.path.isfile(checklist_path):
        raise FileNotFoundError(f"FAIR eDNA checklist not found: {checklist_path}")

    terms = parse_faire_checklist(checklist_path)
    write_faire_json(terms, output_path)
    print(f"Wrote {len(terms)} FAIR eDNA terms to {output_path}")


if __name__ == '__main__':
    main()
