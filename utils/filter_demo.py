import streamlit as st
import pandas as pd
import altair as alt


hypothesis_annotations = pd.read_csv("../utils/hypothesis_data.csv")

index_themes = open("../index_themes.txt").read().splitlines()
index_themes = list(set(index_themes))  # removing duplicates

filters = st.multiselect("Choose a set of Labels", list(index_themes))

if not filters:
    st.error("Please select at least one filter.")

else:
    for n in range(0, len(filters)):
        hypothesis_annotations = hypothesis_annotations[hypothesis_annotations['label'].str.contains(filters[n])]
    st.write(hypothesis_annotations)