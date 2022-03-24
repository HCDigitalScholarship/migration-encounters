# How to us generate_json script

## File parameters

1. -f path to interview file (transcripts v2)
2. -b path to bio file
3. -an hypothesis annotation name for api (can handle argument with spaces)
4. -au audio name in google drive (can handle argument with spaces)
5. -p path to portrait file
6. -o the output file (if not provided file will be generated in current directory)

## Example Usage

```bash
python generateJson.py -f interview.txt -b bio.txt -an john -au john doe -p portrait.jpg
```

## About

There are two files with data that the script depends on

1. interviewee_annotation.py
   - Json file that has the hypothesis api endpoint for each person's interview annotations
2. interviewee_audio.py
   - Json file that has the audio source and text for each person

The script also only works when the transcript is formatted the same way as before ie. the heading of the interview file is the same

## How to update with new interviews

Simply update both json files mentioned in the previous section with the appropriate information.

There are also 2 helper scripts for this task: parseHypothesisSheet.py, parseAudioSheet.py.
These two scripts help parse the annotation and audio sheet file from google drive, respectively
into json files that generate_json.py uses. It is recommended to add the appropriate interview data
to the annotation and google sheets file, export to csv, then run these two helper scripts to update
the existing json files with the new data, but you can also directly add to the json files.
