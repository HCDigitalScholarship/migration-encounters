import csv
import json
import os

if __name__ == "__main__":
	base_path = os.path.dirname(os.path.realpath(__file__))
	# change this to the google sheet file that is downloaded as csv
	file = f"{base_path}/audio.csv"

	out = f"{base_path}/interviewee_audio.json"

	all_data = {}
	with open(file, "r") as f:
		reader = csv.reader(f)
		# skip line with google drive src url
		next(reader)
		# skip line with headers
		next(reader)

		base_url = "https://drive.google.com/uc?export=download&id="
		bad_interview_parts = ["raw file", "not found"]
		for row in reader:
			name = row[0].strip("., ").lower()
			topic = row[1].strip(".,")
			src = f"{base_url}{row[2]}"
			raw_interview_part = row[3]
			interview_part = None if ("raw file" in raw_interview_part.lower() and "not found" in raw_interview_part.lower()) else raw_interview_part
			if interview_part:
				# to unparse double backslashes to get escaped characters back
				# \\n -> \n or \\u... -> \u...
				interview_part = bytes(interview_part, 'utf-8').decode('unicode_escape')
			data = {
				"topic": topic,
				"src": src,
				"interview_part": interview_part,
			}
			if name in all_data:
				all_data[name].append(data)
			else:
				all_data[name] = [data]
	with open(out, "w") as f:
		json.dump(all_data, f, indent=4)