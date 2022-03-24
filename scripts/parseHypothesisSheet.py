import csv
import json
import os


if __name__ == "__main__":
	base_path = os.path.dirname(os.path.realpath(__file__))
	# change this to the google sheet file that is downloaded as csv
	file = f"{base_path}/annotations.csv"

	out = f"{base_path}/interviewee_annotation_url.json"
	data = {}
	with open(file) as f:
		reader = csv.reader(f)
		for n, row in enumerate(reader):
			# might need to alter next line if more interviews are added
			if 6 <= n <= 158:
				url = row[2]
				interviewee = url.split("/")[-1]
				key = f"{interviewee}_{'v1' if n <= 67 else 'v2'}"
				data[key] = url
	with open(out, "w") as f:
		json.dump(data, f, indent = 4)