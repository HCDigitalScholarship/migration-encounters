import srsly
from pathlib import Path
from lunr import lunr
from tqdm import tqdm
from main import load_data
# Generate search index for use by lunr.js https://lunr.readthedocs.io/en/latest/lunrjs-interop.html

data = Path.cwd() / 'data'
#interviews = [srsly.read_json(f) for f in tqdm(data.iterdir()) if f.is_file()]
interviews, _ = load_data()
interviews = [a.dict() for a in interviews]

lune_path = Path.cwd() / 'assets' / 'lunr'
if not lune_path.exists():
    lune_path.mkdir(parents=True, exist_ok=True)

idx = lunr(ref="name", fields=["name","text"], documents=interviews)
serialized_idx = idx.serialize()
index_path = data = Path.cwd() / 'assets' / 'lunr' / 'interviews.json'
srsly.write_json(index_path, serialized_idx)

# process student hypothesis annotations and sentence spans
#Change so that we're reading the ids from the data folder
annos = []
sents = []

for interview in tqdm(interviews):
    for snippet in interview['annotations']: 
        if snippet['label'] == 'SENT':
            #snippet['id'] = interview['id']    
            snippet['name'] = interview['name']
            snippet['text'] = interview['text'][snippet['start']:snippet['end']]
            sents.append(snippet) 
        else:
            #snippet['id'] = interview['id']
            snippet['name'] = interview['name']
            snippet['text'] = interview['text'][snippet['start']:snippet['end']]
            annos.append(snippet)
   
idx = lunr(ref="id", fields=["label","text"], documents=annos)
serialized_idx = idx.serialize()
annos_path = data = Path.cwd() / 'assets' / 'lunr' / 'annotations.json'
srsly.write_json(annos_path, serialized_idx)

quotes_path = Path.cwd() / 'assets' / 'quotes'
if not quotes_path.exists():
    quotes_path.mkdir(parents=True, exist_ok=True)

print('writing quote json files')
for quote in tqdm(annos):
    quote_path = quotes_path / quote['id']
    srsly.write_json(quote_path, quote) 

# create lookup for labels and quote files
data = {}
for quote in tqdm(annos):
    if quote['label'] not in list(data.keys()):
        data[quote['label']] = [quote['id']]
    else:
        data[quote['label']].append(quote['id'])

srsly.write_json((quotes_path / 'quote_lookup.json'), data)

### SENTS

idx = lunr(ref="id", fields=["name","text"], documents=sents)
serialized_idx = idx.serialize()
ents_path = data = Path.cwd() / 'assets' / 'lunr' / 'sents.json'
srsly.write_json(ents_path, serialized_idx)

sents_path = Path.cwd() / 'assets' / 'sents'
if not sents_path.exists():
    sents_path.mkdir(parents=True, exist_ok=True)



print('writing sent json files')
for sent in tqdm(sents):
    sent_path = sents_path / (sent['id'] + '.json')
    srsly.write_json(sent_path, sent) 

# lunr only returns the ids of the documents, so we need to fetch data
# for snippets, create  a json file for each with the snippet text, nave of interviewee and snippet id

# for interviews, link to the thumbnail image, search query in context in the text

#page has search bar at the top, below are two columns
# row with ents and freqs of ents, button filters search results
# left column is a list of interviews (each interview has a thumbnail image, link to the full text, and interview ents)
#  -- each interview json needs a field with ents and freqs of ents
# right column is a list of snippets (with link to the snippet in the full interview, so snippets need anchors in the interview page)
# each snippet needs a uuid

# The shuffle grid on index.html loads from a json file with the name and labels of each interview
def make_shuffle_json(): 
    interviews, subjects = load_data()
    result = {}
    outs = []
    for i in tqdm(interviews):
        meow = {"name":i.name, "date":i.date,"location":i.location,"thumbnail":i.thumbnail}
        annos = [a['label'] for a in i.annotations if a['label'] != 'SENT']
        meow.update({'labels':list(set(annos))})
        outs.append(meow)
    # Sort interviews alphabetically by name
    outs = sorted(outs, key = lambda i: i['name'])
    result.update({'interviews':outs})
    result.update({'subjects':subjects})
    #result.
    data_path = Path.cwd() / 'assets' / 'lunr'/ 'shuffle.json'
    srsly.write_json(data_path, result)
make_shuffle_json()
