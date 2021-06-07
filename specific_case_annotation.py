"""This program reformats a *specific* annotation from a *specific* hypothes.is interview into a form that aligns
more closely with the JSON files for the interview."""

def main():
    # Remember to install httpx - in terminal type "pip install httpx"
    import httpx

    # asking for an interview name to append to end of URL
    interview_name = input("Enter name of Interview: ")
    interview_name = str(interview_name).lower()
    data = httpx.get(
        'https://api.hypothes.is/api/search?uri=https://www.migrationencounters.org/stories/' + interview_name)

    # extracting the annotations from the dictionary given by the webpage
    # TODO Figure out why there are only 20 elements in the rows list sent by this webpage (ex. Luisa).
    datadict = data.json()
    datadictrows = datadict.get("rows")

    # from the list of annotations, inputting the number of a specific annotation and pulling that specific
    # annotation from the list of annotations
    annotation_number = int(input("Enter number of annotation: "))
    specific_annotation = datadictrows[annotation_number - 1]

    # creating a dictionary for the relevant information from the annotation
    result_dictionary = {}

    # inputting the text of the annotation and the relevant tags to our dictionary
    # TODO perhaps split each of these text labels and tags into separate entries.
    annotation_text = str(specific_annotation.get('text'))
    result_dictionary['label_text'] = annotation_text
    annotation_tags = str(specific_annotation.get('tags'))
    result_dictionary['label_tags'] = annotation_tags

    # inputting the text being referenced to our dictionary
    # TODO perhaps resolve typos/ incomplete words here?
    target = specific_annotation.get("target")
    target_dictionary = target[0]
    selector = target_dictionary.get('selector')
    referenced_text = selector[2]
    exact_text = referenced_text.get('exact')
    result_dictionary['exact_text'] = exact_text

    # inputting the start and end locations to our dictionary
    # TODO resolve this with the actual start and end characters of our json files.
    text_location = selector[1]
    start = text_location.get('start')
    result_dictionary['start'] = start
    end = text_location.get('end')
    result_dictionary['end'] = end

    # printing our completed dictionary for a specific annotation
    print(result_dictionary)

if __name__ == '__main__':
    main()
