from fastapi import FastAPI, Request,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Json
from typing import Optional, List
from functools import cache
import json 
import spacy
from spacy import displacy
from spacy.displacy import EntityRenderer,parse_ents
from spacy.lang.en import English
import uuid
import random
import srsly
from pathlib import Path
import re
from markupsafe import Markup, escape

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

#Register custom filter to convert \n to <br>
def nl2br(value):
    br = "<br>\n"
    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}<\p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return result
templates.env.filters['nl2br'] = nl2br

# def textrank_me(item:dict):
#     text = item['name']
#     nlp = spacy.load("en_core_web_sm")
#     nlp.add_pipe("textrank")
#     doc = nlp(text)
#     # TODO add item annotations to doc.ents

#     # examine the top-ranked phrases in the document
#     for phrase in doc._.phrases:
#         print(phrase.text)
#         print(phrase.rank, phrase.count)
#         print(phrase.chunks)



class Interview(BaseModel):
    name: str
    date: str
    location: str
    interviewer: str
    portrait: str
    thumbnail: str
    text: Optional[str] = ''
    annotations: List[dict] #for both audio, text and images
    audio: Optional[List[dict]] = None
    subjects: Optional[List[str]] = None

@cache
def load_data():
    interviews = []
    subjects = []
    data_dir = Path.cwd() / 'data'  
    for item in data_dir.iterdir():
        data = srsly.read_json(item)
        if data:
            i = Interview(**data)
            i.subjects = list(set([a['label'] for a in i.annotations if a['label'] !='SENT']))
            interviews.append(i)
            subjects.extend(i.subjects)
        else:
            print('error',data)
    return interviews, list(set(subjects))

green = [
        "Abel_6-2-2019_Portrait.jpg", #
        #"Angelo_6-2-2019_Portrait.jpg",
        "Bernabe_6-1-2019_Portrait.jpg", #
        #"Billy_6-4-2019_Portrait.jpg",
        "Cuauhtemoc_6-9-2019_Portrait.jpg", #
        "Daniel_6-3-2019_Portrait.jpg", #
        "Diana_6-6-2019_Portrait.jpg",
        "Hugo_6-9-2019_Portrait.jpg", ##
        #"Frank_6-8-2019_Portrait.jpg",
        'Laura_1_6-10-2019_Portrait.jpg', #
        #"Lucero_6--2019_Portrait.jpg",
        "Miguel_3_6-10-2019_Portrait.jpg", #
        #"Olimpya_6-7-2019_Portrait.jpg",
        "Roberto_6-3-2019_Portrait.jpg", ##
        #Yosell_6-12-2019_Portrait.jpg",
        "Zayuri_6-10-2019_Portrait.jpg",
        ]
brick = [
        "Ivan_6-3-2019_Portrait.jpg",
        "Jeimmy_6-17-18_Portrait.jpg", 
        "Jesus_1_6-5-2019_Portrait.jpg", 
        "Jesus_3_6-5-2019_Portrait.jpg",
        "Joana_6-8-2019_Portrait.jpg"
        ]
photos = brick

interviews = Path.cwd() / "assets"/ "img" / "thumbnails"
interviews = [{"file":a.name,"title":a.stem,"subjects":"","date":2018} for a in interviews.iterdir()]
#add random subjects 
temp = ["Migration","Mexico City","ICE","California", "Nogales", "Dallas"]
for i in interviews:
    eek = random.randrange(len(temp))
    i['subjects'] = f'"[{temp[eek]}]"'

filters = temp


def add_spans_to_text(interview:Interview):
    renderer = EntityRenderer()
    renderer.colors = {"PERSON": "#03fc41", "SENT":"transparent" }
    renderer.ent_template = """<span id="{id}" style="background: {bg}" class="entity" value="{label}">{text}</span>"""
    parsed = dict(text=interview.text,ents=interview.annotations, title=interview.name, settings={'lang': 'en', 'direction': 'ltr'})
    return renderer.render([parsed], page=False, minify=False).strip()
    


#TODO, change interviews to list of Interview objects, which load from TEI files in a data directory
@app.get("/")
def index(request:Request):
    #choose three random images from the photographs with a green background
    oral_histories, photographs, teaching = random.sample(photos, 3)
    interviews, subjects = load_data()
    context = dict(
        request=request,
        interviews=interviews,
        filters= filters,
        oral_histories= oral_histories, 
        photographs=photographs,
        subjects=subjects, 
        teaching=teaching)
    return templates.TemplateResponse("index.html", context)

@app.get("/interview/{person}.html")
def interview(request:Request,person:str):
    context = {}
    context['request'] =request
    interviews, subjects = load_data()
    person = [i for i in interviews if i.name.lower() == str(person).lower()]
    context['person'] = person[0]
    #mark_sentence_spans_with_ids(person[0])
    context['text'] = add_spans_to_text(person[0])
    return templates.TemplateResponse("interview.html", context)

@app.get("/interview_json/{person}")
def interview_json(person:str):
    interviews, subjects = load_data()
    person = [i for i in interviews if i.name.lower() == str(person).lower()]
    if person:
        return person[0]
    else: 
        raise HTTPException(status_code=404, detail="Interview not found")

@app.get("/search")
def search(request:Request, q:str=None):
    return templates.TemplateResponse("search.html", {'request': request})


@app.get("/add_interview")
def add_interview(request:Request):
    return templates.TemplateResponse("add_interview.html", {'request': request})

