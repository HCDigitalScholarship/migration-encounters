from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

photos = [
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


@app.get("/")
def index(request:Request):
    #choose three random images from the photographs with a green background
    oral_histories, photographs, teaching = random.sample(photos, 3)
    
    return templates.TemplateResponse("index.html", {"request": request, "oral_histories": oral_histories, "photographs":photographs, "teaching":teaching})