"""
Normalize the term by converting to lowercase, replacing underscores and hyphens
with spaces, and removing any non-alphanumeric characters except spaces.
"""

import re

def normalize(term):
    # Convert to lowercase
    term = term.lower()
    # Replace underscores and hyphens with spaces
    term = term.replace('_', ' ').replace('-', ' ')
    # Remove non-alphanumeric characters except spaces
    term = re.sub(r'[^a-z0-9\s]', '', term)
    # Remove extra spaces
    term = ' '.join(term.split())
    return term