import httpx
import re


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


def main():
    """This program re-formats the annotations from a *specific* hypothesis interview into a list of dictionaries that
    align more closely with the JSON files for the interview."""

    # asking for an interview name to append to end of URL
    interview_name = input("Enter name of Interview (spaces are underscores): ")
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

    # replacing underscores with spaces, in order to align with the github link
    if '_' in interview_name:
        interview_name = interview_name.replace("_", "%20")
        # making the last initial upper case when necessary
        interview_name = interview_name[:-1] + interview_name[-1].upper()

    # retrieving the raw text of the interviews
    raw_text_document = httpx.get(
        'https://raw.githubusercontent.com/HCDigitalScholarship/migration-encounters/main'
        '/data/' + interview_name + '.json')
    raw_text_document = raw_text_document.json()
    raw_text_document = raw_text_document.get('text')

    # defining a list of un-parsed annotations
    unparsed_annotations = []

    # appending each reformatted annotation to the final list.
    for annotation_number in range(0, int(total_annotations)):
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

    # defining a list of finalized annotations
    annotations = []

    # separating each un-parsed annotation into several annotations by parsing by semicolons
    # when there are several separate ideas in one annotation, this for loop will separate them into different entries
    # each of which references the same point in the text.
    for annotation_number in range(0, len(unparsed_annotations)):
        working_annotation = unparsed_annotations[annotation_number]  # working with a specific annotation
        working_annotation_text = working_annotation["label_text"]

        # separating into a list of strings by splitting with semicolons
        working_annotation_text = re.split(";|\n", working_annotation_text)

        # appending the tags (which are already formatted as a list of strings)
        working_annotation_tags = working_annotation["label_tags"]
        working_annotation_total = working_annotation_text + working_annotation_tags

        for text in range(0, len(working_annotation_total)):
            # working with one tag at a time
            specific_working_annotation_text = working_annotation_total[text]
            specific_working_annotation_text = specific_working_annotation_text.strip()  # removing whitespace

            # removing any blank annotations created in the previous processes
            if specific_working_annotation_text == "":
                continue

            # defining a dictionary for our parsed annotation
            parsed_annotation = {}

            # adding the relevant data to our parsed data dictionary
            parsed_annotation["type"] = "text"
            parsed_annotation["start"] = working_annotation["start"]
            parsed_annotation["end"] = working_annotation["end"]
            # uncomment the following line to include the referenced text in the final annotation
            # parsed_annotation["text"] = working_annotation["exact_text"]
            parsed_annotation["label"] = str(specific_working_annotation_text)

            # appending this parsed annotation to our list of finalized annotations
            annotations.append(parsed_annotation)

    print(annotations)


if __name__ == '__main__':
    main()

