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
    for m in range(0, len(hypothesis_annotations)):
        # Turning our relevant values into strings.
        labels = hypothesis_annotations['label']
        labels = labels.iloc[[m]].to_string()

        name = hypothesis_annotations['name']
        name = name.iloc[[m]].to_string()

        text = hypothesis_annotations['text']
        text = text.iloc[[m]].to_string()

        # Removing unnecessary characters.
        remove = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "\\n"]
        for l in range(0, len(remove)):
            labels = labels.replace(remove[l], "")
            name = name.replace(remove[l], "")
            text = text.replace(remove[l], "")

        st.write(name)
        st.write(labels)
        st.write(text)
        st.write("---")