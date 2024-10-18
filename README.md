# TermMatchAI

TermMatchAI is a library designed to match terms between two datasets using exact syntactical matching, fuzzy search matching, and semantic matching with AI models.

What is the use case?
- Data is much less useful if you are unable to compare data between different datasets. __For example:__ my lab measures the general sampling environment with term name of 'habitat', with data like: 'oceanic mesopelagic zone biome', and another lab uses the term name 'env_local_scale' with data like: 'marine photic zone [ENVO:00000209]'. TermMatchAI will tell you that they are the closest match to one another.
- This project also identifies lists of ID and Date/time related fields for each dataset and groups them together. It also identifies the compound key of the ID fields for each dataset.

Please see `term_matching_report.csv` for an example output. To format it in nicely in Excel, Press:
```
CTRL + A
ALT + O + C + A
```

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
- Please note: your workplace's network may block Huggingface.io, which is how the SciBERT AI model is installed. 
    - If you get an error regarding 'Huggingface', consider a VPN or using a different network. The AI model only needs to be downloaded once.
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

### 1. Term Matching
To compare terms between two datasets, use the `main.py` script. Ensure your input is formatted correctly as dictionaries. __See `data_loading/data_loading.py` for more information on input format__
```python
# Example dictionary for dataset 1, or the dataset which you'd like to match TO
noaa_terms_w_data={'sample_name': 'GOMECC4_27N_Sta1_DCM_A', 'sample_type': 'seawater', ... }

# Example dictionary for dataset 2, or the dataset which is INCOMING / needs to be matched
user_terms_w_data={'eventID': 'EX2107_D01_01', 'country': 'USA', ... }
```
You're ready to go! (hopefully):
```bash
python main.py
```
- Before it runs, you can specify __how many matches__ will be generated for each term in the incoming dataset, 1-5 matches per term in the incoming dataset
- After it runs, a report will be generated by `core/generate_report.py`. This will create a CSV file in the home project directory.

### 2. Training the AI Model
__Currently under development, this is how I was training the model previously. Barely improved results__

Our custom eDNA SciBERT model is located in `ai_matching/eDNA_scibert_model/`
These are mostly binary files that are unreadable, and you shouldn't directly modify. Instead, it is trained using the `ai_matching/eDNA_model_trainer.py` script. You will probably have to write a short function to get your training data into a [dictionary in the correct format](#Term-comparison). I suggest looking at the dictionary-building functions already in there, like build_darwincore_dict. You can place CSVs, TSVs, YAMLs, Excel files, etc in the `script-dependencies` folder to keep things organized and build relative paths. Once ready, you can train the model using: 
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