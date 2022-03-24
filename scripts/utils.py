import re
from typing import List
import json
import spacy
from rapidfuzz import process, fuzz
import os
import requests

nlp = spacy.load("en_core_web_lg")

def search_ignore_space(pattern_text, string):
	# from hikaru (kinda)
	"""This function takes two variables, a string to search (pattern_text) within a larger string (string). It matches
	(pattern_text) within (string), ignoring all whitespace characters [^ \t\n\r\f\v]. It then returns the matched
	string with whitespace characters included, as well as the start and end character locations of
	(pattern_text) in (string)"""

	original_string_char_positions = []
	for pos, char in enumerate(string):
		if re.match(r'\S', char):  # upper \S matches non-whitespace chars
			original_string_char_positions.append(pos)
	# removing whitespace from pattern text
	pattern_text = "".join(pattern_text.split())
	string_no_space = "".join(string.split())
	#
	matched_string_start = string_no_space.find(pattern_text)
	matched_string_end = matched_string_start + len(pattern_text)

	if matched_string_start == -1:
		return [None, None, None]

	# match.start() and match.end() are indices of start and end
	# of the found string in the spaceless string
	# (as we have searched in it).
	start = original_string_char_positions[matched_string_start]  # in the original string
	end = original_string_char_positions[matched_string_end] - 1 if matched_string_end < len(original_string_char_positions) else original_string_char_positions[-1] # in the original string
	matched_string = string[start:end]

	# the match WITH spaces, and the start and end locations in the original string is returned.
	return [matched_string, start, end]

def find_fuzzy_match(string: str, bank: List[str], cut_off: float):
	# from hikaru
	if string is None:
		return None
	if len(bank) == 0 or len(string) == 0:
		return string
	# finding the most similar index theme to our annotation by accounting for typos/ different spellings
	match, similarity, _ = process.extractOne(string, bank, scorer=fuzz.WRatio)
	if similarity >= cut_off:
		return match
	return match

def find_semantic_match(string: str, bank: List[str], cut_off: float):
	# from hikaru
	max_semantic_similarity = 0  # initializing our variables
	semantic_match = ""
	for phrase in bank:
		semantic_similarity = nlp(string).similarity(nlp(phrase))
		if semantic_similarity > max_semantic_similarity:
			max_semantic_similarity = semantic_similarity
			semantic_match = phrase
	if max_semantic_similarity >= cut_off:
		return semantic_match
	return None

#==================================================================

def get_interviewee(lines):
	for n, line in lines.items():
		if "Interviewee" in line:
			if (n - 1 < 0):
				return None
			name = lines[n - 1].strip()
			return name
	return None

def get_interviewer(lines):
	for n, line in lines.items():
		if "Interviewer" in line:
			if (n - 1 < 0):
				return None
			name = lines[n - 1].strip()
			return name
	return None

def contains_month(date):
	date = date.lower()
	if "january" in date or \
		"february" in date or \
		"march" in date or \
		"april" in date or \
		"may" in date or \
		"june" in date or \
		"july" in date or \
		"august" in date or \
		"september" in date or \
		"october" in date or \
		"november" in date or \
		"december" in date :
			return True
	return False

def get_date(lines):
	for n, line in lines.items():
		if contains_month(line):
			return line.strip()
	return None

def get_location(lines):
	for n, line in lines.items():
		if contains_month(line):
			return lines[n + 1].strip()
	return None

def get_text(lines):
	start = 0
	for n, line in lines.items():
		if ":" in line:
			start = n
			break
	lines_without_header = {line_num:line for line_num,line in lines.items() if line_num >= start}
	text = [a[1] for a in sorted(lines_without_header.items(), key=lambda x: x[0])]
	return "".join(text)

base_path = os.path.dirname(os.path.realpath(__file__))
audioJsonFile = f"{base_path}/interviewee_audio.json"
interviewee_audio_url = {}
with open(audioJsonFile, "r") as f:
	interviewee_audio_url = json.load(f)

def get_audio(interviewee, full_text):
	if interviewee is None:
		return []
	name = interviewee.lower()
	interviewee_raw_audio = None
	if name in interviewee_audio_url:
		interviewee_raw_audio = interviewee_audio_url[name]
	else:
		# try to find key
		keys = interviewee_audio_url.keys()
		similar = list(filter(lambda x:x in name or name in x, keys))
		if len(similar) == 0:
			return []
		interviewee_raw_audio = interviewee_audio_url[similar[0]]
	all_audio = []
	for raw_audio in interviewee_raw_audio:
		topic_raw = raw_audio["topic"]
		src = raw_audio["src"]
		interview_part = raw_audio["interview_part"]
		topic = " ".join(topic_raw.replace("On_", "").split("_"))
		audio = {
				"name": topic,
				"src": src,
			}
		if interview_part:
			_, start, end = search_ignore_space(interview_part, full_text)
			audio["start"] = start
			audio["end"] = end
		else:
			audio["start"] = None
			audio["end"] = None
		all_audio.append(audio)
	return all_audio

# def get_filename_from_google_drive_download(url):
# 	# https://stackoverflow.com/a/61363759
# 	res = requests.get(url)
# 	header = res.headers["Content-Disposition"]
# 	filename = re.search(r'filename="(.*)"', header).group(1)
# 	return filename 