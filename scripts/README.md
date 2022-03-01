# How to us generate_json script

## File parameters

1. -f path to interview file (transcripts v2)
2. -b path to bio file
3. -a hypothesis annotation name

## Example

```python
python generateJson.py -f interview.txt -b bio.txt -a john
```

## About

There are two files with data that the script depends on

1. interviewee_annotation.py
   - Json file that has the hypothesis api endpoint for each person's interview annotations
2. interviewee_audio.py
   - Json file that has the audio source and text for each person

The script also only works when the transcript is formatted the same way as before ie. the heading of the interview file is the same

## How to update with new interviews

Simply update both json files mentioned in the previosu section with the appropriate information
