from fastapi import Request
from main import templates, photos 
import random 
import shutil
from pathlib import Path 

site_path = Path.cwd() / 'site'
if not site_path.exists():
    site_path.mkdir(parents=True, exist_ok=True)

def index():
    request = Request
    oral_histories, photographs, teaching = random.sample(photos, 3)
    page = templates.TemplateResponse("index.html", {"request":request,"oral_histories": oral_histories, "photographs":photographs, "teaching":teaching})
    (site_path / 'index.html').write_bytes(page.body)

if __name__ == '__main__':
    # copy assets to site 
    shutil.copytree((Path.cwd() / 'assets'), (site_path / 'assets')) 
    index()