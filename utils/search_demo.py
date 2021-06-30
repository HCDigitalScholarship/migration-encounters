import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import spacy
from spacy.lang.en import English
from spacy.tokenizer import Tokenizer


token_nlp = English()
tokenizer = Tokenizer(token_nlp.vocab)
nlp = spacy.load("en_core_web_lg")
hypothesis_annotations = pd.read_csv("../utils/hypothesis_data.csv")
pd.set_option('display.max_colwidth', None)

user_input = st.text_input("Search Term")

label = hypothesis_annotations['label']
text = hypothesis_annotations['text']

similarity_vector = []

progress_bar = st.progress(0)

for n in range(0, len(hypothesis_annotations)):
    label_direct = label.iloc[[n]].to_string()
    text_direct = text.iloc[[n]].to_string()

    # Removing unnecessary characters.
    remove = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "\\n"]
    for l in range(0, len(remove)):
        label_direct = label_direct.replace(remove[l], "")
        text_direct = text_direct.replace(remove[l], "")

    label_direct = label_direct.split(",")

    max_semantic_similarity = 0  # initializing our variables

    for m in range(0, len(label_direct)):
        semantic_similarity = nlp(user_input).similarity(nlp(label_direct[m])) * 100
        # finding the most similar term from our index
        if semantic_similarity > max_semantic_similarity:
            max_semantic_similarity = semantic_similarity
        else:
            continue

    fuzzy_similarity = process.extractOne(user_input, label_direct, scorer=fuzz.WRatio)
    match_percentage = max(semantic_similarity, fuzzy_similarity[1])

    text_direct = tokenizer(text_direct)

    text_max_semantic_similarity = 0  # initializing our variables

    for token in text_direct:
        text_semantic_similarity = nlp(user_input).similarity(nlp(str(token))) * 100
        # finding the most similar term from our index
        if text_semantic_similarity > text_max_semantic_similarity:
            text_max_semantic_similarity = semantic_similarity
        else:
            continue

    text_match_percentage = text_max_semantic_similarity

    similarity = max(text_match_percentage, match_percentage)
    similarity_vector.append(similarity)
    progress_bar.progress(float(n / len(hypothesis_annotations)))

hypothesis_annotations.append("Similarity", similarity_vector, True)
st.write(hypothesis_annotations)