import streamlit as st
import pandas as pd

def nonempty_checker(index_themes, hypothesis_annotations):
    """ This function takes two variables, a list of index themes and a CSV of annotations. It outputs
    a list of lists, each of which gives us an index theme that appears in our annotations - and the
    number of times this index theme occurs. """
    nonempty_index_themes = []  # Initializing our output variables.
    number_of_occurrences = []
    for theme in range(0, len(index_themes)):
        # Checking whether our index themes appear in the annotations.
        non_empty_checker = hypothesis_annotations[hypothesis_annotations['label'].str.contains(index_themes[theme])]
        if non_empty_checker.empty:  # ignoring the index theme if it doesn't appear in the annotations.
            continue
        else:
            # appending our index theme to our finalized list, and taking the length of the matched CSV as
            # the number of occurrences.
            nonempty_index_themes.append(index_themes[theme])
            number_of_occurrences.append(len(non_empty_checker))

    pre_dataframe = []

    for n in range(0, len(nonempty_index_themes)):
        nonempty_reorganizer = [nonempty_index_themes[n],number_of_occurrences[n]]
        pre_dataframe.append(nonempty_reorganizer)

    output = pd.DataFrame(pre_dataframe, columns= ['Theme', 'Frequency'])
    output = output.sort_values(by=['Frequency'], ascending=False)
    output = output.reset_index(drop=True)

    return output


# opening our CSV of hypothesis annotations - this notation only works on the deployed Streamlit platform.
# locally, add "../" to the beginning of the filepath.
hypothesis_annotations = pd.read_csv("utils/hypothesis_data.csv")

index_themes = open("index_themes.txt").read().splitlines()
index_themes = list(set(index_themes))  # removing duplicates

filters = st.multiselect("Choose Labels", list(index_themes))  # creating an input field.

st.write("---")  # including a horizontal line for readability.

sidebar_click = ""

if not filters:  # An error message for when there is no input.
    st.error("Please select at least one filter.")

else:
    pd.set_option('display.max_colwidth', None)  # removing the character limit.

    for n in range(0, len(filters)):  # finding which annotations match the inputted filters
        # at each iteration, the hypothesis_annotations variable updates to only include the relevant terms
        hypothesis_annotations = hypothesis_annotations[hypothesis_annotations['label'].str.contains(filters[n])]

    # running our checker for non-empty index themes.
    nonempty_index = nonempty_checker(index_themes, hypothesis_annotations)

    # creating a sidebar for the non-empty labels.
    st.sidebar.title("These Labels Are Paired With:")
    for entry in range(0, len(nonempty_index)):  # writing each of our non-empty labels and their frequency.
        if st.sidebar.button(str(nonempty_index.loc[entry, 'Theme']) + " (" + str(nonempty_index.loc[entry, 'Frequency']) + ")", str(entry)):
            sidebar_click = str(nonempty_index.loc[entry, 'Theme'])
            st.write(sidebar_click)

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

        # writing our final output
        st.write(name)
        st.write(labels)
        st.write(text)
        st.write("---")