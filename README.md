# TermMatchAI

TermMatchAI is a library designed to match terms between two datasets using exact syntactical matching, fuzzy search matching, and semantic matching with 2 AI models. It is specifically tailored for comparing eDNA data templates.

This repository is under active development, please raise an issue or reach out to bayden.willms@noaa.gov

## Setup

### Conda Environment

To set up the conda environment:
```bash
conda env create -f environment.yml
conda activate term-matching-env
```

### Installing AI Models

#### SpaCy Model
After setting up the conda environment, download the SpaCy model:
```bash
python -m spacy download en_core_web_md
```

#### Word2Vec Model
Download the pre-trained Word2Vec model:
- Go to [Google's pre-trained word2vec model](https://code.google.com/archive/p/word2vec/)
- Download the `GoogleNews-vectors-negative300.bin.gz` file
- Place the downloaded model in the `ai_matching/models/` directory

### Running the Script
- Instructions will be added here.