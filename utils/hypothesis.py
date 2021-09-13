import httpx
import re
import spacy
from rapidfuzz import process, fuzz
from pathlib import Path
from tqdm import tqdm
import srsly
import pandas as pd
from typing import List


names_files = {'Joseph': 'joseph',
               'Jesus A': 'jesus_a',
               'Erik': 'erik',
               'Abel': 'abel',
               'Luisa': 'luisa',
               'Edgar': 'edgar',
               'Ivan B': 'ivan_b',
               'Ben': 'ben',
               'Beto': 'beto',
               'Miguel B': 'beto_b',
               'Ilse': 'ilse',
               'Yosell': 'yosell',
               'Jose': 'jose',
               'Rodolfo': 'rodolfo',
               'Angelo': 'angelo',
               'Noe': 'noe',
               'Mike': 'mike',
               'Laila': 'laila',
               'Ana': 'ana',
               'Frank': 'frank',
               'Hugo': 'hugo',
               'Maria': 'maria',
               'Josue': 'josue',
               'Luis B': 'luis_b',
               'Donovan': 'donovan',
               'Miguel A': 'miguel_a',
               'Billy': 'billy',
               'Yair': 'yair',
               'Juan A': 'juan_a',
               'Laura B': 'laura_b',
               'Daniel': 'daniel',
               'Pablo': 'pablo',
               'Miguel C': 'miguel_c',
               'Yordani': 'yordani',
               'Daniel B': 'daniel_b',
               'Sylent': 'sylent',
               'Carolina': 'carolina',
               'Rodrigo': 'rodrigo',
               'Lucero': 'lucero',
               'Luis A': 'luis_a',
               'Zayuri': 'zayuri',
               'Ivan': 'ivan',
               'Axel': 'axel',
               'Ruben': 'ruben',
               'Jesus C': 'jesus_c',
               'Laura A': 'laura_a',
               'Roberto': 'roberto',
               'Carlos': 'carlos',
               'Cuauhtémoc': 'cuauhtemoc',
               'Juan B': 'juan_b',
               'Diana': 'diana',
               'Brenda': 'brenda',
               'Valeria': 'valeria',
               'Many': 'many',
               'Olimpya': 'olimpya',
               'Joana': 'joana',
               'Melani': 'melani',
               'Angel': 'angel',
               'Jeimmy': 'jeimmy',
               'Cris': 'cris',
               'Rocio': 'rocio',
               'Kevin': 'kevin',
               'Julio Cesar': 'julio'}


def hypothesis_grabber(interview_name, offset):
    """This program takes two variables, the interview name and the offset. Starting at the offset,
     it returns the next 200 annotations (or as many as available) as a list."""

    data = httpx.get(
        "https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/" + interview_name +
        "&limit=200" + "&offset=" + str(offset))
    grabbed_datadict = data.json()
    grabbed_annotations = grabbed_datadict.get("rows")
    return grabbed_annotations


def search_ignore_space(pattern_text, string):
    """This program takes two variables, a string to search (pattern_text) within a larger string (string). It matches
    (pattern_text) within (string), ignoring all whitespace characters [^ \t\n\r\f\v]. It then returns the matched
    string with whitespace characters included, as well as the start and end character locations of
    (pattern_text) in (string)"""

    no_spaces = ''
    char_positions = []

    for pos, char in enumerate(string):
        if re.match(r'\S', char):  # upper \S matches non-whitespace chars
            no_spaces += char
            char_positions.append(pos)

    # removing whitespace from pattern text
    whitespace_characters = ['^', ' ', '\t', '\n', '\r', '\f', '\v']
    for char in whitespace_characters:
        pattern_text = pattern_text.replace(char, '')

    #
    matched_string_start = no_spaces.find(pattern_text)
    matched_string_end = matched_string_start + len(pattern_text)

    # match.start() and match.end() are indices of start and end
    # of the found string in the spaceless string
    # (as we have searched in it).
    start = char_positions[matched_string_start]  # in the original string
    end = char_positions[matched_string_end] - 1  # in the original string
    matched_string = string[start:end]

    # the match WITH spaces, and the start and end locations in the original string is returned.
    return [matched_string, start, end]


def collect_annotations(interview_name: str):
    """This program re-formats the annotations from a *specific* hypothesis interview into a list of dictionaries that
    align more closely with the Spacy auto-generated annotations."""

    # asking for an interview name to append to end of URL
    interview_name = interview_name  # input("Enter name of Interview (spaces are underscores): ")
    interview_name = str(interview_name).lower()

    # finding the number of annotations
    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name +
        '&limit=1')
    datadict = data.json()
    total_annotations = int(datadict.get("total"))
    total_remaining_annotations = total_annotations

    # initializing our variables
    offset = 0
    annotations_list = []

    # grabbing our annotations 200 at a time and appending them to annotations_list
    while total_remaining_annotations > 0:
        grabbed_annotations = hypothesis_grabber(interview_name, offset)
        for n in range(0, len(grabbed_annotations)):
            annotations_list.append(grabbed_annotations[n])
        offset = offset + 200
        total_remaining_annotations = total_remaining_annotations - 200

    # reformatting the interview name in order to align with the github link
    interview_name = interview_name[0].upper() + interview_name[1:]

    # replacing underscores with spaces, in order to align with the github formatting
    if '_' in interview_name:
        interview_name = interview_name.replace("_", "%20")
        # making the last initial upper case when necessary
        interview_name = interview_name[:-1] + interview_name[-1].upper()

    # retrieving the raw text of the interviews
    raw_text_document = httpx.get(
        'https://raw.githubusercontent.com/HCDigitalScholarship/migration-encounters/main'
        '/data/' + interview_name + '.json')
    if raw_text_document.status_code == 200:
        raw_text_document = raw_text_document.json()
        raw_text_document = raw_text_document.get('text')
    else:  # error loading json file
        return "error"
    # defining a list of un-parsed annotations
    unparsed_annotations = []

    # appending each reformatted annotation to the final list.
    for annotation_number in range(0, int(total_annotations)):
        try:
            specific_annotation = annotations_list[annotation_number - 1]
            # creating a dictionary for the relevant information from the annotation
            result_dictionary = {}

            # inputting the text of the annotation and the relevant tags to our dictionary
            annotation_text = specific_annotation.get('text')
            result_dictionary['label_text'] = annotation_text
            annotation_tags = specific_annotation.get('tags')
            result_dictionary['label_tags'] = annotation_tags

            # finding the referenced text in the annotation
            target = specific_annotation.get("target")
            target_dictionary = target[0]
            selector = target_dictionary.get('selector')
            referenced_text = selector[2]
            exact_text = referenced_text.get('exact')  # from the hypothesis api

            try:
                # finding the location of the annotation in the larger text and adding to our dictionary
                string_location = search_ignore_space(exact_text, raw_text_document)
                result_dictionary['exact_text'] = string_location[0]
                result_dictionary['start'] = string_location[1]
                result_dictionary['end'] = string_location[2]

                # appending our resultant dictionary to our list of annotations
                unparsed_annotations.append(result_dictionary)

            except:
                # the above code sometimes fails if the string overflows, in that case, we can remove a few characters
                # from the end of the string and try again.
                try:
                    # Dealing with overflow cases (when the annotation reference goes past the raw text)
                    overflow_fix_text = exact_text[:-3]
                    string_location = search_ignore_space(overflow_fix_text, raw_text_document)
                    result_dictionary['exact_text'] = string_location[0]
                    result_dictionary['start'] = string_location[1]
                    result_dictionary['end'] = string_location[2]

                    # appending our resultant dictionary to our list of annotations
                    unparsed_annotations.append(result_dictionary)

                except:
                    # if it still fails, we discard the annotation
                    pass
        except Exception as e:
            print(e)

    # putting our pre-defined index themes into a list
    index_themes = open("./index_themes.txt").read().splitlines()

    # importing our semantic search vocabulary
    nlp = spacy.load("en_core_web_lg")

    # defining a list of finalized annotations
    annotations = []

    # FOR DEBUGGING OUR MATCHER
    matched = []
    semanticmatched = []
    unmatched = []
    # END

    for annotation_number in range(0, len(unparsed_annotations)):
        working_annotation = unparsed_annotations[annotation_number]  # working with a specific annotation
        working_annotation_text = working_annotation["label_text"]

        # Turning our annotation text into a 1 element list, so that we can concatenate it later.
        working_annotation_text = [str(working_annotation_text)]

        # appending the tags (which are already formatted as a list of strings)
        working_annotation_tags = working_annotation["label_tags"]
        working_annotation_total = working_annotation_text + working_annotation_tags

        for text in range(0, len(working_annotation_total)):

            # working with one tag at a time
            annotation_text = working_annotation_total[text]
            annotation_text = annotation_text.strip()  # removing whitespace

            # removing any blank texts or tags created in the previous processes
            if annotation_text == "":
                continue

            matched_annotation = ""

            # splitting our annotation by the commas (*and semicolons*) in order to work with one phrase at a time
            index_split = re.split(",|;|\n", annotation_text)
            for n in range(0, len(index_split)):

                # removing any blank texts created in the previous processes
                if index_split[n] == "":
                    continue

                # finding the most similar index theme to our annotation by accounting for typos/ different spellings
                index_fuzzy_matcher = process.extractOne(index_split[n], index_themes, scorer=fuzz.WRatio)

                # if the annotation is at least an 85% match, we replace it with its matched index theme
                if index_fuzzy_matcher[1] >= 85:
                    matched_annotation = matched_annotation + index_fuzzy_matcher[0] + ", "
                    matched.append([index_split[n], index_fuzzy_matcher[0]])  # this line is for testing

                # if the annotation is less than an 85% match, we attempt a semantic search
                else:
                    max_semantic_similarity = 0  # initializing our variables
                    most_similar_index = ""  # initializing our variable
                    for m in range(0, len(index_themes)):
                        # performing our semantic search
                        semantic_similarity = nlp(index_split[n]).similarity(nlp(index_themes[m])) * 100

                        # finding the most similar term from our index
                        if semantic_similarity > max_semantic_similarity:
                            most_similar_index = index_themes[m]
                            max_semantic_similarity = semantic_similarity

                    if max_semantic_similarity >= 70:  # a 70% confidence tells us to match our annotation
                        matched_annotation = matched_annotation + most_similar_index + ", "
                        semanticmatched.append(
                            [index_split[n], most_similar_index, max_semantic_similarity])  # this line is for testing

                    # if neither the fuzzy search nor the semantic search return anything, we simply append the
                    # original term
                    else:
                        matched_annotation = matched_annotation + index_split[n] + ", "
                        unmatched.append(
                            [index_split[n], most_similar_index, max_semantic_similarity])  # this line is for testing

            matched_annotation = matched_annotation[:-2]  # removing the final comma

            # defining a dictionary for our parsed annotation
            parsed_annotation = {}

            # adding the relevant data to our parsed data dictionary
            parsed_annotation["type"] = "text"
            parsed_annotation["start"] = working_annotation["start"]
            parsed_annotation["end"] = working_annotation["end"]
            # uncomment the following line to include the referenced text in the final annotation
            # parsed_annotation["text"] = working_annotation["exact_text"]
            parsed_annotation["label"] = str(matched_annotation)

            # appending this parsed annotation to our list of finalized annotations
            annotations.append(parsed_annotation)

    # FOR DEBUGGING OUR MATCHER
    # print(annotations)
    # print(matched)
    # print(semanticmatched)
    # print(unmatched)
    return annotations


def load_data():
    """This program takes every interview in the data directory, runs collect_annotations on each one, and then
    returns a list of dictonaries, each of which corresponds to a specific interview."""
    all_data = []  # initializing our list
    interviews = list(Path('./data').iterdir())  # iterating over our /data folder
    for interview in tqdm(interviews):
        data = srsly.read_json(interview)  # opening our interview .txt file.
        name = names_files[interview.stem]  # correlating the /data folder names with the website path names
        annotations = collect_annotations(name)  # collecting the annotations for our specific interview
        data['annotations'].extend(annotations)  # appending our annotations to our interview text
        all_data.append(data)
    return all_data


def make_csv(data: List[dict]):
    """This program takes the output of load_data() and re-formats it into a .csv file"""
    df_data = []
    for row in data:
        for i in row['annotations']:
            if isinstance(i, str):
                pass
            else:
                i['name'] = row['name']
                i['text'] = row['text'][i['start']:i['end']]
                df_data.append(i)
    df = pd.DataFrame(df_data)
    return df

# Remove spacy ents
# drop = ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP','ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']
# df = df[~df['label'].isin(drop)]

# Writing to an external CSV file.
# df.to_csv('file.csv')
