# TermMatchAI

TermMatchAI is a library designed to match terms between two datasets using exact syntactical matching, fuzzy search matching, and semantic matching with AI models.

What is the use case?
- Data is much less useful if you are unable to compare data between different datasets. __For example:__ my lab measures the general sampling environment with term name of 'habitat', with data like: 'oceanic mesopelagic zone biome', and another lab uses the term name 'env_local_scale' with data like: 'marine photic zone [ENVO:00000209]'. TermMatchAI will tell you that they are the closest match to one another.
- Matching methods: exact name, normalized name, fuzzy name similarity, then semantic (SciBERT) using field descriptions plus field-name tokens.

After a run, open `term_matching_report.html` in a browser (it should open automatically).

The project uses a custom trained version of [SciBERT](#citations). SciBERT is a SentenceBERT AI model that is trained on scientific vocabulary and data. __Custom training of this model is coming soon.__

<!-- The model used in this repo, [eDNA_scibert_model](#Training-the-AI-Model), is SciBERT with custom training from eDNA repositories such as DarwinCore and MIMARKS MIXs. -->

This project is under active development. Please raise an issue or reach out to bayden.willms@noaa.gov for any questions.

## Setup

### 1. Clone the Repository
First, clone the repository:
```bash
git clone https://github.com/baydenwillms/TermMatchAI.git
cd TermMatchAI
```

### 2. Conda Environment
Environment configuration is up to the user. Dependencies are listed in the `environment.yml`. To set up the environment using Conda (__you must have pip installed__):

```bash
conda env create -f environment.yml
conda activate term-matching-env
```

### 3. Configure Git Large File Storage (Handles AI Model installation)
<!-- Spacy Installation:
```bash
python -m spacy download en_core_web_lg
``` -->
- AI model is managed using Git LFS, Large File Storage. __LFS only needs to be configured/installed once.__
- Please note: your workplace's network may block Huggingface.io, which is how the SciBERT AI model is installed. __It's worth noting that the AI model does not communicate with the internet once installed.__
#### Windows
```bash
git lfs install
git lfs pull
```
#### macOS (Homebrew)
```bash
brew install git-lfs
```
#### macOS (MacPorts)
```bash
sudo port install git-lfs
```
#### dnf (Fedora)
```bash
sudo dnf install git-lfs
```
## Usage

### What you need
Two JSON files. Defaults live in `inputs/`. `main.py` will ask for paths (hit ENTER to use the defaults).

| File | What it is |
|------|------------|
| `inputs/FAIRe_standard.json` | The FAIRe eDNA standard. This is what everything gets mapped **to**. |
| `inputs/user_standard_example.json` | An example mapping of a fake data standard for trying the tool. Parse your data standard into the JSON format below to compare against the FAIR eDNA data standard. |

The report answers: *how does the user's data standard map onto FAIRe?*

Each field in those JSON files looks like:
```json
{
  "habitat": {
    "value": "oceanic mesopelagic zone biome",
    "description": "Local-scale environment where the sample was collected."
  }
}
```

`value` is one example data point. `description` is what the field means (this helps the AI matching a lot).

### Build / refresh the FAIRe JSON
The source file is `script_dependencies/FAIRe_checklist_v1.0.2.xlsx` (sheet `checklist`: column C = term name, D = description, L = example).

```bash
python data_loading/parse_faire_checklist.py
```

That rewrites `inputs/FAIRe_standard.json`. Run it again if the checklist gets new terms.

### Your own standard
Same JSON shape: `{ "field": { "value": ..., "description": "..." } }`. Write a small parser for your Excel/YAML/whatever, or edit by hand. Drop the file in `inputs/` or pass the path when `main.py` asks.

The shipped `user_standard_example.json` is a larger fake lab template so you can smoke-test matching:
- some names match FAIRe exactly (`temp`, `salinity`, `ph`, `country`)
- many are close but differently named (`sample_id`, `habitat`, `collection_gear`, `filter_pore_um`, ...)
- one is lab-only junk that should not map cleanly (`lab_internal_batch`)

### Run matching
```bash
python main.py
```
1. How many FAIRe matches to show per user term (1-5)
2. Paths to the two JSONs, or ENTER for the defaults above
3. Browser opens `term_matching_report.html` (summary table + field-by-field candidates)

Semantic matching embeds **descriptions** (example values are not used in the AI score), then blends that with field-name token overlap. Template embeddings are cached under `.cache/embeddings/` so re-runs against the same FAIRe JSON are much faster. The first run still downloads SciBERT once from HuggingFace into your local cache.

### Training the AI Model
__Currently under development, this is how I was training the model previously. Barely improved results__

Our custom eDNA SciBERT model is located in `ai_matching/eDNA_scibert_model/`
These are mostly binary files that are unreadable, and you shouldn't directly modify. Instead, it is trained using the `ai_matching/eDNA_model_trainer.py` script. You will probably have to write a short function to get your training data into the right dictionary format. I suggest looking at the dictionary-building functions already in there, like build_darwincore_dict. You can place CSVs, TSVs, YAMLs, Excel files, etc in the `script-dependencies` folder to keep things organized and build relative paths. Once ready, you can train the model using: 
```bash
python ai_matching/eDNA_model_trainer.py
```
#### Current Training Data
The eDNA SciBERT model has been trained using:
- Darwin Core Vocabulary: [CSV](https://github.com/tdwg/dwc/blob/master/vocabulary/term_versions.csv)
- More to come soon!

The eDNA SciBERT model is configured in `.gitattributes` to be managed using Git LFS, large file storage. No further setup required, just train the model, and commit changes as you normally would.

## Citations
### SciBERT: Pretrained Language Model for Scientific Text
```bibtext
@inproceedings{Beltagy2019SciBERT,
title={SciBERT: Pretrained Language Model for Scientific Text},
author={Iz Beltagy and Kyle Lo and Arman Cohan},
year={2019},
booktitle={EMNLP},
Eprint={arXiv:1903.10676}
}
```
[SciBERT](https://github.com/allenai/scibert) is an open-source project developed by the Allen Institute for Artificial Intelligence (AI2). AI2 is a non-profit institute with the mission to contribute to humanity through high-impact AI research and engineering.