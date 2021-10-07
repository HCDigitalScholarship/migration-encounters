from os import terminal_size
import spacy
from pydantic import BaseModel, Json
from typing import Optional, List
from pathlib import Path
from utils.hypothesis import collect_annotations as get_hypothesis_annotations
from tqdm import tqdm
import srsly 
import uuid 
nlp = spacy.load('en_core_web_trf')
#nlp.add_pipe('dbpedia_spotlight', config={'language_code': 'en'})

data_dir = Path.cwd() / 'data'
text_dir = Path.cwd() / 'texts'
portrait_dir = Path.cwd() /  'assets' / 'img' /'portraits'
thumbnail_dir = Path.cwd() /  'assets' / 'img' /'thumbnails'
portraits = srsly.read_json('./data_migration/participants.json')
from main import Interview


def get_text(stem:str):
    text = [f.read_text() for f in text_dir.iterdir() if f.stem == stem]
    if text:
        text = text[0]
    else:
        text = ''
    return text

def get_annotations(text:str, ENTS=False, SENTS=True):
    doc = nlp(text)
    annotations = []
    if ENTS:
        for ent in doc.ents:
            annotation = dict(
                type='text',
                start=ent.start_char, 
                end=ent.end_char, 
                text=ent.text, 
                label=ent.label_)
            annotations.append(annotation)
    if SENTS:
        for sent in doc.sents:
            sent_id = str(uuid.uuid4())
            # params id is used by displacy 
            sent_dict = dict(start=sent.start_char, end=sent.end_char, label="SENT",type="sent", text=sent.text)
            annotations.append(sent_dict)

    
    return annotations

def make_interviews(): 
    interviews = []
    for person in portraits.keys(): 
      
        i = Interview(
            name=portraits[person]['name'],
            date=portraits[person]['date'],
            portrait=portraits[person]['image'],
            thumbnail=portraits[person]['thumbnail'],
            interviewer=portraits[person]['interviewer'],
            location=portraits[person]['location'],
            text=get_text(person),
            annotations = [],
            audio=portraits[person]['audioParts'],
        )
        i.annotations.extend(get_annotations(get_text(person)))
        i.annotations.extend(get_hypothesis_annotations(i.name))
        
        # TODO remove error messages from hypothesis, temporary fix
        # get_hypothesis_annotations returns 'e','r','r','o','r'
        i.annotations = [a for a in i.annotations if isinstance(a,dict)]

        # add span ids
        for annotation in i.annotations:
            span_id = str(uuid.uuid4())
            annotation.update({'id':span_id, 'params':{'id':span_id}})
        
        
        interviews.append(i)
    assert len(interviews) == len(portraits.keys())
    print(f"🥳 Created {len(interviews)} interview objects")
    return interviews



if __name__ == '__main__':
    interviews = make_interviews()
    for interview in tqdm(interviews):
        file = (data_dir /(interview.name + '.json'))
        file.write_text(interview.json())
    
    #TODO add make_index so that both are run?