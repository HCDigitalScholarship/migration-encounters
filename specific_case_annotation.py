import httpx
import re


def hypothesisgrabber(interview_name, offset):
    """This program takes two variables, the interview name and the offset. Starting at the offset,
     it returns the next 200 annotations (or as many as available) as a list."""

    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name +
        '&limit=200' + '&offset=' + str(offset))
    grabbed_datadict = data.json()
    grabbed_annotations = grabbed_datadict.get("rows")
    return grabbed_annotations


def regex_search_ignore_space(pattern_text, string):
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

    matched_string_start = no_spaces.find(pattern_text)
    matched_string_end = matched_string_start + len(pattern_text)

    # match.start() and match.end() are indices of start and end
    # of the found string in the spaceless string
    # (as we have searched in it).
    start = char_positions[matched_string_start]  # in the original string
    end = char_positions[matched_string_end]-1  # in the original string
    matched_string = string[start:end]

    # the match WITH spaces, and the start and end locations in the original string is returned.
    return [matched_string, start, end]


def main():
    """This program re-formats a *specific* annotation from a *specific* hypothesis interview into a form that aligns
    more closely with the JSON files for the interview."""

    # asking for an interview name to append to end of URL
    interview_name = input("Enter name of Interview: ")
    interview_name = str(interview_name).lower()

    # finding the number of annotations
    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name +
        '&limit=1')
    datadict = data.json()
    total_remaining_annotations = int(datadict.get("total"))

    # initializing our variables
    offset = 0
    annotations_list = []

    # grabbing our annotations 200 at a time and appending them to annotations_list
    while total_remaining_annotations > 0:
        grabbed_annotations = hypothesisgrabber(interview_name, offset)
        for n in range(0, len(grabbed_annotations)):
            annotations_list.append(grabbed_annotations[n])
        offset = offset + 200
        total_remaining_annotations = total_remaining_annotations - 200

    # from the list of annotations, inputting the number of a specific annotation and pulling that specific
    # annotation from the list of annotations
    annotation_number = int(input("Enter number of annotation: "))
    specific_annotation = annotations_list[annotation_number - 1]

    # creating a dictionary for the relevant information from the annotation
    result_dictionary = {}

    # inputting the text of the annotation and the relevant tags to our dictionary
    # TODO perhaps split each of these text labels and tags into separate entries.
    annotation_text = specific_annotation.get('text')
    result_dictionary['label_text'] = annotation_text
    annotation_tags = specific_annotation.get('tags')
    result_dictionary['label_tags'] = annotation_tags

    # inputting the text being referenced to our dictionary
    target = specific_annotation.get("target")
    target_dictionary = target[0]
    selector = target_dictionary.get('selector')
    referenced_text = selector[2]
    exact_text = referenced_text.get('exact')  # from the hypothesis api

    # TODO put in a checker using the prefix and suffix
    # defining the prefix and suffix of our exact text
    prefix = referenced_text.get("prefix")  # from the hypothesis api
    suffix = referenced_text.get("suffix")  # from the hypothesis api

    # TODO the following line only works with single word names.
    # retrieving the raw text of the interviews
    raw_text_document = httpx.get('https://raw.githubusercontent.com/HCDigitalScholarship/migration-encounters/main'
                                  '/data/' + interview_name[0].upper() + interview_name[1:] + '.json')
    raw_text_document = raw_text_document.json()
    raw_text_document = raw_text_document.get('text')

    string_location = regex_search_ignore_space(exact_text, raw_text_document)
    result_dictionary['exact_text'] = string_location[0]
    result_dictionary['start'] = string_location[1]
    result_dictionary['end'] = string_location[2]

    # printing our completed dictionary for a specific annotation
    print(result_dictionary)


if __name__ == '__main__':
    main()
