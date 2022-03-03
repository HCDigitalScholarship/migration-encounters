import argparse
import json
from datetime import datetime
from hypothesis import get_annotations
from utils import get_interviewee, get_interviewer, get_date, get_location, get_text, get_audio

if __name__ == '__main__':
	# parser to get the command line arguments
	parser = argparse.ArgumentParser()

	# sets up a flag argument for the parser
	parser.add_argument('-f', '--file', help="path to interview file")
	parser.add_argument('-b', '--bio', help="path to bio file")
	parser.add_argument('-an', '--annotation', nargs='*', help="hypothesis api name")
	parser.add_argument('-au', '--audio', nargs='*', help="audio name")
	parser.add_argument('-o', '--out', help="output directory for json file")

	# parses the arguments into a variable
	args = parser.parse_args()
 
	file = args.file
	bio_file = args.bio
	annotation_name = None if args.annotation is None or len(args.annotation) == 0 else " ".join(args.annotation)
	audio_name = None if args.audio is None or len(args.audio) == 0 else " ".join(args.annotation)
	out = args.out
	
	interview_lines = {}
	with open(file, mode="r", encoding="utf-8-sig") as f:
		for n, line in enumerate(f):
			interview_lines[n] = line

	bio = ""
	if bio_file is not None:
		with open(bio_file, mode="r", encoding="utf-8-sig") as f:
			bio = f.read()

	
	interviewee = get_interviewee(interview_lines)
	interviewer = get_interviewer(interview_lines)
	date_month_dd_yyyy = get_date(interview_lines)
	# Januaray 1, 2000 -> 1-1-2000
	date_mm_dd_yyyy = datetime.strptime(date_month_dd_yyyy, "%B %d, %Y").strftime('%-m-%-d-%-Y')
	location = get_location(interview_lines)
	text = get_text(interview_lines)
	portrait = f'{interviewee}_{date_mm_dd_yyyy}_Portrait.jpg'
	thumbnail = f'{interviewee}_{date_mm_dd_yyyy}_Thumbnail.jpg'
	annotations = get_annotations(annotation_name, text)
	audio = get_audio(audio_name, text)

	data = {
		"name": interviewee,
		"date": date_month_dd_yyyy,
		"location": location,
		"interviewer": interviewer,
		"portrait": portrait,
		"thumbnail": thumbnail,
		"text": text,
		"annotations": annotations,
		"audio": audio,
		"subjects": None,
		"bio": bio
	}

	out = out if out else f"./{interviewee}.json"
	with open(out, "w") as a:
		json.dump(data, a, indent = 4)
   