"""
excel_loading.py - Legacy Excel loader (name + example values only).

Prefer the FAIR eDNA checklist parser or a custom parser that writes:
  field_name -> { "value": ..., "description": "..." }

See inputs/ and data_loading/parse_faire_checklist.py.
"""

import pandas as pd
from data_loading.data_loading import make_term_entry

def load_from_excel(template_path, data_path, terms_row, include_examples=True):
    """
    Load terms and example values from Excel files (no descriptions).

    Args:
        template_path (str): Path to template Excel file
        data_path (str): Path to data Excel file
        terms_row (int): Row number containing the terms (1-based indexing)
        include_examples (bool): Whether to include example data (HIGHLY RECOMMENDED)

    Returns:
        tuple: (template_terms_dict, user_terms_dict) in standard
               field_name -> {value, description} format (description empty)
    """
    if not include_examples:
        print("""
        WARNING: You have chosen not to include example data.
        This will SIGNIFICANTLY reduce matching accuracy!
        It is HIGHLY RECOMMENDED to include example data.
        """)

    # Convert to 0-based indexing
    terms_row = terms_row - 1
    
    try:
        # Load both Excel files
        template_df = pd.read_excel(template_path)
        data_df = pd.read_excel(data_path)
        
        # Get terms from specified row
        template_terms = template_df.iloc[terms_row].dropna().tolist()
        user_terms = data_df.iloc[terms_row].dropna().tolist()
        
        template_terms_dict = {}
        user_terms_dict = {}
        
        if include_examples:
            # For template terms, use the first non-empty example below each term
            for term in template_terms:
                col_idx = template_df.iloc[terms_row].eq(term).idxmax()
                examples = template_df.iloc[terms_row+1:][col_idx].dropna().tolist()
                value = examples[0] if examples else None
                template_terms_dict[term] = make_term_entry(value=value, description='')
                
            # For user terms, use the first non-empty example below each term
            for term in user_terms:
                col_idx = data_df.iloc[terms_row].eq(term).idxmax()
                examples = data_df.iloc[terms_row+1:][col_idx].dropna().tolist()
                value = examples[0] if examples else None
                user_terms_dict[term] = make_term_entry(value=value, description='')
        else:
            template_terms_dict = {term: make_term_entry() for term in template_terms}
            user_terms_dict = {term: make_term_entry() for term in user_terms}
            
        return template_terms_dict, user_terms_dict
        
    except Exception as e:
        print(f"Error loading Excel files: {str(e)}")
        raise
