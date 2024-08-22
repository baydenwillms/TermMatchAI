import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses, models, datasets
from torch.utils.data import DataLoader
import os

# Function to create the dictionary from Darwin Core CSV
def build_darwincore_dict():
    SCRIPT_DEPENDENCIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'script_dependencies')
    excel_file_path = os.path.join(SCRIPT_DEPENDENCIES_DIR, 'term_versions_dwc.csv')
    
    df = pd.read_csv(excel_file_path, sep=',')
    
    terms_dict = {}
    for index, row in df.iterrows():
        term_name = row['term_localName']
        definition = row['definition'] if pd.notnull(row['definition']) else "No definition available"
        examples = row['examples'] if pd.notnull(row['examples']) else "No examples available"
        
        terms_dict[term_name] = {
            'definition': definition,
            'examples': examples
        }
    return terms_dict

# Function to train the SciBERT model with the desired dictionary
def train_scibert_with_data(terms_dict, output_dir='eDNA_scibert_model'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load SciBERT model
    word_embedding_model = models.Transformer('allenai/scibert_scivocab_uncased')
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    # Prepare training examples
    train_examples = []
    for term, data in terms_dict.items():
        examples = data.get('examples', '').strip()
        definition = data.get('definition', '').strip()
        
        if not examples and not definition:
            continue  # Skip terms without examples and definitions
        
        example_text = f"{term}: {definition}. Examples: {examples}"
        train_examples.append(InputExample(texts=[example_text, definition], label=0))

    if len(train_examples) == 0:
        print("No valid training examples were found. Training aborted.")
        return

    # Convert to DataLoader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)

    # Use MultipleNegativesRankingLoss
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # Train the model
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=4, warmup_steps=100)

    # Save the trained model
    for name, param in model.named_parameters():
        if not param.is_contiguous():
            param.data = param.data.contiguous()

    model.save(output_dir)
    print(f"Model trained and saved to {output_dir}")

darwincore_dict = build_darwincore_dict()
print("Successfully generated dictionary:")
print({k: darwincore_dict[k] for k in list(darwincore_dict)[:3]})

use_for_training = input("Use dictionary to train eDNA_scibert_model? (yes or no): ")
if use_for_training.lower() in ['yes', 'y']:
    train_scibert_with_data(darwincore_dict)
