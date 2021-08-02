import srsly
from pathlib import Path
from lunr import lunr
from tqdm import tqdm
# Generate search index for use by lunr.js https://lunr.readthedocs.io/en/latest/lunrjs-interop.html

data = Path.cwd().parents[0] / 'data'
interviews = [srsly.read_json(f) for f in tqdm(data.iterdir()) if f.is_file()]
idx = lunr(ref="name", fields=["name","text"], documents=interviews)
serialized_idx = idx.serialize()
index_path = data = Path.cwd().parents[0] / 'assets' / 'lunr' / 'interviews.json'
srsly.write_json(index_path, serialized_idx)

annos = []
ents = []
for interview in tqdm(interviews):
    for snippet in interview['annotations']: 
        if snippet['label'].isupper():
            snippet['name'] = interview['name']
            snippet['text'] = interview['text'][snippet['start']:snippet['end']]
            ents.append(snippet) 
        else:
            snippet['name'] = interview['name']
            snippet['text'] = interview['text'][snippet['start']:snippet['end']]
            annos.append(snippet)
   
idx = lunr(ref="name", fields=["label","text"], documents=annos)
serialized_idx = idx.serialize()
annos_path = data = Path.cwd().parents[0] / 'assets' / 'lunr' / 'annotations.json'
srsly.write_json(annos_path, serialized_idx)

idx = lunr(ref="name", fields=["label","text"], documents=ents)
serialized_idx = idx.serialize()
ents_path = data = Path.cwd().parents[0] / 'assets' / 'lunr' / 'ents.json'
srsly.write_json(ents_path, serialized_idx)

# lunr only returns the ids of the documents, so we need to fetch data
# for snippets, create  a json file for each with the snippet text, nave of interviewee and snippet id

# for interviews, link to the thumbnail image, search query in context in the text

#page has search bar at the top, below are two columns
# row with ents and freqs of ents, button filters search results
# left column is a list of interviews (each interview has a thumbnail image, link to the full text, and interview ents)
#  -- each interview json needs a field with ents and freqs of ents
# right column is a list of snippets (with link to the snippet in the full interview, so snippets need anchors in the interview page)
# each snippet needs a uuid

