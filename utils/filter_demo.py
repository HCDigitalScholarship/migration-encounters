import streamlit as st
import pandas as pd

def nonempty_checker(index_themes, hypothesis_annotations):
    nonempty_index_themes = []
    number_of_occurrences = []
    for theme in range(0, len(index_themes)):
        non_empty_checker = hypothesis_annotations[hypothesis_annotations['label'].str.contains(index_themes[theme])]
        if non_empty_checker.empty:
            continue
        else:
            nonempty_index_themes.append(index_themes[theme])
            number_of_occurrences.append(len(non_empty_checker))

    return [nonempty_index_themes, number_of_occurrences]


hypothesis_annotations = pd.read_csv("utils/hypothesis_data.csv")

index_themes = open("index_themes.txt").read().splitlines()

index_themes = list(set(index_themes))  # removing duplicates
filters = st.multiselect("Choose Labels", list(index_themes))


if not filters:
    st.error("Please select at least one filter.")

else:
    pd.set_option('display.max_colwidth', None)
    for n in range(0, len(filters)):
        hypothesis_annotations = hypothesis_annotations[hypothesis_annotations['label'].str.contains(filters[n])]

    nonempty_index = nonempty_checker(index_themes, hypothesis_annotations)
    st.sidebar.title("These Labels Are Paired With:")
    for entry in range(0, len(nonempty_index[0])):
        st.sidebar.write(nonempty_index[0][entry], nonempty_index[1][entry])
    st.write("---")

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

