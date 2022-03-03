import uuid
import requests
import re
import json
import os
from utils import search_ignore_space, find_fuzzy_match, find_semantic_match

base_path = os.path.dirname(os.path.realpath(__file__))
annotationJsonFile = f"{base_path}/interviewee_annotation_url.json"
interviewee_annotation_url = {}
with open(annotationJsonFile, "r") as f:
	interviewee_annotation_url = json.load(f)

def get_annotations(interviewee, full_text):
	uri = interviewee_annotation_url.get(interviewee, None)
	if uri is None:
		return []
	base_url = "https://api.hypothes.is/api/search"
	url = f"{base_url}?uri={uri}"
	res = requests.get(url)
	annotations_raw = res.json()
	annotations = parse_annotations(annotations_raw, full_text)
	return annotations

def parse_annotations(annotations_raw, full_text):
	annotations_all = []
	rows = annotations_raw["rows"]
	for data in rows:
		annotation_text = data["text"]
		tags = data["tags"]
		for target in data["target"]:
			exact_text_from_api = target["selector"][2]["exact"]
			_, start, end = search_ignore_space(exact_text_from_api, full_text)
			
			id = str(uuid.uuid4())

			annotation = {
				"id": id,
				"type": "text",
				"start": start,
				"end": end,
				"label": tags,
				"params": {
					"id": id,
					"class": "anno"
				},
				"text": annotation_text,
			}
			annotations_all.append(annotation)
	bank = open("../index_themes.txt").read().splitlines()
	for idx, annotation in enumerate(annotations_all):
		annotation_text_and_tags = [annotation["text"], *annotation["label"]]
		matched_parts = []
		for text in annotation_text_and_tags:
			text_parts = re.split(",|;|\n", text)
			for phrase in text_parts: 
				if len(phrase) == 0:
					continue
				fuzzy_match = find_fuzzy_match(phrase, bank, 0.85)
				if fuzzy_match is not None:
					matched_parts.append(fuzzy_match)
					continue
				semantic_match = find_semantic_match(phrase, bank, 0.7)
				if semantic_match is not None:
					matched_parts.append(semantic_match)
					continue
				matched_parts.append(phrase)
		del annotations_all[idx]["text"]
		annotations_all[idx]["label"] = ",".join(matched_parts)
	return annotations_all