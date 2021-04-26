from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Json
from typing import Optional, List
import json 
import random
from pathlib import Path
app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

class Interview(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    portrait: str
    thumbnail: str
    date: str
    short_bio:str
    text: str
    annotations: Json
    subjects: Optional[List[str]] = None
    

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

#TODO, change interviews to list of Interview objects, which load from TEI files in a data directory
@app.get("/")
def index(request:Request):
    #choose three random images from the photographs with a green background
    oral_histories, photographs, teaching = random.sample(photos, 3)
    context = dict(
        request=request,
        interviews=interviews,
        filters= filters,
        oral_histories= oral_histories, 
        photographs=photographs, 
        teaching=teaching)
    return templates.TemplateResponse("index.html", context)