"""
excel_loading.py - Module for creating dictionaries for TermMatchAI from Excel data templates

USAGE:
1. Prepare two Excel files:
   - Template file (e.g. NOAA terms)
   - Your data template file (your terms to match)

2. Each Excel file should have:
   - A column for term names
   - (HIGHLY RECOMMENDED) Columns containing example data for each term
   
3. Call load_from_excel() with:
   - Path to template Excel
   - Path to your data Excel  
   - Row number containing terms
   - include_examples flag (DEFAULT TRUE AND HIGHLY RECOMMENDED)
"""

import pandas as pd

def load_from_excel(template_path, data_path, terms_row, include_examples=True):
    """
    Load terms and their example data from Excel files.
    
    Args:
        template_path (str): Path to template Excel file
        data_path (str): Path to data Excel file
        terms_row (int): Row number containing the terms (1-based indexing)
        include_examples (bool): Whether to include example data (HIGHLY RECOMMENDED)
        
    Returns:
        tuple: (template_terms_dict, user_terms_dict) where each dict maps terms to their example data
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
            # For template terms, get all data below each term
            for term in template_terms:
                col_idx = template_df.iloc[terms_row].eq(term).idxmax()
                examples = template_df.iloc[terms_row+1:][col_idx].dropna().tolist()
                template_terms_dict[term] = examples
                
            # For user terms, get all data below each term    
            for term in user_terms:
                col_idx = data_df.iloc[terms_row].eq(term).idxmax()
                examples = data_df.iloc[terms_row+1:][col_idx].dropna().tolist()
                user_terms_dict[term] = examples
        else:
            # If not including examples, just store empty lists
            template_terms_dict = {term: [] for term in template_terms}
            user_terms_dict = {term: [] for term in user_terms}
            
        return template_terms_dict, user_terms_dict
        
    except Exception as e:
        print(f"Error loading Excel files: {str(e)}")
        raise