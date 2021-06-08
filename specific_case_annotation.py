import httpx

def hypothesisgrabber(interview_name, offset):
    """This program takes two variables, the interview name and the offset. Starting at the offset,
     it returns the next 200 annotations as a list."""
    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name + '&limit=200' + '&offset=' + str(offset))
    grabbed_datadict = data.json()
    grabbed_annotations = grabbed_datadict.get("rows")
    return grabbed_annotations

def main():
    """This program reformats a *specific* annotation from a *specific* hypothesis interview into a form that aligns
    more closely with the JSON files for the interview."""

    # asking for an interview name to append to end of URL
    interview_name = input("Enter name of Interview: ")
    interview_name = str(interview_name).lower()

    # finding the number of annotations
    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name + '&limit=1')
    datadict = data.json()
    total_remaining_annotations = int(datadict.get("total"))

    # initializing our vairables
    offset = 0
    annotations_list = []

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
    # TODO perhaps resolve typos/ incomplete words here?
    target = specific_annotation.get("target")
    target_dictionary = target[0]
    selector = target_dictionary.get('selector')
    referenced_text = selector[2]
    html_exact_text = referenced_text.get('exact')
    result_dictionary['exact_text'] = html_exact_text

    html_exact_text_reformatted = html_exact_text.replace('?', '? ')

    # defining the prefix and suffix of our exact text
    prefix = referenced_text.get("prefix")
    suffix = referenced_text.get("suffix")

    # TODO resolve this with the actual start and end characters of our json files.

    # TODO the following line only works with single word names.
    # retrieving the raw text of the interviews
    raw_text_document = httpx.get('https://raw.githubusercontent.com/HCDigitalScholarship/migration-encounters/main'
                                  '/data/' + interview_name[0].upper() + interview_name[1:] + '.json')
    raw_text_document = raw_text_document.json()
    raw_text_document = raw_text_document.get('text')

    # TODO put a checker on this one using prefix and suffix
    string_location = raw_text_document.find(html_exact_text)

    start = string_location
    result_dictionary['start'] = start
    end = string_location + len(html_exact_text)
    result_dictionary['end'] = end

    # printing our completed dictionary for a specific annotation
    print(result_dictionary)


if __name__ == '__main__':
    main()
