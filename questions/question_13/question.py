description = """
A compliance team wants to automatically extract key entities (people, organizations, 
locations, dates, etc.) from text.

You are given a single input sentence as a Python string named `text`.

### Task
Use spaCy NER to extract entities and return them in a structured format.

### Requirements
- Load a spaCy English pipeline (`en_core_web_sm`)
- Run NER on the given text
- Extract all entities from the sentence
- Return a pandas DataFrame named `result` with the following columns:
  - `entity_text` (the exact entity span as it appears in the sentence)
  - `entity_label` (spaCy label like PERSON, ORG, GPE, DATE, etc.)
  - `start_char`
  - `end_char`
- Sort the output by `start_char` in ascending order

### Evaluation
- Output format validation (entity_text, entity_label, start_char, end_char)
- Character offsets must match the entity spans
- Entity order must be sorted by start_char
- Entity labels must match spaCy's predictions for the given model
"""

hint = """
- Access entities via `doc.ents` after processing with `nlp(text)`
"""


inital_sample_code = """import spacy
import pandas as pd

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Process the text and extract entities
# Your code here

# Create result DataFrame with columns: entity_text, entity_label, start_char, end_char
# Sort by start_char ascending
result = None  # Replace with your DataFrame
"""


# Input text that will be provided to users
input_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California on April 1, 1976."


def get_description():
    return description

def get_hint():
    return hint

def get_inital_sample_code():
    return inital_sample_code

def get_input_text():
    return input_text
